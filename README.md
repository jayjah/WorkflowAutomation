# Python Workflow Automation v000+1
## This software automates a workflow to set up android devices on the easy way.

### usage and information
#### generally used for testing, but could be an alternative to monkeyrunner
#### to accomplish the same result
#### more info: https://github.com/dtmilano/AndroidViewClient/wiki

#### CULEBRA seems to be the right and easy choice to get view / activity information from current android device screen. With this part of information it should be easy to handle the right android touches and moves.

##### requirements:
###### - python 2.7
###### - androidviewclient (-> culebra --version)
###### - android sdk -> adb homepath
###### [- android file transfer only macOS]

##### install culebra:
###### sudo pip/easy_install install androidviewclient
###### sudo easy_install --upgrade androidviewclient
###### Download src(siehe Link oben) und Homepath setzen:
###### export ANDROID_VIEW_CLIENT_HOME=/path/to/androidviewclient/