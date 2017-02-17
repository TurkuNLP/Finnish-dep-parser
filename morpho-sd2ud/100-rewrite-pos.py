#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import codecs

from morphoconllu import read_conllu
from tools import warn
from tools import numtype, CARDINAL, ORDINAL

usage = '%s IN OUT' % os.path.basename(__file__)

def rewrite_A(word):
    # Assign "Pron" to instances of particular words given "A"
    # analyses by lemma.
    # (see https://github.com/TurkuNLP/UniversalFinnish/issues/66)
    if word.lemma in ('muu', 'sama'):
        warn('assigning %s to Pron/PRON' % word.form)
        return ('PRON', 'Pron')

    return 'ADJ'

def rewrite_Adp(word):
    return 'ADP'

def rewrite_Adv(word):
    return 'ADV'

def rewrite_C(word):
    fmap = word.feat_map()
    try:
        value = fmap['SUBCAT']
    except KeyError:
        assert False, 'missing subcat for C'

    if value == 'CC':
        return 'CCONJ'
    elif value == 'CS':
        return 'SCONJ'
    else:
        assert False, 'unexpected C SUBCAT value %s' % value

def rewrite_Foreign(word):
    # Feature 'Foreign' added in add-feats.py
    return 'X'

def rewrite_Interj(word):
    return 'INTJ'

def rewrite_N(word):
    fmap = word.feat_map()

    if fmap.get('SUBCAT') == 'Prop':
        return 'PROPN'
    else:
        return 'NOUN'

def rewrite_Num(word):
    value = word.feat_map().get('SUBCAT')

    if value == 'Card':
        return 'NUM'
    elif value == 'Ord':
        return 'ADJ'

    # surface form-based heuristics
    t = numtype(word.form)

    if t == CARDINAL:
        return 'NUM'
    elif t == ORDINAL:
        # not quite sure about this, gives e.g. 1./ADJ
        warn('assigning ADJ to "ordinal": ' + word.form)
        return 'ADJ'
    elif t is None:
        warn(word.cpostag + u' without SUBCAT Card or Ord:' + word.form)
        # default to NUM (TODO: avoid guessing)
        return 'NUM'
    else:
        assert False, 'internal error'

pro_adjective_lemmas = set([
    # from http://scripta.kotus.fi/visk/sisallys.php?p=610
    u'sellainen',
    u'semmoinen',
    u'tällainen',
    u'tämmöinen',
    u'tuollainen',
    u'tuommoinen',
    u'kaikenlainen',
    u'eräänlainen',
    u'jonkinlainen',
    u'kunkinlainen',
    u'monenlainen',
    u'minkäänlainen',
    u'yhdenlainen',
    u'erilainen',
    u'muunlainen',
    u'samanlainen',
    u'toisenlainen',
    u'jollainen',
    u'jommoinen',
    u'millainen',
    u'mimmoinen',
    u'minkälainen',
    u'silloinen',
    u'tuolloinen',
    u'kulloinenkin',
    u'taannoinen',
    u'sikäläinen',
    u'täkäläinen',
    # others
    u'minkään#lainen',
    u'jonkalainen',
    u'senlainen',
    u'tämänlainen',
])

def rewrite_Pron(word):
    # Assign "A" to pro-adjectives such as "millainen" based on lemma
    # (see https://github.com/TurkuNLP/UniversalFinnish/issues/67).
    if word.lemma in pro_adjective_lemmas:
        warn('assigning %s to A/ADJ' % word.form)
        return ('ADJ', 'A')

    # NOTE: this is not a full mapping: some words tagged Pron should
    # map into DET instead. See
    # https://github.com/TurkuNLP/UniversalFinnish/issues/1,
    # https://github.com/TurkuNLP/UniversalFinnish/issues/27,
    # https://github.com/UniversalDependencies/docs/issues/97.
    # However, we're currently postponing this exception.
    return 'PRON'

# NOTE: very badly incomplete, see e.g.
# http://en.wikipedia.org/wiki/Emoticons_(Unicode_block)
unicode_emoticons = set([
        u'\u2639',
        u'\u263a',
])

def is_emoticon(s):
    # note: very limited regex, see
    # e.g. http://en.wikipedia.org/wiki/Emoticon
    if re.match(r'^[:;=]-?[)(DP\\\/]+$', s):
        return True
    elif s in unicode_emoticons:
        return True
    elif s in (u'<3',):
        return True
    else:
        return False

# subset from http://en.wikipedia.org/wiki/Currency_symbol
currency_symbols = set([
        u'฿', u'₵', u'¢', u'₡', u'$', u'₫', u'€', u'ƒ', u'₲', u'₴', u'₭',
        u'ლ ', u'£', u'₤', u'₦', u'₱', u'៛', u'₹', u'$', u'₪', u'৳', u'₸',
        u'₮', u'₩ ', u'¥',
])

def is_currency_symbol(s):
    return s in currency_symbols

# Note: again, very incomplete list mostly taken from
# http://universaldependencies.github.io/docs/u/pos/SYM.html
mathematical_operators_etc = set([
        u'+', u'×', u'÷', u'=', u'<', u'>', u'%', u'&', u'±', u'@',
        u'#', # "number"
        u'°', # "degrees"
        u'~', # "approx"
        # ambiguous, but more likely punct?
        # u'−',
])

def is_mathematical_operator_etc(s):
    return s in mathematical_operators_etc

def is_url(s):
    # NOTE: *very* incomplete, only checks for ending in a short (2-3
    # char) TLD from http://data.iana.org/TLD/tlds-alpha-by-domain.txt
    return re.match(r'.*\.(ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|axa|az|ba|bar|bb|bd|be|bf|bg|bh|bi|bid|bio|biz|bj|bm|bmw|bn|bo|boo|br|bs|bt|bv|bw|by|bz|bzh|ca|cab|cal|cat|cc|cd|ceo|cf|cg|ch|ci|ck|cl|cm|cn|co|com|cr|crs|cu|cv|cw|cx|cy|cz|dad|day|de|dj|dk|dm|dnp|do|dz|eat|ec|edu|ee|eg|er|es|esq|et|eu|eus|fi|fj|fk|fly|fm|fo|foo|fr|frl|ga|gal|gb|gd|ge|gf|gg|gh|gi|gl|gle|gm|gmo|gmx|gn|gop|gov|gp|gq|gr|gs|gt|gu|gw|gy|hiv|hk|hm|hn|how|hr|ht|hu|ibm|id|ie|il|im|in|ing|ink|int|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|kim|km|kn|kp|kr|krd|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mil|mk|ml|mm|mn|mo|moe|mov|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|net|new|nf|ng|ngo|nhk|ni|nl|no|np|nr|nra|nrw|nu|nyc|nz|om|ong|onl|ooo|org|ovh|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|pro|ps|pt|pub|pw|py|qa|re|red|ren|rio|rip|ro|rs|ru|rw|sa|sb|sc|sca|scb|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|soy|sr|st|su|sv|sx|sy|sz|tax|tc|td|tel|tf|tg|th|tj|tk|tl|tm|tn|to|top|tp|tr|tt|tui|tv|tw|tz|ua|ug|uk|uno|uol|us|uy|uz|va|vc|ve|vet|vg|vi|vn|vu|wed|wf|wme|ws|wtc|wtf|xxx|xyz|ye|yt|za|zip|zm|zw)$', s, re.IGNORECASE)

def is_symbol(s):
    # NOTE: incomplete, misses e.g. §, ©,
    # http://universaldependencies.github.io/docs/u/pos/SYM.html
    if is_emoticon(s):
        return True
    elif is_currency_symbol(s):
        return True
    elif is_mathematical_operator_etc(s):
        return True
    elif is_url(s):
        return True
    else:
        return False

punctuation_characters = set([
        u'.', u',', u':', u';', u'?', u'!',
        u'(', u')', u'[', u']', u'{', u'}',
        u'"', u'“', u'”', u"'", u'`', u'’', u'´', u'‘', u'«', u'»',
        u'…', u'-', u'—', u'--',
        u'|',
        u'_',
        # not 100% sure about the following (math ops?)
        u'/',
        u'−',
        u'*',
        u'–',
])

def is_punctuation(s):
    if s in punctuation_characters:
        return True
    elif re.match(r'\.+', s):
        return True
    else:
        return False

def rewrite_Punct(word):
    # NOTE: likely not a final mapping, see
    # https://github.com/TurkuNLP/UniversalFinnish/issues/1
    if is_symbol(word.form):
        assert not is_punctuation(word.form), 'internal error'
        return 'SYM'
    elif is_punctuation(word.form):
        assert not is_symbol(word.form), 'internal error'
        return 'PUNCT'
    else:
        warn(u'assigning SYM to unrecognized word ' + word.form)
        return 'SYM'

def rewrite_Symb(word):
    # punct / symb distinction purely on form, share implementation
    return rewrite_Punct(word)

def rewrite_V(word):
    return 'VERB'

def rewrite_AUX(word):
    # Already a CoNLL-U tag from add-aux.py.
    return word.cpostag

rewrite_func = {
    'A' : rewrite_A,
    'Adp' : rewrite_Adp,
    'Adv' : rewrite_Adv,
    'C' : rewrite_C,
    'Foreign' : rewrite_Foreign,
    'Interj' : rewrite_Interj,
    'N' : rewrite_N,
    'Num' : rewrite_Num,
    'Pron' : rewrite_Pron,
    'Punct' : rewrite_Punct,
    'Symb' : rewrite_Symb,
    'V' : rewrite_V,
    'AUX': rewrite_AUX,
}

def rewrite_pos(sentence):
    for w in sentence.words():
        try:
            rewritten = rewrite_func[w.cpostag](w)
        except KeyError:
            warn(u'unexpected cpostag ' + w.cpostag)
            assert False, 'unexpected cpostag ' + w.cpostag

        # if rewrite_func returns a tuple, assign both cpostag and
        # postag; otherwise assign only cpostag
        if isinstance(rewritten, tuple):
            w.cpostag, w.postag = rewritten
        else:
            w.cpostag = rewritten

def process(inf, outf):
    for s in read_conllu(inf):
        if not isinstance(s, basestring): # skip comments and sentence breaks
            rewrite_pos(s)
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
