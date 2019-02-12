#!/bin/bash

source ENV/bin/activate
pipreqs --force . --ignore ENV 
pip install -r requirements.txt

if [[ ( -n "$2" ) && ( "$2" = "y" ) ]]
  then
    echo -e "Executing a \e[0;31mclean\e[0m run!!"
    sudo rm *.obj
  else
    echo -e "Executing a \e[0;33mnormal\e[0m run!!" 
fi

if [ -z "$1" ]
  then
    echo -e "\e[0;31mNo File Selected.\e[0m \nCommand should be of format: \e[0;32m/path/to/run.bash <file> <y for clean run>\e[0m \n"
  else
    python $1
fi
deactivate
