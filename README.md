### Objective

Your challenge is to develop a solution that crawls a website, collects specific data from the response, stores it in a database and provides a REST API.

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

#### Additional details

- You can use any languages and frameworks of your choice.
- You can use any type of database of your choice.
- Stored data must be available via the API.
- No UI is required. 
- Make sure the URL of the property (immobilien) is included to enable comparison to the original.

### Evaluation Criteria

- Overall solution design
- Coding standards and conventions
- Testing strategy
- Project documentation

### Deliverables

Make sure to include all source code in the repository.

### CodeSubmit

Please organize, design, test, and document your code as if it were going into production - then push your changes to the master branch. After you have pushed your code, you may submit the assignment on the assignment page.

All the best and happy coding,

The MAYD Group GmbH Team

### Architecture

The solution consists of a Python Flask app, Selenium and MongoDB.

### Getting started

- Create Docker network: $ docker-compose -f docker-compose.yml up --build

- Navigate to [Scraper page](http://localhost:5000/start), and click the button "Start Scrapping!". The scrapper will run on background. The process might take several hours to complete.

- Navigate to [queryHouses Sandbox page](http://localhost:5000/endpoints/queryHouses), there you¿ll find some basic documentation and a Sandbox, to generate POST request body from form, and to see the API en action, by clicking "Try it!". The button might retrieve results after approx 15 after clicking "Start Scrapping!" in the last step. 

