# keyword-mining
API to extract keywords from a text.

The algorithm extracts the main nominal groups (relevant keywords) from the text and, for each one, attribute a score based on multiple parameters including the number of occurrences.

## INSTALL
```
pip install -r requirements.txt
FLASK_APP=index.py flask run
```

To launch in debug mode :
```
FLASK_APP=index.py FLASK_DEBUG=1 flask run
```

To list all services of API, type this endpoint in your web browser : "http://localhost:5000/"

## USAGE AND EXAMPLE
The example below shows how to extract keywords from an English text with cURL :
```
curl http://localhost:5000/keywords --data-urlencode "text=Machine Learning is the subfield of computer science that, according to Arthur Samuel in 1959, gives computers the ability to learn without being explicitly programmed." --data "language=en"
```

The result is a list of keywords in a JSON dictionary :
```
{
  "keywords": [
    "Arthur Samuel",
    "subfield of computer science",
    "Machine Learning"
  ]
}
```

## NOTE
This API works with Python2.5+ but not Python3+.
