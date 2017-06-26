# keyword-mining
API to extract keywords from a text (document, press article, ...).

The algorithm extracts the main nominal groups (relevant keywords) and, for each one, attribute a score based on multiple parameters including the number of occurrences.

## INSTALL
```
pip install -r requirements.txt
FLASK_APP=index.py flask run
```

To launch in debug mode :
```
FLASK_APP=index.py FLASK_DEBUG=1 flask run
```

## USAGE
To list all services of API, type this endpoint in your web browser : "http://localhost:5000/"

## NOTE
This API works only with Python2.5+ but not Python3.
