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

import pygst
pygst.require("0.10")
import gst


class Playback:

    def __init__(self):

        #create pipeline (container for the playback chain)
        self.pipeline = gst.Pipeline("mypipeline")

        #building that playback chain :

        #create source
        self.source = gst.element_factory_make("filesrc", "file-source")
        self.pipeline.add(self.source)

        #create generic decoder
        self.decoder = gst.element_factory_make("decodebin2", "audio-decoder")
        #call OnDynamicPad to link it when pads are ready.
        self.decoder.connect("new-decoded-pad", self.__on_decoder_dynpad)
        self.pipeline.add(self.decoder)

        #link source -> decoder
        self.source.link(self.decoder)

        #create audio converter, can't link it to decoder yet. (dynamic pads)
        self.conv = gst.element_factory_make("audioconvert", "converter")
        self.pipeline.add(self.conv)

        #create audio sink
        self.sink = gst.element_factory_make("pulsesink", "pulseaudio-output")
        self.pipeline.add(self.sink)

        #link audio converter -> sink
        self.conv.link(self.sink)

    #This does not need the mainloop and can be left in playback.py
    def __on_decoder_dynpad(self, dbin, pad, islast):
        '''called when decoder's dyn pads are ready'''
        pad.link(self.conv.get_pad("sink"))

    #Methods used to interact with playback

    def set_song(self, path):
        '''Sets a song into the gst pipeline'''
        self.source.set_property("location", path)

    def set_play(self):
        self.pipeline.set_state(gst.STATE_PLAYING)

    def set_pause(self):
        self.pipeline.set_state(gst.STATE_PAUSED)

    def set_stop(self):
        self.pipeline.set_state(gst.STATE_READY)

    def set_clean(self):
        '''Set the pipeline to a state where everything is cleared and free.'''
        self.pipeline.set_state(gst.STATE_NULL)
