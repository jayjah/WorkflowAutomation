#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

print "Arguments: "
print sys.argv

print "Device || Id: Serialno: "
print "Bitte entsperre den Screen, damit die App Lock App eingerichtet werden kann."
inputval = raw_input("Nachdem die App entsperrt wurde, bitte Enter drücken.")
print inputval
exit(1)
