# -*- coding: utf-8 -*-
with open('output/N0001_贝莱斯芽孢杆菌科普/N0001_贝莱斯芽孢杆菌科普.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('SFX_CUES present:', 'var SFX_CUES' in text)
print('checkSfxCues present:', 'checkSfxCues' in text)
print('whoosh count in HTML:', text.count("whoosh"))
print('pop count in HTML:', text.count("pop"))
print('ding count in HTML:', text.count("ding"))
print('chime count in HTML:', text.count("chime"))
