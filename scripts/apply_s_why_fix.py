# -*- coding: utf-8 -*-
with open('scripts/prepare_n0001_html.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_bc_css = '''  /* S2 菌体结构化卡：要点清单化，杜绝生硬截断词汇 */
  .bug-card {
    width: 82cqw;
    background: linear-gradient(160deg, rgba(16,28,38,.94), rgba(10,18,26,.94));
    border: 1px solid rgba(74,222,128,.35);
    border-radius: 3.2cqw;
    padding: 2.6cqw 3.6cqw;
    text-align: left;
    margin-top: 1.2cqw;
    box-shadow: 0 4px 20px rgba(0,0,0,.45);
  }
  .bc-head {
    display: flex;
    align-items: center;
    gap: 2cqw;
    border-bottom: 1px solid rgba(148,163,184,.14);
    padding-bottom: 1.4cqw;
    margin-bottom: 1.8cqw;
  }
  .bc-tag {
    font-size: 2.4cqw;
    font-weight: 800;
    color: var(--green);
    background: rgba(74,222,128,.12);
    border: 1px solid rgba(74,222,128,.4);
    border-radius: 4cqw;
    padding: 0.4cqw 1.8cqw;
    flex: none;
  }
  .bc-t {
    font-size: 3.3cqw;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: 0.03em;
  }
  .bc-body {
    display: flex;
    align-items: center;
    gap: 3.2cqw;
  }
  .bc-svg-wrap {
    width: 22cqw;
    flex: none;
  }
  .bc-svg-wrap svg {
    width: 100%;
    height: auto;
    display: block;
  }
  .bc-points {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1.4cqw;
  }
  .bc-row {
    display: flex;
    align-items: center;
    gap: 1.8cqw;
    white-space: nowrap;
  }
  .bp-badge {
    font-size: 2.4cqw;
    font-weight: 700;
    color: var(--cyan);
    background: rgba(56,189,248,.1);
    border: 1px solid rgba(56,189,248,.3);
    border-radius: 4cqw;
    padding: 0.3cqw 1.5cqw;
    flex: none;
  }
  .bp-txt {
    font-size: 2.8cqw;
    color: var(--ink);
    font-weight: 600;
    letter-spacing: 0.02em;
  }'''

new_bc_css = '''  /* S2 菌体结构化卡：垂直堆叠优先，条目通栏排布 */
  .bug-card {
    width: 82cqw;
    background: linear-gradient(160deg, rgba(16,28,38,.94), rgba(10,18,26,.94));
    border: 1px solid rgba(74,222,128,.35);
    border-radius: 3.2cqw;
    padding: 2.4cqw 3.2cqw;
    text-align: left;
    margin-top: 1.2cqw;
    box-shadow: 0 4px 20px rgba(0,0,0,.45);
    box-sizing: border-box;
  }
  .bc-top {
    display: flex;
    align-items: center;
    gap: 3cqw;
    border-bottom: 1px solid rgba(148,163,184,.14);
    padding-bottom: 1.6cqw;
    margin-bottom: 1.8cqw;
  }
  .bc-svg-wrap {
    width: 18cqw;
    flex: none;
  }
  .bc-svg-wrap svg {
    width: 100%;
    height: auto;
    display: block;
  }
  .bc-title-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.8cqw;
  }
  .bc-tag {
    font-size: 2.4cqw;
    font-weight: 800;
    color: var(--green);
    background: rgba(74,222,128,.12);
    border: 1px solid rgba(74,222,128,.4);
    border-radius: 4cqw;
    padding: 0.3cqw 1.8cqw;
    display: inline-block;
    align-self: flex-start;
  }
  .bc-t {
    font-size: 3.2cqw;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: 0.02em;
  }
  .bc-points {
    display: flex;
    flex-direction: column;
    gap: 1.2cqw;
  }
  .bc-row {
    display: flex;
    align-items: center;
    gap: 1.4cqw;
    font-size: 2.7cqw;
  }
  .bp-dot {
    color: var(--green);
    font-size: 2.2cqw;
    flex: none;
  }
  .bp-label {
    font-weight: 800;
    color: var(--cyan);
    flex: none;
  }
  .bp-val {
    color: var(--ink);
    font-weight: 600;
    letter-spacing: 0.02em;
    flex: 1;
  }'''

assert old_bc_css in code, 'old_bc_css not found'
code = code.replace(old_bc_css, new_bc_css)

old_bc_html = '''      <div class="bug-card w w3">
        <div class="bc-head">
          <div class="bc-tag">明星菌株</div>
          <div class="bc-t">革兰氏阳性细菌 · 从实验室走向田间</div>
        </div>
        <div class="bc-body">
          <div class="bc-svg-wrap">
            <svg viewBox="0 0 120 66" fill="none" stroke="currentColor">
              <rect x="18" y="26" width="70" height="22" rx="11" fill="rgba(74,222,128,.12)" stroke="#4ade80" stroke-width="2.4"/>
              <ellipse cx="88" cy="37" rx="9" ry="3" fill="rgba(74,222,128,.5)"/>
              <path d="M88 30c10-3 15 0 17 7-8 5-13 4-17-7z" fill="rgba(74,222,128,.25)"/>
              <path d="M18 37l-10-7M18 37l-10 7" stroke-linecap="round"/>
              <circle cx="68" cy="37" r="6" stroke-width="1.8"/>
              <circle cx="48" cy="30" r="4.4" fill="rgba(251,191,36,.3)" stroke="#fbbf24" stroke-width="1.6"/>
              <path d="M96 6c8 0 14 4 16 10M100 12c4 0 7 2 8 5" stroke="#38bdf8" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>
              <circle cx="24" cy="6" r="2.4" fill="#4ade80" opacity=".7"/>
            </svg>
          </div>
          <div class="bc-points">
            <div class="bc-row"><span class="bp-badge">形态特征</span><span class="bp-txt">杆状菌体 · 可产芽孢 · 鞭毛自主运动</span></div>
            <div class="bc-row"><span class="bp-badge">胞外酶系</span><span class="bp-txt">分泌淀粉酶 · 蛋白酶 · 脂肪酶</span></div>
          </div>
        </div>
      </div>'''

new_bc_html = '''      <div class="bug-card w w3">
        <div class="bc-top">
          <div class="bc-svg-wrap">
            <svg viewBox="0 0 120 66" fill="none" stroke="currentColor">
              <rect x="18" y="26" width="70" height="22" rx="11" fill="rgba(74,222,128,.12)" stroke="#4ade80" stroke-width="2.4"/>
              <ellipse cx="88" cy="37" rx="9" ry="3" fill="rgba(74,222,128,.5)"/>
              <path d="M88 30c10-3 15 0 17 7-8 5-13 4-17-7z" fill="rgba(74,222,128,.25)"/>
              <path d="M18 37l-10-7M18 37l-10 7" stroke-linecap="round"/>
              <circle cx="68" cy="37" r="6" stroke-width="1.8"/>
              <circle cx="48" cy="30" r="4.4" fill="rgba(251,191,36,.3)" stroke="#fbbf24" stroke-width="1.6"/>
              <path d="M96 6c8 0 14 4 16 10M100 12c4 0 7 2 8 5" stroke="#38bdf8" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>
              <circle cx="24" cy="6" r="2.4" fill="#4ade80" opacity=".7"/>
            </svg>
          </div>
          <div class="bc-title-box">
            <div class="bc-tag">革兰氏阳性菌</div>
            <div class="bc-t">从实验室走向田间 · 绿色农业新宠</div>
          </div>
        </div>
        <div class="bc-points">
          <div class="bc-row">
            <span class="bp-dot">✦</span>
            <span class="bp-label">形态特征：</span>
            <span class="bp-val">杆状菌体 · 可产抗逆芽孢 · 具鞭毛自主运动</span>
          </div>
          <div class="bc-row">
            <span class="bp-dot">✦</span>
            <span class="bp-label">多重酶系：</span>
            <span class="bp-val">分泌淀粉酶 · 蛋白酶 · 脂肪酶等多种胞外酶</span>
          </div>
        </div>
      </div>'''

assert old_bc_html in code, 'old_bc_html not found'
code = code.replace(old_bc_html, new_bc_html)

with open('scripts/prepare_n0001_html.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('Updated prepare_n0001_html.py successfully!')
