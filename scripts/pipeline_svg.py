"""Small static SVG subset, rasterized offline through the test browser to a local PNG."""
import base64
import io
import re
import xml.etree.ElementTree as ET
from PIL import Image

TAGS={'svg','g','path','rect','circle','ellipse','polygon','polyline','line'}
ATTRS={'viewBox','width','height','x','y','cx','cy','r','rx','ry','x1','x2','y1','y2','points','d','fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity','transform'}

def sanitize(data):
    if len(data)>256000 or b'<!' in data:raise ValueError('SVG declarations/entities and oversized SVG are unsupported')
    doc=ET.fromstring(data)
    if doc.tag.split('}')[-1]!='svg':raise ValueError('SVG root required')
    for node in doc.iter():
        if node.tag.startswith('{') and not node.tag.startswith('{http://www.w3.org/2000/svg}'):raise ValueError('Unsupported SVG namespace')
        tag=node.tag.split('}')[-1]
        if tag not in TAGS:raise ValueError('Unsupported SVG element: '+tag)
        if set(node.attrib)-ATTRS:raise ValueError('Unsupported SVG attribute')
        if (node.text or '').strip() or (node.tail or '').strip():raise ValueError('SVG text unsupported; use native text for font fidelity')
        for key,value in node.attrib.items():
            if key in ('fill','stroke'):
                if value!='none' and not re.fullmatch('#[0-9a-fA-F]{6}',value):raise ValueError('SVG colors must be explicit hex or none')
            elif not re.fullmatch(r'[0-9a-zA-Z.,()+\s\-]*',value) or any(token in value.lower() for token in ('url','http','javascript')):raise ValueError('Unsupported SVG value')
    dims=[]
    for key in ('width','height'):
        value=doc.get(key,'')
        if not value.isdigit() or not 256<=int(value)<=2048:raise ValueError('SVG width/height must be integer256..2048')
        dims.append(int(value))
    return data,dims

def rasterize(source,destination):
    from playwright.sync_api import sync_playwright
    data,dims=sanitize(source.read_bytes())
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        try:
            page=browser.new_page();page.route('**/*',lambda route:route.abort())
            encoded=page.evaluate('''async ({data,w,h})=>{const img=new Image();img.src='data:image/svg+xml;base64,'+data;await img.decode();const c=document.createElement('canvas');c.width=w;c.height=h;c.getContext('2d').drawImage(img,0,0,w,h);return c.toDataURL('image/png').split(',')[1];}''',dict(data=base64.b64encode(data).decode(),w=dims[0],h=dims[1]))
        finally:browser.close()
    png=base64.b64decode(encoded)
    with Image.open(io.BytesIO(png)) as image:
        alpha=image.getchannel('A')
        if alpha.getextrema()[1]==0:raise ValueError('Empty SVG')
    destination.write_bytes(png)
    return dims
