#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from functools import partial
import multiprocessing
from random import shuffle
from gtranslate import get_translation
from tools import urlopen, strip_newline, strip_indicators, split_to_chunks
import sys
import re
from functional import compose
from bs4 import BeautifulSoup

FORBIDDEN_CHARACTERS = "'."
USE_MULTIPROCESSING = True
MULTIPROCESSING_POOL_SIZE = 20


def extract_words(args):
    url = args.url
    response = urlopen(url)
    html = response.read()
    words = []

    soup = BeautifulSoup(html)
    for link in soup.find_all('a'):
        if u'href' in link.attrs and u'title' in link.attrs:
            href = link['href']
            title = link['title']
            if re.match("""\/wiki\/([a-z]+)""", href):
                words.append(title)

def filter_out_words(words, filtering_type):
    def word_filter(word):
        return word and (word[0] == '*' or word[0] == '.')

    def word_filter2(word):
        return not (word and (word[0] == '/' or word[0] == '\\'))

    filtr = word_filter if filtering_type == 'easy' else word_filter2

    words = filter(filtr, words)
    words = map(compose(strip_newline, strip_newline), words)
    words = map(strip_indicators, words)

    for c in FORBIDDEN_CHARACTERS:
        words = filter(lambda x: x.find(c) == -1, words)
    return words


def fetch_translations(words, anki_media_dir):
    translations = []
    lock = multiprocessing.Lock()

    def callback(word, result):
        if 'error' in result:
            (type, error, traceback) = result['error']
            print "ERROR processing word {}".format(word)
            print error
            print traceback
            sys.exit(-1)
        else:
            translation = result['result']

        with lock:
            translations.append((word, translation))
    if USE_MULTIPROCESSING:
        pool = multiprocessing.Pool(MULTIPROCESSING_POOL_SIZE)
        for word in words:
            pool.apply_async(get_translation, args=(word, anki_media_dir), callback=partial(callback, word))
        pool.close()
        pool.join()
    else:
        for word in words:
            result = get_translation(word, anki_media_dir)
            callback(word, result)
    return translations


def convert_to_anki(translations, nof_meanings):
    out = []
    for (word, translation) in translations:
        o = translation.anki_rep(nof_meanings)
        out += o

    chunkk = split_to_chunks(out, 200)

    res = []
    for chunk in chunkk:
        shuffle(chunk)
        res += chunk
    return res


def generate_anki(args):
    """
    If easy is present only words WITH a prefix '*', '.' will be considered.
    If hard is present only words WITHOUT a prefix '/', '\' will be considered.
    """

    words_file_path = args.words_file
    out_file_path = args.out_file
    anki_media_dir = args.anki_media_dir
    words_file = open(words_file_path, "r")
    words = words_file.readlines()
    words_file.close()
    out_file = open(out_file_path, "w+")
    nof_meanings = args.nof_meanings

    if args.easy and args.hard:
        print("Can't use --easy and --hard together")
        return 1

    if not args.easy and not args.hard:
        print("Please use --easy or --hard.")
        return 1

    filtering_type = 'easy' if args.easy else 'hard'
    words = filter_out_words(words, filtering_type)
    translations = fetch_translations(words, anki_media_dir)
    anki_output = convert_to_anki(translations, nof_meanings)
    out_file.write("\n".join(anki_output).encode("utf-8"))
    out_file.close()

def main():
    parser = argparse.ArgumentParser(prog="anki_creator.py")
    subparsers = parser.add_subparsers()

    parser_extract_words = subparsers.add_parser("extract-words")
    parser_extract_words.add_argument('url', type=str)
    parser_extract_words.set_defaults(func=extract_words)

    parser_generate_anki = subparsers.add_parser("generate-anki")
    parser_generate_anki.add_argument('words_file', type=str)
    parser_generate_anki.add_argument('--easy', action='store_true')
    parser_generate_anki.add_argument('--hard', action='store_true')
    parser_generate_anki.add_argument('--nof-meanings', type=int, default=2)
    parser_generate_anki.add_argument('out_file', type=str)
    parser_generate_anki.add_argument('anki_media_dir', type=str)
    parser_generate_anki.set_defaults(func=generate_anki)

    args = parser.parse_args()
    return args.func(args)

if __name__ == '__main__':
    sys.exit(main())

