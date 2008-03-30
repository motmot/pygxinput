# ----------------------------------------------------------------------------
# Copyright (c) 2008 Andrew D. Straw
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
__version__ = '0.0.1' # keep in sync with setup.py

import ctypes

import pyglet.event
import pyglet.window.xlib
import pygxinput.xinput as xinput
import pyglet.window.xlib.xlib as xlib

# TODO: find out how to discover these.
#XinputKeyPress = ??
#XinputKeyRelease = ??
XinputButtonPress = 100
XinputButtonRelease = 101
XinputMotion = 102

class XlibWithXinputWindow( pyglet.window.xlib.XlibWindow ):
    def __init__(self, *args, **kwargs):
        self.register_event_type('on_xinput_button_press')
        self.register_event_type('on_xinput_button_release')
        self.register_event_type('on_xinput_motion')
        super(XlibWithXinputWindow, self).__init__(*args, **kwargs)

    @pyglet.window.xlib.XlibEventHandler(XinputButtonPress)
    @pyglet.window.xlib.XlibEventHandler(XinputButtonRelease)
    def _event_xinput_button( self, ev ):
        evptr = ctypes.cast( ctypes.byref(ev), ctypes.POINTER(xinput.XDeviceButtonEvent))
        button = evptr.contents
        if ev.type == XinputButtonPress:
            self.dispatch_event('on_xinput_button_press', button.button)
        elif ev.type == XinputButtonRelease:
            self.dispatch_event('on_xinput_button_release', button.button)

    @pyglet.window.xlib.XlibEventHandler(XinputMotion)
    def _event_xinput_motion( self, ev ):
        evptr = ctypes.cast( ctypes.byref(ev), ctypes.POINTER(xinput.XDeviceMotionEvent))
        motion = evptr.contents
        axis_data = []
        for i in range(motion.axes_count):
            axis_data.append( motion.axis_data[i] )
        self.dispatch_event('on_xinput_motion', axis_data)

def get_xinput_device_identifiers( window ):
    names = []
    count = ctypes.c_int(0)
    devices = xinput.XListInputDevices(window._x_display, count)

    found = False
    for i in range(count.value):
        info = devices[i]
        names.append( info.name )
    return names

class XInputDevice(object):
    def __init__(self, window, identifier):
        count = ctypes.c_int(0)
        devices = xinput.XListInputDevices(window._x_display, count)

        found = False
        for i in range(count.value):
            info = devices[i]
            if info.name == identifier:
                found = True
                break

        if not found:
            raise ValueError('No device with identifier "%s" was found'%identifier)

        self.window = window
        self.device = xinput.XOpenDevice( window._x_display, info.id )
        self.last_time = 0

        if info.num_classes > 0:
            # This is inspired by test.c of xinput package by Frederic
            # Lepied available at x.org.
            event_list = []
            for i in range(info.num_classes):
                device = self.device[0]
                ip = device.classes[i]
                if ip.input_class == xinput.KeyClass:

                    # In C, this stuff is normally handled by the
                    # macro DeviceKeyPress and friends. Since we don't
                    # have access to those macros here, we do it this
                    # way.

                    _type = ip.event_type_base + xinput._deviceKeyPress
                    _class = device.device_id << 8 | _type
                    event_list.append( _class )

                    _type = ip.event_type_base + xinput._deviceKeyRelease
                    _class = device.device_id << 8 | _type
                    event_list.append( _class )

                elif ip.input_class == xinput.ButtonClass:
                    _type = ip.event_type_base + xinput._deviceButtonPress
                    _class = device.device_id << 8 | _type
                    event_list.append( _class )
                    assert _class == XinputButtonPress # double check that our hard-coding is OK

                    _type = ip.event_type_base + xinput._deviceButtonRelease
                    _class = device.device_id << 8 | _type
                    event_list.append( _class )
                    assert _class == XinputButtonRelease # double check that our hard-coding is OK

                elif ip.input_class == xinput.ValuatorClass:
                    _type = ip.event_type_base + xinput._deviceMotionNotify
                    _class = device.device_id << 8 | _type
                    event_list.append( _class )
                    assert _class == XinputMotion # double check that our hard-coding is OK
                else:
                    raise ValueError("unknown input_class")

            XEventArray = xinput.XEventClass*len(event_list)
            xea = XEventArray( *event_list )
            err=xinput.XSelectExtensionEvent( window._x_display,
                                              window._window,
                                              xea,
                                              len(event_list) )
            if err:
                raise RuntimeError('error %d registering events'%err)
