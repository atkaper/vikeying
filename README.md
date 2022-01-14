# Vikeying

The name is just a silly play on words: VI + Key + King = Vikeying = pronounced like "Viking".
This README.md is a copy of this blog post: https://www.kaper.com/software/vikeying/

## Description

Enable special functions on the CAPS-LOCK key, to support VI users ;-)
This script was created by me as a sort of "study" object, not for any serious use.

A colleague of mine has created a Linux kernel module to modify his keyboard behaviour to what is
described in this document. I was just wondering if it would be possible to create the
complex logic he needed, without having to make a kernel module. As maintaining a kernel
module might require some work or rebuilds on every new kernel release.

So what are we talking about here?

Enable special functions on the CAPS-LOCK key, to support VI users ;-)

## Specifications

The requirements are:

- make the pause key do the caps-lock toggling.
- make the caps-lock key do something special:
  - when keeping caps-lock pressed and hitting another key, let it behave like a control-key.
  - when pressing and releasing caps-lock key without other keys, it should do two things:
    - if caps-lock state is ON, disable caps-lock state.
    - send ESC key.

Reason for the new behaviour is mainly for VI users. To get back in VI command mode, you can hit the
new caps-lock function, which disables caps-lock state if it was on, and executes the ESC key.

Next to this, the simulation of it being a CTRL key when used with other keys, is to ease typing of
for example CTRL-A, CTRL-W or other CTRL combinations which get your fingers into a Gordian knot.

Bonus implementation: you can hit ALT + caps-lock to toggle the caps-lock state. See CAPS_TOGGLE_MODIFIER
in the python script on how to disable this, or change it to shift or control.

## Running the script

You do need:

- a Linux machine (I tested this on Linux Mint with XFCE, which is an Ubuntu like system).
- python3 - python script interpreter.
- xmodmap - keyboard mapping tool.
- setxkbmap - keyboard mapping tool.
- sudo (+permissions).

Install evdev python library by once running:

```
sudo pip3 install evdev
```

You can run a check script to see keyboard mappings. You can run that before starting the
tool, or after, or after resetting (killing) the tool.

```
./list-keys.sh
```

The script to start the tool is:

```
./vikeying-runner.sh
```

Or you can start it with a parameter to NOT map the pause key as caps-lock-toggle
(you can use alt + caps-lock to toggle caps state):

```
./vikeying-runner.sh nopause
```

It does reconfigure some keys using the ```xmodmap``` and ```setxkbmap``` commands. And then it starts the
```vikeying.py``` python script (as root) which does more of the magic.

Note: the DISPLAY_DEBUG_INFO flag in the python script will determine if the script runs in the
foreground with debug logging to the console, or that it will go run in the background.

When you are done playing, or are in need of restoring the keyboard mapping, you can execute:

```
./reset-keyboard.sh
```

Note: both ```vikeying-runner.sh``` and ```reset-keyboard.sh``` require sudo root permissions to run.
This is because the tool needs access to some privileged I/O devices to which only root has access.
Quite likely because the technology used in this script can also be used to make a keylogger.
So only run this when you trust it (so please first read the code thoroughly, it is not that much code anyway).

## Script Configurations

In the python script, there are three settings you can play around with:

```
# Depending on if you let the Linux keyboard driver do the control
# mapping on caps-lock or not, set this to False or True.
# Use True if python does the control key pressing/releasing.
# Use False if the Linux keyboard definition does this for you.
# Note: the difference is subtle: the order of releasing the CTRL
# might differ for the two (e.g. hitting ctrl-esc or ctrl and then esc).
CAPS_DOES_CONTROL_KEY = False

# Fairly obvious setting... show debug logs (to console) or not.
# Note/Warning: if you set this to True, BE AWARE that this scripts acts as a keylogger.
# It will send all keystrokes to the console log when in debug mode.
DISPLAY_DEBUG_INFO = True

# When hitting the key defined here, and then the caps-lock, we will toggle caps-lock state.
# If you want to disable this, set the value to -1, e.g. "CAPS_TOGGLE_MODIFIER = -1"
# Or you can change it to KEY_LEFTSHIFT or KEY_LEFTCTRL if you prefer.
CAPS_TOGGLE_MODIFIER = ecodes.KEY_LEFTALT
#CAPS_TOGGLE_MODIFER = ecodes.KEY_LEFTSHIFT
#CAPS_TOGGLE_MODIFER = ecodes.KEY_LEFTCTRL
#CAPS_TOGGLE_MODIFER = -1
```

## Sudo stuff

If someone would seriously consider using this tool, or a modified version of this, I would suggest to
copy the script files to /usr/local/bin/vikeying/* and change the files to root:root to prevent anyone
or anything from changing them. And configure a /etc/sudoers.d/vikeying file to allow sudo use to start
the tool without needing to enter a password. And then put the start command in the list of applications
which need to start after login (Mint has a GUI widget for that to configure things to automatically start).

## Testing it out

- Start the script (in debug mode in one terminal session).
- Start VI (```vi /tmp/test.txt```) in another terminal session.
- Hit ```a``` to enter append mode.
- Hit Pause key to turn on caps-lock.
- Type some characters ```abcd```, they should show as ```ABCD``` ;-)
- Hit ALT, keep it pressed, and hit and release caps-lock key, and then release ALT. This should toggle off the caps-lock led.
- Type some characters ```abcd```, they should show as ```abcd```.
- Hit ALT, keep it pressed, and hit and release caps-lock key, and then release ALT. This should toggle off the caps-lock led.
- Type some characters ```abcd```, they should show as ```ABCD```.
- Hit caps-lock and keep it pressed down, and hit the ```v``` key twice, release caps-lock key. You should see ^V as result.
- Hit caps-lock, and release it. You should see caps-lock led turning off.
- Type ```:x``` and enter. This should execute the lowercase ```:x``` command: save the file and exit VI. It should NOT type this as text (as the caps-lock will have send an escape key).

All done. I hope this works on other Linux machines / distributions also.

## Disclaimer

The requirements are not fully met by the python script, you need to use some other tools to set-up
some stuff also, next to running this script. The other things to arrange outside of the script
are remapping the pause key to act like a caps-lock toggle. And to disable all functions of the
existing caps-lock key. Next to that, the python script will ADD the new behaviour on the caps-lock key.
The ```vikeying-runner.sh``` script will execute those additionally needed tools/commands.

The script has only been tested on my Linux-Mint 20.2 release (is a bit like using Ubuntu).
My window manager is XFCE. My guess is that the python script should function on any flavour of Linux,
but the ```xmodmap``` and ```setxkbmap``` commands might need some tweaking. Just remember that you
should aim for a caps-lock key which does nothing anymore after you are done with those two commands.
The python script will fill in the blanks afterwards.

## Conclusion

~~The script does seem to work, however, I have seen some occasions where I ended up with a non-working
ctrl-key, or mysterious enabling of caps-lock-state when hitting the caps-lock-key together with some
other keys or when keeping caps-lock pressed for a while (which it should not do that anymore with this
script!).~~ _I did find (and fix) a small bug in the script while writing the blog page about it ;-) So
maybe the weird behaviour is gone? I suggest you just try it out for a while..._

My conclusion would be that this was a nice exercise to find out what is possible in keyboard
manipulation. ~~I suspect that there might be some small timing issues to iron out, or perhaps
some concurrency issues or other race conditions to dig in to.~~ _(I hope this is fxed)_.

I will leave this as is for now. My caps-lock key has a completely different mapping which I got used to
(compose, using ```setxkbmap -option compose:caps```, for example hitting caps + " + e will lead to ë),
so I won't be running this set of scripts. This script might serve to others as some inspiration for any
complex keyboard macro handling.

I am impressed by what you can do with such a small python script! And thank you Ovidiu for providing the
challenge of trying to implement this without kernel module (but I suggest you keep using your module ;-)).

Thijs Kaper, January 14, 2022.


## Appendix, used resources

Of course this would not have gotten anywhere without an internet search engine (duckduckgo), which landed
me on these two pages:

- https://www.reddit.com/r/linux/comments/8geyru/diy_linux_macro_board/
- https://python-evdev.readthedocs.io/en/latest/tutorial.html
