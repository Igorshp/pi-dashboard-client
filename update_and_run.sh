#!/bin/bash

# this script pulls latest version from git and runs client.py
# it's launched with systemd on the pi to make upgrades easy

git reset --hard
git checkout master
git pull 

echo "Setting up virtualenv"
virtualenv --python="$(command -v python3)" .virtualenv 
source .virtualenv/bin/activate

pip install -r requirements.txt

echo "Running client.py"
python3 client.py
