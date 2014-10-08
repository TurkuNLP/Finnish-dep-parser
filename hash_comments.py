import sys
import codecs
import os
import hashlib
import json

SCRIPTDIR=os.path.dirname(os.path.abspath(__file__))

hashes=dict()
inp=codecs.getreader("utf-8-sig")(os.fdopen(0,"U"))
for line in inp:
    line=line.rstrip(u"\n")
    if line.startswith(u"###C:"): # this is a comment, hash it
        hashed_line=hashlib.sha1(line.encode(u"utf-8")).hexdigest().encode(u"utf-8") # hash in string format
        hashes[hashed_line]=line
        print hashed_line
    else:
        print line.encode(u"utf-8")
with open(os.path.join(SCRIPTDIR,u"tmp_data","comment_hashes.json"),"w") as f:
    json.dump(hashes,f)
