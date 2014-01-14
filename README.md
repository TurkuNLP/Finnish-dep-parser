Finnish-dep-parser
==================

This repository holds the dependency parsing pipeline being developed by the [University of Turku NLP group](http://bionlp.utu.fi). This is a work in progress and should be considered "early beta". A version of this pipeline was used to parse 1.5B tokens of text; it is relatively stable but still a research prototype.

Installation and prerequisites
==============================

The pipeline relies on several external tools:

* [OpenNLP](http://opennlp.apache.org) for sentence splitting and tokenization
* [OMorFi](http://code.google.com/p/omorfi/) and [HFST optimized lookup](http://sourceforge.net/projects/hfst/files/optimized-lookup/) for morphological analysis
* [HunPOS](http://code.google.com/p/hunpos/) for morphological disambiguation (tagging)
* [mate-tools](https://code.google.com/p/mate-tools/) for dependency parsing

 

