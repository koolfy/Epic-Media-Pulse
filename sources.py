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

import pickle, glob
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

class local:
    
    @classmethod
    def dbcreate (self, file):
        '''Create a void database'''
        db = {}
        dbfile = open(file, 'wb')
        pickle.dump(db, dbfile)
        dbfile.close()
        return db

    @classmethod
    def dbload (self, file):
        '''Load a database from a file'''
        dbfile = open(file, 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
        return db

    @classmethod
    def dbsave (self, file, db):
        '''Save a database to a file'''
        dbfile = open(file, 'wb')
        pickle.dump(db, dbfile)
        dbfile.close()

    @classmethod
    def dbimport (self, folder, db):
        '''Import all mp3(for now) files from a folder to the database'''
        
        for filename in glob.glob(folder + '/*.mp3'):
            try:
                tags = MP3(filename, ID3=EasyID3)
            except mutagen.mp3.HeaderNotFoundError:
                print('ERROR : ' + filename + ' has no ID3 tag, skipping...')
            else:
                db[filename] = tags
        
        return db


# only a temporary test of the local pickle database implementation
if __name__ == '__main__':
    print('> creating database')
    db = local.dbcreate('database')
    print('> initializing database')
    db['koolfy - kakalol.mp3'] = {'artist' : ['koolfy'], 'title' : ['kakalol']}
    print('> saving database')
    local.dbsave('savedDatabase', db)
    print('> loading database')
    db2 = local.dbload('savedDatabase')

    print('this is the database that was loaded : ')
    for key in db2:
        print('file name : ' + key)
        for (fname, fvalue) in db2[key].items():
            print('-- ' + fname + ' : ' + fvalue[0])
    print('\n> importing files')
    db3 = local.dbimport('music', db2)
    print('this is the new database :')
    for key in db3:
        print('file name : ' + key)
        for (fname, fvalue) in db3[key].items():
            print('-- ' + fname + ' : ' + fvalue[0])
