#! /usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import threading
import time
from subprocess import check_output

from com.dtmilano.android.viewclient import ViewClient, EditText, TextView

# Handles all orders from device manager
#   A device object controls a physical device
# Slave
from src.helper import Waiter, debug_print, Model, debug_error_print, keyboard_enter, print_and_exit_script


class Device(threading.Thread):
    lock = threading.Lock()
    waiter = Waiter()

    # Flags to let the threads run independently on their own and do work
    # Flags will be set from DeviceManager
    wifissid = None
    wifipw = None
    installappsappstore = []

    def __init__(self, number, serialno, telephonenummber=None):
        threading.Thread.__init__(self)

        # flags
        self.isdone = False
        self.initialized = False
        self.isnotallreadyloggedin = False
        # elf.wifistate = Error()
        self.installedappsappstore = 0

        self.currentdevice = number
        self.serialno = serialno
        self.serialnoavc = None
        self.telephonenumber = telephonenummber
        debug_print("DEVICE SERIAL NUMBER: " + str(serialno) + " intern Device Number: " + str(number))

        # action which could cause a deadlock or unsafe thread operation
        # not sure how viewclient react in python on multithreading that's why I put it in here
        try:
            Device.lock.acquire()
            kwargs1 = {'verbose': True, 'ignoresecuredevice': False}
            kwargs2 = {'autodump': False,
                       'ignoreuiautomatorkilled': True}
            device2, serialn2o = ViewClient.connectToDeviceOrExit(serialno=serialno, **kwargs1)
            vc2 = ViewClient(device2, serialn2o, **kwargs2)
            self.device = device2
            self.serialnoavc = serialn2o
            self.vc = vc2
            self.vc.dump(window=-1)
            self.initialized = True
            Device.lock.release()

        except:
            debug_error_print("Unexpected error:", sys.exc_info()[0])
            print sys.exc_info()
            debug_print("Could not start Device: " + str(self.currentdevice))
            self.isdone = True

    # Runner Method from slave
    def run(self):
        # evice.lock.acquire()
        while not self.isdone:

            if self.initialized and not self.isnotallreadyloggedin and Device.wifissid is not None and Device.wifipw is not None:
                self.wifi_login()

            if self.initialized and len(Device.installappsappstore) != 0 and len(
                    Device.installappsappstore) != self.installedappsappstore:
                self.download_app(Device.installappsappstore[self.installedappsappstore])
                self.installedappsappstore += 1
                time.sleep(1)

            # print state of device
            debug_print("Device: " + str(self.currentdevice) + " Status: [ initialized : " + str(
                self.initialized) + ", isdone: " + str(self.isdone) + ", wifi enabled : " + str(
                self.isnotallreadyloggedin) + " ] ")
            time.sleep(1.3)
        # Device.lock.release()

    # Goes back with android back button
    def go_back(self, times):
        for i in range(times):
            self.wait()
            self.device.press('BACK')

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

    def go_to_home_screen(self):
        self.device.shell('input keyevent KEYCODE_HOME')

    # TODO
    def check_if_on_home_menu(self):
        result = False
        return result

    def go_to_home_menu(self):
        self.swipe_up_adb()

    def check_if_screen_contains(self, tosearch, ignoretextfields=False):
        result = None
        Device.lock.acquire()
        #list =
        for entry in self.vc.views:
            if not ignoretextfields:
                if entry is not None and entry.isClickable():
                    id = self._get_proper_viewid(entry, tosearch)
                    if id is not None:
                        result = id
            else:
                if entry is not None and entry.isClickable() and (
                        isinstance(entry, EditText) or isinstance(entry, TextView)):
                    id = self._get_proper_viewid(entry, tosearch)
                    if id is not None:
                        result = id
        Device.lock.release()
        return result

    def _get_proper_viewid(self, entry, tosearch):
        result = None
        contentdesc = entry.getContentDescription()
        text = entry.getText()
        tag = entry.getTag()
        uniqid = entry.getUniqueId()
        if contentdesc is not None and (tosearch in contentdesc or re.search(tosearch, contentdesc, re.IGNORECASE)):
            result = uniqid
            return result
        if text is not None and (tosearch in text or re.search(tosearch, text, re.IGNORECASE)):
            result = uniqid
            return result
        if tag is not None and (tosearch in tag or re.search(tosearch, tag, re.IGNORECASE)):
            result = uniqid
            return result
        if uniqid is not None and (tosearch in uniqid or re.search(tosearch, uniqid, re.IGNORECASE)):
            result = uniqid
            return result
        if self.vc.findViewWithAttributeThatMatches("text", re.compile(tosearch)):
            result = uniqid
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
        viewid = self.check_if_screen_contains(searchtext)
        if viewid is not None and not androidviewclientvariant:
            self.vc.findViewByIdOrRaise(viewid).touch()
        else:
            self.vc.findViewWithTextOrRaise(searchtext).touch()
        self.wait()

    def type_by_text(self, texttotype, searchtext):
        viewid = self.check_if_screen_contains(searchtext)
        if viewid is not None:
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

    def _get_correct_viewid(self, views, search):
        result = None
        if views is not None and search is not None:
            for entry in views:
                try:
                    print (entry)
                except:
                    print ("error in view")
                if search in entry.getText():
                    result = entry.getUniqueId()
        return result

    def kill_all_running_apps(self):
        self.device.shell(
            'ps | grep -v root | grep -v system | grep -v "android.process." | grep -v radio | grep -v "com.google.process." | grep -v "com.lge." | grep -v shell | grep -v NAME | awk "{print $NF}" | tr "\r" " " | xargs kill')

    # Enables wifi with given data from model
    def wifi_login(self):
        result = False

        Device.lock.acquire()
        Device.waiter.setwaitveryshort()
        Device.lock.release()
        try:
            self.vc.dump(window=-1)

            self.wait()
            self.touch_by_text(u'''Einstellungen''')
            self.open_in_settings("Verbindungen")
            self.open_in_settings("WLAN")
            # vc.findViewWithTextOrRaise(u'''WLAN''').touch()
            if self.find_by_text(u'Ein'):
                Device.lock.acquire()
                Device.waiter.setwaitveryshort()
                Device.lock.release()
                self.go_back(2)
                self.isnotallreadyloggedin = True
                return True
            Device.lock.acquire()
            Device.waiter.setwaitmiddle()
            Device.lock.release()
            if not self.open_in_settings("Aus"):
                self.go_back(2)
                self.isnotallreadyloggedin = True
                return True
            Device.lock.acquire()
            Device.waiter.setwaitveryshort()
            Device.lock.release()
            id = self.check_if_screen_contains(Device.wifissid)
            if id is not None:
                self.touch_by_text(id)
            if self.find_by_text(u'Entfernen'):
                self.go_back(4)
                self.isnotallreadyloggedin = True
                return True
            self.type_by_text(Device.wifipw, u'Passwort eingeben')
            self.touch_by_text(u'Verbinden')
            if self.find_by_text(u'Entfernen'):
                self.go_back(4)
            else:
                self.go_back(3)
            self.isnotallreadyloggedin = True
            result = True
        except:
            print sys.exc_info()
            print str(self.currentdevice)
            return False

        return result

    # TODO
    def create_google_account(self):
        result = False
        self.vc.dump(window=-1)
        return result

    def enter_text_adb(self, text):
        self.device.shell('input text ' + text)

    # works on samsung a10
    def swipe_up_adb(self):
        self.device.shell('input swipe 300 1000 300 500')

    def unlock_self(self):
        self.device.shell('adb shell input keyevent 26')

    def dismiss_keyboard(self):
        if self.device.isKeyboardShown():
            self.device.press('KEYCODE_BACK')

    def start_wifi_settings(self):
        return self._start_intent('android.settings.WIRELESS_SETTINGS')

    def start_sound_settings(self):
        return self._start_intent('android.settings.SOUND_SETTINGS')

    def start_location_settings(self):
        return self._start_intent('android.settings.LOCATION_SOURCE_SETTINGS')

    def start_battery_optimization_settings(self):
        return self._start_intent('android.settings.IGNORE_BATTERY_OPTIMIZATION_SETTINGS')

    # TODO click on "Zulassen" to fulfill this function
    def disable_battery_optimization_driverapp(self):
        return self._start_intent(
            'android.settings.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS -d package:com.talex.mytaxidriver')

    def start_play_store(self, appname):
        result = self._start_intent('android.intent.action.VIEW -d market://details?id=' + appname)
        if result:
            # if self.check_if_screen_contains("Play")
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
        ViewClient.sayText(text, verbose=True)
        self.vc.dump(window=-1, sleep=10)
        time.sleep(10)

    # TODO
    #def take_screenshot(self):
        # image1 = self.device.takeSnapshot().save(os.getcwd()+'\\Screenshots\\'+'OS_version.png')
        # adb:
        # adb shell screencap /sdcard/screen.png
        # self.wait()

    def _check_if_app_is_installed(self, packagename):
        return self.device.shell('pm list packages | grep ' + packagename)

    def download_app(self, appname):
        result = False
        self.vc.dump(window=-1)
        print "should start play store with: " + str(appname)
        self.start_play_store(appname)
        self.wait()
        deinstall = self.check_if_screen_contains("Deinstallieren")
        if deinstall is not None:
            self.go_to_home_screen()
            return True
        install = self.find_by_text("Installieren")
        if install:
            self.touch_by_text("Installieren", True)
            if self.find_by_text(u'Weiter') is not None:
                try:
                    self.touch_by_text(u'WEITER')
                    self.touch_by_text(u'ÜBERSPRINGEN')
                except:
                    print ("Error")
            result = True
            self.wait(10)

        isinstalled = self._check_if_app_is_installed(appname)
        if isinstalled is not None:
            result = True
        self.go_to_home_screen()
        return result

    # not used any more!
    def search_app_in_appstore(self, appname):
        result = False
        print ("SEARCH IN TEXT: " + str(appname))
        self.vc.dump(window=-1)

        if self.find_by_text(u'Nach Apps & Spielen suchen') is None:
            self.device.press(keyboard_enter)
        if self.find_by_text(u'Nach Apps & Spielen suchen') is None:
            self.device.press(keyboard_enter)
        self.touch_by_text(u'Nach Apps & Spielen suchen')
        self.type_by_text(appname, u'Nach Apps & Spielen suchen')
        self.touch_by_text(appname)
        self.device.press(keyboard_enter)
        if self.find_by_text(appname) is None and self.find_by_text(u'Meintest du:') is not None:
            self.touch_by_text(u'Meintest du:')
        # self.touch_by_text(appname)
        # self.vc.findViewWithText(appname)
        result = True
        return result


# Handles all devices, give orders to devices for given config
# Master
class DeviceManager(object):

    def __init__(self, model):
        self.device = None
        self.serialno = None
        self.vc = None
        self.initialized = False
        self.alldevicesinitiliazed = False
        self.alldevicesdone = False
        self.connecteddevices = []
        self.model = model

        # results from devices to metrics the result
        self.resultswifi = {}
        self.resultsgoogleacc = {}
        self.resultsinstallappsps = {}

        # all device serial numbers
        # index 0 in alldevs is device 0
        self.alldevs = []
        self.alldevscounter = 0
        for device in self.adb_devices():
            if "devices" not in device and "device" not in device:
                self.alldevs.append(device)
                self.alldevscounter += 1

        # start threads if enough connected phones exist this session
        self.devices = {}
        if self.check_phones_connected():
            for i in range(int(self.model.countercars)):

                phonenumber = None
                if self.model.phonenumbersgiven:
                    phonenumber = self.model.phonenumbers[i]
                thread = Device(i, self.alldevs[i], phonenumber)
                self.devices.update({i: thread})
                thread.start()

                # after last device was started, go in watch mode
                if str(i + 1) == str(self.model.countercars):
                    time.sleep(1)
                    debug_print(
                        "DeviceManager : Last device started, DeviceManager goes in watch mode and gives orders")
                    self.run()
        else:
            debug_print("should init phones: " + str(self.model.countercars))
            debug_print("connected phones: " + str(self.alldevscounter))
            debug_error_print("Not enough phones connected!", "Connect more phones or maybe put another value in "
                                                              "config settings")
            print_and_exit_script()

    # Runner Method from master
    # Sets Class Flags in Device class to let the device threads do their job
    # Script - Flow
    def run(self):
        # waits till all devices are initialized
        while not self.alldevicesinitiliazed:
            # wait 5 sec
            # TODO check error state of all threads/devices and make error handling
            time.sleep(5)
            self.check_if_all_devices_are_initialized()
            debug_print("DeviceManager : Not all devices initialized")

        debug_print("DeviceManager : All devices are initialized")

        # enable wifi if flag is set
        # if self.model.loginwifi:
        #    debug_print("DeviceManager : Starting Wifi on connected devices")
        #    # save result for measures
        #    self.resultswifi.update(self.enable_wifi_mode())
        #    time.sleep(10)

        if len(self.model.installappsps) > 0:
            debug_print("DeviceManager : Install apps from Play Store")
            self.resultsinstallappsps.update(self.install_apps_from_playstore())
            time.sleep(10)

        # create google acc if flag is set
        if self.model.creategoogleaccount:
            debug_print("DeviceManager : Creating google accounts on connected devices")
            # save result data
            self.resultsgoogleacc.update()
            time.sleep(10)

        # prints results
        print "RESUUULT WIFI:"
        print self.resultswifi
        print "RESUUULT GOOGLEACCS:"
        print self.resultsgoogleacc

        # wait till all devices are done with their work
        while not self.alldevicesdone:
            if self.check_if_all_devices_are_initialized():
                # wait 10 sec
                time.sleep(10)
                self.check_if_all_devices_are_done()
                debug_print("DeviceManager : All devices are initialized. But Not all all of them are done are done")

        # all devices are done
        debug_print("DeviceManager : All devices are done")

        # stop threads if their state is not finalized
        for thread in self.devices.values():
            if not bool(thread.isdone):
                thread.join()

        # Close automator
        debug_print("DeviceManager : Close Session")
        print_and_exit_script()

    # Checks for connected devices with adb and reformat that output
    def adb_devices(self):
        return set([device.split('\t')[0] for device in check_output(['adb', 'devices']).splitlines() if
                    device.endswith('\tdevice')])

    # Checks for connected devices with adb and reformat that output [old]
    def _adb_devices_second(self):
        adb_ouput = str(check_output(["adb", "devices"]))
        print adb_ouput
        list = adb_ouput.split('\n')
        return list

    # Checks if all connected devices are initialized in their state
    def check_if_all_devices_are_initialized(self):
        if len(self.model.countercars) == 0 or self.alldevicesinitiliazed:
            return True
        counter = 0
        for i in range(int(self.model.countercars)):
            if self.devices.get(i).initialized:
                counter += 1
        if int(self.model.countercars) == counter:
            self.alldevicesinitiliazed = True
            return True
        else:
            return False

    # Checks if all connected devices are done in their state
    def check_if_all_devices_are_done(self):
        if len(self.model.countercars) == 0 or self.alldevicesdone:
            return True
        counter = 0
        for i in range(int(self.model.countercars)):
            if self.devices.get(i).isdone:
                counter += 1
        if self.model.countercars == counter:
            self.alldevicesdone = True
            return True
        else:
            return False

    # check if adb_devices or adb_devices_second should be the correct method to take
    # probably it's the first one
    def check_phones_connected(self):
        list = self.adb_devices()
        if int(len(list)) == int(self.model.countercars):
            return True
        else:
            return False

    # enables wifi on all devices with given credentiels from models
    def enable_wifi_mode(self):
        results = {}
        # TODO dont block here to let it parallel running
        Device.lock.acquire()
        # result = alldevices[i].wifi_login(self.model.wifissid, self.model.wifipw)
        # alldevices[i].wifi_login(self.model.wifissid, self.model.wifipw)
        Device.wifissid = self.model.wifissid
        Device.wifipw = self.model.wifipw
        time.sleep(1)
        Device.lock.release()
        # results.update({i: result})
        return results

    def install_apps_from_playstore(self):
        results = {}
        Device.lock.acquire()
        Device.installappsappstore = str(self.model.installappsps).split(',')
        print "Result of extending device strings"
        print Device.installappsappstore
        Device.lock.release()
        return results

    # creates google accounts on all devices
    def enable_google_account(self):
        results = {}
        alldevices = self.devices.values()
        for device in alldevices:
            if device.initialized:
                result = device.create_google_account()
                # self.devices.get(i).wifi_login()
                results.update({device.currentdevice: result})
        return results


# Dummy - Main - Part
class Controller(object):

    def __init__(self):
        debug_print("init Controller")
        self.model = Model()
        print self.model.__str__()
        self.devicemanager = DeviceManager(self.model)
        debug_print("init Controller succesfully")


controller = Controller()
