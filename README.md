In development mode, the app expects a local postgresql server running with the following credentials :

Database name : 'intpdb'

Database user : 'intpdb_user'

Password : 'pw'

Once that's up, you should be able to run `poke_pipeline.sh`, which should take quite a while to run but will set everything up for you.

At that point, it's the usual. Start up the server with `python3 manage.py runserver` and go to `localhost:8000` on your browser.
