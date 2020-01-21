#!/bin/bash

# this script pulls latest version from git and runs client.py
# it's launched with systemd on the pi to make upgrades easy

git reset hard
git pull origin/master

pip3 install -r requrements.txt

python3 client.py
