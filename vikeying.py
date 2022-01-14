#!/usr/bin/python3

"""
Enable special functions on the CAPS-LOCK key, to support VI users ;-)
Note: this script was created by my as a sort of "study" object, not for serious use.

Prepare by once running:
$ sudo pip3 install evdev

And for normal use, start this script using the ./vikeying-runner.sh script.

It will reset the keyboard layout, change caps-lock and pause key definitions,
and then start this python script to handle caps-lock key events in the background.

See README.md for more information.

Thijs Kaper, January 14, 2022.
"""

from selectors import DefaultSelector, EVENT_READ
from evdev import InputDevice, list_devices, categorize, ecodes, UInput

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

def debug(*values: object):
    """
        Show debug information on console, if debug flag enabled.
    """
    if DISPLAY_DEBUG_INFO:
        print(*values)

def caps_down(virtual_keyboard):
    """
        CAPS key pressed, translate into pressing CTRL key (if flag enabled).
    """
    debug("caps_down (e.g. pressing and holding the key)")
    if CAPS_DOES_CONTROL_KEY:
        debug("simulate pressing (and holding) the control key")
        virtual_keyboard.write(ecodes.EV_KEY, ecodes.KEY_LEFTCTRL, 1)
        virtual_keyboard.syn()

def caps_up(virtual_keyboard, other_key_pressed, capslock_is_on):
    """
        CAPS key released, translate into releasing CTRL key (if flag enabled),
        and optionally disable CAPS-state (if on) and hitting ESC key.
        These last two actions only happen if NO other keys were pressed.
    """
    debug("caps_up (e.g. releasing the key) - other_key_pressed=" + str(other_key_pressed) + \
          ", caps-lock_is_on=" + str(capslock_is_on))
    if CAPS_DOES_CONTROL_KEY:
        debug("simulate releasing the control key")
        virtual_keyboard.write(ecodes.EV_KEY, ecodes.KEY_LEFTCTRL, 0)
        virtual_keyboard.syn()
    if not other_key_pressed:
        if capslock_is_on:
            toggle_capslock_state(virtual_keyboard)
        debug("send ESC key")
        virtual_keyboard.write(ecodes.EV_KEY, ecodes.KEY_ESC, 1)
        virtual_keyboard.write(ecodes.EV_KEY, ecodes.KEY_ESC, 0)
        virtual_keyboard.syn()

def toggle_capslock_state(virtual_keyboard):
    """
        Toggle the caps-lock key state. So to turn it OFF, we would need to
        know that it is ON before toggling.
    """
    debug("toggle_capslock_state")
    virtual_keyboard.write(ecodes.EV_KEY, ecodes.KEY_CAPSLOCK, 1)
    virtual_keyboard.write(ecodes.EV_KEY, ecodes.KEY_CAPSLOCK, 0)
    virtual_keyboard.syn()

# Alternative way to turn OFF caps-lock state, using X11 library.
# But I did not like this too much... Seems too low level connected to window manager.
# Just using keyboard events might be more portable across Linux distributions.
#
#from ctypes import cdll, c_uint
#
# def disable_caps_state():
#     """
#         Disable CAPSLOCK state, if it was enabled.
#     """
#     x11 = cdll.LoadLibrary("libX11.so.6")
#     display = x11.XOpenDisplay(None)
#     x11.XkbLockModifiers(display, c_uint(0x0100), c_uint(2), c_uint(0))
#     x11.XCloseDisplay(display)

def find_keyboards(selector):
    """
        Find keyboard input devices (by searching for it having a CAPSLOCK key).
        All found keyboards are added to the "selector" to listen for their events.
    """
    debug("find_keyboards (and register in event selector)")
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        caps = device.capabilities()
        if ecodes.KEY_CAPSLOCK in caps.get(ecodes.EV_KEY, []):
            debug(device.path, device.name, device.phys)
            selector.register(device, EVENT_READ)

def event_loop(selector, virtual_keyboard):
    """
        Listen for all key events, and process them to get the special
        capslock key behaviour.
    """
    other_key_pressed = False
    while True:
        for key, _ in selector.select():
            device = key.fileobj
            for event in device.read():
                if event.type == ecodes.EV_KEY:
                    key = categorize(event)
                    if key.keystate != key.key_hold:
                        debug(key, device.active_keys(verbose=True))
                    if key.keycode == 'KEY_CAPSLOCK' and key.keystate == key.key_down:
                        if not CAPS_TOGGLE_MODIFIER in device.active_keys():
                            other_key_pressed = False
                            caps_down(virtual_keyboard)
                    elif key.keycode == 'KEY_CAPSLOCK' and key.keystate == key.key_up:
                        if CAPS_TOGGLE_MODIFIER in device.active_keys():
                            # Bonus behaviour... hitting ALT-CAPS will toggle caps-lock state.
                            toggle_capslock_state(virtual_keyboard)
                        else:
                            capslock_is_on = ecodes.LED_CAPSL in device.leds()
                            caps_up(virtual_keyboard, other_key_pressed, capslock_is_on)
                    else:
                        other_key_pressed = True

def main():
    """
        Main loop, find keyboards, and listen in on events.
    """
    selector = DefaultSelector()

    # Add all keyboards to the selector
    find_keyboards(selector)

    # define UInput here, after checking devices, as this opens a new
    # keyboard device (which we do not want monitored).
    virtual_keyboard = UInput()

    # Listen to all keyboards, and handle the CAPS-LOCK a bit differently.
    event_loop(selector, virtual_keyboard)

if __name__ == "__main__":
    main()
