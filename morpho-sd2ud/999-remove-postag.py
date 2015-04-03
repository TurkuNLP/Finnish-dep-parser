#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Remove POSTAG, changing 5-field input into 4-field format with only
# coarse posttag (CPOSTAG).

import os
import sys
import codecs

usage = '%s IN OUT' % os.path.basename(__file__)

def process(inf, outf):
    for line in inf:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            print >> outf, line
            continue
        fields = line.split('\t')
        assert len(fields) == 5, 'got %d fields: %s' % (len(fields), line)
        form, lemma, cpostag, postag, feats = fields
        removed = [form, lemma, cpostag, feats]
        print >> outf, '\t'.join(removed)
        
def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) != 3:
        print >> sys.stderr, 'Usage:', usage
        return 1

    infn, outfn = argv[1], argv[2]

    with codecs.open(infn, encoding='utf-8') as inf:
        with codecs.open(outfn, 'w', encoding='utf-8') as outf:
            process(inf, outf)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
