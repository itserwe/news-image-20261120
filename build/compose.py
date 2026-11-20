#!/usr/bin/env python3
"""Compose the news-image-20261120 entry: a one-day newspaper front page.

Layout: masthead + date, hero photo (markets in turmoil), lead story,
three columns, bottom briefs strip. All text drawn with PIL.
Output: 1024x1024 PNG, falling back to JPEG if over 1 MiB.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HERO_PATH = os.path.join(
    ROOT, "assets",
    "media-generation-hero-markets-20nov-0-09627fd4-1780-40f5-b336-eaadd0e3d393.webp")
OUT_PATH = os.path.join(ROOT, "entry.png")

W, H = 1024, 1024
MARGIN = 28
CONTENT = W - 2 * MARGIN
PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (178, 34, 34)
MUTED = (60, 60, 60)
DARK = (17, 17, 17)
GOLD = (255, 190, 60)
RULE = (180, 175, 165)


def load_font(name, size):
    for folder in ("/usr/share/fonts/truetype/dejavu",
                   "/usr/share/fonts/truetype/liberation"):
        path = os.path.join(folder, name + ".ttf")
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def serif_b(size):
    return load_font("DejaVuSerif-Bold", size)


def serif(size):
    return load_font("DejaVuSerif", size)


def sans_b(size):
    return load_font("DejaVuSans-Bold", size)


def sans(size):
    return load_font("DejaVuSans", size)


def wrap_text(draw, text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered(draw, y, text, font, fill=INK):
    draw.text((W / 2, y), text, font=font, fill=fill, anchor="ma")


def story_column(draw, x, y, width, kicker, headline, deck):
    draw.text((x, y), kicker, font=sans_b(20), fill=RED)
    y += 30
    for line in wrap_text(draw, headline, serif_b(29), width):
        draw.text((x, y), line, font=serif_b(29), fill=INK)
        y += 36
    y += 4
    for line in wrap_text(draw, deck, sans(20), width):
        draw.text((x, y), line, font=sans(20), fill=MUTED)
        y += 26
    return y


page = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(page)

# Masthead
draw_centered(d, 22, "FRIDAY, 20 NOVEMBER 2026", sans_b(25))
draw_centered(d, 52, "THE WORLD TODAY", serif_b(88))
d.line([(MARGIN, 158), (W - MARGIN, 158)], fill=INK, width=3)
d.line([(MARGIN, 164), (W - MARGIN, 164)], fill=INK, width=1)

# Hero photo, cropped to fill
hero = Image.open(HERO_PATH).convert("RGB")
print("hero size:", hero.size)
target_w, target_h = CONTENT, 250
scale = max(target_w / hero.width, target_h / hero.height)
hero = hero.resize((round(hero.width * scale), round(hero.height * scale)),
                   Image.LANCZOS)
left = (hero.width - target_w) // 2
top = (hero.height - target_h) // 2
hero = hero.crop((left, top, left + target_w, top + target_h))
page.paste(hero, (MARGIN, 176))
d.rectangle([(MARGIN, 176), (W - MARGIN, 176 + target_h)], outline=INK, width=2)

# Lead story
y = 176 + target_h + 18
d.text((MARGIN, y), "MARKETS IN TURMOIL  ·  TAIPEI", font=sans_b(23), fill=RED)
y += 32
for line in wrap_text(d, "Taiwan crashes 6.2% in worst week since 1991", serif_b(48), CONTENT):
    d.text((MARGIN, y), line, font=serif_b(48), fill=INK)
    y += 56
lead = ("Anthropic slides after its record Nasdaq debut as the Nikkei dives 5%, "
        "Kospi 5.2% and the S&P falls for a sixth straight day.")
for line in wrap_text(d, lead, sans(23), CONTENT):
    d.text((MARGIN, y), line, font=sans(23), fill=MUTED)
    y += 30

# Divider
y += 12
d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
y += 16

# Three columns
columns = [
    ("POLAND",
     "Mystery object burns in Polish field",
     "Military probes a suspected airspace incursion; Rzeszów airport closed."),
    ("SHENZHEN",
     "Three leaders sign peace declaration",
     "Trump, Xi and Putin agree nuclear war must never be fought; no Ukraine deal."),
    ("THE HAGUE",
     "Court: Myanmar committed genocide",
     "The ICJ rules the 2017 crackdown on the Rohingya was genocide."),
]
col_w = (CONTENT - 2 * 28) // 3
top = y
for i, (kicker, headline, deck) in enumerate(columns):
    x = MARGIN + i * (col_w + 28)
    if i:
        d.line([(x - 14, top), (x - 14, top + 190)], fill=RULE, width=1)
    story_column(d, x, top, col_w, kicker, headline, deck)
y = top + 196

# Bottom briefs strip
strip_y = 892
d.rectangle([(0, strip_y), (W, strip_y + 100)], fill=DARK)
briefs = [
    ("UKRAINE", "Kerch Bridge hit a third time; Kyiv struck by missiles"),
    ("WASHINGTON", "Trump says Iran decision waits until next year"),
    ("COP31", "Fossil fuels cut from draft deal as talks near end"),
]
by = strip_y + 12
for kicker, text in briefs:
    d.text((MARGIN, by), kicker, font=sans_b(19), fill=GOLD)
    kw = d.textlength(kicker, font=sans_b(19))
    d.text((MARGIN + kw + 14, by), text, font=sans(19), fill=(240, 240, 240))
    by += 27

# Save, shrinking to JPEG only if the PNG is over the limit
page.save(OUT_PATH, "PNG")
size = os.path.getsize(OUT_PATH)
print("PNG bytes:", size)
if size > 1048576:
    page.save(OUT_PATH, "JPEG", quality=90)
    size = os.path.getsize(OUT_PATH)
    print("JPEG q90 bytes:", size)
if size > 1048576:
    page.save(OUT_PATH, "JPEG", quality=85)
    size = os.path.getsize(OUT_PATH)
    print("JPEG q85 bytes:", size)
print("final:", OUT_PATH, os.path.getsize(OUT_PATH), "bytes;", page.size)
