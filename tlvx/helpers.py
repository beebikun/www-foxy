# -*- coding: utf-8 -*-

_eng_chars = u'~!@#$%^&qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?'
_rus_chars = u'ё!\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,'
_both_chars = u'.,'
_trans_table = dict(zip(_eng_chars, _rus_chars))


def change_keyboard(s):
    def _check(i, c):
        is_tmp = 0 if (c not in _both_chars or is_ch) else (i, c)
        return _trans_table.get(c, c), is_tmp
    is_ch = False
    s, tmp = zip(*[_check(i, c) for i, c in enumerate(s)])
    tmp = filter(lambda v: isinstance(v, tuple), tmp)
    s = list(s)
    if tmp and not is_ch:
        for i, c in tmp:
            s[i] = c
    return u''.join(s)
