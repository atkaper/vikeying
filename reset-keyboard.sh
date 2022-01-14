#!/bin/bash

# Kill the python script (note: needs ROOT do do this!)
sudo pkill -e vikeying.py

# Reset keyboard definitions to default
setxkbmap -option ""
