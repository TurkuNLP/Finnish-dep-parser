---
layout: default
title:  'Finnish-dep-parser'
---

# About

This project holds the dependency parsing pipeline being developed by the [University of Turku NLP group](http://bionlp.utu.fi). This is still a work in progress, but a version of this pipeline has successfully been applied to several billions of tokens large corpora.

# Download

Choose whichever option suits you best:

* Clone the repository `git clone https://github.com/TurkuNLP/Finnish-dep-parser.git` 
* Download the current source code using the *Download ZIP* link of [the project GitHub repository](https://github.com/TurkuNLP/Finnish-dep-parser)

# Installation and prerequisites

On most systems, all you need is to run the `install.sh` script, which will download and test all of the necessary pre-requisites. You'll need to have Java and Python 2.X installed. The script downloads the external tools needed to run the pipeline:

* [OpenNLP](http://opennlp.apache.org) for sentence splitting and tokenization
* [OMorFi](http://code.google.com/p/omorfi/) and [HFST optimized lookup](http://sourceforge.net/projects/hfst/files/optimized-lookup/) for morphological analysis
* [MarMoT](https://code.google.com/p/cistern/wiki/marmot) for morphological disambiguation (tagging)
* [mate-tools](https://code.google.com/p/mate-tools/) for dependency parsing

These all are Java programs and tend to work fine anywhere with a sane Java installation.

# Parsing plain text

The following command will run the entire pipeline (sentence splitting, tokenization, tagging, parsing) on a text file. All programs throughout the pipeline expect *UTF-8* as text encoding.

    cat sometext.txt | ./parser_wrapper.sh > output.conll09

# Parsing CoNLL-09 formatted input
    
    cat input.conll09 | ./parse_conll.sh > output.conll09

# Visualizing trees

Parser output trees can be visualized by using the following command and opening the resulting .html file in a modern web browser. Use the `--max_sent` parameter to limit the number of trees shown.

    cat output.conll09 | python visualize.py > output.html
    
# Testing

The `data` directory contains two files: `wiki-test.txt` is a small piece of text from the Finnish Wikipedia and `tdt_test_set.conll09` is the (blank) official test set of the TDT treebank. You can parse these files as follows:

    cat data/wiki-test.txt | ./parser_wrapper.sh > wiki-test-parsed.txt
    cat data/tdt_test_set.conll09 | ./parse_conll.sh > tdt_test_set_parsed.conll09
    
To check that everything went fine, you can upload `tdt_test_set_parsed.conll09` to [the TDT treebank test service](http://bionlp-www.utu.fi/tdteval/) and check that the LAS is around 81%.

# Other features

## Splitting sentences into clauses

    cat output.conll09 | python split_clauses.py > output_clauses.conll09
    
This script uses the two last columns in the CONLL-09 format to mark the clause boundaries.

## Visualizing clauses

Separate clauses can be visualized by using the following command and opening the resulting .html file in a modern web browser. Use the `--max_sent` parameter to limit the number of trees shown.

    cat output_clauses.conll09 | python visualize_clauses.py > output_clauses.html
    
## Passing comments through sentence splitting and tokenization

    cat sometext.txt | ./split_text_with_comments.sh | ./parse_conll.sh > output.conll09
    
You can include comments also in plain text. All lines starting with `###C:` are interpreted as comments and are passed through as such.
