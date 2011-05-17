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
    def __init__(self, id=None, prev=None, next=None):
        self.id = id
        self.next= next
        self.prev = prev

    def __str__(self):
        return str(self.id)


class qlist:
    '''queue lists for the player to browse'''

    @classmethod
    def generateFromList(self, list):
        '''generate a linked list from a regular list'''    
        previous= None
        for entry in list:
            if (previous == None):
                head = song(entry, None, None)
                head.next = song()
                previous = head
            else:
                tail = song(entry, previous, None)
                previous.next = tail
                previous = tail
        
        return head



#only to test the linked list implementation
if __name__ == '__main__':
    testlist = [ "kaka", "lol", "proute", "toast" ]
    qlist = qlist.generateFromList(testlist)
    print (qlist)
    print (qlist.next)
    qleast = qlist.next
    print (qleast.next)
