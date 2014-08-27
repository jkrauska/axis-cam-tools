#!/usr/bin/python

"""
axis-linker

This script is meant to be run as a cron job to help overlay a more usaable
symlinked directory structure on top of the one that axis cameras make when
storing video to a network share.

Problem:
The axis software makes a new subdirectory for every small capture file.
This makes reviewing the captures sequentially difficult to do.
eg. axis-CAMERA/20140428/19/20140428_191525_8085_macaddr/20140428_19/20140428_191525_D751_macaddr.mkv

Solution:
Creates two hierarchies of relative symlinks to the original files.
 - One by unique camera name in per day folders (to review a single camera's footage easily)
   eg. axis-CAMERA/20140428/20140428_191525_D751_macaddr.mkv

 - One by time series (to review ALL cameras in a time series easily)
   eg. axis-bydate/20140428/20140428_191525_D751_macaddr.mkv

Prerequsites:
 - You must create a friendly symlink folder name for your camera's default director.
   eg. ln -s axis-0040FFFFFFFF axis-mainlobby
   This script will SKIP any directory that begins with axis-0
"""

import os
import datetime

rootdir='/data/ipcameras'
bydate_dirname='axis-ALL-bydate'
totalcount=0

print 'axis-linker.py'
print datetime.datetime.now()

# Walk down directory paths, starting at rootdir
for currentpath, dirs, files in os.walk(rootdir, followlinks=True):

    # Skip paths we don't care about
    if 'axis-' not in currentpath: continue

    # Skip paths created by axis software (see prereq about friendly top level names)
    if 'axis-0' in currentpath: continue

    # Skip paths created by this script
    if bydate_dirname in currentpath: continue

    # Using os.path.split, we can pull out the data we care about (datestamp and cameraname)
    #             tail5            tail4  tail3           tail2                   tail1
    #src .../axis-3-main-entrance/20140428/19/20140428_191525_8085_00408CFF5A9D/20140428_19/20140428_191525_D751_00408CFF5A9D.mkv

    # Grab different parts of the path (see above for locations of tailX)
    head1, tail1 = os.path.split(currentpath)
    head2, tail2 = os.path.split(head1)
    head3, tail3 = os.path.split(head2)
    head4, tail4 = os.path.split(head3)
    head5, tail5 = os.path.split(head4)

    # The names we care about...
    datestamp  = tail4
    cameraname = tail5

    # Walk each filename in the current path
    for filename in files:

        # We only care about .mkv video files
        if 'mkv' in filename:

            # Create a src and dst for the symlink
            src=os.path.join(currentpath,filename)
            dst=os.path.join(head3,filename)

            # Don't make symlinks of symlinks (safety check)
            if os.path.islink(src): continue

            ############################################################
            # Create new links in camera hierarchy
            if not os.path.exists(dst):
                print '-'*80
                print 'DEBUG datestamp ', datestamp
                print 'DEBUG source    ', src
                print 'DEBUG bycamera  ', dst

                # link it using a relative path
                os.symlink(os.path.relpath(src, head3), dst)
                totalcount+=1

            ############################################################
            # Create new links in bydate hierarchy

            # mkdir top level if missing
            if not os.path.exists(os.path.join(rootdir,bydate_dirname)):
               os.mkdir(os.path.join(rootdir,bydate_dirname))

            # directory with datestamp
            dateddirectory=os.path.join(rootdir,bydate_dirname, '%s' % datestamp)

            # mkdir datestamp directory if missing
            if not os.path.exists(dateddirectory):
                os.mkdir(dateddirectory)

            # Insert camera name in filename
            filenamewithcamera=filename.replace('.mkv', '-%s.mkv' % cameraname )

            # new full filename with datestamp and camera name
            datefilename=os.path.join(dateddirectory,'%s' % filenamewithcamera)

            # link it using a relative path
            if not os.path.exists(datefilename):
                print 'DEBUG bydate    ', datefilename
                os.symlink(os.path.relpath(src, dateddirectory), datefilename)
                totalcount+=1

print '='*80
print 'Links created: %s' % (totalcount)
print datetime.datetime.now()
