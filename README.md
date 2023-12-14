# Team Newt Small Group project

## Team members

The members of the team are:

- Adil Khan
- Muhammad Khan (Ali)
- Munye Jeilani
- Yusuf Yusuf

## Project structure

The project is called `task_manager`. It currently consists of a single app `tasks`.

## Deployed version of the application

The deployed version of the application can be found at [http://ak0345.pythonanywhere.com/dashboard/](http://ak0345.pythonanywhere.com/dashboard/).

## Installation instructions

To install the software and use it in your local development environment, you must first set up and activate a local development environment. From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:

```
$ python3 manage.py test
```

_The above instructions should work in your version of the application. If there are deviations, declare those here in bold. Otherwise, remove this line._

## Sources

The packages used by this application are specified in `requirements.txt`

For highlighting the search result matches in yellow: https://medium.com/geekculture/how-to-highlight-a-keyword-inside-a-text-in-a-django-search-6a8e33cc8496

Home page graphics: https://undraw.co/
