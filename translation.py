from tools import LudiException

__author__ = 'maciek'


class Translation(object):
    class Type(object):
        NOUN = 'n'
        VERB = 'v'
        ADJECTIVE = 'adj'
        ADVERB = 'adv'
        PRONOUN = 'pn'
        PREPOSITION = 'prep'
        CONJUNCTION = 'conj'

    def __init__(self, word):
        self.meanings = {}
        self.word = word

    def add_audio(self, audio):
        if 'audio' in self.meanings:
            raise LudiException("Audio already defined")
        self.meanings['audio'] = audio

    def add_typ(self, idx0, typ):
        if idx0 in self.meanings:
            raise LudiException("Typ %i already defined" % (idx0,))

        self.meanings[idx0] = {'submeanings': {}, 'typ': typ}

    def add_meaning(self, idx0, idx1, meaning):
        if idx0 not in self.meanings:
            raise LudiException("Typ not defined.")
        if idx1 not in self.meanings[idx0]['submeanings']:
            self.meanings[idx0]['submeanings'][idx1] = {'pl': []}
        self.meanings[idx0]['submeanings'][idx1]['pl'].append(meaning)

    def anki_rep(self, nof_meanings, tag=""):
        audio = self.meanings.get('audio', None)
        out = []
        for i in range(1, 10):
            if i in self.meanings:
                p1 = '(' + self.meanings[i]['typ'] + '.) ' + self.word + (
                        ' [sound:' + audio + '] ' if audio is not None else '')
                p2 = []
                print self.meanings
                for j in range(1, 1 + nof_meanings):
                    if j in self.meanings[i]['submeanings']:
                        if 'example' in self.meanings[i]['submeanings'][j] and ('en' not in
                                self.meanings[i]['submeanings'][j]['example']):
                            raise Exception("zle zle!")
                        if not self.meanings[i]['submeanings'][j]['pl']:
                            print self.word

                        p2.append(self.meanings[i]['submeanings'][j]['pl'][0] + (
                            ("<br \>" + self.meanings[i]['submeanings'][j]['example']['en']) if 'example' in
                                                                                                self.meanings[i][
                                                                                                    'submeanings'][
                                                                                                    j] else ''))
                if p2:
                    out.append(p1 + ';' + '<br \>'.join(p2) + ';' + tag)
        return out
