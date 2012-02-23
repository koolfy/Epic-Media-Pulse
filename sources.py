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

import os
import glob
import mutagen
import mimetypes
import sqlite3

SUPPORTED_TYPES = [
    'audio/mpeg',
    'audio/ogg',
    'audio/flac',
    ]

class Local:
    @classmethod
    def __init__(self, filename):
        if (os.path.exists(filename) == False):
            self.db_create(filename)
        else:
            self.directory = filename
            self.db = sqlite3.connect(self.directory)
            self.cursor = self.db.cursor()


    @classmethod
    def db_create(self, filename):
        '''Create a void database'''
        self.directory = filename
        self.db = sqlite3.connect(self.directory)
        self.cursor = self.db.cursor()
        self.cursor.execute('''create table artist ( id integer, name text)''')
        self.cursor.execute('''create table album ( id integer, title text,\
                   year integer, idartist integer)''')
        self.cursor.execute('''create table song ( id integer, title text, file text,\
                    genre integer, idalbum integer, idartist integer)''')
        
        self.db.commit()

    @classmethod
    def db_close(self):
        '''Close the active database'''
        self.db.commit()
        self.cursor.close()

    @classmethod
    def db_import(self, folder):
        '''Import all files from a folder to the database'''
        for filename in glob.glob(folder + '/*'):
            filetype = mimetypes.guess_type(filename)[0]
            
            if filetype not in SUPPORTED_TYPES:
                print "File %s unsupported, passing..." % filename
                continue

            print "Importing " + filename + " ..."
            
            tags = mutagen.File(filename, easy=True)
            if tags == None:
                print('ERROR : ' + filename + ' has no ID3 tag, skipping...')
            #else:
            ## Insert here the code of an actual importation
            ## in the sqlite database for each song
            ## - has to check if it is already there
            ## - has to hack if the artist/album already exists
            ## - if so, link to them. If not, create and link
            ## - what if an important tag is missing ? -> UNKNOWN
