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
        
        self.maxSongId = 0
        self.maxArtistId = 0
        self.maxAlbumId= 0

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
        self.songList = []
        self.artistList = []
        self.albumList = []
        self.albumIdList = []
        self.artistIdList = []
        self.artistId = 0
        self.albumId= 0
        dblist = ['song', 'artist', 'album']
        for db in dblist:
            self.cursor.execute('''select * from ''' + db)
            for entry in self.cursor:
                if (db == 'song'): self.songList.append(entry[2])
                if (db == 'artist'): 
                    self.artistList.append(entry[1])
                    self.artistIdList.append(entry[0])
                else: 
                    self.albumList.append(entry[1])
                    self.albumIdList.append(entry[0])
        
        self.cursor.execute('''select * from song order by 1 desc limit 1''')
        for entry in self.cursor:
                self.maxSongId = entry[0]

        self.cursor.execute('''select * from artist order by 1 desc limit 1''')
        for entry in self.cursor:
                self.maxArtistId = entry[0]

        self.cursor.execute('''select * from album order by 1 desc limit 1''')
        for entry in self.cursor:
                self.maxAlbumId = entry[0]


        for filename in glob.glob(folder + '/*'):
            filetype = mimetypes.guess_type(filename)[0]
            
            if filetype not in SUPPORTED_TYPES:
                print "File %s unsupported, passing..." % filename
                continue

            print "Importing " + filename + " ..."
            
            tags = mutagen.File(filename, easy=True)
            if tags == None:
                print('ERROR : ' + filename + ' has no ID3 tag, skipping...')
                continue
            
            if filename in self.songList:
                print('ERROR : ' + filename + ' already in the database,'\
                    + ' skipping...')
                continue
            else:
                if (tags['artist'][0] in self.artistList):
                    index = self.artistList.index(tags['artist'][0])
                    self.artistId = self.artistIdList[index]
                else:
                    self.maxArtistId = self.maxArtistId +1
                    t = (self.maxArtistId, tags['artist'][0])
                    self.cursor.execute('''insert into artist (id, name) '''\
                                        + '''VALUES (?, ?)''', t)
                    self.artistId = self.maxArtistId

                if (tags['album'][0] in self.albumList):
                    index = self.albumList.index(tags['album'][0])
                    self.albumId = self.albumIdList[index]
                else:
                    self.maxAlbumId = self.maxAlbumId +1
                    t = (self.maxAlbumId, tags['album'][0])
                    self.cursor.execute('''insert into album (id, title,'''\
                                        ''' year, idartist) VALUES'''\
                                        '''(?, ?, 0, 0)''', t)
                    self.albumId = self.maxAlbumId

                self.maxSongId = self.maxSongId +1
                t = [self.maxSongId, tags['title'][0], filename,\
                     self.albumId, self.artistId ]
                self.cursor.execute('''insert into song (id, title, file,\
                    genre, idalbum, idartist)\
                    VALUES (?, ?, ?, 0, ?, ?)''', t)
                
                self.db.commit()
            
if __name__ == '__main__':
        testbase = Local('database')
        testbase.db_import('Music')
        testbase.db_close()

            
            ## Insert here the code of an actual importation
            ## in the sqlite database for each song
            ## - has to check if it is already there
            ## - has to hack if the artist/album already exists
            ## - if so, link to them. If not, create and link
            ## - what if an important tag is missing ? -> UNKNOWN
