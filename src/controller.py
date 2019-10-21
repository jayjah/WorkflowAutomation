#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import string
import threading
import os
import time
import random
from subprocess import check_output

from com.dtmilano.android.viewclient import ViewClient, EditText, TextView

from src.helper import Waiter, debug_print, Model, debug_error_print, keyboard_enter, print_and_exit_script, AccountSettings

# Handles all orders from device manager
#   A device object controls a physical device
# Slave Class
class Device(threading.Thread):
    lock = threading.Lock()
    waiter = Waiter()

    # Flags to let the threads run independently on their own and do work
    # Flags will be set from DeviceManager
    wifissid = None
    wifipw = None
    installappsappstore = []
    creategoogleaccount = False
    phonenumbersgiven = False
    pairdriverapp = False
    pairdriverappname = ''
    pairdriverapppw = ''
    configuresoundsettings = False
    configurelocationsettings = False
    configurepowersavingmode = False

    def __init__(self, number, serialno, telephonenummber=None):
        threading.Thread.__init__(self)

        # flags
        self.isdone = False
        self.initialized = False
        self.wifienabled = False
        # elf.wifistate = Error()
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
            #kwargs2 = {'autodump': False,
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

        except:
            debug_error_print("Unexpected error:", sys.exc_info()[0])
            print sys.exc_info()
            debug_print("Could not start Device: " + str(self.currentdevice))
            self.isdone = True
        Device.lock.release()

    # Runner Method from slave
    def run(self):
        while not self.isdone:

            # wifi
            if self.initialized and not self.wifienabled and Device.wifissid is not None and Device.wifipw is not None:
                self.wifienabled = self.wifi_login()
                self.wait(1)

            # create google account
            if self.initialized and Device.creategoogleaccount and self.googlefname != '' and self.googlelname != '' and self.googlebirthday != 0 and self.googlebirthmonth != 0 and self.googlebirthmonth != 0 and self.email == '' and self.password == '':
                self.createdgoogleaccount = self.create_google_account()
                self.wait(1)

            # install apps from play store
            if self.initialized and len(Device.installappsappstore) != 0 and len(
                    Device.installappsappstore) != self.installedappsappstore:
                result = self.download_app(Device.installappsappstore[self.installedappsappstore])
                self.installedapps[str(Device.installappsappstore[self.installedappsappstore])] = result
                if result:
                    print "Installed app succesfully"
                else:
                    print "Could not install app"
                self.installedappsappstore += 1
                self.wait(1)

            # pair driver app
            if self.initialized and Device.pairdriverapp and not self.ispaired and Device.pairdriverappname != '' and Device.pairdriverapppw != '':
                self.ispaired = self.pair_driverapp()

            # configure sound settings
            if self.initialized and Device.configuresoundsettings and not self.soundconfigconfigured:
                self.soundconfigconfigured = self.configure_all_sound_settings()

            # TODO location settings and disable power saving mode for driverapp

            # print state of device
            debug_print("Device: " + str(self.currentdevice) + " Status: [ initialized : " + str(
                self.initialized) + ", isdone: " + str(self.isdone) + ", enable wifi : " + str(
                self.wifienabled) + ", create Google Acc: "+str(self.createdgoogleaccount)+"[ Google First Name: "+str(self.googlefname)+", Google Last Name: "+str(self.googlelname)+", Google Birthday: "+str(self.googlebirthday)+" ] ] ")
            time.sleep(1.3)

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
        self.swipe_up()

    def check_if_screen_contains(self, tosearch, ignoretextfields=False):
        result = None
        Device.lock.acquire()
        #list =
        print "Views"
        for entry in self.vc.views:
            try:
                print str(entry)
            except:
                print "error in view"
            if not ignoretextfields:
                if entry is not None and entry.isClickable():
                    id = self._get_proper_viewid(entry, tosearch)
                    if id is not None :
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
            if contentdesc is not None and tosearch in contentdesc: # or re.search(tosearch, contentdesc, re.IGNORECASE)):
                result = uniqid
                return result
            if text is not None and tosearch in text: # or re.search(tosearch, text, re.IGNORECASE)):
                result = uniqid
                return result
            if tag is not None and tosearch in tag: # or re.search(tosearch, tag, re.IGNORECASE)):
                result = uniqid
                return result
            if uniqid is not None and tosearch in uniqid: # or re.search(tosearch, uniqid, re.IGNORECASE)):
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
                print ("ID of view: "+str(viewid)+"to text: "+str(texttotype) )
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

            print("View with ssid of taxi.de: "+str(viewid))
            self.wait(1)
            if viewid is not None:
                self.touch_by_id(viewid)
                print ("ssid of taxi.de was selected")
            if self.find_by_text(u'Entfernen'):
                result = True
            self.type_by_text(Device.wifipw, u'Passwort eingeben', True)
            self.device.press('KEYCODE_ENTER')
            self.wait(1)
            result = True
        except:
            print sys.exc_info()
            print str(self.currentdevice)
            return False

        self.destroy_current_running_app()
        return result

    # TODO
    def create_google_account(self):
        self.wait(1)
        result = False
        self.wait(1)
        if self.start_creating_google_acc():
            self.wait(1)
            self.touch_by_text(u'''Konto erstellen''', True)
            self.touch_by_text(u'''Für mich selbst''', True)
            self.type_by_id(self.googlefname+str(self.currentdevice), "firstName") #+str(000)+str(self.currentdevice)
            self.device.press('KEYCODE_ENTER')
            self.wait(1)
            self.type_by_id(self.googlelname+str(self.currentdevice), "lastName")
            self.device.press('KEYCODE_ENTER')
            self.wait(1)
            if self.find_by_text(u'Bestätigen Sie, dass Sie kein Roboter sind'):
                # error handling
                # if something like: Bist du ein Roboter
                if Device.phonenumbersgiven:
                    print ("enter own phone number and verify code from sms")
                else:
                    print ("will ask user for pin, cause given phone number is from setter")
                debug_print("Device: "+str(self.currentdevice) + " Serialno: "+self.serialno+ " -> need PIN to create Google Account; press Enter to generate PIN and send to given phonenumber to generate Google Account:")
                raw_input()
                self.type_by_id(self.telephonenumber, "phoneNumberId")
                #self.touch_by_text("next", True)
                #self.touch_by_text(u'Weiter', True)
                self.device.press('KEYCODE_ENTER')
                debug_print("Device: "+str(self.currentdevice) + " Serialno: "+self.serialno+ " -> need PIN to create Google Account; enter PIN Code:")
                pin = int(raw_input())
                self.wait(1)
                self.type_by_id(pin, "code")
                #self.touch_by_text("next", True)
                #self.touch_by_text(u'Weiter', True)
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

            #select email
            self.wait(1)
            viewid = self._get_correct_viewid(self.vc.views, 'Gmail-Adresse erstellen')
            print "View id of: Gmail-Adresse erstellen: " + str(viewid)
            self.touch_by_id(viewid)
            print("should be selected")
            self.email = str(self.googlefname) + str(self.googlelname) + "000" + str(self.currentdevice)
            if self.email.endswith('.'):
                self.email.replace('.', '')
            self.enter_text_adb(self.email)
            self.wait(1)
            self.device.press('KEYCODE_ENTER')

            #press password
            self.password = self.pw_generator()
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
            if self.find_by_text(u'Einen Moment noch…'):
                self.touch_by_text(u'Bestätigen', True)
            self.wait(1)
            result = True
            self.destroy_current_running_app()
        else:
            print ""
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
        self.device.drag((0.5*w, 0.9*h),(0.5*w, 0.4*h), 300)

    # works on samsung a10
    def swipe_down(self):
        disp_inf = self.device.getDisplayInfo()
        w = disp_inf["width"]
        h = disp_inf["height"]
        self.device.drag((0.5*w, 0.01*h),(0.5*w, 0.6*h), 300)

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
        self.wait(3)
        if result:
            if self.find_by_text(u'Öffnen mit'):
                self.touch_by_text(u'Google Play Store', True)
                self.touch_by_text(u'Immer', True)
            return True
        else:
            return False

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
        #self.device.shell('exec-out screencap -p > screen.png')
        image1 = self.device.takeSnapshot(reconnect=True).save(os.getcwd()+'/ImagesFromDevice/test.png', 'PNG')
        try:
            self.vc.dump(window=-1, sleep=3)
        except:
            print "Error happened after took screenshot"
        # adb:
        # adb shell screencap /sdcard/screen.png
        # self.wait()

    def increase_screen_brigthness(self):
        self.device.shell('input keyevent 221')

    def increase_standard_volume(self):
        self.device.shell('input keyevent 24')

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
            self.device.shell('am force-stop '+app)
            self.wait(2)
            return True
        else:
            return False


    def _check_if_app_is_installed(self, packagename):
        package =  self.device.shell('pm list packages | grep ' + packagename)
        if package in packagename:
            return True
        else:
            return False

    def configure_all_sound_settings(self):
        try:
            self.start_sound_settings()
            self.wait(2)
            self.touch_by_text(u'Lautstärke', True)
            self.vc.findViewWithContentDescriptionOrRaise(u'''Medien''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''Medien''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''Medien''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''Klingelton''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''Klingelton''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''Klingelton''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''Benachrichtigungen''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''Benachrichtigungen''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''Benachrichtigungen''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''System''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''System''').touch()
            self.wait(1)
            self.vc.findViewWithContentDescriptionOrRaise(u'''System''').touch()
            self.wait(1)
            self.destroy_current_running_app()
            return True
        except:
            return False

    def _check_permission_app(self):
        if self.find_by_id("com.android.packageinstaller:id/permission_allow_button") is not False:
            self.touch_by_id("com.android.packageinstaller:id/permission_allow_button")
            self._check_permission_app()

    def pair_driverapp(self):
        self.device.shell('am start -n com.talex.mytaxidriver/.activities.main.MainActivity')
        self.wait()
        self._check_permission_app()
        self.type_by_id(Device.pairdriverappname, "com.talex.mytaxidriver:id/nickET")
        self.type_by_id(Device.pairdriverapppw, "com.talex.mytaxidriver:id/passET")
        self.touch_by_id("com.talex.mytaxidriver:id/BtnLogin")
        if self.find_by_id("android:id/search_button") is not False:
            self.wait(1)
            self.destroy_current_running_app()
            return True
        else:
            self.wait(1)
            self.destroy_current_running_app()
            return False

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
        self.go_to_home_screen()
        self.wait(1)
        return result

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


# Handles all devices, give orders to devices for given config
# Master Class
class DeviceManager(object):

    def __init__(self, model):
        self.initialized = False
        self.alldevicesinitiliazed = False
        self.alldevicesdone = False
        self.connecteddevices = []
        self.model = model

        # results from devices to metrics the result
        self.resultswifi = dict()
        self.resultsgoogleacc = dict()
        self.resultsinstallappsps = dict()
        self.resultspaireddriverapp = dict()

        # all device serial numbers
        # index 0 in alldevs is device 0
        self.alldevs = []
        self.alldevscounter = 0
        for device in self.adb_devices():
            if "devices" not in device and "device" not in device:
                self.alldevs.append(device)
                self.alldevscounter += 1

        # start threads/devices if enough connected phones exist
        self.devices = {}
        if self.check_phones_connected():
            for i in range(int(self.model.countercars)):
                phonenumber = None
                if self.model.phonenumbersgiven:
                    phonenumber = int(str(self.model.phonenumbers).split(',')[i])
                else:
                    phonenumber = int(str(self.model.phonenumbers).split(',')[0])
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
            debug_error_print("Something wrong here!", "Connect more phones or maybe put another value in "
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
            self.check_if_all_devices_are_initialized()
            debug_print("DeviceManager : ⌛ Not all devices are initialized")
            time.sleep(5)


        debug_print("DeviceManager : ✅ All devices are initialized")

        if self.model.configuresettings and self.model.configuresoundsettings:
            debug_print("DeviceManager : Configure Sound Settings")
            Device.lock.acquire()
            Device.configuresoundsettings = True
            Device.lock.release()

        # enable wifi if flag is set
        if bool(self.model.loginwifi):
            debug_print("DeviceManager : Enable WiFi")
            self.enable_wifi_mode()
            time.sleep(5)

        # create google acc if flag is set
        if self.model.creategoogleaccount:
            debug_print("DeviceManager : Creating Google Account")
            self.enable_google_account()
            time.sleep(5)

        if len(self.model.installappsps) > 0:
            debug_print("DeviceManager : Install apps from Play Store")
            self.install_apps_from_playstore()
            time.sleep(5)

        if self.model.pairdriverapp:
            debug_print("DeviceManager : Pair Driver App")
            Device.lock.acquire()
            Device.pairdriverapp = True
            Device.pairdriverappname = self.model.drivername
            Device.pairdriverapppw = self.model.driverpw
            Device.lock.release()
            time.sleep(5)

        # wait till all devices are done with their work
        while not self.alldevicesdone:
            if self.check_if_all_devices_are_initialized():
                self.check_if_all_devices_are_done()
                debug_print("DeviceManager : ⌛️ All devices are initialized. But Not all all of them are done")

                # store all results
                for i in range(int(self.model.countercars)):
                    self.resultswifi[self.devices.get(i).currentdevice] = self.devices.get(i).wifienabled

                    googleaccsettings = AccountSettings(self.devices.get(i).createdgoogleaccount, self.devices.get(i).email, self.devices.get(i).password)
                    self.resultsgoogleacc[self.devices.get(i).currentdevice] = googleaccsettings

                    self.resultsinstallappsps[self.devices.get(i).currentdevice] = self.devices.get(i).installedapps

                    self.resultspaireddriverapp[self.devices.get(i).currentdevice] = self.devices.get(i).ispaired

                # prints results
                print "RESUUULT WIFI:"
                print self.resultswifi
                print "RESUUULT GOOGLEACCS:"
                print self.resultsgoogleacc
                print "RESUUULT INSTALLEDAPPS:"
                print self.resultsinstallappsps
                print "RESUUULT PAIRED DRIVER APP"
                print self.resultspaireddriverapp

                # wait 10 sec
                time.sleep(10)

        # all devices are done
        debug_print("DeviceManager : ✅ All devices are done")

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
        Device.lock.acquire()
        Device.wifissid = self.model.wifissid
        Device.wifipw = self.model.wifipw
        Device.lock.release()

    def install_apps_from_playstore(self):
        Device.lock.acquire()
        Device.installappsappstore = str(self.model.installappsps).split(',')
        Device.lock.release()

    # creates google accounts on all devices
    def enable_google_account(self):
        Device.lock.acquire()
        Device.creategoogleaccount = bool(self.model.creategoogleaccount)
        Device.phonenumbersgiven = bool(self.model.phonenumbersgiven)
        for i in range(int(self.model.countercars)):
            self.devices.get(i).googlefname = str(self.model.customerfirstname)
            self.devices.get(i).googlelname = str(self.model.customerlastname)
            self.devices.get(i).googlebirthday = int(self.model.birthday)
            self.devices.get(i).googlebirthmonth = int(self.model.birthmonth)
            self.devices.get(i).googlebirthyear = int(self.model.birthyear)
        Device.lock.release()


# Dummy - Main - Part
class Controller(object):

    def __init__(self):
        debug_print("init Controller")
        self.model = Model()
        print self.model.__str__()
        self.devicemanager = DeviceManager(self.model)
        debug_print("init Controller succesfully")


controller = Controller()
