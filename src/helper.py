#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from ConfigParser import SafeConfigParser
from enum import Enum

# Strings
settings_menu = u'''Einstellungen'''
keyboard_enter = 'KEYCODE_ENTER'
keyboard_delete = 'KEYCODE_DEL'
log_file = None
FILELOG = True


# Global write functions to display something on terminal
def print_and_exit_script(success=False):
    print ("---------------------")
    print ("---- End Scipt ----")
    print ("---------------------")
    print ("---------------------")
    if success:
        exit(0)
    exit(1)


def debug_print(value, log=True):
    log_file = open('./../res/log.txt', 'a+')
    value = "---- Time: "+ str(datetime.now()) +" --- "+str(value)+ " ----\n"
    paragraph = "---------------------\n"
    if FILELOG and log:
        log_file.flush()
        log_file.writelines(value)
        log_file.writelines(paragraph)
    print value
    print paragraph
    log_file.close()


def debug_error_print(mssage, error):
    print "--- ", mssage, " ----"
    print ("---------------------")
    print "--- ", error, " ----"
    print ("---------------------")


# Class to hold gmail account settings in measures/log
class AccountSettings(object):
    def __init__(self, success, email, pw):
        self.success = success
        self.email = email
        self.emailpassword = pw


# Interactive class for getting config from user
#   reads all values from terminal through an interactive session with an user
class InteractiveMode(object):

    def __init__(self):
        self.print_start_script()

    def count_customer_cars(self):
        print 'Wie viele Fahrzeuge/Handys sollen eingerichtet werden? (Zahl eingeben)'
        try:
            value = int(raw_input())
            return value
        except:
            print ("--- wrong input ----")
            print ("---------------------")
            print_and_exit_script()

    def get_customer_name(self):
        print 'Wie heißt der Kunde? (z.B. Minicar, Alstertal etc)'
        return raw_input()

    def taxi_customer(self):
        print 'Taxi Unternehmen? ("true" oder "false" eingeben)'
        taxiorshift = raw_input()
        if taxiorshift == "true":
            return True
        elif taxiorshift == "false":
            return False
        else:
            print ("--- wrong input ----")
            print ("---------------------")
            print_and_exit_script()

    def print_start_script(self):
        print ("---------------------")
        print ("------- Start -------")
        print ("---------------------")
        print ("---------------------")


# Config and model class
class Model:

    def __init__(self):
        # gui flag
        self.gui = False
        # cred config section
        self.taxicompany = False
        self.rentcompany = False
        self.countercars = 0
        self.allcars = 0
        self.currentfirstcar = 0
        self.phonenumbersgiven = False
        self.phonenumbers = []

        # flag config section
        self.loginwifi = False
        self.creategoogleaccount = False
        self.installapps = False
        self.pairdriverapp = False
        self.configuresettings = False

        # wifi config section
        self.wifissid = ""
        self.wifipw = ""

        # create google account config section
        self.birthday = "00"
        self.birthmonth = "00"
        self.birthyear = "0000"
        self.customerfirstname = ""
        self.customerlastname = ""

        #       # install apps config section
        self.installappsps = []
        self.installappslf = []
        self.startapps = []
        self.simpins = []

        # pair driver app config section
        self.drivername = ""
        self.driverpw = ""

        # configure settings config section
        self.configurepowersavingmode = False
        self.configurehomescreen = False
        self.configurelockscreenapp = False
        self.configurelocationsettings = False
        self.configuresoundsettings = False
        self.disablesimlock = False
        self.configurescreenbrightness = False
        self.disabledevoptions = False
        self.rebootdevicewhenfinished = False

        # configure device lock
        self.enablelockdevice = False
        self.lockpattern = -1

        # which mode should start ? (-c = Config Mode)
        if len(sys.argv) > 0 and sys.argv[1] == '-c':
            debug_print("Read Config")
            self.parser = SafeConfigParser()
            self.mode = ScriptMode.configmode
            self.interactivemode = None
            self.parser.read('../config.cfg')

            for section_name in self.parser.sections():
                print 'Section:', section_name
                if section_name == "cred":
                    self._iterateoverlistandaddproperties(self.parser.items(section_name))
                if section_name == "flags":
                    self._iterateoverlistandaddproperties(self.parser.items(section_name), True)
                print '  Options:', self.parser.options(section_name)
                for name, value in self.parser.items(section_name):
                    print '  %s = %s' % (name, value)


        if len(sys.argv) > 2:
            if sys.argv[2] == '-g':
                debug_print("GUI will be displayed")
                self.gui = True

        else:
            debug_print("Interactive Mode")
            self.mode = ScriptMode.interactivemode
            self.interactivemode = InteractiveMode()
            self.parser = None

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def _iterateoverlistandaddproperties(self, list, flagcred=None):
        if flagcred is None:
            for name, value in list:
                for ownattribute in [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]:
                    if name == ownattribute:
                        setattr(self, name, value)
                        print "Added to own model: " + name + " and value: " + value
        else:
            for name, value in list:
                for ownattribute in [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]:
                    if name == ownattribute:
                        setattr(self, name, value)
                        print "Added to own model: " + name + " and value: " + value
                if bool(value):
                    self._iterateoverlistandaddproperties(self.parser.items(name))

    def get_current_birthday(self):
        if int(self.birthday) == 28:
            self.birthday = 1
            return self.birthday
        self.birthday += 1
        return self.birthday

    def get_current_birthmonth(self):
        if int(self.birthmonth) == 12:
            self.birthmonth = 1
            return self.birthmonth
        self.birthmonth += 1
        return self.birthmonth

    def get_current_birthyear(self):
        if self.birthyear == 1995:
            self.birthyear = 1951
            return self.birthyear
        self.birthyear += 1
        return self.birthyear


class Waiter(object):

    def __init__(self):
        self.currentwaiter = WaitState.veryshot

    def setwaitveryshort(self):
        self.currentwaiter = WaitState.veryshot

    def setwaitshort(self):
        self.currentwaiter = WaitState.short

    def setwaitmiddle(self):
        self.currentwaiter = WaitState.middle

    def setwaitlong(self):
        self.currentwaiter = WaitState.long

    def setwaitverylong(self):
        self.currentwaiter = WaitState.verylong

    def resetwaiter(self):
        self.currentwaiter = WaitState.veryshot


# Enum for handling waiting state
#   number displays seconds to wait
class WaitState(Enum):
    veryshot = 0.7
    short = 3
    middle = 5
    long = 7
    verylong = 10


# Enum to representing the mode of the model class
#   config mode reads all values from given config file
#   interactive mode reads all values from terminal through an interactive session with an user
class ScriptMode(Enum):
    configmode = 0
    interactivemode = 1
