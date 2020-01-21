#!/bin/bash

# this script pulls latest version from git and runs client.py
# it's launched with systemd on the pi to make upgrades easy

git reset --hard
git checkout master
git pull 

pip3 install -r requirements.txt

python3 client.py
