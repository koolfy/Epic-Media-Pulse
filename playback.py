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

import qlist


class Playback:

    def __init__(self, qlist=None):
        #qlist is a tuple containing both qlist and list
        # in order to generate a new qlist from list if needed.
        #   this should be moved to a dedicated method
        #   triggered by the daemon, as it makes no sense
        #   in a constructor.
        if(qlist is not None):
            self.qlist = qlist[0]
            self.list = qlist[1]

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
        try:
            self.sink = gst.element_factory_make("pulsesink", "pulseaudio-output")
        except gst.ElementNotFoundError:
            print "PulseAudio not found, falling back to ALSA"
            self.sink = gst.element_factory_make("alsasink", "alsa-output")
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

    def set_qlist(self, qlist):
        '''Affects a qlist to the player. qlist is a tuple'''
        self.qlist = qlist[0]
        self.list = qlist[1]
        # state must be set to paused if another song was already set
        self.set_stop()
        self.set_song(self.qlist.current.id)

    def set_prev(self):
        '''switch to the prev song in the qlist'''
        # THE STATE MUST BE SET TO STOP PRIOR TO CALLING THIS

        prev = self.qlist.prev()

        if prev:
            self.set_song(prev.id)
            return True

        if self.qlist.mode == "repeat" and self.qlist.order == "shuffle":
            self.qlist = qlist.Qlist(self.list, "shuffle")
            self.qlist.current = self.qlist.last
            self.set_song(self.qlist.current.id)
            return True

        if self.qlist.mode == "repeat" and self.qlist.order == "normal":
            self.qlist.current = self.qlist.last
            self.set_song(self.qlist.current.id)
            return True

        return False

    def set_next(self):
        '''switch to the next song in the qlist'''
        # THE STATE MUST BE SET TO STOP PRIOR TO CALLING THIS

        next = self.qlist.next()

        if next:
            self.set_song(next.id)
            return True

        if self.qlist.mode == "repeat" and self.qlist.order == "shuffle":
            self.qlist = qlist.Qlist(self.list, "shuffle")
            self.set_song(self.qlist.current.id)
            return True

        if self.qlist.mode == "repeat" and self.qlist.order == "normal":
            self.qlist.current = self.qlist.first
            self.set_song(self.qlist.current.id)
            return True

        return False

    def set_play(self):
        print "playing " + self.qlist.current.id
        self.pipeline.set_state(gst.STATE_PLAYING)

    def set_pause(self):
        self.pipeline.set_state(gst.STATE_PAUSED)

    def set_stop(self):
        self.pipeline.set_state(gst.STATE_READY)

    def set_clean(self):
        '''Set the pipeline to a state where everything is cleared and free.'''
        self.pipeline.set_state(gst.STATE_NULL)

    def get_state(self):
        '''Return the state of the pipeline'''
        real_state = self.pipeline.get_state()
        return real_state

    def get_state_string(self):
        '''Return a string representation of the pipeline state'''
        real_state = self.get_state()
        #real_state is a tuple, we want the second value here.
        string_state = gst.element_state_get_name(real_state[1])
        return string_state
