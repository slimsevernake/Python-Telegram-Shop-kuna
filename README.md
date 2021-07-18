* Pre-requirments:
- python3.8
- python3-venv
- python3-pip
- sqlite3



* Install process
- (Optional) Install or check installed pachages for Ubuntu.
- sudo apt install -y python3, python3-pip, python3-venv, sqlite3
- Create virtual environment
- python3 -m venv venv
- Activate virtual environment
- source ./venv/bin/activate
- Install python packages
- python3 -m pip install -r requirements.txt
- Exit virtual environment
- deactivate
- Create empty from database from dump
- echo ".read dump.sql" | sqlite3 database.sqlite



* Runnning
- Activate virtual environment
- source ./venv/bin/activate
- Run the program
- python3 main.py
