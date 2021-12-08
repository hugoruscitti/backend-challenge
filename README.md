# Backend Challenge

## How to run the project

First, create a python virtual enviroment with
this commands:

```
python3 -m venv venv
. venv/bin/activate
```

Then, install dependencies, run migrations and start
the web server:

```
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver
```

Lastly, to create a super user run this command:

```
python manage.py createsuperuser
```


## Examples

To obtain a token:

```
curl -X POST -d "username=test&password=test12******" \
  http://localhost:8000/api-token-auth/

{"token":"99780545172d51704108f268dc01ab53b6f2dea0"}
```

Then, use that token to create a product:

```
curl \
  -X POST -d "name=test&price=10.0&stock=20" \
  http://localhost:8000/api/products/ \
  -H 'Authorization: Token 99780545172d51704108f268dc01ab53b6f2dea0'

{"id":3,"name":"test","price":10.0,"stock":20}
```

Or simply call get to list all products:

```
curl \
  http://localhost:8000/api/products/ \
  -H 'Authorization: Token 99780545172d51704108f268dc01ab53b6f2dea0'

[{"id":4,"name":"test","price":10.0,"stock":20}]
```
