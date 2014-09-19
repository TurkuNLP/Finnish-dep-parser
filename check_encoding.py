import sys
import codecs
import os

if __name__==u"__main__":
    try:
        #utf-8-sig interprets BOM as BOM not as space
        inp=codecs.getreader("utf-8-sig")(os.fdopen(0,"U")) #Switches universal newlines on, so all newlines are now simply "\n"
        for line in inp:
            line=line.rstrip(u"\n")
            print line.encode(u"utf-8") #
    except UnicodeDecodeError:
        print >> sys.stderr, "Error: Input file encoding is not utf-8, terminate parsing."
        sys.exit(1)
    
