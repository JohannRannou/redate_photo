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
