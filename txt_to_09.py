import sys
import json

with open(u"tmp_data/comment_hashes.json","r") as f:
    hashes=json.load(f)

for lineIdx,line in enumerate(sys.stdin):
    line=unicode(line,"utf-8").rstrip()
    if not line or line.startswith(u"###START") or line.startswith(u"###END"):
        continue
    tokens=line.split()
    if lineIdx!=0 and comment==False: # do not print empty line after comment
        print
    if len(tokens)==1 and tokens[0] in hashes: # this is hashed comment, extract it
        print hashes[tokens[0]]
        comment=True
        continue
    for tIdx,t in enumerate(tokens):
        print (u"%d\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_"%(tIdx+1,t)).encode("utf-8")
        comment=False

