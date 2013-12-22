# -*- coding: utf-8 -*-
import json
import os
from urllib import urlencode
import urllib
import urllib2
from tools import urlopen2, remote_ex
from translation import Translation
import wikislownik

WORD_GOOGLE_TRANSLATE_MINIMAL_SCORE = 0.003


def download_mp3(word):
    mp3url = "http://translate.google.com/translate_tts?tl=%s&q=%s" % ("en", urllib.quote(word))
    headers = {"Host": "translate.google.com",
               "Referer": "http://www.gstatic.com/translate/sound_player2.swf",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.163 Safari/535.19"}
    req = urllib2.Request(mp3url, '', headers)
    response = urlopen2(req)
    return response.read()

@remote_ex
def get_translation(word, anki_media_dir):
    GOOGLE_TRASLATE_URL = 'http://translate.google.com/translate_a/t'
    GOOGLE_TRASLATE_PARAMETERS = {
        # 't' client will receiver non-standard json format
        # change client to something other than 't' to get standard json response
        'client': 'z',
        'sl': 'en',
        'tl': 'pl',
        'ie': 'UTF-8',
        'oe': 'UTF-8',
        'text': word
    }

    typ_mapping = {
        u'noun': Translation.Type.NOUN,
        u'verb': Translation.Type.VERB,
        u'adjective': Translation.Type.ADJECTIVE,
        u'adverb': Translation.Type.ADVERB,
        u'preposition': Translation.Type.PREPOSITION,
        u'pronoun': Translation.Type.PRONOUN,
        u'conjunction': Translation.Type.CONJUNCTION,
    }
    url = '?'.join((GOOGLE_TRASLATE_URL, urlencode(GOOGLE_TRASLATE_PARAMETERS)))
    req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/4.0'})
    t = urlopen2(req).read()
    w = json.loads(t)
    translation = Translation(word)
    if 'dict' not in w:
        return translation
    w = w['dict']
    idx0 = 1
    for typ_dict in w:
        entries = typ_dict.get('entry', None)
        typ = typ_mapping.get(typ_dict['pos'], None)
        if typ_dict.get('base_form', "") != word:
            continue

        if typ is None or entries is None:
            continue

        translation.add_typ(idx0, typ)
        idx1 = 1

        for entry in entries:
            w = entry['word']
            if entry.get('score', 0) >= WORD_GOOGLE_TRANSLATE_MINIMAL_SCORE:
                translation.add_meaning(idx0, idx1, w)
                idx1 += 1

        idx0 += 1
    tr2 = wikislownik.get_translation(word, anki_media_dir)
    if 'audio' not in tr2:
        blob = download_mp3(word)
        output = open(os.path.join(anki_media_dir, word + ".mp3"), 'wb')
        output.write(blob)
        output.close()
        translation.add_audio(word + ".mp3")
    else:
        translation.add_audio(tr2['audio'])
    return translation
