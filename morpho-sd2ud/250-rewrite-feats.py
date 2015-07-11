#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import codecs

from morphoconllu import read_conllu
from tools import warn

usage = '%s IN OUT' % os.path.basename(__file__)

VERB_TAGS = set(['VERB', 'AUX'])
NOUN_TAGS = set(['NOUN', 'PROPN'])
CONJ_TAGS = set(['CONJ', 'SCONJ'])
PRON_TAGS = set(['PRON'])
ADJ_TAGS = set(['ADJ'])
ADP_TAGS = set(['ADP'])
ADV_TAGS = set(['ADV'])
NUM_TAGS = set(['NUM'])

def rewrite_CASE(word):
    fmap = word.feat_map()
    value = fmap['CASE']

    # any nouns, pronouns, adjectives and numbers can take case, as
    # can non-finite verbs (infinititives and participles), others
    # can't.
    if word.cpostag not in (NOUN_TAGS | PRON_TAGS | ADJ_TAGS | NUM_TAGS):
        if word.cpostag not in VERB_TAGS:
            warn(word.cpostag + ' with CASE')
        elif 'INF' not in fmap and 'PCP' not in fmap:
            warn('non-INF/PCP ' + word.cpostag + ' with CASE')

    if value == 'Abe':        # abessive
        return [('Case', 'Abe')]
    elif value == 'Abl':      # ablative
        return [('Case', 'Abl')]
    elif value == 'Acc':      # accusative
        return [('Case', 'Acc')]
    elif value == 'Ade':      # adessive
        return [('Case', 'Ade')]
    elif value == 'All':      # allative
        return [('Case', 'All')]
    elif value == 'Com':      # comitative
        return [('Case', 'Com')]
    elif value == 'Ela':      # elative
        return [('Case', 'Ela')]
    elif value == 'Ess':      # essive
        return [('Case', 'Ess')]
    elif value == 'Gen':      # genitive
        return [('Case', 'Gen')]
    elif value == 'Ill':      # illative
        return [('Case', 'Ill')]
    elif value == 'Ine':      # inessive
        return [('Case', 'Ine')]
    elif value == 'Ins':      # instructive
        return [('Case', 'Ins')]
    elif value == 'Nom':      # nominative
        return [('Case', 'Nom')]
    elif value == 'Par':      # partitive
        return [('Case', 'Par')]
    elif value == 'Tra':      # translative
        return [('Case', 'Tra')]
    elif value == 'Dis':      # distributive
        # see https://github.com/TurkuNLP/UniversalFinnish/issues/55
        warn('not generating Case Dis')
        return []
    elif value == 'Lat':      # lative
        # see https://code.google.com/p/omorfi/wiki/AnalysisPossibilities,
        # http://scripta.kotus.fi/visk/sisallys.php?p=120 Huom 1,
        # https://github.com/TurkuNLP/UniversalFinnish/issues/44
        warn('not generating Case Lat')
        return []
    else:
        return [] #assert False, 'unknown CASE value ' + value

def rewrite_CASECHANGE(word):
    # In Omorfi output, the feature "CASECHANGE" marks a small number
    # of instances where character case has changed through
    # e.g. sentence-initial capitalization. This is not mapped to
    # anything in UD.
    return []

def rewrite_CLIT(word):
    values = word.feat_map()['CLIT']

    mapped = []

    for value in values.split('+'):
        if value == 'Foc_kin':
            mapped.append('Kin')
        elif value == 'Qst':
            mapped.append('Ko')
        elif value == 'Foc_kaan':
            mapped.append('Kaan')
        elif value == 'Foc_ka':
            mapped.append('Ka')
        elif value == 'Foc_han':
            mapped.append('Han')
        elif value == 'Foc_pa':
            mapped.append('Pa')
        elif value == 'Foc_s':
            mapped.append('S')
        else:
            #assert False, 'unknown CLIT value ' + value
            pass

    return [('Clitic', ','.join(sorted(mapped)))]

def rewrite_CMP(word):
    value = word.feat_map()['CMP']

    if word.cpostag not in (ADJ_TAGS | VERB_TAGS | ADV_TAGS):
        warn(word.cpostag + ' with CMP')

    if value == 'Comp':
        return [('Degree', 'Cmp')]
    elif value == 'Pos':
        return [('Degree', 'Pos')]
    elif value == 'Superl':
        return [('Degree', 'Sup')]
    else:
        return [] #assert False, 'unknown CMP value ' + value

def rewrite_DRV(word):
    value = word.feat_map()['DRV']

    if value == 'Der_minen':
        # "-minen" produces noun (e.g. "valmistaminen")
        # http://scripta.kotus.fi/visk/sisallys.php?p=221,
        # https://github.com/TurkuNLP/UniversalFinnish/issues/21
        if word.cpostag not in NOUN_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Minen')]
    elif value == 'Der_sti':
        # "-sti" produces adverb (e.g. "pysyvästi")
        # http://scripta.kotus.fi/visk/sisallys.php?p=371
        if word.cpostag not in ADV_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Sti')]
    elif value == 'Der_inen':
        # "-inen" produces adjective or noun (e.g. "omenainen")
        # http://scripta.kotus.fi/visk/sisallys.php?p=261, for Omorfi
        # apparently only adjectives.
        if word.cpostag not in ADJ_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Inen')]
    elif value == 'Der_lainen':
        # "-lainen" produces noun (e.g. "Turkulainen")
        # http://scripta.kotus.fi/visk/sisallys.php?p=190
        if word.cpostag not in (ADJ_TAGS | NOUN_TAGS):
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Lainen')]
    elif value == 'Der_ja':
        # "-ja" produces noun (e.g. "oppija")
        # http://scripta.kotus.fi/visk/sisallys.php?p=252
        if word.cpostag not in NOUN_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Ja')]
    elif value == 'Der_ton':
        # "-ton" produces adjective (e.g. "voimaton")
        # http://scripta.kotus.fi/visk/sisallys.php?p=292
        if word.cpostag not in ADJ_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Ton')]
    elif value == 'Der_vs':
        # "-vs" produces noun (e.g. "toimivuus")
        if word.cpostag not in NOUN_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Vs')]
    elif value == 'Der_llinen':
        # "-llinen" produces adjective (e.g. "vaunullinen")
        # http://scripta.kotus.fi/visk/sisallys.php?p=276
        if word.cpostag not in ADJ_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Llinen')]
    elif value == 'Der_ttain':
        # "-ttain" produces adverb (e.g. "lajeittain")
        if word.cpostag not in ADV_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Ttain')]
    elif value == 'Der_u':
        # "-u" produces noun (e.g. "lopettelu")
        # http://scripta.kotus.fi/visk/sisallys.php?p=221,
        # https://github.com/TurkuNLP/UniversalFinnish/issues/21
        if word.cpostag not in NOUN_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'U')]
    elif value == 'Der_ttaa':
        # "-ttaa" produces verb (e.g. "vaivaannuttaa")
        if word.cpostag not in VERB_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Ttaa')]
    elif value == 'Der_tar':
        # "tar-" produces noun (e.g. "suojelijatar")
        if word.cpostag not in NOUN_TAGS:
            warn(word.cpostag + ' with ' + value)
        return [('Derivation', 'Tar')]
    else:
        warn('unknown DRV value ' + value)
        return []

def rewrite_INF(word):
    # INF partially mapped when introducing the VerbForm feature in
    # add-feats.py, sanity check and add InfForm here.

    vfvalue = word.feat_map()['VerbForm']
    assert vfvalue == 'Inf', 'internal error'
    
    infvalue = word.feat_map()['INF']

    if infvalue == 'Inf1':
        return [('InfForm', '1')]
    elif infvalue == 'Inf2':
        return [('InfForm', '2')]
    elif infvalue == 'Inf3':
        return [('InfForm', '3')]
    else:
        return [] #assert False, 'unknown INF value ' + infvalue

def rewrite_MOOD(word):
    value = word.feat_map()['MOOD']

    if value == 'Ind':      # indicative
        return [('Mood', 'Ind')]
    elif value == 'Imprt':  # imperative
        return [('Mood', 'Imp')]
    elif value == 'Cond':   # conditional
        return [('Mood', 'Cnd')]
    elif value == 'Pot':    # potential
        return [('Mood', 'Pot')]
    elif value == 'Opt':    # optative
        # Omorfi defines the archaic optative mood (e.g. "kävellös"),
        # which is extremely rare (e.g. no occurrences in TDT). Should
        # this ever appear, we will approximate as imperative.
        warn('mapping optative mood to imperative')
        return [('Mood', 'Imp')]
    elif value == 'Eve':    # eventive
        # Omorfi defines the archaic eventive mood (e.g. "kävelleisin"),
        # which is extremely rare (e.g. no occurrences in TDT). Should
        # this ever appear, we will approximate as potential.
        warn('mapping eventive mood to potential')
        return [('Mood', 'Pot')]
    else:
        return [] #assert False, 'unknown MOOD value ' + value

def rewrite_NEG(word):
    value = word.feat_map()['NEG']

    # this is the only one defined
    assert value == 'ConNeg', 'unexpected NEG value'

    return [('Connegative', 'Yes')]

def rewrite_OTHER(word):
    # OTHER contains non-Omorfi features.
    value = word.feat_map()['OTHER']

    if value == 'Coll':
        # see https://github.com/UniversalDependencies/docs/issues/126
        return [('Style', 'Coll')]
    elif value == 'Arch':
        # warn('not mapping OTHER value ' + value)
        return [('Style', 'Arch')]
    elif value == 'Err':
        return [('Typo', 'Yes')]
    else:
        return [] #assert False, 'unknown OTHER value ' + value


def rewrite_PCP(word):
    # PCP partially mapped when introducing the VerbForm feature in
    # add-feats.py, sanity check and add PartForm here.

    vfvalue = word.feat_map()['VerbForm']
    assert vfvalue == 'Part', 'internal error'

    pcpvalue = word.feat_map()['PCP']

    if pcpvalue == 'PrsPrc':
        return [('PartForm', 'Pres')]
    elif pcpvalue == 'PrfPrc':
        return [('PartForm', 'Past')]
    elif pcpvalue == 'AgPcp':
        return [('PartForm', 'Agt')]
    elif pcpvalue == 'Pcp':
        # apparent Omorfi error: instead of the documented value
        # "NegPrc" (https://code.google.com/p/omorfi/wiki/TagSets),
        # the tool returns just "Pcp" with a separate "Neg" value that
        # gets assigned to SUBCAT.
        assert word.feat_map().get('SUBCAT') == 'Neg', 'unexpected PCP value'
        # TODO: remove SUBCAT=Neg
        return [('PartForm', 'Neg')]
    else:
        return []
        #assert False, 'unknown PCP value ' + pcpvalue

    return []

def rewrite_POSS(word):
    value = word.feat_map()['POSS']

    # see https://github.com/TurkuNLP/UniversalFinnish/issues/38
    if value == 'PxSg1':
        return [('Number[psor]', 'Sing'), ('Person[psor]', '1')]
    elif value == 'PxSg2':
        return [('Number[psor]', 'Sing'), ('Person[psor]', '2')]
    elif value == 'PxPl1':
        return [('Number[psor]', 'Plur'), ('Person[psor]', '1')]
    elif value == 'PxPl2':
        return [('Number[psor]', 'Plur'), ('Person[psor]', '2')]
    elif value == 'Px3':
        return [('Person[psor]', '3')]
    else:
        return []
        #assert False, 'unknown POSS value ' + value

def rewrite_VERB_SUBCAT(word):
    fmap = word.feat_map()
    value = fmap['SUBCAT']

    # Neg is exceptionally used to identify negative participles, in
    # which case it maps to PartForm=Neg only, not the Negative
    # feature.
    if fmap.get('VerbForm') == 'Part':
        return []

    # TODO: should 'Negative=No' be generated for others?
    # see http://universaldependencies.github.io/docs/u/feat/Negative.html

    if value == 'Neg':
        return [('Negative', 'Yes')]
    else:
        return []
        #assert False, 'unknown VERB/AUX SUBCAT ' + value

def rewrite_NOUN_SUBCAT(word):
    value = word.feat_map()['SUBCAT']

    # In the initial CoNLL-U conversion implementation, the only
    # common noun SUBCAT value was Prop (proper noun), which has
    # already been mapped in rewrite-pos.py. Since then, we've
    # encountered also Acro and Abbr. Just sanity-check the former but
    # add the latter two using a mapping matching that for ACRO=Yes
    # and ABBR=Yes.

    if value == 'Prop':
        assert word.cpostag == 'PROPN', 'internal error'
    elif value == 'Pfx':
        # see https://github.com/TurkuNLP/UniversalFinnish/issues/60
        warn('not mapping NOUN SUBCAT Pfx')
    elif value in ('Acro', 'Abbr'):
        return [('Abbr', 'Yes')]
    else:
        return []
        #assert False, 'unknown NOUN SUBCAT ' + value

    return []

def rewrite_CONJ_SUBCAT(word):
    value = word.feat_map()['SUBCAT']

    # CC/SC distinction should already be encoded in POS, just check
    if value == 'CC':
        assert word.cpostag == 'CONJ'
    elif value == 'CS':
        assert word.cpostag == 'SCONJ'
    else:
        return []
        #assert False, 'unknown CONJ SUBCAT ' + value
    return []

def rewrite_PRON_SUBCAT(word):
    value = word.feat_map()['SUBCAT']

    if value == 'Dem':      # demonstrative
        return [('PronType', 'Dem')]
    elif value == 'Pers':   # personal
        return [('PronType', 'Prs')]
    elif value == 'Rel':    # relative
        return [('PronType', 'Rel')]
    elif value == 'Indef':  # indefinite
        return [('PronType', 'Ind')]
    elif value == 'Interr': # interrogative
        return [('PronType', 'Int')]
    elif value == 'Recipr': # reciprocal
        return [('PronType', 'Rcp')]
    elif value == 'Refl':   # reflexive
        # NOTE: UD defines Reflexive as a separate feature from PronType
        # (http://universaldependencies.github.io/docs/u/feat/Reflex.html)
        # TODO: consider adding PronType also?
        return [('Reflex', 'Yes')]
    elif value == 'Qnt':
        # NOTE: UD does not define "quantifier" as a pronoun type, so
        # these are (tentatively) mapped to the closest corresponding
        # subcategory, indefinite pronouns.
        # see https://github.com/TurkuNLP/UniversalFinnish/issues/37
        warn('mapping PRON SUBCAT ' + value + ' to Ind')
        return [('PronType', 'Ind')]
    else:
        return []
        #assert False, 'unknown PRON SUBCAT value ' + value

def rewrite_ADJ_SUBCAT(word):
    value = word.feat_map()['SUBCAT']

    # NOTE: UD NumType applies also to adjectives, see
    # http://universaldependencies.github.io/docs/u/feat/NumType.html
    if value == 'Card':
        return [('NumType', 'Card')]
    elif value == 'Ord':
        return [('NumType', 'Ord')]
    if value == 'Interr' or value == 'Rel':
        # see https://github.com/TurkuNLP/UniversalFinnish/issues/61
        warn('not mapping ADJ SUBCAT ' + value)
    elif value == 'Pfx':
        # see https://github.com/TurkuNLP/UniversalFinnish/issues/60
        warn('not mapping ADJ SUBCAT Pfx')
    else:
        return []
        #assert False, 'unknown ADJ SUBCAT ' + value

    return []

def rewrite_ADP_SUBCAT(word):
    value = word.feat_map()['SUBCAT']

    # TODO: check if we want this, AdpType is an "extra" UD feature

    if value == 'Pr':
        return [('AdpType', 'Prep')]
    elif value == 'Po':
        return [('AdpType', 'Post')]
    else:
        #assert False, 'unknown ADP SUBCAT ' + value
        return []

def rewrite_NUM_SUBCAT(word):
    value = word.feat_map()['SUBCAT']

    # NOTE: should cover missing SUBCAT
    if value == 'Card':
        return [('NumType', 'Card')]
    elif value == 'Ord':
        return [('NumType', 'Ord')]
    else:
        #assert False, 'unknown NUM SUBCAT ' + value
        return []

subcat_rewrite_func = [
    (VERB_TAGS, rewrite_VERB_SUBCAT),
    (NOUN_TAGS, rewrite_NOUN_SUBCAT),
    (CONJ_TAGS, rewrite_CONJ_SUBCAT),
    (PRON_TAGS, rewrite_PRON_SUBCAT),
    (ADJ_TAGS, rewrite_ADJ_SUBCAT),
    (ADP_TAGS, rewrite_ADP_SUBCAT),
    (NUM_TAGS, rewrite_NUM_SUBCAT),
]

def rewrite_SUBCAT(word):
    for tagset, func in subcat_rewrite_func:
        if word.cpostag in tagset:
            return func(word)

    warn(word.cpostag + ' with SUBCAT')
    return []

def rewrite_NUM(word):
    fmap = word.feat_map()

    if word.cpostag not in (VERB_TAGS | NOUN_TAGS | ADJ_TAGS | PRON_TAGS):
        warn(word.cpostag + ' with NUM')

    # Both PRS and NUM would generate redundant Number features
    assert 'PRS' not in fmap

    value = word.feat_map()['NUM']
    if value == 'Sg':
        return [('Number', 'Sing')]
    elif value == 'Pl':
        return [('Number', 'Plur')]
    else:
        #assert False, 'unknown NUM value %s' % value
        return []

def rewrite_TENSE(word):
    if word.cpostag not in VERB_TAGS:
        warn(word.cpostag + ' with TENSE')

    value = word.feat_map()['TENSE']
    if value == 'Prs':
        return [('Tense', 'Pres')]
    elif value == 'Prt':
        return [('Tense', 'Past')]
    else:
        return [] #assert False, 'unknown TENSE value %s' % value

def rewrite_VOICE(word):
    if word.cpostag not in VERB_TAGS:
        warn(word.cpostag + ' with VOICE')

    value = word.feat_map()['VOICE']
    if value == 'Act':
        return [('Voice', 'Act')]
    elif value == 'Pass':
        return [('Voice', 'Pass')]
    else:
        return [] #assert False, 'unknown VOICE value %s' % value

def rewrite_PRS(word):
    if word.cpostag not in VERB_TAGS:
        warn(word.cpostag + ' with PRS')

    # Both PRS and NUM would generate redundant Number features
    assert 'NUM' not in word.feat_map()

    value = word.feat_map()['PRS']
    if value == 'Sg1':
        return [('Person', '1'), ('Number', 'Sing')]
    elif value == 'Sg2':
        return [('Person', '2'), ('Number', 'Sing')]
    elif value == 'Sg3':
        return [('Person', '3'), ('Number', 'Sing')]
    elif value == 'Pl1':
        return [('Person', '1'), ('Number', 'Plur')]
    elif value == 'Pl2':
        return [('Person', '2'), ('Number', 'Plur')]
    elif value == 'Pl3':
        return [('Person', '3'), ('Number', 'Plur')]
    else:
        warn('unmapped PRS '+word.feat_map()['PRS'])
        return []

def rewrite_ABBR(word):
    value = word.feat_map()['ABBR']
    assert value == 'Yes', 'unexpected ABBR value %s' % value
    return [('Abbr', 'Yes')]

def rewrite_ACRO(word):
    value = word.feat_map()['ACRO']
    assert value == 'Yes', 'unexpected ACRO value %s' % value
    # Note: TDT/Omorfi abbr and acro both map to UD Abbr.
    return [('Abbr', 'Yes')]

def rewrite_VerbForm(word):
    return [('VerbForm', word.feat_map()['VerbForm'])]    # no-op

def rewrite_Person(word):
    return [('Person', word.feat_map()['Person'])]    # no-op

def rewrite_Foreign(word):
    return [('Foreign', word.feat_map()['Foreign'])]    # no-op

rewrite_func = {
    'CASE': rewrite_CASE,
    'CASECHANGE': rewrite_CASECHANGE,
    'CLIT': rewrite_CLIT,
    'CMP': rewrite_CMP,
    'DRV': rewrite_DRV,
    'INF': rewrite_INF,
    'MOOD': rewrite_MOOD,
    'NEG': rewrite_NEG,
    'NUM': rewrite_NUM,
    'OTHER': rewrite_OTHER,
    'PCP': rewrite_PCP,
    'POSS': rewrite_POSS,
    'PRS': rewrite_PRS,
    'SUBCAT': rewrite_SUBCAT,
    'TENSE': rewrite_TENSE,
    'VOICE': rewrite_VOICE,
    'ABBR': rewrite_ABBR,
    'ACRO': rewrite_ACRO,
    # non-omorfi features added by add-feats.py
    'VerbForm': rewrite_VerbForm,
    'Person': rewrite_Person,
    'Foreign': rewrite_Foreign,
}    

def rewrite_feats(sentence):
    for w in sentence.words():
        new_feats = []
        for f in w.feat_map():
            try:
                new_feats.extend(rewrite_func[f](w))
            except KeyError:
                assert False, 'unexpected feature %s' % f
        w.set_feats(new_feats)

def process(inf, outf):
    for s in read_conllu(inf):
        if not isinstance(s, basestring): # skip comments and sentence breaks
            rewrite_feats(s)
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
