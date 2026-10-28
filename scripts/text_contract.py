"""Text identity keeps numeric punctuation; raw timestamps remain the source of truth."""
import json
import math
import re

PUNCT = '，、：；。！？,.!?：;'


def normalized_tokens(tokens):
    tokens=[(c,a) for c,a in tokens if not c.isspace()]
    text = ''.join(c for c, _ in tokens)
    return [(c, anchor) for i, (c, anchor) in enumerate(tokens)
            if not c.isspace() and (c not in PUNCT or
                c == '.' and i < len(text)-1 and text[i+1].isdigit())]


def clean(text):
    return ''.join(c for c, _ in normalized_tokens([(c, None) for c in text]))


def number_tokens(text):
    text=''.join(text.split()).replace('摄氏度','°C').replace('℃','°C').replace('％','%')
    return re.findall(r'[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:%|°C|倍)?',text)


def quote_at(rows,index,quote):
    """Match an actual original-word start, never the middle of a numeric/ASCII token."""
    wanted=clean(quote)
    if not wanted:return False
    suffix=''.join(r['Char'] for r in rows[index:])
    tokens=normalized_tokens([(c,i) for i,c in enumerate(suffix)])
    if not tokens or tokens[0][1]>=len(rows[index]['Char']):return False
    if not ''.join(c for c,_ in tokens).startswith(wanted):return False
    before=''.join(r['Char'] for r in rows[:index]).rstrip()
    token=lambda c:c.isascii() and (c.isalnum() or c in '._+-')
    if token(wanted[0]) and before and token(before[-1]):return False
    raw_end=tokens[len(wanted)-1][1]+1
    rest=suffix[raw_end:].lstrip()
    continuation=bool(rest and token(rest[0]))
    if rest.startswith('.') and (len(rest)==1 or not rest[1].isdigit()):continuation=False
    if token(wanted[-1]) and continuation:return False
    return True


def strict_loads(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: '+key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('Non-finite JSON constant: '+value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)


def validate_rows(rows, duration_us):
    if not isinstance(rows, list) or not rows:
        raise ValueError('Original character timestamps are required')
    previous = -1
    for row in rows:
        if not isinstance(row.get('Char'), str) or not row['Char']:
            raise ValueError('Empty timestamp character')
        start, end = row.get('StartSeconds'), row.get('EndSeconds')
        if any(isinstance(v, bool) or not isinstance(v, (float,int)) or not math.isfinite(v) for v in (start,end)):
            raise ValueError('Non-finite/invalid character timestamp')
        if start < previous or start < 0 or end < start or round(end*1e6) > duration_us:
            raise ValueError('Character timestamps exceed the original WAV or are unordered')
        previous = start
