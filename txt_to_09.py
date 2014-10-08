import sys
import json
import os.path
try:
    import argparse
except ImportError:
    import compat.argparse as argparse


parser = argparse.ArgumentParser(description='Options')
parser.add_argument('-d', help='Where to read the comments?')
args = parser.parse_args()

hashes=None
if args.d and os.path.isfile(args.d):
    with open(args.d,"r") as f:
        hashes=json.load(f)

for lineIdx,line in enumerate(sys.stdin):
    line=unicode(line,"utf-8").rstrip()
    if not line or line.startswith(u"###START") or line.startswith(u"###END"):
        continue
    tokens=line.split()
    if lineIdx!=0 and comment==False: # do not print empty line after comment
        print
    if hashes and len(tokens)==1 and tokens[0] in hashes: # this is hashed comment, extract it
        print hashes[tokens[0]].encode(u"utf-8")
        comment=True
        continue
    for tIdx,t in enumerate(tokens):
        print (u"%d\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_"%(tIdx+1,t)).encode("utf-8")
        comment=False

