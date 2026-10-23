# -*- coding: utf-8 -*-
"""VIBE 精品音效库生成器 (generate_sfx.py)
用于一键生成 VIBE 视频量产所需的 5 款高品质标准 UI 音效：
1. pop.wav    - 数据弹出、标签浮现、Q 弹点击 (0.12s)
2. whoosh.wav - 场景切换、风切转场、气流呼啸 (0.35s)
3. ding.wav   - 核心重点、顿悟时刻、水晶提示 (0.45s)
4. chime.wav  - 结尾收束、总结 CTA、正向琶音三和弦 (1.10s)
5. click.wav  - 科技脉冲、时间轴跳跃、微点触 (0.05s)

技术实现：标准库 wave + math + random + struct，零外部第三方依赖。
输出格式：44100Hz, 16-bit PCM, 单声道/立体声 WAV，并可选导出 Base64 内联字典。
"""
import base64
import io
import json
import math
import os
from pathlib import Path
import random
import struct
import sys
import wave

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SAMPLE_RATE = 44100
MAX_AMP = 32767

ROOT_DIR = Path(__file__).resolve().parent.parent
SOUNDS_DIR = ROOT_DIR / "assets" / "sounds"


def write_wav(path: Path, samples: list[float], sample_rate: int = SAMPLE_RATE):
    """将浮点音频样本 (-1.0 ~ 1.0) 写入 16-bit PCM WAV"""
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    for s in samples:
        # 限幅削波保护
        clamped = max(-1.0, min(1.0, s))
        val = int(round(clamped * 32000))  # 留 0.8dB 动态余量防溢出
        raw.extend(struct.pack("<h", val))

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)  # 单声道
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(raw)


def gen_pop(duration: float = 0.12) -> list[float]:
    """Q 弹弹出音：频率从 1100Hz 急速滑向 320Hz + 指数衰减"""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        progress = i / n_samples
        # 频率快速下坠曲线
        freq = 1100.0 * math.exp(- progress * 3.5) + 320.0
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        # 快速攻击与平滑指数衰减
        if t < 0.004:
            env = t / 0.004
        else:
            env = math.exp(- (t - 0.004) * 35.0)

        # 基音 + 微量二次谐波增加饱满度
        val = (math.sin(phase) + 0.25 * math.sin(phase * 2.0)) * env * 0.95
        samples.append(val)
    return samples


def gen_whoosh(duration: float = 0.35) -> list[float]:
    """转场风切声：粉红滤波噪声 + 动态扫频与正弦包络"""
    n_samples = int(SAMPLE_RATE * duration)
    # 1. 生成白噪声
    noise = [random.uniform(-1.0, 1.0) for _ in range(n_samples)]

    # 2. 模拟简易粉红滤波与带通滤波扫频
    # 扫频中心：从 300Hz 升到 2000Hz 再落回 400Hz
    samples = []
    b0, b1, b2 = 0.0, 0.0, 0.0
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        progress = i / n_samples

        # 伪粉红滤波积分
        white = noise[i]
        b0 = 0.99765 * b0 + white * 0.0990460
        b1 = 0.96300 * b1 + white * 0.2965164
        b2 = 0.57000 * b2 + white * 1.0526913
        pink = b0 + b1 + b2 + white * 0.1848

        # 钟形风切包络 (sin^2)
        env = math.sin(progress * math.pi) ** 1.8

        # 加入深沉的微气流调制 (sub-air)
        sub_mod = 1.0 + 0.3 * math.sin(2.0 * math.pi * 12.0 * t)
        val = (pink * 0.12) * env * sub_mod
        samples.append(val)
    return samples


def gen_ding(duration: float = 0.45) -> list[float]:
    """清脆重点强调音：高频双谐波 (A6 1760Hz + E7 2637Hz) 水晶质感"""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    f1, f2, f3 = 1760.0, 2637.0, 3520.0
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        # 极速 2ms 启动，随后指数衰减
        if t < 0.003:
            env = t / 0.003
        else:
            decay_time = t - 0.003
            env = math.exp(- decay_time * 8.5)

        val1 = math.sin(2.0 * math.pi * f1 * t) * 0.65
        val2 = math.sin(2.0 * math.pi * f2 * t) * 0.35 * math.exp(- t * 12.0)
        val3 = math.sin(2.0 * math.pi * f3 * t) * 0.15 * math.exp(- t * 20.0)

        val = (val1 + val2 + val3) * env * 0.9
        samples.append(val)
    return samples


def gen_chime(duration: float = 1.10) -> list[float]:
    """结尾收束和弦：温暖正向大三和弦琶音 (E5 659Hz, A5 880Hz, C#6 1108Hz, E6 1318Hz)"""
    n_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * n_samples
    notes = [
        (659.25, 0.00, 1.0),   # E5
        (880.00, 0.04, 0.9),   # A5
        (1108.73, 0.08, 0.8),  # C#6
        (1318.51, 0.12, 0.75), # E6
    ]

    for freq, delay, weight in notes:
        start_idx = int(delay * SAMPLE_RATE)
        for i in range(start_idx, n_samples):
            t = (i - start_idx) / SAMPLE_RATE
            if t < 0.005:
                env = t / 0.005
            else:
                env = math.exp(- (t - 0.005) * 3.8)
            # 基频 + 微量八度泛音
            tone = (math.sin(2.0 * math.pi * freq * t) + 0.15 * math.sin(4.0 * math.pi * freq * t)) * env
            samples[i] += tone * weight * 0.3

    return samples


def gen_click(duration: float = 0.05) -> list[float]:
    """科技脉冲微触击：时间轴光标、打字微反馈"""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        env = math.exp(- t * 110.0)
        val = (math.sin(2.0 * math.pi * 1450.0 * t) + (random.uniform(-1, 1) * 0.3)) * env * 0.8
        samples.append(val)
    return samples


def generate_all():
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    generators = {
        "pop.wav": gen_pop(),
        "whoosh.wav": gen_whoosh(),
        "ding.wav": gen_ding(),
        "chime.wav": gen_chime(),
        "click.wav": gen_click(),
    }

    b64_dict = {}

    print(f"[SFX] 开始生成标准 UI 音效库至: {SOUNDS_DIR}")
    for name, samples in generators.items():
        out_path = SOUNDS_DIR / name
        write_wav(out_path, samples)
        size = out_path.stat().st_size
        dur = len(samples) / SAMPLE_RATE
        print(f"  [+] {name:<12} 时长: {dur:.2f}s, 大小: {size:>6} 字节")

        # 读取并转为 base64
        with open(out_path, "rb") as f:
            b64_dict[out_path.stem] = "data:audio/wav;base64," + base64.b64encode(f.read()).decode("ascii")

    # 导出 base64 资源文件，方便前端快速引用
    b64_path = SOUNDS_DIR / "sfx_base64.json"
    with open(b64_path, "w", encoding="utf-8") as f:
        json.dump(b64_dict, f, indent=2)
    print(f"  [+] 已输出内嵌 Base64 资源表: {b64_path.name}")
    print("[SFX] 音效库生成完毕！")


if __name__ == "__main__":
    generate_all()
