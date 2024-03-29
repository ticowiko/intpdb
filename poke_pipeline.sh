#!/usr/bin/env bash

rm -rf pokemon/migrations/*;
touch pokemon/migrations/__init__.py;
sudo -u postgres dropdb intpdb --if-exists;
sudo -u postgres dropuser intpdb_user --if-exists;
sudo -u postgres createuser intpdb_user -P;
sudo -u postgres createdb -O intpdb_user intpdb;
python3 manage.py makemigrations;
python3 manage.py migrate;
#python3 manage.py fetch_pokemon_data;
#python3 manage.py fetch_pokemon_sprites;
python3 manage.py fill_pokemon_db_with_presets;
python3 manage.py fill_pokemon_db_from_data;
python3 manage.py post_process_pokemon_db;
