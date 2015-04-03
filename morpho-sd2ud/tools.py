# -*- coding: utf-8 -*-

import sys
import re
import codecs
import atexit

def warn(s):
    if not warn.registered:
        atexit.register(print_warnings)
        warn.registered = True

    if s in warn.counts:
        warn.counts[s] += 1
    else:
        warn.strings.append(s)
        warn.counts[s] = 1
warn.strings, warn.counts, warn.registered = [], {}, False

def print_warnings():
    out = codecs.getwriter('utf-8')(sys.stderr)

    def count_string(c):
        return '' if c == 0 else ' (x %d)' % c

    for s in warn.strings:
        out.write('Warning: ' + s + count_string(warn.counts[s]) + '\n')

    warn.strings = []
    warn.counts = {}

def error(s):
    assert False, s

rationalRe = re.compile(u'^-?[0-9]+(?:[.,/][0-9]+)?$', re.U)

#The unicode chars below are various dashes, from
#https://github.com/TurkuNLP/Finnish-dep-parser/blob/alpha/omorfi_pos.py
rangeRe = re.compile(u'^-?[0-9]+(?:[.,/][0-9]+)?[\u2012\u2013\u2014\u2015\u2053~-]+-?[0-9]+(?:[.,/][0-9]+)?$', re.U)

ordinalRe = re.compile(u'^[0-9]+\.$', re.U)

def split_suffix(s):
    # Split into stem and alphabetical suffix where the suffix is
    # separated by at least one non-alpha (e.g. "8:sta", "8sta").
    # Return (stem, suffix) on match, None otherwise.

    # see http://stackoverflow.com/a/8923988
    m = re.match(u'^(.*[\W\d_])([^\W\d_]+)$', s, re.U)
    if m is None:
        return None
    else:
        return m.groups()

# derived semiautomatically from Finnish Internet barsebank data
# available from http://bionlp.utu.fi/finnish-internet-parsebank.html.
known_suffix = set(u'a|ä|aa|ää|ääkin|aan|ään|an|än|ässä|ästä|ät|den|een|eet|eillä|en|han|hta|ia|iä|ien|iin|iksi|illa|illä|ille|in|inä|issa|jä|kaan|kään|kin|ksi|lä|lla|llä|llaan|llään|llahan|llakaan|lläkään|llakin|lläkin|llani|lläni|lle|llekin|lleni|lta|ltä|mme|n|na|nä|neen|neksi|nen|ni|nkaan|nkään|nkin|nneksi|nnella|nnellä|nnelle|nneltä|nnen|nnessa|nnessä|nnesta|nnestä|nnet|nsa|nsä|ntä|nteen|ntena|ntenä|s|sa|sää|sään|seen|seksi|sella|sellä|selle|selta|sen|sena|seni|sessa|sesta|sestä|set|si|sia|siä|siin|sissa|sissä|sista|ssa|ssä|ssahan|ssähän|ssakaan|ssäkään|ssakin|ssäkin|ssani|ssäni|sta|stä|staan|stään|stakaan|stakin|stäkin|stäni|sten|sti|t|ta|tä|taan|tään|teen|tenä|tta|ttä'.split('|'))

# subset of the above that make ordinal numbers (incomplete)
ordinal_number_suffix = set(u'nneksi|nnella|nnellä|nnelle|nneltä|nnen|nnessa|nnessä|nnesta|nnestä|nnet|nteen|ntena|ntenä|tta|ttä'.split('|'))

def split_known_suffix(s):
    # Like split_suffix, but also checks that the suffix appears in a
    # set of known inflectional or derivational suffixes.  Returns
    # None if no suffix or only an unknown suffix is found.
    ss = split_suffix(s)
    if ss is None:
        return None
    suffix = ss[1]
    if suffix in known_suffix:
        return ss
    else:
        #out = codecs.getwriter('utf-8')(sys.stderr)
        #out.write('reject on suffix: %s\n' % s)
        return None

CARDINAL, ORDINAL = range(2)

def is_rational_number(s):
    # simple rational number
    m = rationalRe.match(s)
    if m is not None:
        return True
    # with suffix (e.g. "5:een")
    ss = split_known_suffix(s)
    if (ss is not None and rationalRe.match(ss[0].rstrip(':')) and
        not ss[1] in ordinal_number_suffix):
        return True
    # others not recognized
    return False

def is_ordinal_number(s):
    m = ordinalRe.match(s)
    return m is not None

def is_numeric_range(s):
    m = rangeRe.match(s)
    return m is not None

def numtype(s):
    if is_rational_number(s):
        return CARDINAL
    elif is_ordinal_number(s):
        return ORDINAL
    elif is_numeric_range(s):
        # ranges are considered a subtype of cardinal numbers, see
        # http://universaldependencies.github.io/docs/u/feat/NumType.html
        return CARDINAL
    else:
        return None

# (POS, deprel) pairs from ordered by feasibility of serving as a head
# when a *null* is eliminated. (deprel is the relation to the *null*.)
head_candidate_priority_list = [
    # verbs, including the negation verb
    (u'AUX', u'aux'),
    (u'VERB', u'neg'),
    (u'VERB', u'csubj'), # ?
    (u'VERB', u'xcomp'), # ?
    # subjects
    (u'NOUN', u'nsubj'),
    (u'PROPN', u'nsubj'),
    (u'PRON', u'nsubj'),
    (u'NUM', u'nsubj'),
    (u'ADJ', u'nsubj'), # ?
    # objects
    (u'NOUN', u'dobj'),
    (u'PROPN', u'dobj'),
    (u'PRON', u'dobj'),
    (u'NUM', u'dobj'),
    (u'ADJ', u'dobj'), # ?
    # nominal modifiers. Both nmod and nommod to allow application before
    # and after syntax remap.
    (u'NOUN', u'nmod'),
    (u'NOUN', u'nommod'),
    (u'PROPN', u'nmod'),
    (u'PROPN', u'nommod'),
    (u'PRON', u'nmod'),
    (u'PRON', u'nommod'),
    (u'NUM', u'nmod'),
    (u'NUM', u'nommod'),
    (u'ADJ', u'nmod'), # error?
    (u'ADJ', u'nommod'), # error?
    # advmod
    (u'ADV', u'advmod'),
]
hcp_map = dict((c, i) for i, c in enumerate(head_candidate_priority_list))

def head_candidate_priority(c):
    pos, dep = c[0].cpostag, c[1]
    return hcp_map.get((pos, dep), len(hcp_map))

def pick_null_head(word, candidates):
    candidates = sorted(candidates, key=head_candidate_priority)

    # check for failures to discern between top-ranking candidates
    top_ranked = [c for c in candidates if head_candidate_priority(c) ==
                  head_candidate_priority(candidates[0])]
    if len(top_ranked) > 1:
        warn('multiple top-ranked head candidates: %s' %
             str(['%s/%s(%s)' % (w.form, w.cpostag, d) for w, d in top_ranked]))

    # finalize ranking by distance to null
    def null_dist(candidate):
        return abs(int(word.id)-int(candidate[0].id))
    top_ranked = sorted(top_ranked, key=null_dist)

    return top_ranked[0][0]

def rewrite_null_dependents(sentence, null, head):
    # current implementation assumes the new head is a "first layer"
    # dependent of the null
    assert head.head == null.id

    # mark
    if not head.has_feat('NullHead'):
        head.add_feats([('NullHead', 'Yes')])
    #head.append_misc('NullHead=Yes')

    # reassign first layer head and null (remembering the discarded one)
    null_deprel = head.deprel
    head.head, head.deprel = null.head, null.deprel
    null.head, null.deprel = '0', 'root'

    # reassign first layer (excepting head and null)
    for w in sentence.words():
        if w == head or w == null:
            continue
        if w.head == null.id:
            w.head = head.id

    # reassign second layer. Note: second layer dependency relations
    # matching the type of that previously between the null and the
    # new head are not remapped (but discarded), mirroring the way in
    # which the relation between the null and the new head is removed
    # in the null elimination. (To see why this is necessary, consider
    # e.g. "reunoilla *null* juustoa ja kinkkua" [simplified from
    # b712-merged.d.xml], which would othewise give nsubj(juustoa,
    # kinkkua) by propagation of 2nd-layer nsubj(*null*, kinkkua).)
    for w in sentence.words():
        if w == null:
            continue
        deps = w.deps()
        if not deps:
            continue
        new_deps = []
        for h, d in deps:
            if h != null.id:
                new_deps.append((h, d))
            elif d != null_deprel:
                # no self-loops
                if w != head:
                    new_deps.append((head.id, d))
            else:
                # don't remap null_deprel (see comment above)
                pass
        w.set_deps(new_deps)
