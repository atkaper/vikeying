#!/bin/bash

# You can pass in a parameter "nopause" to skip mapping pause to caps-toggle.
# For the rest, the script will check two flags in the python script:
# - CAPS_DOES_CONTROL_KEY - if True, then python does control, if False, then xmodmap will handle control on capskey.
# - DISPLAY_DEBUG_INFO - if True, process will start in foreground, if False, process will start in background.

# CD to the script folder (in case an absolute path was used to start this)
cd $(dirname $(readlink -f $0))

# Reset all keyboard keys to default
setxkbmap -option ""

# The next quadruple "IF/ELSE" will execute only one of the xmodmap commands, depending on situation.
if [ "$1" == "nopause" ]
then
   # Check the caps flag
   grep '^\s*CAPS_DOES_CONTROL_KEY' vikeying.py | grep "=" | grep -qi "true"
   if [ "$?" == "0" ]
   then
      # Reconfigure caps-lock to do nothing, and do not touch the pause key (you can use left-alt + caps-lock to toggle caps-lock state)
      xmodmap -e 'clear lock' -e 'clear control' -e 'keysym Caps_Lock ='
   else
      # Reconfigure caps-lock to be a control key, and do not touch the pause key (you can use left-alt + caps-lock to toggle caps-lock state)
      xmodmap -e 'clear lock' -e 'clear control' -e 'keysym Caps_Lock = Control_L' -e 'add control = Control_L Control_R'
   fi
else
   # Check the caps flag
   grep '^\s*CAPS_DOES_CONTROL_KEY' vikeying.py | grep "=" | grep -qi "true"
   if [ "$?" == "0" ]
   then
      # Reconfigure caps-lock to do nothing, and set pause to do caps-lock-toggle.
      xmodmap -e 'clear lock' -e 'clear control' -e 'keysym Caps_Lock =' -e 'keysym Pause = Caps_Lock'
      # I was thinking we would need to "add lock" also, but it seems to work without also.
      #xmodmap -e 'clear lock' -e 'clear control' -e 'keysym Caps_Lock =' -e 'add lock = Pause' -e 'keysym Pause = Caps_Lock'
   else
      # Reconfigure caps-lock to be a control key, and set pause to do caps-lock-toggle.
      xmodmap -e 'clear lock' -e 'clear control' -e 'keysym Caps_Lock = Control_L' -e 'add control = Control_L Control_R' -e 'keysym Pause = Caps_Lock'
      # I was thinking we would need to "add lock" also, but it seems to work without also.
      #xmodmap -e 'clear lock' -e 'clear control' -e 'keysym Caps_Lock = Control_L' -e 'add control = Control_L Control_R' -e 'add lock = Pause' -e 'keysym Pause = Caps_Lock'
   fi
fi

# Check the debug flag
grep '^\s*DISPLAY_DEBUG_INFO' vikeying.py | grep "=" | grep -qi "true"
if [ "$?" == "0" ]
then
   # When debug mode is on, run this in foreground, we do not want a key-logger writing to a log file.
   sudo ./vikeying.py
else
   # Start the python key event handler in the background, any errors go to a log file.
   nohup sudo ./vikeying.py >>/tmp/vikeying.log 2>&1 &
fi
