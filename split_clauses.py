import argparse
import codecs
import sys
import os
from collections import defaultdict

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))

class Tree(object):

    def __init__(self):
        self.gov={}
        self.deps=defaultdict(lambda:set())
        self.dtypes={0:u"ROOTDEP"}
        self.morpho={}
    
    def add_dep(self,g,d,t,morpho):
        self.deps[g].add(d)
        self.gov[d]=g
        self.dtypes[d]=t
        self.morpho[d]=morpho

def read_conll(inp):
    """ Read conll format file and yield one sentence at a time as a list of lists of columns. If inp is a string it will be interpreted as filename, otherwise read from sys.stdin"""
    if isinstance(inp,basestring):
        f=codecs.open(inp,u"rt",u"utf-8")
    else:
        f=codecs.getreader("utf-8")(sys.stdin) # read stdin
    sent=[]
    for line in f:
        line=line.strip()
        if not line or line.startswith(u"#"): #Do not rely on empty lines in conll files, ignore comments
            continue 
        if line.startswith(u"1\t") and sent: #New sentence, and I have an old one to yield
            yield sent
            sent=[]
        sent.append(line.split(u"\t"))
    else:
        if sent:
            yield sent

    if isinstance(inp,basestring):
        f.close() #Close it if you opened it

types=u"ccomp advcl rcmod".split()

def orig_dtype(tree,node):
    dtype=tree.dtypes[tree.gov[node]]
    if dtype==u"conj":
        return orig_dtype(tree,tree.gov[node])
    else: return dtype,tree.morpho[node]

def DFS(tree,node,idx,indexes,hier):
    dtype=tree.dtypes[node]
    new_idx=idx
    if dtype in types: # this is a new clause
        if (dtype!=u"ccomp") or (u"CASE_Gen" not in tree.morpho[node]) or (u"PCP_PrsPrc" not in tree.morpho[node]): # remove ccomp when it is not subclause
            suffix=max(hier.get(idx)) if idx in hier else 0
            new_idx=idx+u"."+unicode(suffix+1)
            hier[idx].add(suffix+1)
    elif dtype==u"conj": # coordination of two subclauses or coordination from sentence root
        t,m=orig_dtype(tree,node) 
        if t in types or t==u"ROOT":
            if (t!=u"ccomp") or (u"CASE_Gen" not in m) or (u"PCP_PrsPrc" not in m):
                suffix=int(idx[-1])
                new_idx=idx[:-1]+unicode(suffix+1)
                hier[idx].add(suffix+1)
    indexes[node]=new_idx
    for dep in sorted(tree.deps[node]):
        DFS(tree,dep,new_idx,indexes,hier)
    
def split(args):
    for sent in read_conll(args.input):
        
        tree=Tree()
        for token in sent:
            head=int(token[8])
            if head==0:
                tree.add_dep(0,int(token[0]),u"ROOT",u"_")
            else:
                tree.add_dep(head,int(token[0]),token[10],u"|".join(m for m in [token[4],token[6]]))
        # now dictionary is ready, start search from root
        indexes={}
        hier=defaultdict(lambda:set()) # wipe the set
        DFS(tree,0,u"1",indexes,hier)
        for token in sent:
            token[12]=unicode(indexes[int(token[0])])
            token[13]=unicode(indexes[int(token[0])])
            print (u"\t".join(c for c in token)).encode(u"utf-8")
        print
        


if __name__==u"__main__":

    parser = argparse.ArgumentParser(description='Split parsed sentences into clauses.')
    g=parser.add_argument_group("Input/Output")
    g.add_argument('input', nargs='?', help='Parser output file name, or nothing for reading on stdin')
    args = parser.parse_args()
    split(args)
