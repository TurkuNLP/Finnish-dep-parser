import argparse
import codecs
import sys
import os

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))

def read_conll(inp,maxsent):
    """ Read conll format file and yield one sentence at a time as a list of lists of columns. If inp is a string it will be interpreted as filename, otherwise as open file for reading in unicode"""
    if isinstance(inp,basestring):
        f=codecs.open(inp,u"rt",u"utf-8")
    else:
        f=codecs.getreader("utf-8")(sys.stdin) # read stdin
    count=0
    sent=[]
    for line in f:
        line=line.strip()
        if not line or line.startswith(u"#"): #Do not rely on empty lines in conll files, ignore comments
            continue 
        if line.startswith(u"1\t") and sent: #New sentence, and I have an old one to yield
            count+=1
            yield sent
            sent=[]
            if count>=maxsent:
                break
        sent.append(line.split(u"\t"))
    else:
        if sent:
            yield sent

    if isinstance(inp,basestring):
        f.close() #Close it if you opened it

header=u'<div class="conllu-parse">\n'
footer=u'</div>\n'

def visualize(args):

    data_to_print=u""
    for sent in read_conll(args.input,args.max_sent):
        tree=header
        for line in sent:
            l=u"\t".join(line[i] for i in [0,1,2,4,5,6,8,10]) # take idx,token,lemma,pos,feat,deprel,head
            tree+=l+u"\n"
        tree+=footer
        data_to_print+=tree
    with codecs.open(os.path.join(SCRIPTDIR,u"templates","simple_brat_viz.html"),u"r",u"utf-8") as template:
        data=template.read().replace(u"CONTENTGOESHERE",data_to_print,1)
        print >> sys.stdout, data.encode(u"utf-8")


if __name__==u"__main__":

    parser = argparse.ArgumentParser(description='Trains the parser in a multi-core setting.')
    g=parser.add_argument_group("Input/Output")
    g.add_argument('input', nargs='?', help='Parser output file name, or nothing for reading on stdin')
    g.add_argument('--max_sent', type=int, default=50, help='How many trees to show? (default %(default)d)')
    args = parser.parse_args()
    visualize(args)

