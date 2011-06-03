#  Copyright 2011 Daniel "koolfy" Faucon <koolfy@geekmx.org>
#
#  This file is part of Epic Media Pulse.
#
#  Epic Media Pulse is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Epic Media Pulse is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Epic Media Pulse.  If not, see <http://www.gnu.org/licenses/>.
#!/usr/bin/env python

import time #only used for testing.

import gobject
gobject.threads_init() #dynamic pads will not work without this.

import pygst
pygst.require("0.10")
import gst

class playback:
    
    def __init__(self):
        
        #create pipeline (container for the playback chain)
        self.pipeline = gst.Pipeline("mypipeline")
        
        #create source
        self.source = gst.element_factory_make("filesrc", "file-source")
        self.pipeline.add(self.source)
        
        #create generic decoder
        self.decoder = gst.element_factory_make("decodebin2", "audio-decoder")
        #call OnDynamicPad to link it when pads are ready.
        self.decoder.connect("new-decoded-pad", self.__OnDecoderDPad)
        self.pipeline.add(self.decoder)
        

        #link source -> decoder
        self.source.link(self.decoder)

        #create audio converter, can't link it to decoder yet. ('cause of dynamic pads)
        self.conv = gst.element_factory_make("audioconvert", "converter")
        self.pipeline.add(self.conv)


        #create audio sink
        self.sink = gst.element_factory_make("pulsesink", "pulseaudio-output")
        self.pipeline.add(self.sink)

        #link audio converter -> sink
        self.conv.link(self.sink)


    def __OnDecoderDPad(self, dbin, pad, islast):
        '''called when decoder's dyn pads are ready'''
        pad.link(self.conv.get_pad("sink"))


    #Methods used to interact with playback

    def SetSong(self, path):
        '''Sets a song into the gst pipeline'''
        self.source.set_property("location", path)

    def SetPlay(self):
        self.pipeline.set_state(gst.STATE_PLAYING)

    def SetPause(self):
        self.pipeline.set_state(gst.STATE_PAUSED)

    def SetStop(self):
        self.pipeline.set_state(gst.STATE_READY)

    def SetClean(self):
        '''Set the pipeline to a state where everything is cleared and free.'''
        self.pipeline.set_state(gst.STATE_NULL)

#Ugly testing, will be cleaned up... eventually.
if __name__ == '__main__':

    player = playback()
    filepath = "2001.ogg" # Strauss - Also Sprach Zarathustra
    player.SetSong(filepath)
   
    print "Playing..."
    player.SetPlay()
    time.sleep(25)
    
    print "Pausing..."
    player.SetPause()
    time.sleep(3)
    
    print "Resuming..."
    player.SetPlay()
    time.sleep(10)
    
    print "stopping."
    player.SetStop()
    time.sleep(2)

    print "Cleaning the pipes and exiting."
    player.SetClean()
