from visualize import read_conll
import codecs
import json
try:
    import argparse
except ImportError:
    import compat.argparse as argparse

def print_sent(sent):
    print (u"\n".join(u"\t".join(cols) for cols in sent)).encode(u"utf-8")

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('-d', required=True, help='Where to save the comments?')
args = parser.parse_args()

comms=dict()
sent_count=0
for sent,comments in read_conll(None,0):
    sent_count+=1
    if comments:
        comms[sent_count]=comments
    if sent_count!=1:
        print
    print_sent(sent)
    
    
with codecs.open(args.d,u"w") as f:
    json.dump(comms,f)
