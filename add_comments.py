from visualize import read_conll
import codecs
import json
import os.path
try:
    import argparse
except ImportError:
    import compat.argparse as argparse

def print_sent(sent,comments):
    if comments:
        print (u"\n".join(comments)).encode(u"utf-8")
    print (u"\n".join(u"\t".join(cols) for cols in sent)).encode(u"utf-8")

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('-d', required=True, help='Where to read the comments?')
args = parser.parse_args()

comms=None
if os.path.isfile(args.d):
    with open(args.d,"r") as f:
        comms=json.load(f)

sent_count=0
for sent,comments in read_conll(None,0):
    sent_count+=1
    if sent_count!=1:
        print
    if comms:
        comments=comms.get(unicode(sent_count),[])
    print_sent(sent,comments)
