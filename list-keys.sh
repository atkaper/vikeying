#!/bin/bash

echo "Note: keycode 66 is your physical caps-lock key, and keycode 127 is your pause key."
echo "The list below shows what meaning is connected to the keys:"
echo

# show some of the keys to see what state we are in
xmodmap -pke | grep -i -e \ 66 -e 127 -e caps -e control -e \ pause -e caps
