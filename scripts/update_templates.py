# -*- coding: utf-8 -*-
import os

with open('template/skeleton.html', 'r', encoding='utf-8') as f:
    skel = f.read()

chap_css = '''  /* 制作与卡点排查辅助 HUD（置于安全区外左上角盲区，平台发布后自然避让） */
  #chapText {
    position: fixed;
    top: 3.2cqh;
    left: 4cqw;
    z-index: 10;
    font-size: 2.2cqw;
    font-weight: 600;
    color: rgba(147, 167, 160, 0.75);
    background: rgba(10, 20, 32, 0.55);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 999px;
    padding: 0.5cqw 2.4cqw;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    pointer-events: none;
    letter-spacing: 0.05em;
    user-select: none;
  }
  .head {'''

if '#chapText {' not in skel:
    skel = skel.replace('  .head {', chap_css, 1)

if 'id="chapText"' not in skel:
    skel = skel.replace(
        '<div class="head">',
        '<div id="chapText">第 1 / 1 节</div>\n  <div class="head">',
        1
    )

old_comment = '// 顶部已彻底废除分镜指示胶囊与 HUD，只纯粹呈现作品标题'
new_code = '''var ct = document.getElementById("chapText");
  if (ct) ct.innerHTML = "第 " + (idx + 1) + " / " + _activeScenes.length + " 节";'''
if old_comment in skel:
    skel = skel.replace(old_comment, new_code)

with open('template/skeleton.html', 'w', encoding='utf-8') as f:
    f.write(skel)

print('template/skeleton.html updated successfully!')
