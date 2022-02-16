### Description

Python app that scrapes McMakler website, and offer an API endpoint to query the data.
Miranha comes from the way brazilians refer to Spideman, so Miranha Imobiliario would almost translate to "Real-Estate-Broker-Spiderman".

### Objective

Develop a solution that crawls a website, collects specific data from the response, stores it in a database and provides a REST API.

### Brief

The following data must be collected from the [McMakler](https://www.mcmakler.de/immobilien) website:

- Objekttyp (Object type)
- Wohnfläche (Living space)
- Kaufpreis (Purchase price)
- Kaufpreis pro qm (Purchase price per sqm)
- Verfügbar ab (Available from)
- URLs

The API provides the following:

- A search endpoint for all entries.
	- Both "Object type" and/or "Purchase price" fields can be used as filters.
	- Both "Object type" and "Purchase price" fields must be sortable.

### Architecture

The solution consists of a Python Flask app, Selenium and MongoDB.

### Getting started

- Docker-compose: $ docker-compose -f docker-compose.yml up --build

- Navigate to [Scraper page](http://localhost:5000/start), and click the button "Start Scrapping!". The scrapper will run on background. The process might take several hours to complete.

- Navigate to [queryHouses Sandbox page](http://localhost:5000/endpoints/queryHouses), there you¿ll find some basic documentation and a Sandbox, to generate POST request body from form, and to see the API en action, by clicking "Try it!". The button might retrieve results after approx 15 after clicking "Start Scrapping!" in the last step. 

