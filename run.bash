#!/bin/bash

source ENV/bin/activate
pipreqs --force . --ignore ENV 
pip install -r requirements.txt
python main.py
deactivate