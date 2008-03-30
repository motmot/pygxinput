from setuptools import setup, find_packages

setup(name='pygxinput',
      description="Use XInput devices in pyglet.",
      long_description = \
"""pygxinput allows use of XInput devices in pyglet. Such devices
include 3Dconnexion Space Navigator and Wacom tablets.
""",
      version='0.0.1', # keep in sync with pygxinput/pygxinput.py
      install_requires=['pyglet>=1.1alpha2',],
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      url='http://code.astraw.com/projects/motmot/wiki/pygxinput',
      license='BSD',
      packages=find_packages(),
      )
