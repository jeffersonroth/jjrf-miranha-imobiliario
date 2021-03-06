"""Flask app."""

import json
import logging
import os
import sys
from threading import Thread
from time import sleep
from markupsafe import Markup
import traceback

from flask import Flask, request, render_template, jsonify, send_from_directory, Blueprint
from pymongo.errors import PyMongoError
from werkzeug.exceptions import HTTPException

from utils.mongo import get_client, setup_db
from scraper import states_collection, cities_collection, houses_collection

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

sleep(15)
setup_db()


@app.route('/static/images/favicon.ico')
def static_favicon_ico():
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.png',
                               mimetype='image/x-icon')


@app.route('/static/images/favicon.png')
def static_favicon_png():
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.png',
                               mimetype='image/png')


@app.route('/static/css/<file>')
def static_css(file):
    return send_from_directory(os.path.join(app.root_path, 'static/css'), file,
                               mimetype='text/css')


@app.route('/')
@app.route('/endpoints')
@app.route('/endpoints/queryHouses')
def app_index():
    try:
        cities_count = get_client()["mcmakler"]["cities"].count_documents({})
        app.logger.info(f"cities_count: {cities_count}")
        if cities_count < 1:
            states_collection()
            cities_collection()
        states = get_client()["mcmakler"]["cities"].distinct("state")
        app.logger.info(f"states: {states}")
        optgroups = ""
        for state in states:
            cities = get_client()["mcmakler"]["cities"].distinct("city", {"state": state})
            if len(cities) < 1:
                states_collection()
                cities_collection()
                cities = get_client()["mcmakler"]["cities"].distinct("city", {"state": state})
            app.logger.info(f"cities: {cities}")
            cities_options = "".join(
                [f'<option class="navbar-item">{city}</option>' for city in cities if len(cities) > 0])
            optgroups += f'<optgroup class="navbar-item" label="{state}">{cities_options}</optgroup>' if len(
                cities) > 0 else ""

        cities_markup = Markup(optgroups)

        object_types = get_client()["mcmakler"]["houses"].distinct("object_type")
        object_options = "".join(
            [f'<option class="navbar-item">{obj}</option>' for obj in object_types if len(object_types) > 0])
        object_markup = Markup(
            f'<optgroup class="navbar-item" label="Objekttyp">{object_options}</optgroup>' if len(
                object_types) > 0 else "")

        return render_template("queryHouses.html", cities=cities_markup, object_types=object_markup)

    except PyMongoError as error:
        traceback.print_exc()
        handle_exception(HTTPException(status_code=500, response=error))
        return render_template("errors.html", giphy_query="my+bad", error_title="Error 500", error_message=error), 500

    except Exception as error:
        traceback.print_exc()
        return render_template("errors.html", giphy_query="my+bad", error_title="Error 500", error_message=error), 500


@app.route('/queryHouses', methods=['POST'])
def query_houses():
    try:
        queries = json.loads(request.data)
        app.logger.info(queries)
        filters = {"$and": []}
        if "state" in queries and "city" in queries and queries["state"] is not None and queries["city"] is not None:
            filters["$and"].append({"state": queries["state"]})
            filters["$and"].append({"city": queries["city"]})
        if "object_type" in queries and queries["object_type"] is not None:
            filters["$and"].append({"object_type": queries["object_type"]})
        price_min = None
        if "price_min" in queries and queries["price_min"] is not None and float(queries["price_min"]) > 0:
            price_min = float(queries["price_min"])
        price_max = None
        if "price_max" in queries and queries["price_max"] is not None and float(queries["price_max"]) > 0:
            price_max = float(queries["price_max"])
        if price_min is not None and float(price_min) > 0:
            filters["$and"].append({"purchase_price": {"$gte": float(price_min)}})
        if price_max is not None and float(price_max) > 0 and (
                price_min is None or float(price_max) >= price_min):
            filters["$and"].append({"purchase_price": {"$lte": float(price_max)}})
        if len(filters["$and"]) < 2:
            filters = filters["$and"][0] if len(filters["$and"]) == 1 else {}
        sort_by = "house_url"
        if "sort_by" in queries and queries["sort_by"] in ["house_url", "object_type", "purchase_price"]:
            sort_by = queries["sort_by"]
        direction = 1
        if queries["sort_asc"] is not None:
            direction = -1 if bool(queries["sort_asc"]) is False else 1
        app.logger.info(f"filters: {filters}")
        houses_cursor = get_client()["mcmakler"]["houses"].find(filters).sort(key_or_list=sort_by, direction=direction)
        houses = []
        for house in houses_cursor:
            houses.append({
                "url": house["house_url"],
                "state": house["state"],
                "city": house["city"],
                "object_type": house["object_type"],
                "purchase_price": house["purchase_price"],
                "living_space": house["living_space"],
                "purchase_price_sqm": house["purchase_price_sqm"],
                "available_from": house["available_from"]
            })
        app.logger.info(houses)

        return jsonify({"message": houses})

    except PyMongoError as error:
        traceback.print_exc()
        handle_exception(HTTPException(status_code=500, response=error))

    except Exception as error:
        traceback.print_exc()
        return jsonify({"message": {"error": error}})


@app.route('/scrapeHouses', methods=['POST'])
def scrape_houses():
    def do_work(value):
        states_collection()
        cities_collection()
        houses_collection()
        sleep(value)

    thread = Thread(target=do_work, kwargs={'value': request.args.get('value', 20)})
    thread.start()
    return jsonify({"message": "Scraping!"})


@app.route('/start')
@app.route('/endpoints/scrapeHouses')
def scrape_houses_endpoint():
    return render_template("scrapeHouses.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors.html", giphy_query="not+found", error_title="Error 404", error_message=error), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("errors.html", giphy_query="my+bad", error_title="Error 500", error_message=error), 500


@app.errorhandler(HTTPException)
def handle_httpexception(error):
    """Return JSON instead of HTML for HTTP errors."""
    response = error.get_response()
    response.data = json.dumps({
        "code": error.code,
        "name": error.name,
        "description": error.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(Exception)
def handle_exception(error):
    # pass through HTTP errors
    if isinstance(error, HTTPException):
        response = error.get_response()
        response.data = json.dumps({
            "code": error.code,
            "name": error.name,
            "description": error.description,
        })
        response.content_type = "application/json"
        return response

    # now you're handling non-HTTP exceptions only
    return render_template("errors.html", giphy_query="my+bad", error_title=f"Error {error.name} ({error.code})",
                           error_message=error), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
