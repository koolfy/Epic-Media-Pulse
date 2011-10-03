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
import qlist

import sources


class Daemon:

    def __init__(self):

        #Create the playback interface
        self.player = playback.Playback()
        self.bus_init(self.player)

        #Create the gobject mainloop for bus events watching
        self.mainloop = gobject.MainLoop()

        #Create the network interface
        self.network = Network(self, self.player)
        gobject.timeout_add(300, self.network.check_input)

    def bus_init(self, player):
        '''Create event watching bus.'''
        self.bus = self.player.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.__on_message, self.player)

    def __on_message(self, bus, message, player):
        type = message.type
        #testing handling, only cleaning nicely for now.
        if (type == gst.MESSAGE_EOS):
            print "File ended."
            self.player.set_stop()

            if not self.player.set_next():
                print "Playlist ended.\ncleaning."
                self.player.set_clean()
            else:
                self.player.set_play()

    def run(self):
        '''Launch the main loop'''
        self.mainloop.run()

    def quit(self):
        '''Destroy the main loop'''
        self.mainloop.quit()


class Network:

    def __init__(self, daemon, player,\
                 listen_sock=None, communication_sock=None):

        self.daemon = daemon
        self.player = player

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
        self.s.close()
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
            self.daemon.quit()

        if buffer == "load qlist\n":
            print "Loading generic testing queue list."
            generic_list = ["2001.ogg"]  # Strauss - Also Sprach Zarathustra
            generic_qlist = (qlist.Qlist(generic_list), generic_list)
            self.player.set_qlist(generic_qlist)

        if buffer == "db-create\n":
            print "Creating void database."
            self.daemon.db = sources.Local.db_create('database')

        if buffer == "db-import\n":
            print "Importing audio files in ./Music."
            self.daemon.db = sources.Local.db_import('Music', self.daemon.db)
            # Temporary debug code :
            print('this is the new database :')
            for key in self.daemon.db:
                print('file name : ' + key)
                for (fname, fvalue) in self.daemon.db[key].items():
                    print('-- ' + fname + ' : ' + fvalue[0])

        if buffer == "play\n":
            print "Reiceived a play query"
            self.player.set_play()

        if buffer == "pause\n":
            print "Received a pause query."
            self.player.set_pause()

        if buffer == "next\n":
            print "Received a 'Next song' query."
            if self.player.get_state_string() == "PLAYING":
                was_playing = True
            else:
                was_playing = False
            self.player.set_stop()
            if not self.player.set_next():
                print "Playlist ended.\ncleaning."
                self.player.set_clean()
            elif was_playing:
                self.player.set_play()

        if buffer == "prev\n":
            print "Received a 'Previous song' query."
            if self.player.get_state_string() == "PLAYING":
                was_playing = True
            else:
                was_playing = False
            self.player.set_stop()
            if not self.player.set_prev():
                print "There is no previous entry in the playlist."
            if was_playing:
                self.player.set_play()

        if "volume" in buffer:
            print "Received a Volume query."
            level = buffer.split(" ")[1][:-1] #split volume and \n
            ret = self.player.set_volume(level)
            print "Volume set to %s%%" % (ret*100)

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

# Launch EMP :)
if __name__ == '__main__':
    daemon = Daemon()
    daemon.run()
