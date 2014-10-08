from visualize import read_conll
import codecs
import json
import os.path

def print_sent(sent):
    print (u"\n".join(u"\t".join(cols) for cols in sent)).encode(u"utf-8")

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))

comms=dict()
sent_count=0
for sent,comments in read_conll(None,0):
    sent_count+=1
    if comments:
        comms[sent_count]=comments
    if sent_count!=1:
        print
    print_sent(sent)
    
    
with codecs.open(os.path.join(SCRIPTDIR,u"tmp_data",u"comments_parser.json"),u"w") as f:
    json.dump(comms,f)
