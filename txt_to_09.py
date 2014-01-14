import sys

for lineIdx,line in enumerate(sys.stdin):
    line=unicode(line,"utf-8").rstrip()
    if not line or line.startswith(u"###START") or line.startswith(u"###END"):
        continue
    tokens=line.split()
    if lineIdx!=0:
        print
    for tIdx,t in enumerate(tokens):
        print (u"%d\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_\t_"%(tIdx+1,t)).encode("utf-8")

