#!/bin/bash
#insall script for server

echo "Installing server script, please enter y if you wan to proceed"
read -p "Do you want to proceed? (y/n): " answer
if [[ $answer != "y" ]]; then
    echo "Installation aborted."
    exit 1
fi
echo "Installing server script..."
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
source .venv/bin/activate

#install requirements for server
if [ ! -f "requirements_server.txt" ]; then
    echo "Creating requirements_server.txt file..."
    echo "flask==2.3.3" > requirements_server.txt
    echo "requests==2.31.0" >> requirements_server.txt
fi

#install should be complete
echo "Installation completed."

#need to create hidden py file
echo "Creating hidden py file..."
touch hidden.py
echo "hidden.py file created."
echo "created a class in the hidden.py file"
echo "class HiddenClass:" >> hidden.py
echo "    def __init__(self):" >> hidden.py
echo "        self.jetson_ip = '' # enter your jetson ip here" >> hidden.py
echo "        self.flight_path = []" >> hidden.py
echo "        self.mission_data = None" >> hidden.py

echo "hidden.py file set up complete."

#tell user to enter their jetson ip
echo "Please enter your jetson ip in the hidden.py file"
echo "You can use the command 'nano hidden.py' to edit the file"
sleep 2

read -p "You understand you need to enter in the ip? (y/n): " answer
if [[ $answer != "y" ]]; then
    echo "ERROR: You need to enter your jetson ip in the hidden.py file"
    exit 1
fi
sleep 2
echo "You can now run the server using the command 'python web_server.py'"