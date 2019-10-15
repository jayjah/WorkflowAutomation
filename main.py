#! /usr/bin/env python
# -*- coding: utf-8 -*-


def create_google_acc(firstname, lastname, vc, device):
    vc = wait(vc)
    vc.findViewWithTextOrRaise(u'''Einstellungen''').touch()
    vc = wait(vc)
    open_in_settings("Konten", vc)
    vc = wait(vc)
    vc.findViewWithTextOrRaise(u'''Konten''').touch()
    vc = wait(vc)
    vc.findViewWithTextOrRaise(u'''Konto hinzufügen''').touch()
    vc = wait(vc)
    vc.findViewWithTextOrRaise(u'''Google''').touch()
    # wait here longer cause of request to google
    vc.sleep(8)
    vc.dump(window=-1)
    vc.findViewWithTextOrRaise(u'''Konto erstellen''').touch()
    vc = wait(vc)
    vc.findViewWithTextOrRaise(u'''Für mich selbst''').touch()
    vc = wait(vc)
    vc.findViewByIdOrRaise("firstName").type(firstname)
    vc = wait(vc)
    device.press('KEYCODE_ENTER')
    vc = wait(vc)
    vc.findViewByIdOrRaise("lastName").type(lastname)
    vc = wait(vc)
    device.press('KEYCODE_ENTER')
    vc = wait(vc)
    if vc.findViewByIdOrRaise("nameError") is not None:
        # error handling
        print ("error handling should be happenend here")
    # if something like: Bist du ein Roboter error handling
    vc.findViewByIdOrRaise("day").type(birthday)
    vc = wait(vc)

    vc.findViewByIdOrRaise("month-label").type(birthmonth)
    vc = wait(vc)
    vc.findViewByIdOrRaise("year").type(birthyear)





















