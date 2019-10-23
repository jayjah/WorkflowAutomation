#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from com.dtmilano.android.viewclient import ViewClient, EditText, TextView

from src.helper import Waiter, debug_print, debug_error_print, keyboard_enter

reload(sys)
sys.setdefaultencoding('utf8')
import re
import string
import threading
import os
import time
import random


# Handles all orders from device manager
#   A device object controls a physical device
# Slave Class
class Device(threading.Thread):
    lock = threading.Lock()
    waiter = Waiter()

    # global flags
    BRIGHTNESS_HIGH = True

    # Flags to let the threads run independently on their own and do work
    # Flags will be set from DeviceManager
    wifissid = None
    wifipw = None
    installappsappstore = []
    creategoogleaccount = False
    phonenumbersgiven = False
    pairdriverapp = False
    #pairdriverappname = ''
    #pairdriverapppw = ''
    configuresoundsettings = False
    configurelocationsettings = False
    configurepowersavingmode = False
    disablesimlock = False

    def __init__(self, number, serialno, telephonenummber=None, pin=None):
        threading.Thread.__init__(self)

        # density is used to interact with screen swipes (e.g. lock screen touch)
        # view x and y coordinates multiplied with density results in real device dips coordinates
        # this can be used to use self.device.dragDip function, e.G.
        """
        !works, but starts every time a new drag event, which doesnt hold the DOWN keyevent through each drag!
        self.device.dragDip((104.0, 684.29), (205.71, 581.71), 500, 200, 0)
        self.device.dragDip((205.71, 581.71), (96.0, 477.71), 500, 200, 0)
        self.device.dragDip((96.0, 477.71), (203.43, 477.71), 500, 200, 0)
        self.device.dragDip((203.43, 477.71), (306.29, 584.0), 500, 200, 0)
        self.device.dragDip((306.29, 584.0), (204.57, 683.43), 500, 200, 0)

        the direct opposite of the above snippet should be the following, which is the direct call to keyevent via adb shell keyevent
        !at the moment not working!
        swipegesture = "adb shell sendevent /dev/input/event10 0003 0039 000000d3 && adb shell sendevent /dev/input/event10 0001 014a 00000001 && adb shell sendevent /dev/input/event10 0001 0145 00000001 && adb shell sendevent /dev/input/event10 0003 0035 000000ae && adb shell sendevent /dev/input/event10 0003 0036 000004dc && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0003 0039 0000021c && adb shell sendevent /dev/input/event10 0001 014a 00000001 && adb shell sendevent /dev/input/event10 0001 0145 00000001 && adb shell sendevent /dev/input/event10 0003 0035 000000a1 && adb shell sendevent /dev/input/event10 0003 0036 000004f4 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a2 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 000004f3 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 000004f2 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a3 && adb shell sendevent /dev/input/event10 0003 0036 000004f1 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 000004f0 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a4 && adb shell sendevent /dev/input/event10 0003 0036 000004ef && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a6 && adb shell sendevent /dev/input/event10 0003 0036 000004eb && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a8 && adb shell sendevent /dev/input/event10 0003 0036 000004e8 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a9 && adb shell sendevent /dev/input/event10 0003 0036 000004e6 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000ab && adb shell sendevent /dev/input/event10 0003 0036 000004e3 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000ad && adb shell sendevent /dev/input/event10 0003 0036 000004e1 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000af && adb shell sendevent /dev/input/event10 0003 0036 000004de && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000b1 && adb shell sendevent /dev/input/event10 0003 0036 000004db && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000b4 && adb shell sendevent /dev/input/event10 0003 0036 000004d8 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000b7 && adb shell sendevent /dev/input/event10 0003 0036 000004d4 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000ba && adb shell sendevent /dev/input/event10 0003 0036 000004d0 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000bf && adb shell sendevent /dev/input/event10 0003 0036 000004cb && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000c3 && adb shell sendevent /dev/input/event10 0003 0036 000004c6 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000c8 && adb shell sendevent /dev/input/event10 0003 0036 000004c1 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000cc && adb shell sendevent /dev/input/event10 0003 0036 000004bc && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000d1 && adb shell sendevent /dev/input/event10 0003 0036 000004b6 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000d6 && adb shell sendevent /dev/input/event10 0003 0036 000004b0 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000db && adb shell sendevent /dev/input/event10 0003 0036 000004a9 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000e0 && adb shell sendevent /dev/input/event10 0003 0036 000004a3 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000e6 && adb shell sendevent /dev/input/event10 0003 0036 0000049c && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000eb && adb shell sendevent /dev/input/event10 0003 0036 00000496 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000f0 && adb shell sendevent /dev/input/event10 0003 0036 0000048f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000f6 && adb shell sendevent /dev/input/event10 0003 0036 00000488 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000fc && adb shell sendevent /dev/input/event10 0003 0036 00000482 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000102 && adb shell sendevent /dev/input/event10 0003 0036 0000047b && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000109 && adb shell sendevent /dev/input/event10 0003 0036 00000475 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000010f && adb shell sendevent /dev/input/event10 0003 0036 0000046e && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000115 && adb shell sendevent /dev/input/event10 0003 0036 00000469 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000011b && adb shell sendevent /dev/input/event10 0003 0036 00000463 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000121 && adb shell sendevent /dev/input/event10 0003 0036 0000045d && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000127 && adb shell sendevent /dev/input/event10 0003 0036 00000458 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000012d && adb shell sendevent /dev/input/event10 0003 0036 00000453 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000133 && adb shell sendevent /dev/input/event10 0003 0036 0000044f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000138 && adb shell sendevent /dev/input/event10 0003 0036 0000044a && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000013d && adb shell sendevent /dev/input/event10 0003 0036 00000446 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000142 && adb shell sendevent /dev/input/event10 0003 0036 00000442 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000146 && adb shell sendevent /dev/input/event10 0003 0036 0000043e && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000014a && adb shell sendevent /dev/input/event10 0003 0036 00000439 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000014c && adb shell sendevent /dev/input/event10 0003 0036 00000434 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000014f && adb shell sendevent /dev/input/event10 0003 0036 00000430 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000150 && adb shell sendevent /dev/input/event10 0003 0036 0000042a && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000152 && adb shell sendevent /dev/input/event10 0003 0036 00000425 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000041f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000153 && adb shell sendevent /dev/input/event10 0003 0036 0000041a && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000414 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000040e && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000408 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000152 && adb shell sendevent /dev/input/event10 0003 0036 00000403 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000150 && adb shell sendevent /dev/input/event10 0003 0036 000003fd && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000014e && adb shell sendevent /dev/input/event10 0003 0036 000003f8 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000014b && adb shell sendevent /dev/input/event10 0003 0036 000003f2 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000148 && adb shell sendevent /dev/input/event10 0003 0036 000003ed && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000142 && adb shell sendevent /dev/input/event10 0003 0036 000003e7 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000013c && adb shell sendevent /dev/input/event10 0003 0036 000003e1 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000135 && adb shell sendevent /dev/input/event10 0003 0036 000003da && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000012b && adb shell sendevent /dev/input/event10 0003 0036 000003d2 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000120 && adb shell sendevent /dev/input/event10 0003 0036 000003c8 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000113 && adb shell sendevent /dev/input/event10 0003 0036 000003be && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000108 && adb shell sendevent /dev/input/event10 0003 0036 000003b3 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000fc && adb shell sendevent /dev/input/event10 0003 0036 000003a8 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000f1 && adb shell sendevent /dev/input/event10 0003 0036 0000039e && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000e7 && adb shell sendevent /dev/input/event10 0003 0036 00000394 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000dd && adb shell sendevent /dev/input/event10 0003 0036 0000038b && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000d4 && adb shell sendevent /dev/input/event10 0003 0036 00000381 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000cc && adb shell sendevent /dev/input/event10 0003 0036 00000379 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000c4 && adb shell sendevent /dev/input/event10 0003 0036 00000371 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000bc && adb shell sendevent /dev/input/event10 0003 0036 0000036a && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000b6 && adb shell sendevent /dev/input/event10 0003 0036 00000364 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000b0 && adb shell sendevent /dev/input/event10 0003 0036 00000360 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000ac && adb shell sendevent /dev/input/event10 0003 0036 0000035d && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a9 && adb shell sendevent /dev/input/event10 0003 0036 0000035b && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a7 && adb shell sendevent /dev/input/event10 0003 0036 0000035a && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a5 && adb shell sendevent /dev/input/event10 0003 0036 00000359 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000358 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a6 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000a9 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000ad && adb shell sendevent /dev/input/event10 0003 0036 00000357 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000b2 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000b8 && adb shell sendevent /dev/input/event10 0003 0036 00000358 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000bf && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000c7 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000d0 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000d9 && adb shell sendevent /dev/input/event10 0003 0036 00000359 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000e3 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000ed && adb shell sendevent /dev/input/event10 0003 0036 0000035a && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000f6 && adb shell sendevent /dev/input/event10 0003 0036 0000035c && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000000ff && adb shell sendevent /dev/input/event10 0003 0036 0000035d && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000108 && adb shell sendevent /dev/input/event10 0003 0036 0000035f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000110 && adb shell sendevent /dev/input/event10 0003 0036 00000362 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000119 && adb shell sendevent /dev/input/event10 0003 0036 00000365 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000121 && adb shell sendevent /dev/input/event10 0003 0036 00000368 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000012a && adb shell sendevent /dev/input/event10 0003 0036 0000036c && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000131 && adb shell sendevent /dev/input/event10 0003 0036 0000036f && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000138 && adb shell sendevent /dev/input/event10 0003 0036 00000373 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000013f && adb shell sendevent /dev/input/event10 0003 0036 00000377 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000145 && adb shell sendevent /dev/input/event10 0003 0036 0000037b && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000014b && adb shell sendevent /dev/input/event10 0003 0036 0000037f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000150 && adb shell sendevent /dev/input/event10 0003 0036 00000384 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000154 && adb shell sendevent /dev/input/event10 0003 0036 00000389 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000159 && adb shell sendevent /dev/input/event10 0003 0036 0000038d && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000015d && adb shell sendevent /dev/input/event10 0003 0036 00000392 && adb shell sendevent /dev/input/event10 0003 0030 00000002 && adb shell sendevent /dev/input/event10 0003 0031 00000002 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000160 && adb shell sendevent /dev/input/event10 0003 0036 00000397 && adb shell sendevent /dev/input/event10 0003 0030 00000001 && adb shell sendevent /dev/input/event10 0003 0031 00000001 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000164 && adb shell sendevent /dev/input/event10 0003 0036 0000039c && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000168 && adb shell sendevent /dev/input/event10 0003 0036 000003a1 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000016c && adb shell sendevent /dev/input/event10 0003 0036 000003a5 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000170 && adb shell sendevent /dev/input/event10 0003 0036 000003aa && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000174 && adb shell sendevent /dev/input/event10 0003 0036 000003ae && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000179 && adb shell sendevent /dev/input/event10 0003 0036 000003b2 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000017d && adb shell sendevent /dev/input/event10 0003 0036 000003b6 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000182 && adb shell sendevent /dev/input/event10 0003 0036 000003ba && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000188 && adb shell sendevent /dev/input/event10 0003 0036 000003bf && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000018f && adb shell sendevent /dev/input/event10 0003 0036 000003c4 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000195 && adb shell sendevent /dev/input/event10 0003 0036 000003c8 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000019c && adb shell sendevent /dev/input/event10 0003 0036 000003cd && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a4 && adb shell sendevent /dev/input/event10 0003 0036 000003d2 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ad && adb shell sendevent /dev/input/event10 0003 0036 000003d7 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001b7 && adb shell sendevent /dev/input/event10 0003 0036 000003dc && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c2 && adb shell sendevent /dev/input/event10 0003 0036 000003e1 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001cb && adb shell sendevent /dev/input/event10 0003 0036 000003e6 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001d2 && adb shell sendevent /dev/input/event10 0003 0036 000003ea && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001da && adb shell sendevent /dev/input/event10 0003 0036 000003ed && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001e0 && adb shell sendevent /dev/input/event10 0003 0036 000003ef && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001e4 && adb shell sendevent /dev/input/event10 0003 0036 000003f1 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001e8 && adb shell sendevent /dev/input/event10 0003 0036 000003f2 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ec && adb shell sendevent /dev/input/event10 0003 0036 000003f4 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ef && adb shell sendevent /dev/input/event10 0003 0036 000003f6 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f2 && adb shell sendevent /dev/input/event10 0003 0036 000003f8 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f5 && adb shell sendevent /dev/input/event10 0003 0036 000003fa && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f8 && adb shell sendevent /dev/input/event10 0003 0036 000003fc && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001fa && adb shell sendevent /dev/input/event10 0003 0036 000003ff && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001fc && adb shell sendevent /dev/input/event10 0003 0036 00000401 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001fe && adb shell sendevent /dev/input/event10 0003 0036 00000404 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ff && adb shell sendevent /dev/input/event10 0003 0036 00000406 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000200 && adb shell sendevent /dev/input/event10 0003 0036 00000409 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000040a && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000040c && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ff && adb shell sendevent /dev/input/event10 0003 0036 0000040e && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001fe && adb shell sendevent /dev/input/event10 0003 0036 0000040f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001fd && adb shell sendevent /dev/input/event10 0003 0036 00000410 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001fb && adb shell sendevent /dev/input/event10 0003 0036 00000411 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001fa && adb shell sendevent /dev/input/event10 0003 0036 00000412 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f9 && adb shell sendevent /dev/input/event10 0003 0036 00000413 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000415 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f8 && adb shell sendevent /dev/input/event10 0003 0036 00000416 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000417 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000418 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000041a && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000041b && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000041c && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000041d && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f7 && adb shell sendevent /dev/input/event10 0003 0036 0000041f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000421 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000422 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f6 && adb shell sendevent /dev/input/event10 0003 0036 00000424 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000426 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f5 && adb shell sendevent /dev/input/event10 0003 0036 00000427 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000429 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f4 && adb shell sendevent /dev/input/event10 0003 0036 0000042a && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f3 && adb shell sendevent /dev/input/event10 0003 0036 0000042c && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f2 && adb shell sendevent /dev/input/event10 0003 0036 0000042d && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f1 && adb shell sendevent /dev/input/event10 0003 0036 0000042f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001f0 && adb shell sendevent /dev/input/event10 0003 0036 00000431 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ee && adb shell sendevent /dev/input/event10 0003 0036 00000433 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ec && adb shell sendevent /dev/input/event10 0003 0036 00000435 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ea && adb shell sendevent /dev/input/event10 0003 0036 00000438 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001e9 && adb shell sendevent /dev/input/event10 0003 0036 0000043a && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001e7 && adb shell sendevent /dev/input/event10 0003 0036 0000043d && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001e5 && adb shell sendevent /dev/input/event10 0003 0036 00000440 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001e3 && adb shell sendevent /dev/input/event10 0003 0036 00000443 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001e2 && adb shell sendevent /dev/input/event10 0003 0036 00000446 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001e0 && adb shell sendevent /dev/input/event10 0003 0036 00000449 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001df && adb shell sendevent /dev/input/event10 0003 0036 0000044d && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001dd && adb shell sendevent /dev/input/event10 0003 0036 00000451 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001dc && adb shell sendevent /dev/input/event10 0003 0036 00000453 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001da && adb shell sendevent /dev/input/event10 0003 0036 00000456 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001d8 && adb shell sendevent /dev/input/event10 0003 0036 00000458 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001d7 && adb shell sendevent /dev/input/event10 0003 0036 0000045a && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001d6 && adb shell sendevent /dev/input/event10 0003 0036 0000045c && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001d5 && adb shell sendevent /dev/input/event10 0003 0036 0000045e && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001d3 && adb shell sendevent /dev/input/event10 0003 0036 00000460 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000462 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001d2 && adb shell sendevent /dev/input/event10 0003 0036 00000463 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001d1 && adb shell sendevent /dev/input/event10 0003 0036 00000464 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001d0 && adb shell sendevent /dev/input/event10 0003 0036 00000465 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001cf && adb shell sendevent /dev/input/event10 0003 0036 00000466 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ce && adb shell sendevent /dev/input/event10 0003 0036 00000467 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001cd && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001cc && adb shell sendevent /dev/input/event10 0003 0036 00000468 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001cb && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ca && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c9 && adb shell sendevent /dev/input/event10 0003 0036 00000469 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c8 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c7 && adb shell sendevent /dev/input/event10 0003 0036 0000046a && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000046b && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c6 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c5 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c4 && adb shell sendevent /dev/input/event10 0003 0036 0000046c && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c3 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c2 && adb shell sendevent /dev/input/event10 0003 0036 0000046d && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001c0 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001be && adb shell sendevent /dev/input/event10 0003 0036 0000046e && adb shell sendevent /dev/input/event10 0003 0030 00000007 && adb shell sendevent /dev/input/event10 0003 0031 00000007 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001bc && adb shell sendevent /dev/input/event10 0003 0036 0000046f && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001bb && adb shell sendevent /dev/input/event10 0003 0036 00000470 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001b9 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001b8 && adb shell sendevent /dev/input/event10 0003 0036 00000471 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001b7 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001b6 && adb shell sendevent /dev/input/event10 0003 0036 00000472 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001b5 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001b3 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001b2 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001b0 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001af && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ae && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ad && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ac && adb shell sendevent /dev/input/event10 0003 0036 00000473 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001ab && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001aa && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a9 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a8 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a7 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a6 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a5 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a4 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000474 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a3 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a2 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000475 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a1 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0030 00000008 && adb shell sendevent /dev/input/event10 0003 0031 00000008 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000476 && adb shell sendevent /dev/input/event10 0003 0030 00000009 && adb shell sendevent /dev/input/event10 0003 0031 00000009 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 000001a0 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000477 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000019f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000478 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0030 00000007 && adb shell sendevent /dev/input/event10 0003 0031 00000007 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 00000479 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000019e && adb shell sendevent /dev/input/event10 0003 0036 0000047a && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000047b && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000019d && adb shell sendevent /dev/input/event10 0003 0036 0000047f && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000019b && adb shell sendevent /dev/input/event10 0003 0036 00000487 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000197 && adb shell sendevent /dev/input/event10 0003 0036 00000492 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000193 && adb shell sendevent /dev/input/event10 0003 0036 000004a0 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000018f && adb shell sendevent /dev/input/event10 0003 0036 000004af && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000018a && adb shell sendevent /dev/input/event10 0003 0036 000004c0 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000188 && adb shell sendevent /dev/input/event10 0003 0036 000004cc && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000185 && adb shell sendevent /dev/input/event10 0003 0036 000004d6 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000182 && adb shell sendevent /dev/input/event10 0003 0036 000004e0 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000017f && adb shell sendevent /dev/input/event10 0003 0036 000004ea && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000017a && adb shell sendevent /dev/input/event10 0003 0036 000004f3 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000177 && adb shell sendevent /dev/input/event10 0003 0036 000004f9 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000174 && adb shell sendevent /dev/input/event10 0003 0036 000004fd && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000171 && adb shell sendevent /dev/input/event10 0003 0036 00000500 && adb shell sendevent /dev/input/event10 0003 0030 00000003 && adb shell sendevent /dev/input/event10 0003 0031 00000003 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000016e && adb shell sendevent /dev/input/event10 0003 0036 00000502 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000016b && adb shell sendevent /dev/input/event10 0003 0036 00000504 && adb shell sendevent /dev/input/event10 0003 0030 00000004 && adb shell sendevent /dev/input/event10 0003 0031 00000004 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000168 && adb shell sendevent /dev/input/event10 0003 0036 00000506 && adb shell sendevent /dev/input/event10 0003 0030 00000005 && adb shell sendevent /dev/input/event10 0003 0031 00000005 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000166 && adb shell sendevent /dev/input/event10 0003 0036 00000508 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000163 && adb shell sendevent /dev/input/event10 0003 0036 00000509 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000162 && adb shell sendevent /dev/input/event10 0003 0036 0000050a && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000160 && adb shell sendevent /dev/input/event10 0003 0036 0000050c && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000015f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000015d && adb shell sendevent /dev/input/event10 0003 0036 0000050d && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000015c && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000015b && adb shell sendevent /dev/input/event10 0003 0036 0000050e && adb shell sendevent /dev/input/event10 0003 0030 00000007 && adb shell sendevent /dev/input/event10 0003 0031 00000007 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 0000015a && adb shell sendevent /dev/input/event10 0003 0036 0000050f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000159 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000158 && adb shell sendevent /dev/input/event10 0003 0036 00000510 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000157 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000156 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000155 && adb shell sendevent /dev/input/event10 0003 0036 0000050f && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0035 00000154 && adb shell sendevent /dev/input/event10 0003 0036 0000050e && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0036 0000050d && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0030 00000006 && adb shell sendevent /dev/input/event10 0003 0031 00000006 && adb shell sendevent /dev/input/event10 0000 0000 00000000 && adb shell sendevent /dev/input/event10 0003 0030 00000005"
        """
        # the direct keyevents calls which are send to android os s
        self.density = None

        # flags
        self.isdone = False
        self.initialized = False
        self.wifienabled = False
        # elf.wifistate = Error()
        self.pairdriverappname = ''
        self.pairdriverapppw = ''
        self.installedappsappstore = 0
        self.installedapps = dict()
        self.googlefname = ''
        self.googlelname = ''
        self.googlebirthday = 0
        self.googlebirthmonth = 0
        self.googlebirthyear = 0
        self.createdgoogleaccount = False
        self.email = ''
        self.password = ''
        self.ispaired = False
        self.soundconfigconfigured = False
        self.locationconfigured = False
        self.powersavingmodeconfigured = False
        self.PIN = pin
        self.disabledpin = False
        self.increasedscreenbrightness = False

        # device specific settings
        self.currentdevice = number
        self.serialno = serialno
        self.serialnoavc = None
        self.telephonenumber = telephonenummber
        debug_print("DEVICE SERIAL NUMBER: " + str(serialno) + " intern Device Number: " + str(number))

        # action which could cause a deadlock or unsafe thread operation
        # not sure how viewclient react in python on multithreading that's why I put it in here
        Device.lock.acquire()
        try:
            kwargs1 = {'verbose': True, 'ignoresecuredevice': False}
            # kwargs2 = {'autodump': False,
            #           'ignoreuiautomatorkilled': True}
            kwargs2 = {'forceviewserveruse': False, 'useuiautomatorhelper': False, 'ignoreuiautomatorkilled': True,
                       'autodump': False, 'startviewserver': True, 'compresseddump': True}

            device2, serialn2o = ViewClient.connectToDeviceOrExit(serialno=serialno, **kwargs1)
            vc2 = ViewClient(device2, serialn2o, **kwargs2)
            self.device = device2
            self.serialnoavc = serialn2o
            self.vc = vc2
            self.vc.dump(window=-1)
            self.initialized = True

            self.density = self.device.display['density'] if self.device.display['density'] > 0 else 1
            print "DENSITY of Device: " + str(self.density)
        except:
            debug_error_print("Unexpected error:", sys.exc_info()[0])
            print sys.exc_info()
            debug_print("Could not start Device: " + str(self.currentdevice))
            self.isdone = True
        Device.lock.release()

    # Runner Method from slave
    def run(self):
        while not self.isdone:
            self.wait()
            # disable sim lock
            if self.initialized and Device.disablesimlock and not self.disabledpin:
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " Starting Task: Disable Sim Lock")
                self.disabledpin = self.disable_sim_lock()
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " End Task: Disable Sim Lock --- Result: " + str(self.disabledpin))

            # configure sound settings
            if self.initialized and Device.configuresoundsettings and not self.soundconfigconfigured:
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " Starting Task: Set Volume To Maximum")
                self.soundconfigconfigured = self.configure_all_sound_settings()
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " End Task: Set Volume To Maximum --- Result: " + str(self.soundconfigconfigured))

            # configure location settings
            if self.initialized and Device.configurelocationsettings and not self.locationconfigured:
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " Starting Task: Configure Location Settings")
                self.locationconfigured = self.start_location_settings()
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " End Task: Configure Location Settings --- Result: " + str(
                    self.locationconfigured))

            # wifi
            if self.initialized and not self.wifienabled and Device.wifissid is not None and Device.wifipw is not None:
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " Starting Task: Enable Wifi Settings")
                self.wifienabled = self.wifi_login()
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " End Task: Enable Wifi Settings --- Result: " + str(self.wifienabled))

            # create google account
            if self.initialized and Device.creategoogleaccount and self.googlefname != '' and self.googlelname != '' and self.googlebirthday != 0 and self.googlebirthmonth != 0 and self.googlebirthmonth != 0 and self.email == '' and self.password == '':
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " Starting Task: Creating Google Account")
                self.createdgoogleaccount = self.create_google_account()
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " End Task: Creating Google Account --- Result: " + str(
                    self.createdgoogleaccount) + " Email: " + self.email + " Password: " + self.password)

            # install apps from play store
            if self.initialized and len(Device.installappsappstore) != 0 and len(
                    Device.installappsappstore) != self.installedappsappstore:
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " Starting Task: Installing Apps From Play Store")
                while self.installedappsappstore != len(Device.installappsappstore):
                    result = self.download_app(Device.installappsappstore[self.installedappsappstore])
                    self.installedapps[str(Device.installappsappstore[self.installedappsappstore])] = result
                    if result:
                        print "Installed app succesfully"
                    else:
                        print "Could not install app"
                    self.installedappsappstore += 1
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " End Task: Installing Apps From Play Store")

            # pair driver app
            if self.initialized and Device.pairdriverapp and not self.ispaired and self.pairdriverappname != '' and self.pairdriverapppw != '':
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " Starting Task: Pair Driver App")
                self.ispaired = self.pair_driverapp()
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " End Task: Pair Driver App --- Result: "+str(self.ispaired))

            # configre power saving mode for driver app
            if self.initialized and Device.configurepowersavingmode and not self.powersavingmodeconfigured:
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                self.serialno) + " Starting Task: Disable Powser Saving Mode For Driver App")
                self.powersavingmodeconfigured = self.start_battery_optimization_settings()
                debug_print(" Device Nummer: " + str(self.currentdevice) + " || Serialno: " + str(
                    self.serialno) + " End Task: Pair Driver App --- Result: "+str(self.powersavingmodeconfigured))

            # increase screen brightness to maximum
            if self.initialized and Device.BRIGHTNESS_HIGH and not self.increasedscreenbrightness:
                #self.increase_screen_brigthness(times=5)
                self.increasedscreenbrightness = True

            # print state of device
            debug_print("Device: " + str(self.currentdevice) + " Status: [ initialized : " + str(
                self.initialized) + ", isdone: " + str(self.isdone) + ", enable wifi : " + str(
                self.wifienabled) + ", create Google Acc: " + str(
                self.createdgoogleaccount) + "[ Google First Name: " + str(
                self.googlefname) + ", Google Last Name: " + str(self.googlelname) + ", Google Birthday: " + str(
                self.googlebirthday) + " ] ] ")
            self.wait(1)

            self.configure_homescreen()

            try:
                self.disable_dev_options()
                self.reboot_device()
                self.isdone = True
            except:
                self.isdone = True
            self.isdone = True

    # Goes back with android back button
    def go_back(self, times):
        for i in range(times):
            self.wait()
            self.device.press('BACK')

    def disable_device_lock_screen(self):
        self.device.shell("locksettings clear --old 751268")
        self.wait(1)

    def enable_device_lock_screen(self):
        self.device.shell("locksettings set-pattern 751268")
        self.wait(1)

    # Waits
    def wait(self, sec=None):
        if sec is None:
            self.vc.sleep(Device.waiter.currentwaiter)
            time.sleep(Device.waiter.currentwaiter)
        else:
            self.vc.sleep(sec)
            time.sleep(sec)
        self.vc.dump(window=-1)

    # TODO
    # checks if device is on home screen or on home menu
    # at the moment it's not possible to differ between them
    # maybe it's here a opportunity to verify screen with images
    def check_if_on_home_screen(self):
        result = self.check_if_screen_contains("launcher")
        topactivity = self.get_top_activity()
        if "launcher" in str(topactivity) or re.search("launcher", str(topactivity), re.IGNORECASE):
            return True
        else:
            return False

    def configure_homescreen(self):
        #self.device.dragDip((210.29, 204.57), (211.43, 206.86), 2000, 5, 0)
        #self.wait()
        #self.vc.findViewWithContentDescriptionOrRaise(u'''Seite 0 von 2Entfernen''').touch()
        #self.wait()
        #if self.vc.findViewWithTextOrRaise(u'Seite löschen?') is not None:
        #    self.vc.findViewWithTextOrRaise(u'Löschen').touch()
        #self.wait()
        #self.go_back(1)
        #self.device.dragDip((60.57, 757.71), (77.71, 744.0), 6000, 20, 0)
        #self.wait()
        #self.device.touch(212.0, 964.0, 0)
        #self.wait()
        #self.device.dragDip((74.29, 774.86), (84.57, 756.57), 6000, 20, 0)
        #self.wait()
        #self.device.touchDip(121.14, 620.57, 0)
        #self.wait()
        #self.device.dragDip((205.71, 801.14), (204.57, 785.14), 6000, 20, 0)
        #self.wait()
        #self.vc.findViewWithContentDescriptionOrRaise(u'''Von Start entfernen''').touch()
        #self.wait()
        self.device.dragDip((60.57, 632.0), (60.57, 610.29), 6000, 20, 0)
        self.wait()
        self.vc.findViewWithContentDescriptionOrRaise(u'''Elemente auswählen''').touch()
        self.wait(1)
        self.vc.findViewWithContentDescriptionOrRaise(u'''Kalender, Nicht ausgewählt''').touch()
        self.wait(1)
        self.vc.findViewWithContentDescriptionOrRaise(u'''OneDrive, Nicht ausgewählt''').touch()
        self.wait()
        self.vc.findViewWithContentDescriptionOrRaise(u'''Von Start entfernen, Taste''').touch()
        self.wait()
        self.swipe_up()
        self.wait()
        self.vc.findViewWithContentDescriptionOrRaise(u'''Taxi.de Fahrer''').longTouch()
        self.wait()
        self.swipe_up()
        self.wait()
        self.device.touchDip(160.0, 139.43, 0)
        self.wait()
        self.vc.findViewWithContentDescriptionOrRaise(u'''Maps''').longTouch()
        self.wait()


    def go_to_home_screen(self):
        self.device.shell('input keyevent KEYCODE_HOME')

    # TODO
    def check_if_on_home_menu(self):
        result = False
        return result

    def go_to_home_menu(self):
        self.swipe_up()

    def check_if_screen_contains(self, tosearch, ignoretextfields=False):
        result = None
        Device.lock.acquire()
        # list =
        print "Views"
        for entry in self.vc.views:
            try:
                print str(entry)
            except:
                print "error in view"
            if not ignoretextfields:
                if entry is not None and entry.isClickable():
                    id = self._get_proper_viewid(entry, tosearch)
                    if id is not None:
                        result = id
                        return result
            else:
                if entry is not None and entry.isClickable() and (
                        isinstance(entry, EditText) or isinstance(entry, TextView)):
                    id = self._get_proper_viewid(entry, tosearch)
                    if id is not None:
                        result = id
                        return result
        Device.lock.release()
        return result

    def _get_proper_viewid(self, entry, tosearch):
        result = None
        resourceid = entry.getId()
        contentdesc = entry.getContentDescription()
        text = entry.getText()
        tag = entry.getTag()
        uniqid = entry.getUniqueId()
        try:
            if contentdesc is not None and tosearch in contentdesc:  # or re.search(tosearch, contentdesc, re.IGNORECASE)):
                result = uniqid
                return result
            if text is not None and tosearch in text:  # or re.search(tosearch, text, re.IGNORECASE)):
                result = uniqid
                return result
            if tag is not None and tosearch in tag:  # or re.search(tosearch, tag, re.IGNORECASE)):
                result = uniqid
                return result
            if uniqid is not None and tosearch in uniqid:  # or re.search(tosearch, uniqid, re.IGNORECASE)):
                result = uniqid
                return result
            if resourceid is not None and tosearch in resourceid:
                print("Resourceid: " + str(resourceid))

                return uniqid
            if self.vc.findViewWithAttributeThatMatches("text", re.compile(tosearch)):
                result = uniqid
            return result
        except:
            return result

    def find_by_id(self, searchtext):
        return True if self.vc.findViewById(searchtext) is not None else False

    def find_by_text(self, searchtext):
        return True if self.vc.findViewWithText(searchtext) is not None else False

    def touch_by_id(self, searchtext):
        self.vc.findViewByIdOrRaise(searchtext).touch()
        self.wait()

    def type_by_id(self, texttotype, searchtext):
        self.vc.findViewByIdOrRaise(searchtext).type(texttotype)
        self.wait()

    def touch_by_text(self, searchtext, androidviewclientvariant=False):
        if not androidviewclientvariant:
            viewid = self.check_if_screen_contains(searchtext)
            if viewid is not None:
                self.vc.findViewByIdOrRaise(viewid).touch()
        else:
            self.vc.findViewWithTextOrRaise(searchtext).touch()
        self.wait()

    def type_by_text(self, texttotype, searchtext, androidviewclient=False):
        if not androidviewclient:
            viewid = self.check_if_screen_contains(searchtext)
            if viewid is not None:
                print ("ID of view: " + str(viewid) + "to text: " + str(texttotype))
                self.vc.findViewByIdOrRaise(viewid).type(texttotype)
        else:
            self.vc.findViewWithTextOrRaise(searchtext).type(texttotype)
        self.wait()

    def get_viewid_to_open_in_settings(self, setting):
        result = None
        viewid = self._get_correct_viewid(self.vc.views, setting)
        if viewid is not None:
            if self.find_by_id(viewid):
                result = viewid
        return result

    def open_in_settings(self, setting):
        result = False
        viewid = self._get_correct_viewid(self.vc.views, setting)
        if viewid is not None:
            if self.find_by_id(viewid):
                self.touch_by_id(viewid)
                result = True
        return result

    def write_in_settings(self, setting, value):
        result = False
        viewid = self._get_correct_viewid(self.vc.views, setting)
        if viewid is not None:
            self.touch_by_id(viewid)
            self.type_by_id(value, viewid)
            result = True
        return result

    def disable_sim_lock(self):
        result = False
        self.wait()
        self.start_settings()
        self.wait(1)
        try:
            self.swipe_up()
            self.wait()
            self.touch_by_text("Biometrische Daten und Sicherheit", True)
            self.touch_by_text("Andere Sicherheitseinstellungen", True)
            self.touch_by_text("SIM-Sperre einrichten", True)
            self.touch_by_text("Sperren der SIM-Karte", True)
            self.enter_text_adb(self.PIN)
            # self.wait(1)
            # self.device.press('KEYCODE_ENTER')
            self.wait(1)
            self.touch_by_text("OK", True)

            result = True
        except:
            result = False
        self.destroy_current_running_app()
        self.wait(1)
        return result

    def _get_correct_viewid(self, views, search):
        result = None
        if views is not None and search is not None:
            for entry in views:
                text = entry.getText().encode('utf-8')
                try:
                    print str(entry).encode('utf-8')
                    if entry is not None and text is not None and entry.isClickable() and search in text:
                        result = entry.getUniqueId()
                except:
                    print ("error in view")

        return result

    # TODO doesnt work
    def kill_all_running_apps(self):
        self.device.shell(
            'ps | grep -v root | grep -v system | grep -v "android.process." | grep -v radio | grep -v "com.google.process." | grep -v "com.lge." | grep -v shell | grep -v NAME | awk "{print $NF}" | tr "\r" " " | xargs kill')

    # Enables wifi with given data from model
    def wifi_login(self):
        result = False
        try:
            self.wait(1)
            self.start_wifi_settings()
            self.wait(1)
            self.touch_by_text("WLAN", True)
            if self.find_by_text(u'Ein'):
                return True

            if not self.open_in_settings("Aus"):
                return True
            self.wait(3)

            viewid = None
            for entry in self.vc.views:
                text = entry.getText().encode('utf-8')
                try:
                    print str(entry).encode('utf-8')
                    if entry is not None and text is not None and Device.wifissid in text:
                        viewid = entry.getUniqueId()
                except:
                    print ("error in view")

            self.wait(1)
            if viewid is not None:
                self.touch_by_id(viewid)
            if self.find_by_text(u'Entfernen'):
                result = True
            self.type_by_text(Device.wifipw, u'Passwort eingeben', True)
            self.device.press('KEYCODE_ENTER')
            self.wait(1)
            result = True
        except:
            print sys.exc_info()
            print str(self.currentdevice)
            result = False

        self.destroy_current_running_app()
        return result

    # TODO
    def create_google_account(self):
        self.wait(1)
        result = False
        self.wait(1)
        if self.start_creating_google_acc():
            self.wait(1)
            self.vc.findViewWithTextOrRaise(u'Konto erstellen').touch()
            self.wait()
            self.vc.findViewWithTextOrRaise(u'Für mich selbst').touch()
            #            self.touch_by_text(u'''Konto erstellen''', True)
            #self.touch_by_text(u'''Für mich selbst''', True)
            self.wait()
            self.type_by_id(self.googlefname, "firstName")  # +str(000)+str(self.currentdevice)
            self.device.press('KEYCODE_ENTER')
            self.wait(1)
            self.type_by_id(self.googlelname, "lastName")
            self.device.press('KEYCODE_ENTER')
            self.wait(1)
            if self.find_by_text(u'Bestätigen Sie, dass Sie kein Roboter sind'):
                # error handling
                # if something like: Bist du ein Roboter
                if Device.phonenumbersgiven:
                    print ("enter own phone number and verify code from sms")
                else:
                    print ("will ask user for pin, cause given phone number is from setter")
                debug_print("Device: " + str(
                    self.currentdevice) + " Serialno: " + self.serialno + " -> need PIN to create Google Account; press Enter to generate PIN and send to given phonenumber to generate Google Account:")
                raw_input()
                self.type_by_id(self.telephonenumber, "phoneNumberId")
                # self.touch_by_text("next", True)
                # self.touch_by_text(u'Weiter', True)
                self.device.press('KEYCODE_ENTER')
                debug_print("Device: " + str(
                    self.currentdevice) + " Serialno: " + self.serialno + " -> need PIN to create Google Account; enter PIN Code:")
                pin = int(raw_input())
                self.wait(1)
                self.type_by_id(pin, "code")
                # self.touch_by_text("next", True)
                # self.touch_by_text(u'Weiter', True)
                self.device.press('KEYCODE_ENTER')
            self.wait(1)
            # day
            self.device.touchDip(80.0, 280.57, 0)
            self.wait(1)
            self.enter_text_adb(self.googlebirthday)
            self.wait(1)
            # month
            self.device.touchDip(201.71, 272.0, 0)
            self.wait(1)
            # januar
            self.device.touchDip(83.43, 124.0, 0)
            self.wait(1)
            # year
            self.device.touchDip(314.86, 275.43, 0)
            self.wait(1)
            self.enter_text_adb(self.googlebirthyear)
            # gender
            self.device.touchDip(125.14, 351.43, 0)
            self.wait(1)
            # self.vc.findViewWithTextOrRaise("u'Tag'").type(self.googlebirthday)
            self.touch_by_text(u'Ich möchte dies nicht beantworten', True)
            # weiter button
            self.device.touchDip(314.86, 780, 0)

            # select email
            self.wait(1)
            viewid = self._get_correct_viewid(self.vc.views, 'Gmail-Adresse erstellen')
            print "View id of: Gmail-Adresse erstellen: " + str(viewid)
            self.touch_by_id(viewid)
            print("should be selected")
            self.email = "tax1"+ str(self.googlelname) + str(self.currentdevice)
            if self.email.endswith('.'):
                self.email.replace('.', '')
            self.enter_text_adb(self.email)
            self.wait()
            if self.vc.findViewWithText(u'So melden Sie sich an') is not None:
                self.enter_text_adb(self.email)
            self.wait()
            self.email = "tax1"+ str(self.googlelname) + str(self.currentdevice)+"@gmail.com"
            self.wait(1)
            self.device.press('KEYCODE_ENTER')

            # press password
            self.password = "tax"+str(self.googlelname)+"000!"
            #self.password = self.pw_generator()
            print "Generated Password: " + self.password
            self.enter_text_adb(self.password)
            self.wait(1)
            self.device.press('KEYCODE_ENTER')
            self.wait(1)
            self.enter_text_adb(self.password)
            self.wait(1)
            self.device.press('KEYCODE_ENTER')
            self.wait(1)

            self.swipe_up()
            self.wait(1)
            # überspringen button
            self.device.touchDip(72.0, 773.71, 0)
            self.wait(1)
            # weiter button
            self.device.touchDip(314.86, 780, 0)

            # accept agb
            self.swipe_up()
            self.wait(1)
            self.swipe_up()
            self.wait(1)
            self.device.touchDip(33.14, 604.71, 0)
            self.wait(1)
            self.device.touchDip(33.14, 653.71, 0)
            self.wait(1)
            # weiter button
            self.device.touchDip(314.86, 780, 0)
            self.wait(3)
            if self.vc.findViewWithText(u'Einen Moment noch…') is not None:
                self.vc.findViewWithTextOrRaise(u'Bestätigen').touch()
            #if self.find_by_text(u'Einen Moment noch…'):
            #    self.touch_by_text(u'Bestätigen', True)
            self.wait(1)
            result = True
        else:
            print ""
        self.destroy_current_running_app()
        return result

    def pw_generator(self, sizeofchars=8, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(sizeofchars))

    def enter_text_adb(self, text):
        self.device.shell('input text ' + str(text))

    # works on samsung a10
    def swipe_up(self):
        disp_inf = self.device.getDisplayInfo()
        w = disp_inf["width"]
        h = disp_inf["height"]
        self.device.drag((0.5 * w, 0.9 * h), (0.5 * w, 0.4 * h), 300)

    # works on samsung a10
    def swipe_down(self):
        disp_inf = self.device.getDisplayInfo()
        w = disp_inf["width"]
        h = disp_inf["height"]
        self.device.drag((0.5 * w, 0.01 * h), (0.5 * w, 0.6 * h), 300)

    def unlock_self(self):
        self.device.shell('adb shell input keyevent 26')

    def dismiss_keyboard(self):
        if self.device.isKeyboardShown():
            self.device.press('KEYCODE_BACK')

    def start_wifi_settings(self):
        return self._start_intent('android.settings.WIRELESS_SETTINGS')

    def start_sound_settings(self):
        return self._start_intent('android.settings.SOUND_SETTINGS')

    def start_settings(self):
        return self._start_intent('android.settings.SETTINGS')

    def start_location_settings(self):
        if self._start_intent('android.settings.LOCATION_SOURCE_SETTINGS'):
            self.wait(1)
            if self.find_by_text('Standort, Aus'):
                self.touch_by_text('Standort, Aus', True)
            self.touch_by_text("Genauigkeit verbessern", True)
            self.touch_by_text("WLAN-Scan", True)
            self.touch_by_text("Bluetooth-Scanning", True)
            self.destroy_current_running_app()
            self.wait(1)
            return True
        self.destroy_current_running_app()
        self.wait(1)
        return False

    def start_battery_optimization_settings(self):
        self.wait()
        result = self._start_intent('android.settings.IGNORE_BATTERY_OPTIMIZATION_SETTINGS')
        self.wait()
        if result:
            self.vc.findViewWithTextOrRaise(u'Apps nicht optimiert',
                                            root=self.vc.findViewByIdOrRaise('id/no_id/5')).touch()
            self.wait()
            self.vc.findViewWithTextOrRaise(u'Alle').touch()
            self.wait()
            self.vc.findViewWithContentDescriptionOrRaise(u'''Anwendungen suchen''').touch()
            self.wait()
            self.enter_text_adb("fahrer")
            self.wait(1)
            self.vc.findViewWithTextOrRaise(u'Ein', root=self.vc.findViewByIdOrRaise('id/no_id/11')).touch()
            self.wait()
            result = True
        self.destroy_current_running_app()
        self.wait()
        return result

    # TODO click on "Zulassen" to fulfill this function
    def disable_battery_optimization_driverapp(self):
        return self._start_intent(
            'android.settings.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS -d package:com.talex.mytaxidriver')

    def start_play_store(self, appname):
        result = self._start_intent('android.intent.action.VIEW -d market://details?id=' + appname)
        self.wait(3)
        if result:
            try:
                if self.find_by_text(u'Öffnen mit'):
                    self.touch_by_text(u'Google Play Store', True)
                    self.touch_by_text(u'Immer', True)
                result = True
            except:
                result = False
        else:
            result = False
        return result

    def start_creating_google_acc(self):
        result = self._start_intent('android.settings.ADD_ACCOUNT_SETTINGS --es "account_types" "google.com"')
        self.wait(1)
        if result:
            self.touch_by_text("Google", True)
            return True
        else:
            return False

    def _start_intent(self, intentstr):
        out = self.device.shell('am start -a ' + str(intentstr))
        if re.search(r"(Error type)|(Error: )|(Cannot find 'App')", out, re.IGNORECASE | re.MULTILINE):
            return False
        return True

    def get_top_activity(self):
        return self.device.shell("dumpsys activity | grep top-activity")

    # TODO should work, but no audio is present
    def say_something(self, text):
        ViewClient.sayText(text)
        self.vc.dump(window=-1, sleep=3)
        time.sleep(3)

    # TODO
    # works but afterwards it will crash, reason currently unknown
    # so at the moment don't use this function
    def take_screenshot(self):
        # self.device.shell('exec-out screencap -p > screen.png')
        image1 = self.device.takeSnapshot(reconnect=True).save(os.getcwd() + '/ImagesFromDevice/test.png', 'PNG')
        try:
            self.vc.dump(window=-1, sleep=3)
        except:
            print "Error happened after took screenshot"
        # adb:
        # adb shell screencap /sdcard/screen.png
        # self.wait()

    # Increase screen brightness with keyevent
    def increase_screen_brigthness(self, times=1):
        for i in range(times):
            self.device.shell('input keyevent 221')
            self.wait()

    # Increase standard volume with keyevent
    def increase_standard_volume_keyevent(self, times=1):
        for i in range(times):
            self.device.shell('input keyevent 24')
            self.wait()

    # Increase standrd volume with keyode
    def increase_standard_volume_keycode(self, times=1):
        for i in range(times):
            self.device.press('KEYCODE_VOLUME_UP')
            #self.wait()

    def get_current_packagename(self):
        try:
            activity = self.get_top_activity()
            result = activity.split("/")
            result2 = result[2].split(':')
            packagename = result2[2]
            return packagename
        except:
            return None

    def destroy_current_running_app(self):
        app = self.get_current_packagename()
        if app is not None:
            self.device.shell('am force-stop ' + app)
            self.wait(2)
            return True
        else:
            return False

    def _check_if_app_is_installed(self, packagename):
        package = self.device.shell('pm list packages | grep ' + packagename)
        if package in packagename:
            return True
        else:
            return False

    def configure_all_sound_settings(self):
        result = False
        try:
            self.start_sound_settings()
            self.wait(2)
            self.touch_by_text(u'Lautstärke', True)
            self.device.dragDip((81.14, 254.86), (379.43, 253.71), 1000, 20, 0)
            self.wait()
            self.device.dragDip((73.14, 160.0), (378.29, 161.14), 1000, 20, 0)
            self.wait()
            self.device.dragDip((78.86, 344.0), (379.43, 345.14), 1000, 20, 0)
            self.wait()
            self.device.dragDip((84.57, 437.71), (379.14, 435.43), 1000, 20, 0)

            self.wait()
            result = True
        except:
            result = False
        self.destroy_current_running_app()
        self.wait()
        return result

    def _check_permission_app(self):
        if self.find_by_id("com.android.packageinstaller:id/permission_allow_button") is not False:
            self.touch_by_id("com.android.packageinstaller:id/permission_allow_button")
            self._check_permission_app()

    def pair_driverapp(self):
        result = False
        self.wait(1)
        self.device.shell('am start -n com.talex.mytaxidriver/.activities.main.MainActivity')
        self.wait(3)
        self._check_permission_app()
        self.type_by_id(self.pairdriverappname, "com.talex.mytaxidriver:id/nickET")
        self.type_by_id(self.pairdriverapppw, "com.talex.mytaxidriver:id/passET")
        self.touch_by_id("com.talex.mytaxidriver:id/BtnLogin")
        self.wait(1)
        if self.find_by_id("android:id/search_button") is not False:
            result = True
        else:
            result = False
        self.wait(1)
        self.destroy_current_running_app()
        return result

    def download_app(self, appname):
        result = False
        self.vc.dump(window=-1)
        print "should start play store with: " + str(appname)
        self.start_play_store(appname)
        self.wait()
        if self.find_by_text(u'Nicht gefunden'):
            # TODO start searching app in normal search bar of play store
            self.destroy_current_running_app()
            return False
        deinstall = self.check_if_screen_contains("Deinstallieren")
        if deinstall is not None:
            self.go_to_home_screen()
            return True
        install = self.find_by_text("Installieren")
        if install:
            self.touch_by_text("Installieren", True)
            if self.vc.findViewWithText(u'Kontoeinrichtung abschließen') is not False:
                try:
                    self.device.touchDip(166.86, 797.71, 0)
                    self.wait()
                    self.device.touchDip(222.86, 776.0, 0)
                    #self.touch_by_text(u'WEITER')
                    #self.touch_by_text(u'ÜBERSPRINGEN', True)
                except:
                    self.device.touchDip(166.86, 797.71, 0)
                    self.wait()
                    self.device.touchDip(222.86, 776.0, 0)

                    print ("Error")
            if self.find_by_text(u'Weiter') is not False:
                try:
                    self.touch_by_text(u'WEITER')
                    self.touch_by_text(u'ÜBERSPRINGEN')
                except:
                    print ("Error")
            result = True
            self.wait(10)

        isinstalled = self._check_if_app_is_installed(appname)
        if isinstalled:
            result = True
            self.wait()
        self.wait()
        self.destroy_current_running_app()
        self.wait(1)
        return result

    def reboot_device(self):
        self.device.shell('reboot')

    def disable_dev_options(self):
        self.start_settings()
        self.wait(1)
        self.swipe_up()
        self.wait()
        self.swipe_up()
        self.wait()
        self.vc.findViewWithTextOrRaise(u'Entwickleroptionen', root=self.vc.findViewByIdOrRaise('id/no_id/30')).touch()
        self.wait()
        self.vc.findViewWithTextOrRaise(u'Entwickleroptionen, Ein').touch()



    # not used any more?!
    def search_app_in_appstore(self, appname):
        result = False
        print ("SEARCH IN TEXT: " + str(appname))
        self.vc.dump(window=-1)

        if self.find_by_text(u'Nach Apps & Spielen suchen'):
            self.device.press(keyboard_enter)
        if self.find_by_text(u'Nach Apps & Spielen suchen'):
            self.device.press(keyboard_enter)
        self.touch_by_text(u'Nach Apps & Spielen suchen')
        self.type_by_text(appname, u'Nach Apps & Spielen suchen')
        self.touch_by_text(appname)
        self.device.press(keyboard_enter)
        if self.find_by_text(appname) and self.find_by_text(u'Meintest du:'):
            self.touch_by_text(u'Meintest du:')
        # self.touch_by_text(appname)
        # self.vc.findViewWithText(appname)
        result = True
        return result
