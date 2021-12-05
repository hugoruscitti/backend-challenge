# Backend Challenge

## How to run the project

First, create a python virtual enviroment with
this commands:

```
python3 -m venv venv
. venv/bin/activate.fish
```

Then, install dependencies, run migrations and start
the web server:

```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
