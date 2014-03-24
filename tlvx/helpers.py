# -*- coding: utf-8 -*-

_eng_chars = u'~!@#$%^&qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?'
_rus_chars = u'ё!\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,'
_both_chars = u'.,'
_trans_table = dict(zip(_eng_chars, _rus_chars))


def change_keyboard(s):
    def _check(i, c):
        is_tmp = (i, c) if (c in _both_chars) else None
        new_c = _trans_table.get(c)
        return new_c or c, is_tmp, new_c and not is_tmp
    s, tmp, is_ch = zip(*[_check(i, c) for i, c in enumerate(s)])
    tmp = filter(lambda v: isinstance(v, tuple), tmp)
    is_ch = filter(lambda c: c, is_ch)
    s = list(s)
    if tmp and not is_ch:
        for i, c in tmp:
            s[i] = c
    return u''.join(s)
