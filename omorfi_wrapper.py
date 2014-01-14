#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import subprocess

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))

class OmorfiWrapper(object):

    def __init__(self, transducer_file):
        if not os.path.exists(transducer_file):
            raise Exception("No transducer file found: %s" % transducer_file)

        self.log = logging.getLogger("hfst")


        self.process = subprocess.Popen(["java","-jar", os.path.join(SCRIPTDIR,"LIBS/hfst-ol.jar"), transducer_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(self.process.stdout.readline,''):
            self.log.info("process: %s" % line.strip())
            if line == "Ready for input.\n":
                break
        self.log.info("Started the HFST process.")


    def lookup(self, word):
        self.log.info("Sending in query: %s" % word)
        self.process.stdin.write(word+"\n")
        self.process.stdin.flush()
        results = []
        for line in iter(self.process.stdout.readline,''):
            if line.strip() == "":
                break
            res = line.strip().split("\t")[1:3]
            if len(res)!=2:
                continue #bad data, unrecognized token?
            results.append(tuple(res))
        self.log.info("Got %d results, returning" % len(results))
        return results


    def close(self):
        self.process.kill()
        self.log.info("Killed the HFST process.")


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    hfst = OmorfiWrapper(sys.argv[1])

    try:
        while True:
            ret = raw_input("token> ")
            print hfst.lookup(ret)
    except KeyboardInterrupt:
        print

    hfst.close()
