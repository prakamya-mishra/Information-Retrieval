#!/bin/bash

source ENV/bin/activate
pipreqs --force . --ignore ENV 
pip install -r requirements.txt
if [ -z "$1" ]
  then
    echo -e "\e[0;31mNo File Selected.\e[0m \nCommand should be of format: \e[0;32m/path/to/run.bash <file>\e[0m"
  else
    python $1
fi
deactivate
