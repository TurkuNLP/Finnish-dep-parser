from visualize import read_conll
import codecs
import json
import os.path

def print_sent(sent,comments):
    if comments:
        print (u"\n".join(comments)).encode(u"utf-8")
    print (u"\n".join(u"\t".join(cols) for cols in sent)).encode(u"utf-8")

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))

comms=None
if os.path.isfile(os.path.join(SCRIPTDIR,u"tmp_data",u"comments_parser.json")):
    with open(os.path.join(SCRIPTDIR,u"tmp_data",u"comments_parser.json"),"r") as f:
        comms=json.load(f)

sent_count=0
for sent,comments in read_conll(None,0):
    sent_count+=1
    if sent_count!=1:
        print
    if comms:
        comments=comms.get(unicode(sent_count),[])
    print_sent(sent,comments)
