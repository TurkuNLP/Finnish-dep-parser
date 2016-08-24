#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import select
logging.basicConfig(level=logging.WARNING)

import subprocess

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))

class HFSTError(Exception): pass

class OmorfiWrapper(object):

    def __init__(self, transducer_file):
        if not os.path.exists(transducer_file):
            raise Exception("No transducer file found: %s" % transducer_file)

        self.log = logging.getLogger("hfst")
        self.process=None
        self.transducer_file=transducer_file
        self.poll=None
        self.restart()


    def restart(self):
        if self.process is not None:
            #Try to kill
            self.process.terminate()
        self.poll=select.poll()
        try:
            self.log.info("Starting hfst-ol.jar")
            self.process = subprocess.Popen(["java","-jar", os.path.join(SCRIPTDIR,"LIBS","hfst-ol.jar"), self.transducer_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if self.process.returncode!=None: #Ended already - something's wrong
                self.log.debug("Non-zero exit code for hfst-ol.jar")
                raise HFSTError()
            self.log.info("hfst-ol.jar started")
            for line in iter(self.process.stdout.readline,''):
                self.log.info("process: %s" % line.strip())
                if line == "Ready for input.\n":
                    break
            else:
                raise HFSTError()
        except HFSTError:
            self.log.error("Did not succeed in launching 'java -jar LIBS/hfst-ol.jar %s'. The most common reason for this is that you forgot to run './install.sh'. Run it, and also run 'test_dependencies.py' to make sure all is OK.\n\nIf it fails even though you did succeed with ./install.sh, try to run 'java -jar LIBS/hfst-ol.jar model/morphology.finntreebank.hfstol'. It should start and ask for input with 'Ready for input.' Then type in 'koiransa' and see if you get a reasonable analysis. Then either open an issue at https://github.com/TurkuNLP/Finnish-dep-parser/issues  or email ginter@cs.utu.fi and jmnybl@utu.fi and we'll try to help you.\n\nGiving up, because the parser cannot run without morphological lookup."%transducer_file)
            sys.exit(1)
        self.log.info("Started the HFST process.")
        self.poll.register(self.process.stdout)
        


    def lookup(self, word):
        self.log.info("Sending in query: %s" % word)
        self.process.stdin.write(word+"\n")
        self.process.stdin.flush()
        results = []
        if not self.poll.poll(5000): #Nothing ready in five seconds - we're stuck
            self.restart()
            return []
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
