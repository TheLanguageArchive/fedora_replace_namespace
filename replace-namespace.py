#!/usr/bin/env python3

"""replace_namespace.py: Changes the namespace prefix of the Fedora PIDs in FOXML files (in place! make a backup copy!).
Takes a file of Fedora PIDs as the input, one PID per line, without info/fedora prefix."""

__author__ = "Paul Trilsbeek"
__license__ = "GPL3"
__version__ = "0.1"

import mmap
import logging
import os
import re
import urllib.parse
import hashlib
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-o", "--objectStore", dest="objectstore", nargs=1, help="the Fedora objectStore directory", required=True)
parser.add_argument("-p", "--pidfile", dest="pidfile", nargs=1,
                    help="the file containing the Feora PIDs (one per line) of the FOXML files that need to be modified", required=True)
parser.add_argument("-on", "--oldnamespace", dest="oldnamespace", nargs=1, help="the old namespace prefix", required=True)
parser.add_argument("-nn", "--newnamespace", dest="newnamespace", nargs=1, help="the new namespace prefix", required=True)
args = parser.parse_args()

pidfile = args.pidfile[0]
foxdir = args.objectstore[0]
oldnamespace = args.oldnamespace[0]
newnamespace = args.newnamespace[0]

# patterns in the FOXML (inc. DC, CMD, RELS-EXT, etc.) where Fedora namespaces occur.
# providing enough context around the namespace should guarantee safe find/replace in the whole file
patterns = ["PID=\"namespace:",
            "Copied datastream from namespace:",
            "<dc:identifier>namespace:",
            "MdSelfLink lat:flatURI=\"namespace:",
            "ResourceRef lat:flatURI=\"namespace:",
            "islandora/object/namespace%3A",
            "rdf:about=\"info:fedora/namespace:",
            "rdf:resource=\"info:fedora/namespace:",
            "oai:archive.mpi.nl:namespace:",
            "REF=\"namespace:"]

# create logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
CH = logging.StreamHandler()
CH.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

try:
    # counter + total number of pids, to have some idea of progress:
    counter = 0
    pf = open(pidfile)
    number_pids = sum(1 for line in pf)
    pf.close()
    # read pidfile using mmap
    with open(pidfile, 'rb', 0) as pf, \
            mmap.mmap(pf.fileno(), 0, access=mmap.ACCESS_READ) as pids:
        # walk through all files in foxdir subdirectories
        for root, dirs, files in os.walk(foxdir, topdown=False):
            for file in files:
                # turn filename into Fedora PID
                pid = re.sub("info%3Afedora%2F", "", file)
                pid = urllib.parse.unquote(pid)
                # turn pid string into bytes for the mmap search in python3
                pid_bytes = bytes(pid, 'utf-8')
                # look whether the pid occurs in our pidlist file
                if pids.find(pid_bytes) != -1:
                    # found it
                    counter += 1
                    LOGGER.info(str(counter) + "/" + str(number_pids) + "\t" + pid)
                    # open FOXML file for reading, read content and close it
                    fox_path = os.path.join(root, file)
                    ff = open(fox_path, 'r')
                    fox = ff.read()
                    ff.close()
                    # replace each pattern with old namespace to pattern with new namespace
                    for pattern in patterns:
                        old_ns_pattern = pattern.replace("namespace", oldnamespace)
                        new_ns_pattern = pattern.replace("namespace", newnamespace)
                        fox = fox.replace(old_ns_pattern, new_ns_pattern)
                    # write modified content back to FOXML file and close it
                    ff = open(fox_path, 'w')
                    ff.write(fox)
                    ff.close()
                    LOGGER.info("modified FOXML file: " + fox_path)
                    # replace namespace in filename and move file to new directory based on md5 hash of PID
                    old_ns_in_filename = 'info%3Afedora%2F' + oldnamespace + '%3A'
                    new_ns_in_filename = 'info%3Afedora%2F' + newnamespace + '%3A'
                    new_filename = file.replace(old_ns_in_filename, new_ns_in_filename)
                    new_filename_unquote = urllib.parse.unquote(new_filename)
                    new_filename_md5 = hashlib.md5(new_filename_unquote.encode('utf-8')).hexdigest()
                    new_root = root[:-2] + new_filename_md5[:2]
                    new_fox_path = os.path.join(new_root, new_filename)
                    os.rename(fox_path,new_fox_path)
                    LOGGER.info("renamed and moved FOXML file: " + new_fox_path)
    pids.close()
except Exception as ex:
    LOGGER.error(ex)
