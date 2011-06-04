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

import gobject
gobject.threads_init()  # dynamic pads will not work without this.

import pygst
pygst.require("0.10")
import gst

import playback


class daemon:

    def __init__(self):

        #Create the gobject mainloop for bus events watching
        self.mainloop = gobject.MainLoop()

    def bus_init(self, player):
        '''Create event watching bus.'''
        self.bus = player.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.__on_message, player)

    def __on_message(self, bus, message, player):
        type = message.type
        #testing handling, only cleaning nicely for now.
        if (type == gst.MESSAGE_EOS):
            print "File ended.\ncleaning."
            player.set_clean()

    def run(self):
        '''Launch the main loop'''
        self.mainloop.run()

    def quit(self):
        '''Destroy the main loop'''
        self.mainloop.quit()

#ugly testing, as usual...
if __name__ == '__main__':
    player = playback.playback()
    filepath = "2001.ogg"  # Strauss - Also Sprach Zarathustra
    player.set_song(filepath)

    player.set_play()
    daemon = daemon()
    daemon.bus_init(player)
    daemon.run()
