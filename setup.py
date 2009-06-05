from setuptools import setup, find_packages

setup(name='pygxinput',
      description="Use XInput devices in pyglet.",
      long_description = \
"""pygxinput allows use of XInput devices in pyglet. Such devices
include 3Dconnexion Space Navigator and Wacom tablets.

For information about how to setup the Space Navigator as an XInput
device, see:

 * http://www.fedorawiki.de/index.php/SpaceNavigator (in German)
 * http://www.3dconnexion.com/forum/viewtopic.php?p=1431&sid=9cb59f09ea21510071372daf670e1f8b#1431
 * http://www.3dconnexion.com/forum/viewtopic.php?p=7683#7683

For an alternative Space Navigator driver (currently not XInput compatible), see:

 * http://spacenav.sourceforge.net/

""",
      version='0.0.1', # keep in sync with pygxinput/pygxinput.py
      install_requires=['pyglet>=1.1',],
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      url='http://code.astraw.com/projects/motmot/wiki/pygxinput',
      license='BSD',
      packages=find_packages(),
      )
