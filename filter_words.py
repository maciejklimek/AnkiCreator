#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def is_good(word):
    for letter in word:
        if not ((ord('a') <= ord(letter) <= ord('z'))
                or
                ((ord(letter) >= ord('Z') >= ord(letter)))):
            return False
    return True


def main():
    out = []
    for line in sys.stdin:
        for word in line.split():
            if word:
                if is_good(word):
                    out.append(word.lower())
    print '\n'.join(out)

if __name__ == '__main__':
    sys.exit(main())
