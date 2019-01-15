#!/bin/bash

# Install virtualenv
python3 -m pip install -U virtualenv

# Set up virtualenv for the project
python3 -m virtualenv ENV
source ENV/bin/activate
pip install pipreqs
pip install nltk
python -m nltk.downloader -d ./ENV/nltk_data all
deactivate

# Run program
./run.bash