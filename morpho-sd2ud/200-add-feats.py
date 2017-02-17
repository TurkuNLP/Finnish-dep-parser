#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import codecs
import unicodedata

from morphoconllu import read_conllu
from tools import warn
from tools import numtype, CARDINAL, ORDINAL

usage = '%s IN OUT' % os.path.basename(__file__)

VERB_TAGS = set(['VERB', 'AUX'])
NOUN_TAGS = set(['NOUN', 'PROPN'])
ADJ_TAGS = set(['ADJ'])

def add_VerbForm(word):
    fmap = word.feat_map()

    if word.cpostag not in VERB_TAGS:
        return []

    # (see https://github.com/TurkuNLP/UniversalFinnish/issues/28)
    if 'INF' in fmap:
        # infinitive
        assert 'PCP' not in fmap, 'INF and PCP'
        assert 'PRS' not in fmap, 'INF and PRS'
        assert 'MOOD' not in fmap, 'INF and MOOD'
        value = fmap['INF']
        if value in ('Inf1', 'Inf2', 'Inf3'):
            return [('VerbForm', 'Inf')]
        else:
            warn(u'unexpected INF value ' + value)
            return []
    if 'PCP' in fmap:
        # participle
        assert 'INF' not in fmap, 'PCP and INF'
        assert 'PRS' not in fmap, 'PCP and PRS'
        assert 'MOOD' not in fmap, 'PCP and MOOD'
        return [('VerbForm', 'Part')]
    else:
        # Should be finite, check for some marker. We consider any
        # non-infinitive, non-participle verb finite if it has either
        # MOOD or PRS.
        # (https://github.com/TurkuNLP/UniversalFinnish/issues/28)
        if 'MOOD' in fmap or 'PRS' in fmap:
            return [('VerbForm', 'Fin')]
        else:
            warn(u'failed to assign VerbForm to ' + unicode(word))
            return []

# sources: TDT, http://fi.wikipedia.org/wiki/Persoonapronomini
person_by_lemma = {
    u'minä': '1',
    u'mä': '1',
    u'mää': '1',
    u'mnää': '1',
    u'mie': '1',
    u'miä': '1',
    u'ma': '1',

    u'sinä': '2',
    u'sä': '2',
    u'sää': '2',
    u'snää': '2',
    u'tie': '2',
    u'siä': '2',

    u'hän': '3',
    u'hää': '3',
}

def add_Person(word):
    # Assign feature Person to personal pronouns, which for some
    # reason lack it in Omorfi analyses.

    fmap = word.feat_map()

    if word.cpostag != 'PRON':
        return []
    elif fmap.get('SUBCAT') != 'Pers':
        return []
    else:
        p = person_by_lemma.get(word.lemma, None)
        if p is not None:
            return [('Person', p)]
        else:
            warn(u'missing person for pronoun lemma ' + word.lemma)
            return []

def add_SUBCAT_to_Num(word):
    # Assign feature SUBCAT to numbers lacking it using surface
    # form-based heuristics.

    fmap = word.feat_map()

    if 'SUBCAT' in fmap or word.postag != 'Num':
        return []

    t = numtype(word.form)

    if t == CARDINAL:
        return [('SUBCAT', 'Card')]
    elif t == ORDINAL:
        return [('SUBCAT', 'Ord')]
    else:
        return []

# add_SUBCAT_to_Pron data
Pron_SUBCAT_by_lemma = {
    # from http://scripta.kotus.fi/visk/sisallys.php?p=713 (table 119)
    # Note: some could be subtypes (esp. Indef), see VISK for details
    u'joku': 'Qnt',
    u'jokin': 'Qnt',
    u'jompikumpi': 'Qnt',
    u'eräs': 'Qnt',
    u'muuan': 'Qnt',
    u'yks': 'Qnt',
    u'yksi': 'Qnt',
    u'kaikki': 'Indef', # from Omorfi
    u'koko': 'Qnt',
    u'jokainen': 'Qnt',
    u'kukin': 'Indef', # from Omorfi
    # itse kukin
    u'kumpikin': 'Indef', # from Omorfi
    u'molemmat': 'Index', # from Omorfi
    # kukaan ~ mikään
    # kuka ~ mikä tahansa
    # vaikka kuka ~ mikä
    # kukakin ~ mi(kä)kin
    u'muutama': 'Qnt',
    u'jokunen': 'Qnt',
    u'harva': 'Qnt',
    u'moni': 'Qnt',
    u'monta': 'Qnt',
    u'usea': 'Qnt',
    # per https://github.com/TurkuNLP/UniversalFinnish/issues/66
    u'muu': 'Qnt',
    u'sama': 'Qnt',
    # others
    u'ken': 'Interr', # http://fi.wikipedia.org/wiki/Pronomini
    u'ainoa': 'Indef', # guess; Omorfi and VISK only have ainoa/A
}
# add in personal pronoun lemmas
Pron_SUBCAT_by_lemma.update({ k: 'Pers' for k in person_by_lemma})

def add_SUBCAT_to_Pron(word):
    # Assign feature SUBCAT to pronouns lacking it using surface
    # form-based heuristics.

    fmap = word.feat_map()

    if 'SUBCAT' in fmap or word.postag != 'Pron':
        return []

    try:
        sc = Pron_SUBCAT_by_lemma[word.lemma]
    except KeyError:
        warn(u'failed to assign SUBCAT to Pron')
        return []

    return [('SUBCAT', sc)]

def latin(c):
    # from http://stackoverflow.com/a/3308844
    return unicodedata.name(c).startswith('LATIN')

def nonlatin_alpha(c):
    if c not in nonlatin_alpha.cache:
        nonlatin_alpha.cache[c] = c.isalpha() and not latin(c)
    return nonlatin_alpha.cache[c]
nonlatin_alpha.cache = {}

def has_nonlatin_alpha(s):
    return any(c for c in s if nonlatin_alpha(c))

def add_Foreign(word):
    # Assign feature Foreign to words that had the corresponding POS
    # tag.

    if word.postag != 'Foreign':
        return []
    elif has_nonlatin_alpha(word.form):
        return [('Foreign', 'Yes')]
    else:
        return [('Foreign', 'Yes')]

add_funcs = [
    add_VerbForm,
    add_Person,
    add_SUBCAT_to_Num,
    add_SUBCAT_to_Pron,
    add_Foreign,
]

def add_feats(sentence):
    for w in sentence.words():
        for add_func in add_funcs:
            w.add_feats(add_func(w))

def process(inf, outf):
    for s in read_conllu(inf):
        if not isinstance(s, basestring): # skip comments and sentence breaks
            add_feats(s)
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
