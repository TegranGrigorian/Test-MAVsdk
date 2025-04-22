#!/bin/bash
# install script for jetson
echo "Installing jetson script, please enter y if you wan to proceed"
read -p "Do you want to proceed? (y/n): " answer
if [[ $answer != "y" ]]; then
    echo "Installation aborted."
    exit 1
fi
echo "Installing jetson script..."
echo "DO NOT CTRL+C THIS SCRIPT"
echo "this script will ask for sudo"
sleep 2
echo "Installing dependencies..."
#update apt
sudo apt update
#install python3-virutalenv
sudo apt install python3-venv -y

#setup virtualenv
virtualenv .venv --python=python3
sleep 1 #give time for virtualenv to set up??
source .venv/bin/activate

#install requirements for jetson
if [ ! -f "requirements_jetson.txt" ]; then
    echo "Creating requirements_jetson.txt file..."
    echo "flask==2.3.3" > requirements_jetson.txt
    echo "requests==2.31.0" >> requirements_jetson.txt
fi
#install requirements
pip install -r requirements_jetson.txt
#install should be complete
echo "Installation completed."

#install should be completed no need for hidden.py file
echo "run jetson.py to start the jetson script"
echo "You can now run the jetson script using the command 'python jetson.py'"

#bug happens with source .venv/bin/activate
echo "bug happens with source .venv/bin/activate"
echo "run 'source .venv/bin/activate' to activate the virtualenv"
source .venv/bin/activate
