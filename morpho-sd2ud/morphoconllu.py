#!/usr/bin/env python

# Variant of CoNLL-U support library that operates on morphology only.

# Specifically, supports working on files that only contain the fields
# FORM, LEMMA, CPOSTAG and FEATS.

import re

from itertools import groupby

from config import DEBUG

# feature name-value separator
FSEP = '='

class FormatError(Exception):
    def __init__(self, msg, line=None, linenum=None):
        self.msg = msg
        self.line = line
        self.linenum = linenum

    def __str__(self):        
        msg = self.msg
        if self.line is not None:
            msg += ' "'+self.line.encode('ascii', 'replace')+'"'
        if self.linenum is not None:
            msg += ' (line %d)' % self.linenum
        return msg

CPOSTAG_RE = re.compile(r'^[a-zA-Z]+$')
POSTAG_RE = re.compile(r'^[a-zA-Z]+$')

class Element(object):
    def __init__(self, form, lemma, cpostag, postag, feats):
        self.form = form
        self.lemma = lemma
        self.cpostag = cpostag
        self.postag = postag
        self._feats = feats

        if DEBUG:
            self.validate()

        self._fmap = None

    def validate(self):
        # minimal format validation (incomplete)

        # some character set constraints
        if not CPOSTAG_RE.match(self.cpostag):
            raise FormatError('invalid CPOSTAG: %s' % self.cpostag)
        if not POSTAG_RE.match(self.postag):
            raise FormatError('invalid CPOSTAG: %s' % self.postag)

        # no feature is empty
        if any(True for s in self._feats if len(s) == 0):
            raise FormatError('empty feature: %s' % str(self._feats))

        # feature names and values separated by feature separator
        if any(s for s in self._feats if len(s.split(FSEP)) < 2):
            raise FormatError('invalid features: %s' % str(self._feats))

        # no feature name repeats
        if any(n for n, g in groupby(sorted(s.split(FSEP)[0] for s in self._feats))
               if len(list(g)) > 1):
            raise FormatError('duplicate features: %s' % str(self._feats))

    def is_word(self):
        try:
            val = int(self.id)
            return True
        except ValueError:
            return False

    def has_feat(self, name):
        return name in self.feat_map()

    def add_feats(self, feats):
        # name-value pairs
        assert not any(nv for nv in feats if len(nv) != 2)
        self._feats.extend(FSEP.join(nv) for nv in feats)
        self._fmap = None

    def set_feats(self, feats):
        self._feats = []
        self.add_feats(feats)
        self._fmap = None

    def remove_feat(self, name, value):
        nv = FSEP.join((name, value))
        self._feats.remove(nv)
        self._fmap = None

    def append_misc(self, value):
        if self.misc == '_':
            self.misc = value
        else:
            self.misc = self.misc + '|' + value

    def feat_names(self):
        return [f.split(FSEP)[0] for f in self._feats]

    def feat_map(self):
        if self._fmap is None:
            try:
                self._fmap = dict([f.split(FSEP, 1) for f in self._feats])
            except ValueError:
                raise ValueError('failed to convert ' + str(self._feats))
        return self._fmap

    def wipe_annotation(self):
        self.lemma = '_'
        self.cpostag = '_'
        self.postag = '_'
        self._feats = '_'

    def __unicode__(self):
        fields = [self.form, self.lemma, self.cpostag, self.postag, self._feats]
        fields[4] = '_' if fields[4] == [] else '|'.join(sorted(fields[4], key=lambda s: s.lower())) # feats
        return '\t'.join(fields)

    @classmethod
    def from_string(cls, s):
        fields = s.split('\t')
        if len(fields) != 5:
            raise FormatError('%d fields' % len(fields), s)
        fields[4] = [] if fields[4] == '_' else fields[4].split('|') # feats
        return cls(*fields)

class DummySentence(object):
    """Dummy single-word "sentence" used to fake the CoNLL-U library API."""

    def __init__(self, word):
        self.word = word

    def words(self):
        yield self.word

    def __unicode__(self):
        return unicode(self.word)
        
def read_conllu(f):
    for ln, line in enumerate(f):
        line = line.rstrip('\n')
        if not line:
            yield line # TODO
        elif line[0] == '#':
            yield line #TODO
        else:
            try:
                yield DummySentence(Element.from_string(line))
            except FormatError, e:
                e.linenum = ln+1
                raise e

