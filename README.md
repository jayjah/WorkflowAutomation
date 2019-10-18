# Python Workflow Automation v000+1
## This software automates a workflow to set up android devices on the easy way.

### usage and information
#### AndroidViewClient is generally used for testing, but could be an alternative to monkeyrunner
#### to accomplish the same result
#### more info and source code: https://github.com/dtmilano/AndroidViewClient/wiki

#### CULEBRA seems to be the right and easy choice to get view / activity information from current android device screen. With this part of information it should be easy to handle the right android touches and moves to set up android devices.

##### requirements:
###### - python 2.7
###### - androidviewclient/culebra
###### - android sdk -> adb homepath
###### [- android file transfer only macOS]

##### install androidviewclient/culebra:
###### sudo easy_install install androidviewclient
###### sudo easy_install --upgrade androidviewclient
###### Download source code from AndroidViewClient (link is above) and set homepath: 'export ANDROID_VIEW_CLIENT_HOME=/path/to/androidviewclient/'
###### To verify correct installation: 'culebra --version' ; connect android device and run 'culebra'