from __future__ import division
import datetime
import glob
import gobject
import os
import sys
import subprocess
import shutil
import time


PROCESSING_DIR = ''
SOURCE_DIR = ''

FILE_TYPES = ('.m4v', '.mkv', '.avi', '.wmv', '.mpg', '.mpeg')
MAX_RATIO = 3.0

FILE_OBJECTS = glob.glob(os.path.join(SOURCE_DIR, '*'))
VIDEO_OBJECTS = []

gobject.threads_init()
import pygst
pygst.require('0.10')
import gst


def get_ratio(f):
    size = (os.path.getsize(f) / 1073741824)
    d = gst.parse_launch("filesrc name=source ! decodebin2 ! fakesink")
    source = d.get_by_name("source")
    source.set_property("location", f)
    d.set_state(gst.STATE_PLAYING)
    d.get_state()
    format = gst.Format(gst.FORMAT_TIME)
    duration = d.query_duration(format)[0]
    d.set_state(gst.STATE_NULL)
    delta = (duration / gst.SECOND) / 3600

    ratio = (size / delta)
    return ratio


for obj in FILE_OBJECTS:
    if os.path.isdir(obj):
        files = glob.glob('{0}/*'.format(obj))
        for f in files:
            if os.path.splitext(f)[1].lower() in FILE_TYPES:
                VIDEO_OBJECTS.append(f)

    if os.path.isfile(obj) and os.path.splitext(obj)[1].lower() in FILE_TYPES:
        VIDEO_OBJECTS.append(obj)


for video in VIDEO_OBJECTS:
    ratio = get_ratio(video)
    if ratio > MAX_RATIO:
        filename = os.path.splitext(os.path.basename(video))
        backup_name = '{0}.orig{1}'.format(*filename)
        new_name = '{0}.mp4'.format(filename[0])
        original_path = os.path.dirname(video)


        if not os.path.isfile(os.path.join(PROCESSING_DIR, backup_name)):
            print '>>> Copying file `{0}` to local system for re-encoding...'.format(video)
            shutil.copy(video, os.path.join(PROCESSING_DIR, backup_name))

        if os.path.isfile(os.path.join(PROCESSING_DIR, new_name)):
            print '>>> Deleting previous copy of new file `{0}`.'.format(new_name)
            os.remove(os.path.join('/media/Data/Ripped/HBTemp/', new_name))

        print '>>> Encoding file `{0}` to `{1}`...'.format(backup_name, new_name)
        s = subprocess.Popen([
            '/usr/bin/HandBrakeCLI', 
            '-i', os.path.join(PROCESSING_DIR, backup_name),
            '-o', os.path.join(PROCESSING_DIR, new_name),
            '-Z', 'AppleTV 2'],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True)

        while True:
            line = s.stdout.readline()
            if not line:
                print '>>> Finished encoding `{0}`.'.format(new_name)
                break

            if 'Encoding' in line:
                print "\r>>> " + str(line.rstrip()), 
                s.stdout.flush()
                time.sleep(1)

        print '>>> Copying new file `{0}` to remote system...'.format(new_name)
        shutil.copy(os.path.join(PROCESSING_DIR, new_name), os.path.join(original_path, new_name))

        print '>>> Deleting orignal file `{0}` on remote system...'.format(video)
        os.remove(video)

        print '>>> Done.\n'
