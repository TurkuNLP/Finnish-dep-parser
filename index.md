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

    cat sometext.txt | ./parser_wrapper.sh > output.conllu

# Parsing plain text with possible comments

If you need to preserve metadata in the input, you can include
comments (lines starting with `###C:`) into the input. These lines
will be passes through the pipeline unchanged and preserved in the
output.

    cat sometext.txt | ./split_text_with_comments.sh | ./parse_conll.sh > output.conllu

# Parsing CoNLL-U formatted input
  
    cat input.conllu | ./parse_conll.sh > output.conllu

Note that comments (lines in the CoNLL-U file that start with `#`)
will be preserved and passed through the pipeline unchanged. Make sure
the comments immediately precede the next sentence, i.e. there
should not be an empty line between the comments and the first token
of the sentence.

# Visualizing trees

Parser output trees can be visualized by using the following command and opening the resulting .html file in a modern web browser. Use the `--max_sent` parameter to limit the number of trees shown.

    cat output.conllu | python visualize.py > output.html
    
# Testing

The `data` directory contains the file `wiki-test.txt` which is a small piece of text from the Finnish Wikipedia. You can parse it as follows:

    cat data/wiki-test.txt | ./parser_wrapper.sh > wiki-test-parsed.conllu

# Other features

## Splitting sentences into clauses

    cat output.conllu | python split_clauses.py > output_clauses.conllu
    
This script uses the two last columns in the CONLL-U format to mark the clause boundaries.

## Visualizing clauses

Separate clauses can be visualized by using the following command and opening the resulting .html file in a modern web browser. Use the `--max_sent` parameter to limit the number of trees shown.

    cat output_clauses.conllu | python visualize_clauses.py > output_clauses.html
    
