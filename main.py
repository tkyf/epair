#! /usr/bin/env python
# -*- coding:utf-8 -*-

def is_ascii(string):
    if string:
        return max([ord(char) for char in string]) < 128

# TODO Word unit edit distance!!!!
def main():
    import sys
    import argparse
    import codecs
    from time import time

    import englishword_edit_distance as ewed

    parser = argparse.ArgumentParser(description="Extract revision pair from English sentence pair")
    parser.add_argument("-c", dest="c", help="Correction file")
    parser.add_argument("-i", dest="i", help="Incorrect file")
    parser.add_argument("-eq", dest="eq_include", action="store_true", help="Result include no revision pair")
    parser.add_argument("-nopos", dest="no_pos", action="store_true", help="without POS tag")
    parser.add_argument("-w", metavar="N", type=int, dest="iso_window", action="store", help="one side window range of  substitution only revision. ")

    if len(sys.argv) < 3:
        parser.print_help()
        exit(-1)

    args = parser.parse_args()
    ed = ewed.EditDistance(eq_include=args.eq_include, no_pos=args.no_pos)

    with codecs.open(args.c, 'r', 'utf-8') as c, codecs.open(args.i, 'r', 'utf-8') as i:
        start = time()
        for i, (corr, incor) in enumerate(zip(c, i)):
            corr = corr.rstrip(u"\n").rstrip(u"\r")
            incor = incor.rstrip(u"\n").rstrip(u"\r")

            if args.iso_window:
                sub_list = ed.extract_isolation_window(incor, corr, args.iso_window)
            else:
                sub_list = ed.extract(incor, corr)

            for sub in sub_list:
                if is_ascii(sub[0]) and is_ascii(sub[1]):
                    print sub[0].encode('utf-8'), sub[1].encode('utf-8'), unicode(i+1).encode('utf-8')

if __name__ == '__main__':
    main()

