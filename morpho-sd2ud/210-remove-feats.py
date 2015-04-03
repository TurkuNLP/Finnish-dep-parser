#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import codecs

from morphoconllu import read_conllu
from tools import warn

usage = '%s IN OUT' % os.path.basename(__file__)

VERB_TAGS = set(['VERB', 'AUX'])

def remove_Adv_CASE(word):
    # Remove case feature from adverbs. Omorfi is only expected to
    # assign the CASE feature value Dis (distributive) to adverbs, and
    # only inconsistently. Distributive is not recognized as a Finnish
    # case by ISK (http://scripta.kotus.fi/visk/sisallys.php?p=81).
    # Decided to remove this altogether, resulting in a consistent
    # treatment where no adjective has case.
    # https://github.com/TurkuNLP/UniversalFinnish/issues/17

    if word.cpostag != 'ADV':
        return

    fmap = word.feat_map()
    if 'CASE' not in fmap:
        return

    value = fmap['CASE']
    if value == 'Dis':
        word.remove_feat('CASE', 'Dis')
    else:
        warn('unexpected CASE value for ADV: ' + value)

def remove_Inf1_CASE_Lat(word):
    # Remove case feature with value Lat (lative) from infinitive
    # verbs. Omorfi follows a dated analysis where the base form of
    # the A-infinitive (Infinitive 1) is termed lative. Lative is not
    # recognized by ISK (http://scripta.kotus.fi/visk/sisallys.php?p=81,
    # see also http://scripta.kotus.fi/visk/sisallys.php?p=120 Huom 1).
    # Decided to remove this case. Note that no information is removed,
    # as the Lat value for case fully coincides with Inf1 and no other
    # case in Omorfi.
    # https://github.com/TurkuNLP/UniversalFinnish/issues/44

    fmap = word.feat_map()
    if 'CASE' not in fmap:
        return

    value = fmap['CASE']
    if value != 'Lat':
        return

    if word.cpostag not in VERB_TAGS:
        warn('unexpected CPOSTAG with CASE=Lat: ' + word.cpostag)

    word.remove_feat('CASE', 'Lat')

def remove_Inf5(word):
    # Remove Inf5 feature from verbs. Omorfi generates Inf5 *very*
    # rarely (once in TDT) and inconsistently, and the "maisillaan"
    # form termed as the "5th infinitive" is not considered as such by
    # ISK (http://scripta.kotus.fi/visk/sisallys.php?p=120).

    fmap = word.feat_map()
    if 'INF' not in fmap:
        return

    value = fmap['INF']
    if value != 'Inf5':
        return

    if word.cpostag not in VERB_TAGS:
        warn('unexpected CPOSTAG with INF=Inf5: ' + word.cpostag)

    word.remove_feat('INF', 'Inf5')

remove_funcs = [
    remove_Adv_CASE,
    remove_Inf1_CASE_Lat,
    remove_Inf5,
]

def remove_feats(sentence):
    for w in sentence.words():
        for remove_func in remove_funcs:
            remove_func(w)

def process(inf, outf):
    for s in read_conllu(inf):
        if not isinstance(s, basestring): # skip comments and sentence breaks
            remove_feats(s)
        print >> outf, unicode(s)

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
