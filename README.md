# flask-api-example

This repo contains the code illustrated in tutorial https://atifazad.com/tutorials/build-api-with-python-flask/


## Quick Setup
If you want to execute the app without going through the steps illustracted in tutorial, do following...

1. Clone this repo.
2. Create vitual environment.
(https://atifazad.com/tutorials/how-to-setup-virtualenvwrapper-on-macos-catalina/)
3. Copy `.env.example` to `.env` file.
4. Create a PostgreSQL DB and add the required values in `.env` file.
(You can use DB other than PostgreSQL but for that you'll have to make appropriate changes in `.env` and `config.py`)
5. Install dependencies
```
> pip freeze > requirements.txt
```
6. Run the application
```
> flask run
```
7. Test the APIs using Postman or any other api client tool. 
https://atifazad.com/tutorials/build-api-with-python-flask/#test-endpoints
