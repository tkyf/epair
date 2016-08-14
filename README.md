epair
=====

Extract word revision pairs with POS from english sentence pair. 

An algorithm to get revision word of sentences is the levenshtein distance in this scripts.

## Platform
Python 3.5.2

## Pre-requisites

1. [nltk](http://nltk.org/)

These scripts use [nltk.tag](http://nltk.org/api/nltk.tag.html).

## Installation
`` git clone git@github.com:tkyf/epair.git ``

## Usage

`` $ python main.py -i english_text_file_1  -c english_text_file_2``

### Sample

     $ python main.py -i test.incor  -c test.corr
     have/VBP him/PRP 1
     was/VBD the/DT 1
     scared/VBN day/NN 1
     him/PRP before/IN 1 

## LICENSE

MIT
