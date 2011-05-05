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

import pickle

class local:
    
    
    @classmethod
    def dbcreate (self, file):
    '''Create a void database with filename "file"'''
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




# only a temporary test of the local pickle database implementation
if __name__ == '__main__':
    db = local.dbcreate('database')
    db['koolfy - kakalol.mp3'] = {'artist' : 'koolfy', 'title' : 'kakalol'}
    local.dbsave('savedDatabase', db)
    db2 = local.dbload('savedDatabase')
    for key in db2:
        print('file name : ' + key)
        for (fname, fvalue) in db2[key].items():
            print('-- ' + fname + ' : ' + fvalue)
