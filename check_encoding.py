import sys
import codecs


if __name__==u"__main__":

    try:
        f=codecs.getreader(u"utf-8")(sys.stdin)
        for line in f:
            print line.encode(u"utf-8")
    except UnicodeDecodeError:
        print >> sys.stderr, "Error: Input file encoding is not utf-8, terminate parsing."
        sys.exit(1)
    
