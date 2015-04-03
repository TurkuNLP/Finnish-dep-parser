#!/usr/bin/env python
# -*- coding: utf-8 -*-

# For every verb (V) in the input that can potentially be tagged AUX
# in CoNLL-U, generate an additional AUX reading.
# (see https://github.com/TurkuNLP/UniversalFinnish/issues/18)

import sys
import os
import codecs

from copy import deepcopy

from morphoconllu import read_conllu

usage = '%s IN OUT' % os.path.basename(__file__)

# see http://universaldependencies.github.io/docs/fi/pos/AUX_.html
aux_lemmas = set([
    u'aikoa',
    u'joutua',
    u'mahtaa',
    u'olla',
    u'pitää',
    u'saattaa',
    u'taitaa',
    u'tarvita',
    u'täytyä',
    u'voida',
])

def extra_aux(word):
    """Return "extra" AUX reading for verbs that can serve as auxiliaries,
    None for others."""
    if word.cpostag != 'V':
        return None
    if word.lemma not in aux_lemmas:
        return None
    aux = deepcopy(word)
    aux.cpostag = 'AUX'
    return aux

def add_aux(sentence, out):
    for w in sentence.words():
        a = extra_aux(w)
        if a is not None:
            print >> out, unicode(a)
    return sentence
            
def process(inf, outf):
    for s in read_conllu(inf):
        print >> outf, unicode(s)
        if not isinstance(s, basestring): # skip comments and sentence breaks
            add_aux(s, outf)
            
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
