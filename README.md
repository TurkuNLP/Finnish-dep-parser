Finnish-dep-parser
==================

This repository holds the dependency parsing pipeline being developed by the [University of Turku NLP group](http://bionlp.utu.fi). This is a work in progress and should be considered "early beta". A version of this pipeline was used to parse 1.5B tokens of text; it is relatively stable but still a research prototype.

Installation and prerequisites
==============================

On most systems, all you need is to run the `install.sh` script, which will download and test all of the necessary pre-requisites. You'll need to have Java and Python 2.X installed. The script downloads the external tools needed to run the pipeline:

* [OpenNLP](http://opennlp.apache.org) for sentence splitting and tokenization
* [OMorFi](http://code.google.com/p/omorfi/) and [HFST optimized lookup](http://sourceforge.net/projects/hfst/files/optimized-lookup/) for morphological analysis
* [HunPOS](http://code.google.com/p/hunpos/) for morphological disambiguation (tagging)
* [mate-tools](https://code.google.com/p/mate-tools/) for dependency parsing

Of these, all but HunPOS are Java programs and tend to work fine anywhere. HunPOS is a binary distribution and generally works OK, but on some systems (possibly 64-bit systems lacking 32-bit code support) we needed to re-compile it from sources.

Parsing plain text
==================

The following command will run the entire pipeline (sentence splitting, tokenization, tagging, parsing) on a text file. All programs throughout the pipeline expect *UTF-8* as text encoding.

    cat sometext.txt | ./parser_wrapper.sh > output.conll09

Parsing CoNLL-09 formatted input
================================
    
    cat input.conll09 | ./tag.sh | ./parse.sh > output.conll09
    
Testing
=======

The `data` directory contains two files: `wiki-test.txt` is a small piece of text from the Finnish Wikipedia and `tdt_test_set.conll09` is the (blank) official test set of the TDT treebank. You can parse these files as follows:

    cat data/wiki-test.txt | ./parser_wrapper.sh > wiki-test-parsed.txt
    cat data/tdt_test_set.conll09 | ./tag.sh | ./parse.sh > tdt_test_set_parsed.conll09
    
To check that everything went fine, you can upload `tdt_test_set_parsed.conll09` to [the TDT treebank test service](http://bionlp-www.utu.fi/tdteval/) and check that the LAS is just above 81%.
    

    
