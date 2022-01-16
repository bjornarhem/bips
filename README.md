# bips: Interview scheduling tool

This is an application for scheduling interviews. Was used in UKA-19 and UKA-21 to schedule interviews for UKAs ~2000 volunteers.

## Setup

Clone the repo, and in the root repo, run:

```
python3 -m venv venv
source venv/bin/active
pip3 install -r requirements.txt
python3 manage.py migrate
```

### Inserting data

To insert interview data you can use the built in Django admin web interface, by first creating a user with

`DJANGO_SUPERUSER_PASSWORD=admin python3 manage.py createsuperuser --no-input --username admin --email null@gmail.com`,

and then running the web app locally with

`python3 manage.py runserver`.

Now you can go to `localhost:8000/admin`, log in with admin/admin, and editing the interview data as you like.

Alternatively, you can insert the data with the Django shell, by running `python3 manage.py shell`. Or, if you prefer SQL, you can use a CLI like `sqlite3` to edit the file `db.sqlite3`.

### Schedule interviews

To run the interview scheduling script, run

`python3 manage.py schedule_interviews`,

which will run the interview scheduling algorithm, and give the user the option to save the result to the database.

## Contact

For questions, suggestions, bug reports or general feedback, feel free to contact me at bjornarhem@gmail.com.
