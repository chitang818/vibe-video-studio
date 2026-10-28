"""Strict validation of the published, intentionally small JSON Schema vocabulary."""
import math
import re
from pathlib import Path
from scripts.text_contract import strict_loads

ROOT = Path(__file__).resolve().parents[1]


def load_profile(profile='knowledge-portrait-v1'):
    files={'knowledge-portrait-v1':'quality-profile.json','presentation-portrait-v1':'presentation-profile.json'}
    if profile not in files:raise ValueError('Unknown production profile: '+str(profile))
    return strict_loads((ROOT/'references'/files[profile]).read_text(encoding='utf-8'))


def validate(value, schema, path='$'):
    allowed = {'$schema','title','description','type','enum','required','properties','additionalProperties',
               'items','minItems','maxItems','minLength','maxLength','minimum','maximum','pattern'}
    if set(schema)-allowed:
        raise ValueError('Unsupported schema keyword: '+str(set(schema)-allowed))
    typ = schema.get('type')
    types = {'object':dict,'array':list,'string':str,'integer':int,'boolean':bool,'number':(int,float),'null':type(None)}
    choices=typ if isinstance(typ,list) else [typ]
    valid=any(t in types and isinstance(value,types[t]) and not (t in ('integer','number') and isinstance(value,bool)) for t in choices)
    if typ and not valid:
        raise ValueError(f'{path}: expected {typ}')
    if isinstance(value, (int,float)) and not isinstance(value,bool) and not math.isfinite(value):
        raise ValueError(f'{path}: non-finite value')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path}: unsupported value {value!r}')
    if isinstance(value,dict):
        missing = set(schema.get('required',[]))-set(value)
        unknown = set(value)-set(schema.get('properties',{}))
        if missing: raise ValueError(f'{path}: missing {sorted(missing)}')
        if unknown and schema.get('additionalProperties') is False:
            raise ValueError(f'{path}: unknown fields {sorted(unknown)}')
        for k,v in value.items():
            if k in schema.get('properties',{}): validate(v,schema['properties'][k],path+'.'+k)
            elif isinstance(schema.get('additionalProperties'),dict):validate(v,schema['additionalProperties'],path+'.'+k)
    if isinstance(value,list):
        if not schema.get('minItems',0)<=len(value)<=schema.get('maxItems',float('inf')):
            raise ValueError(f'{path}: invalid item count')
        for i,v in enumerate(value): validate(v,schema.get('items',{}),f'{path}[{i}]')
    if isinstance(value,str) and not schema.get('minLength',0)<=len(value)<=schema.get('maxLength',float('inf')):
        raise ValueError(f'{path}: invalid string length')
    if isinstance(value,str) and 'pattern' in schema and re.fullmatch(schema['pattern'],value) is None:
        raise ValueError(f'{path}: invalid identifier')
    if typ in ('number','integer') and not schema.get('minimum',-float('inf'))<=value<=schema.get('maximum',float('inf')):
        raise ValueError(f'{path}: value outside range')


def validate_document(name, value):
    schema = strict_loads((ROOT/'references/schemas'/f'{name}.schema.json').read_text(encoding='utf-8'))
    validate(value,schema)
    if name=='scene':
        common={'id','type','x','y','width','height','color','background','enterUs','enterDurationUs','pulse','entrance','enterDelayUs'}
        variants={'text':({'text','size','bold','align','emphasis','verticalAlign'},{'text','size'}),
                  'rect':({'radius'},set()),'path':({'path'},{'path'}),'image':({'source','fit','focusX','focusY','imageZoom','radius'},{'source'}),
                  'ring':({'value','toValue','valueDurationUs'},set()),'bar':({'value','toValue','valueDurationUs'},set())}
        for shot in value['scenes']:
            for node in shot['nodes']:
                optional,required=variants[node['type']]
                if set(node)-common-optional or required-set(node):
                    raise ValueError('Node fields do not match type: '+node['id'])
