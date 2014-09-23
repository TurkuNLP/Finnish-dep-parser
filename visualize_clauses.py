import argparse
import codecs
import sys
import os
from collections import defaultdict

from visualize import read_conll,sort_feat,header,footer

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))

#         0  1    2     3       4  5    6    7      8    9     10     11
#conll-u  ID FORM LEMMA CPOS   POS FEAT HEAD DEPREL DEPS MISC
#conll-09 ID FORM LEMMA PLEMMA POS PPOS FEAT PFEAT  HEAD PHEAD DEPREL PDEPREL _ _
def visualize_clauses(args):
    data_to_print=u""
    count=1
    for sent,comments in read_conll(args.input,args.max_sent):
        d=defaultdict(lambda:[])
        for line in sent:
            if len(line)==10: #conll-u
                line[5]=sort_feat(line[5])
                l=line
                idx=line[9]
            else: #conll-09
                line[6]=sort_feat(line[6])
                l=[line[i] for i in [0,1,2,4,5,6,8,10]] # take idx,token,lemma,pos,pos,feat,deprel,head
                l.append(u"_") #DEPS
                l.append(line[12]) #and MISC for CoNLL-U
                idx=line[12]
            d[count].append(l)
            if idx!=u"_":
                d[idx].append(l)
        
        for idx,tree in sorted(d.iteritems()):
            root=None
            root_deprel=u"ROOT"
            root_token=u"ROOT"
            if idx!=count:
                indexes={}
                for i in xrange(0,len(tree)):
                    token=int(tree[i][0])
                    indexes[token]=len(indexes)+2
                for line in tree:
                    line[0]=unicode(indexes[int(line[0])])
                    if int(line[6]) in indexes: 
                        line[6]=unicode(indexes[int(line[6])])
                    else: # this is root
                        head=int(line[6])
                        line[6]=u"1"
                        root=line[0]
                        root_deprel=line[7]
                        if head!=0:
                            root_token=d[count][head-1][1]
            # tree to text
            text=header
            text+=u"# sentence-label\t%s\n"%(unicode(idx))
            if root is not None:
                text+=u"# visual-style\t%s\tbgColor:red\n"%(u"1")
                text+=u"# visual-style %s %s %s\tcolor:red\n"%(u"1",root,root_deprel)
            if comments:
                text+=u"\n".join(comments)+u"\n"
            if idx!=count:
                root_token=u"**%s**"%(root_token)
                text+=u"\t".join(t for t in [u"1",root_token,u"_",u"_",u"_",u"_",u"0",root_deprel,u"_",u"_"])+u"\n"
            for line in tree:
                text+=u"\t".join(line[i] for i in range(10))+u"\n"

            text+=u"\n" #conll-u expects an empty line at the end of every tree
            text+=footer
            if idx==count or d[idx]!=d[count]:
                data_to_print+=text
        count+=1
    with codecs.open(os.path.join(SCRIPTDIR,u"templates","simple_brat_viz.html"),u"r",u"utf-8") as template:
        data=template.read().replace(u"CONTENTGOESHERE",data_to_print,1)
        print >> sys.stdout, data.encode(u"utf-8")


if __name__==u"__main__":

    parser = argparse.ArgumentParser(description='Trains the parser in a multi-core setting.')
    g=parser.add_argument_group("Input/Output")
    g.add_argument('input', nargs='?', help='Parser output file name, or nothing for reading on stdin')
    g.add_argument('--max_sent', type=int, default=50, help='How many trees to show? (default %(default)d)')
    args = parser.parse_args()
    visualize_clauses(args)
