#!/usr/bin/python3

from gi.repository import GExiv2
from datetime import datetime
import os
import glob
import sys
from optparse import OptionParser
from subprocess import call

"""Renames picture files according to their date exif metadata. Possibly apply time correction.
"""

usage = u"""
Rename (mv) or copy (cp) a file with a new filename according its shottime and possibly applying a time correction.
The possible time correction changes the exif.DateTime field while keeping exif.DateTimeOriginal unchanged.

If move or copy is required, the script runs in dry mode by default. Use --force to do the copy or the move.

If one want to rename a file according to its exif.DateTime metada :
$ redateExif.py  --mv --force *.jpg

If one want to rename a file according to its exif.DateTime metada and applying a suffix:
$ redateExif.py  --mv --force --suffix MyCamera *.jpg

If it has been identified that a picture in the group was shot at 12:00:00 (exif.OriginalDateTime) was actually shot at 12:13:13, the following command simply change the exif.DateTime :
$ redateExif.py -o 12:00:00 -n 12:13:13 *.jpg
This means that exif.DateTime of all pictures will be shifted by 13 min and 13 seconds.

If one want to change time and copy files
$ redateExif.py -o 12:00:00 -n 12:13:13 --cp --force *.jpg
""" 

# usage: %prog node:workingPath \n or    %prog --log"
parser = OptionParser(usage=usage)
# parser = OptionParser()

parser.add_option("-c","--cp",  dest="doCopy", default=False, 
                  help="", 
                  action="store_true")
parser.add_option("-m","--mv",  dest="doMove", default=False, 
                  help="", 
                  action="store_true")
parser.add_option('-f',"--force",  dest="force_mode", default=False, 
                  help="If not specified, dry run ", 
                  action="store_true")
parser.add_option("-o", "--oldTime", dest="oldTime", 
                  default='12:00:00', help="", 
                  action="store", type='string')
parser.add_option("-n", "--newTime", dest="newTime", 
                  default='12:00:00', help="", 
                  action="store", type='string')
parser.add_option("-s", "--suffix", dest="suffix", 
                  default='', help="", 
                  action="store", type='string')

(options, args) = parser.parse_args()


def signe(x) :
    if x == '-' :
        return -1.
    else :
        return 1.

    
def computeNewTime(currentTime, oldTime, newTime) :
    """Returns currentTime + newTime - oldTime
    Compute the difference betwenn oldTime and newTime.
    """
    #    datetime.strptime( "2007-03-04T21:08:12", "%Y-%m-%dT%H:%M:%S" )
    ct=datetime.strptime( currentTime, "%Y:%m:%d %H:%M:%S" )
    ot=datetime.strptime( oldTime, "%H:%M:%S" )
    nt=datetime.strptime( newTime, "%H:%M:%S" )
    diff=nt-ot
    return ct+diff




### Modification of exif
files = args
for filename in files:

    # print('processing  exif of file:', filename)

    metaData = GExiv2.Metadata(filename)
    try:
        shootTime= metaData['Exif.Photo.DateTimeOriginal']
    except KeyError:
        print('Except')
        shootTime= metaData['Exif.Image.DateTime']
    except:
        raise

 
    newTime = computeNewTime(shootTime, options.oldTime, options.newTime)


    metaData['Exif.Image.DateTime'] = newTime.isoformat(sep=' ').replace('-',':')

    metaData.save_file()

def prepare_mv_cp():
    """Build the list of old filename / new filename
    This is usefull to do it before for the dry mode (ie default mode with no --force)

    """
    if options.suffix != "":
        suffix = '__' + options.suffix
    else:
        suffix = ''
    
    old_name_list = []
    new_name_list = []
    for old_name in files:
        metaData = GExiv2.Metadata(old_name)
        extension = old_name.split('.')[-1]
        
        shootTime= metaData['Exif.Image.DateTime']
        date, time = shootTime.split(' ')
        year, month, day = date.split(':')
        hour, minute, second = time.split(':')
        new_name = '{}-{}-{}_{}-{}-{}{}.{}'.format(year, month, day, hour, minute,
                                                     second, suffix, extension)
        
        old_name_list.append(old_name)

        if new_name not in new_name_list:
            new_name_list.append(new_name)
        else:
            im_count = 1
            # this is volontary, the second file will be named toto-2.jpg while the
            # first one will be called toto.jpg and not toto-1.jpg
            while new_name in new_name_list:
                im_count = im_count + 1 
                new_name = '{}-{}-{}_{}-{}-{}_{}{}.{}'.format(year, month, day, hour, minute,
                                                                second, im_count, suffix, extension)
            new_name_list.append(new_name)
                
        if old_name_list[-1] == new_name_list[-1]:
            print()
            raise RuntimeError("\nWarning, old_name={} and new_name={} are the same.\n This could lead to loss of files.\n Try using --suffix".format(old_name_list[-1],new_name_list[-1]))
        
    return old_name_list, new_name_list


### cp or mv (if --force is not used, only apply what would be done)
if options.doCopy or options.doMove:
    old_name_list, new_name_list = prepare_mv_cp()

    if options.doCopy:
        com = 'cp'
    elif  options.doMove:
        com = 'mv'
    else:
        raise RuntimeError

    for old_name, new_name in zip(old_name_list, new_name_list):
        command = '{} {} {}'.format(com, old_name, new_name)
        print(command)
        if options.force_mode:
            call([com, old_name, new_name])
            
