"""스레드 글용 카드 이미지(1080x1350 PNG) 생성.

사용: python make_card.py <card.json> <out.png>
card.json: {"topic": "육아 공감" | "맛집" | "AI 아빠", "hook": "큰 글씨 (\\n 으로 줄바꿈)", "punch": "강조 한 줄 (없으면 생략)"}
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
PAD = 96
FONT_DIR = Path(__file__).resolve().parent / "fonts"

THEMES = {
    "육아 공감": {"bg": "#FFE9C7", "fg": "#2B1D0E", "accent": "#E8772E", "tag": "육아 공감"},
    "맛집": {"bg": "#1F3B4D", "fg": "#FDF6E9", "accent": "#FFB547", "tag": "부산 입맛 아산 맛집"},
    "AI 아빠": {"bg": "#EEF0FF", "fg": "#1A1C3A", "accent": "#5B5BD6", "tag": "AI 아빠"},
}


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def wrap(draw, text, f, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = f"{cur} {word}".strip()
            if draw.textlength(trial, font=f) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def make(topic, hook, punch, out):
    t = THEMES.get(topic, THEMES["육아 공감"])
    img = Image.new("RGB", (W, H), t["bg"])
    d = ImageDraw.Draw(img)

    # 상단 태그
    tag_f = font("NanumGothicBold.ttf", 34)
    tw = d.textlength(t["tag"], font=tag_f)
    d.rounded_rectangle((PAD, PAD, PAD + tw + 48, PAD + 68), radius=34, fill=t["accent"])
    d.text((PAD + 24, PAD + 15), t["tag"], font=tag_f, fill=t["bg"])

    # 훅: 5줄 안에 들어갈 때까지 글자 크기를 줄인다
    max_w = W - PAD * 2
    for size in (104, 96, 88, 80, 72, 64):
        hook_f = font("NanumGothicExtraBold.ttf", size)
        lines = wrap(d, hook, hook_f, max_w)
        if len(lines) <= 5:
            break
    lh = int(size * 1.32)
    punch_f = font("NanumGothicBold.ttf", 52)
    punch_lines = wrap(d, punch, punch_f, max_w) if punch else []
    block_h = lh * len(lines) + (40 + 16 + 70 * len(punch_lines) if punch_lines else 0)
    y = (H - block_h) // 2
    for ln in lines:
        d.text((PAD, y), ln, font=hook_f, fill=t["fg"])
        y += lh
    if punch_lines:
        y += 40
        d.rectangle((PAD, y, PAD + 80, y + 8), fill=t["accent"])
        y += 16 + 14
        for ln in punch_lines:
            d.text((PAD, y), ln, font=punch_f, fill=t["accent"])
            y += 70

    # 하단 서명
    foot_f = font("NanumGothicBold.ttf", 32)
    d.text((PAD, H - PAD - 40), "아산 사는 부산 남자", font=foot_f, fill=t["fg"])
    handle = "@asan_busan_namja"
    hf = font("NanumGothic.ttf", 30)
    d.text((W - PAD - d.textlength(handle, font=hf), H - PAD - 38), handle, font=hf, fill=t["fg"])

    img.save(out, "PNG", optimize=True)


if __name__ == "__main__":
    card = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    make(card.get("topic", ""), card["hook"], card.get("punch"), sys.argv[2])
