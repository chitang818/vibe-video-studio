"""Strict, independent authoring contracts for the staged web-video workflow."""
from scripts.contracts import validate

def text(n=1,m=2000):return dict(type='string',minLength=n,maxLength=m)
def enum(*values):return dict(type='string',enum=list(values))
def obj(properties,required=None):return dict(type='object',properties=properties,required=list(properties) if required is None else required,additionalProperties=False)
def arr(items,lo=0,hi=500):return dict(type='array',items=items,minItems=lo,maxItems=hi)
INDEX=dict(type='integer',minimum=0,maximum=1000000)
ID=dict(type='string',pattern='[A-Za-z][A-Za-z0-9-]{0,63}')
BEAT=obj(dict(index=INDEX,quote=text(1,100),purpose=text(4)))
SHOT=obj(dict(id=ID,startIndex=INDEX,endIndex=INDEX,goal=text(4),relation=enum('focus','parallel','contrast','cause','sequence','spatial','summary'),reason=text(4),beats=arr(BEAT,1,30)))
BRIEF=obj(dict(shotId=ID,focus=text(4),composition=text(4),rationale=text(4),opening=text(4),development=text(4),ending=text(4),continuity=text(4),constraints=arr(text(4),1,20),assetRequests=arr(text(4),0,20),sketch=arr(obj(dict(slot=text(1,40),label=text(1,48),form=enum('text','image','shape'))),1,20)))
SLOTS=('heading','hero','hero-art','hero-label','left','right','connector','top-note','row-one','row-two','row-three','row-four','image-top','caption-one','caption-two','left-icon','right-icon')
ELEMENT=obj(dict(id=ID,kind=enum('text','panel','image','arrow'),slot=enum(*SLOTS),index=INDEX,text=text(1,100),assetId=ID,tone=enum('light','accent','gold'),entrance=enum('fade-up','slide-left','slide-right','zoom'),emphasis=enum('color','marker','underline')),['id','kind','slot','index','entrance'])
IMPLEMENTATION=obj(dict(shotId=ID,reason=text(4),family=text(1,80),elements=arr(ELEMENT,1,50)))
STYLE=obj(dict(version=dict(type='integer',enum=[1]),title=text(1,48),authorId=ID,backgroundPreset=enum('bio-bubbles','constellation','dna-spiral','cyber-grid','aurora-dust','solid'),protectedTerms=arr(text(1,100),0,200),titleLines=arr(text(1,24),1,2)),['version','title','authorId','backgroundPreset','protectedTerms'])
SCHEMAS={
    'shots':obj(dict(version=dict(type='integer',enum=[1]),shots=arr(SHOT,1,500))),
    'briefs':obj(dict(version=dict(type='integer',enum=[1]),briefs=arr(BRIEF,1,500))),
    'implementation':obj(dict(version=dict(type='integer',enum=[1]),scenes=arr(IMPLEMENTATION,1,500))),
    'style':STYLE,
}

def check(name,value):
    validate(value,SCHEMAS[name],name)
    return value
