htpc-scripts
============
shrink.py - Reads in video files from my htpc, checks to see if the ratio of size on disc to length of video is too great, and if so, copies the file over to the processing directory, runs HandBrakeCLI with the AppleTV 2 preset (I only have a 720p TV), and pushes the new file back to the original directory, deleting the original.  If you end up using this script, you must have HandBrakeCLI installed, or modify the subprocess.Popen() command to suit your needs, and must supply the PROCESSING_DIR & SOURCE_DIR.
