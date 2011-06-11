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


class song:
    '''node structure for queue lists'''
    def __init__(self, id=None, prev=None,\
                 next=None, status=None, belongs_to=None):
        self.id = id
        self.next = next
        self.prev = prev
        self.status = status
        self.belongs_to = belongs_to

    def __str__(self):
        return str(self.id)


class qlist:
    '''queue lists for the player to browse'''

    def __init__(self, list, style="normal"):
        if style is "normal":
            self.qlist_extrems = qlist.generate_from_list(list)
        self.first = self.qlist_extrems[0]
        self.last = self.qlist_extrems[1]
        self.current = self.qlist_extrems[0]

    def next(self):
        if self.current.next is None:
            print "There is no entry after " + self.current.id
            return False
        else:
            self.current = self.current.next
            return self.current

    def prev(self):
        if self.current.prev is None:
            print "There is no entry before " + self.current.id
            return False
        else:
            self.current = self.current.prev
            return self.current
    
    @classmethod
    def append_qlist(self, song, list):
        '''add a list of songs right next to an entry from the playlist'''
        next_node = song.next
        qlist_extrems = qlist.generate_from_list(list)
        qlist_head = qlist_extrems[0]
        qlist_tail = qlist_extrems[1]

        song.next = qlist_head
        qlist_tail.next = next_node

        return song

    @classmethod
    def generate_from_list(self, list):
        '''generate a linked list from a regular list'''
        previous = None
        for entry in list:
            if (previous == None):
                head = song(entry, None, None)
                head.next = song()
                previous = head
            else:
                tail = song(entry, previous, None)
                previous.next = tail
                previous = tail

        return (head, tail)


#only to test the linked list implementation
if __name__ == '__main__':
    testlist = ["kaka", "lol", "proute", "toast"]
    qlist1 = qlist(testlist)
    is_next = True
    while (is_next):
        print qlist1.current.id
        is_next = qlist1.next()

    testlist2 = ["1", "2", "3"]
    qlist1.prev()
    qlist1.append_qlist(qlist1.current, testlist2)

    print "\n testing append_qlist()\n"
    is_next2 = True
    while (is_next2):
        print qlist1.current.id
        is_next2 = qlist1.next()
    print "\nreverse !\n"
    is_prev = True
    while (is_prev):
        print qlist1.current.id
        is_prev = qlist1.prev()

