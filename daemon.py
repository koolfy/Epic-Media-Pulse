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

import socket
import select

import playback


class daemon:

    def __init__(self):

        #Create the gobject mainloop for bus events watching
        self.mainloop = gobject.MainLoop()

        #Create the network interface
        self.network = network()
        gobject.timeout_add(300, self.network.check_input)

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


class network:

    def __init__(self, listen_sock=None, communication_sock=None):

        if(listen_sock is None):
            self.s = socket.socket()
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind(('', 39888))  # 39888 is the synodic period of Jupiter
            self.s.listen(1)

        else:
            self.s = listen_sock

        self.socket = communication_sock

    def __accept_incoming(self):
        print "accepting socket..."
        (self.socket, self.address) = self.s.accept()

    def __close_incoming(self):
        print "Gently closing socket."
        self.socket.shutdown(2)
        self.socket.close()
        self.socket = None

    def __close_listening(self):
        print "Closing listening socket"
        self.s.shutdown(2)
        self.s.close()i
        self.s = None

    def __on_incoming(self):
        buffer = self.socket.recv(4096)
        if len(buffer) is 0:
            print "Lost connection to socket."
            self.__close_incoming()
        self.__input_interpret(buffer)

    def __input_interpret(self, buffer):
        '''Interpret queries and act accordingly'''

        print "received : " + buffer,

        #not the actual protocol, only for testing purpose.
        if buffer == "destroy\n":
            print "Received a destroy query."
            self.__close_listening()
            self.__close_incoming()
            daemon.quit()

        if buffer == "pause\n":
            print "Received a pause query."
            player.set_pause()

    def check_input(self):
        '''Check if something is happenning and react.'''

        potential_read = []
        potential_write = []
        potential_errors = []
        timeout = 0.5

        if self.s is None:
            print "Cannot check sockets when none is created"
            return True
        else:
            potential_read.append(self.s)

        if(self.socket is not None):
            potential_read.append(self.socket)
            potential_write.append(self.socket)

        rdy_read, rdy_write, error = select.select(potential_read,\
                                                   potential_write,\
                                                   potential_errors,\
                                                   timeout)
        if self.s in rdy_read:
            print "connection request..."
            self.__accept_incoming()

        if self.socket in potential_write and self.socket not in rdy_write:
            print "socket is not currently active."
            return True

        if self.socket in rdy_read and self.socket is not None:
            self.__on_incoming()

        return True

#ugly testing, as usual...
if __name__ == '__main__':
    player = playback.playback()
    filepath = "2001.ogg"  # Strauss - Also Sprach Zarathustra
    player.set_song(filepath)

    player.set_play()
    daemon = daemon()
    daemon.bus_init(player)
    daemon.run()
