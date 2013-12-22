# -*- coding: utf-8 -*-
import os
import urllib2
import re

from bs4 import NavigableString, BeautifulSoup

from tools import urlopen
from translation import Translation


def get_translation(word, anki_media_dir):
    from gtranslate import download_mp3
    print word

    def get_type(elem):
        text = elem.get_text()
        m = {u'czasownik': Translation.Type.VERB, u'rzeczownik': Translation.Type.NOUN,
             u'przymiotnik': Translation.Type.ADJECTIVE, u'przysłówek': Translation.Type.ADVERB,
             u'czasownik nieprzechodni': Translation.Type.VERB, u'czasownik przechodni': Translation.Type.VERB,
             u'rzeczownik policzalny': Translation.Type.NOUN,
             u'rzeczownik niepoliczalny': Translation.Type.NOUN, u'zaimek dzierżawczy': Translation.Type.PRONOUN,
             u'przyimek': Translation.Type.PREPOSITION,
             u'czasownik modalny': Translation.Type.VERB}
        return m.get(unicode(text), None)

    def extract_audio(elem):
        x = elem.find("span", "audiolink")
        if x:
            x = x.find("a")
            return x['href']
        else:
            return None

    def split_example(example):
        a = int(example[1])
        b = int(example[3])
        rest = example[5:]
        x = rest.split(u"→")
        if len(x) != 2:
            return None
        return (a, b, x[0], x[1])

    def get_words(elem):
        def filter_word(word):
            word = word.replace("[1]", "")
            word = word.replace("[2]", "")
            return word

        words = []
        last_word = ""
        if elem.dfn is not None:
            l = elem.dfn.children
        else:
            l = elem.children

        #print elem.name, elem.get_text(), list(elem.children)
        for el in l:
            if (el.name == 'strong' and el.get("class", []) == [u'selflink']) or (
                        el.name == 'a' and not ('title' in el.attrs and el['title'][0:5] == 'Aneks')):
                last_word += (" " if last_word else "") + el.get_text()
            elif isinstance(el, NavigableString) and (el.string.find(";") != -1 or el.string.find(",") != -1):
                if last_word:
                    words.append(last_word)
                last_word = ""

        if last_word:
            words.append(last_word)
        return map(filter_word, words)

    def init_dict(d, typ, idx0):
        if idx0 not in d:
            d[idx0] = {'submeanings': {}, 'typ': typ}

    def is_example(elem):
        return elem.find(class_='fld-przyklady')

    def get_idx(text):
        g = re.search("""\((\d+)\.(\d+)\)""", text).groups()
        if len(g) != 2:
            raise Exception("Bug!")
        return int(g[0]), int(g[1])

    url = "http://pl.wiktionary.org/wiki/%s" % (word,)
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    spans = filter(lambda span: span.span['id'] == 'en', soup.find_all("span", "mw-headline"))
    if not spans:
        return {}
    else:
        span = spans[0]
    elems = span.parent.find_next_siblings()
    i = 0

    meanings = {}

    while i < len(elems):
        elem = elems[i]
        if elem.name == 'h2':
            break

        if get_type(elem) is not None:
            typ = get_type(elem)
            elem2 = elems[i + 1]
            for child in elem2.children:
                if child.name == 'dd':
                    words = get_words(child)
                    if words:
                        (idx0, idx1) = get_idx(child.get_text())
                        init_dict(meanings, typ, idx0)
                        meanings[idx0]['submeanings'][idx1] = {'pl': words}
            i += 2
        elif is_example(elem):
            examples = elem.find_all("dd")
            for ex in examples:
                x = split_example(ex.get_text())
                if x is not None:
                    (a, b, en, pl) = x
                    if a in meanings and b in meanings[a]['submeanings']:
                        meanings[a]['submeanings'][b]['example'] = {'en': en, 'pl': pl}
            i += 1
        elif extract_audio(elem):
            audio = "http:" + extract_audio(elem)
            print audio
            try:
                #req = urllib2.Request(audio)
                response = urlopen(audio)
            except urllib2.URLError as e:
                i += 1
                continue

            output = open(os.path.join(anki_media_dir, word + ".ogg"), 'wb')
            output.write(response.read())
            output.close()
            meanings['audio'] = word + ".ogg"
            i += 1
        else:
            i += 1
    if 'audio' not in meanings:
        blob = download_mp3(word)
        output = open(os.path.join(anki_media_dir, word + ".mp3"), 'wb')
        output.write(blob)
        output.close()
        meanings['audio'] = word + ".mp3"

    return meanings
