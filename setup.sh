#!/bin/bash


pip install -r requirements.txt
python app/manage.py migrate

# password: admin
python app/manage.py loaddata fixtures.json