#!/usr/bin/env python3
"""
Static SEO site generator for add9 (https://github.com/jarvisrr/add9.com).
Reads chord-atlas.json and Localizable.xcstrings from ../alternative-chord
and generates 28+ bilingual (EN / ZH-Hans) static HTML pages, sitemap.xml,
and robots.txt optimized for Google, Bing, and Baidu.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import re
from pathlib import Path

APP_STORE_US = "https://apps.apple.com/us/app/add9-no-more-boring-chords/id6834397836"
APP_STORE_CN = "https://apps.apple.com/cn/app/add9-no-more-boring-chords/id6834397836"
APP_ID = "6834397836"
TODAY = datetime.date.today().isoformat()

NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

STYLE_SLUGS = {
    "math-rock": "math-rock",
    "shoegaze": "shoegaze",
    "neo-soul-rnb": "neo-soul-rnb",
    "midwest-emo": "midwest-emo",
    "jazz": "jazz",
    "jpop": "jpop",
    "city-pop": "city-pop",
    "bossa-nova": "bossa-nova",
    "lofi": "lofi",
    "indie": "jangle-pop",
    "bedroom-pop": "bedroom-pop",
}

STYLE_ORDER = [
    "math-rock",
    "shoegaze",
    "neo-soul-rnb",
    "midwest-emo",
    "jazz",
    "jpop",
    "city-pop",
    "bossa-nova",
    "lofi",
    "indie",
    "bedroom-pop",
]

# Targeted SEO copy per genre (EN & ZH-Hans), aligned with AGENTS.md localization rules
# (Shoegaze = 盯鞋, Bossa nova = Bossa nova, no invented translations).
GENRE_SEO = {
    "math-rock": {
        "en_title": "Math Rock Guitar Chords & Voicings (Standard & FACGCE) — add9",
        "en_h1": "Math Rock Guitar Chords & Voicings",
        "en_desc": "Playable math rock guitar chords in Standard and FACGCE tuning. Audition 22 curated maj9, add9, and open-string voicings with fret diagrams and audio.",
        "en_kw": "math rock guitar chords,math rock chords,math rock chords standard tuning,math rock chords facgce,add9 guitar voicings",
        "zh_title": "数学摇滚吉他和弦与指法（标准调弦 & FACGCE）— add9",
        "zh_h1": "数学摇滚吉他和弦与指法",
        "zh_desc": "精选 22 个数学摇滚吉他和弦指法，涵盖标准调弦与 FACGCE 开放调弦中的 maj9、add9 与空弦延伸音，点击即可试听。",
        "zh_kw": "数学摇滚吉他和弦,数摇和弦指法,FACGCE调弦和弦,add9吉他和弦,开放调弦指法",
        "en_faq": [
            ("Can you play math rock chords in Standard tuning?", "Yes. While FACGCE is famous for ringing open extensions, compact maj7, add9, and 6/9 shapes in Standard tuning deliver the same bright intervals without retuning."),
            ("Why is FACGCE popular for math rock?", "Tuning to F-A-C-G-C-E turns the open strings into an Fmaj9 chord, letting simple two-finger grips ring against bright upper drones."),
        ],
        "zh_faq": [
            ("标准调弦也能弹数学摇滚和弦吗？", "可以。虽然 FACGCE 开放调弦很适合空弦共鸣，但在标准调弦下使用紧凑的 maj7、add9 和 6/9 指型同样能弹出明亮的数摇色彩。"),
            ("为什么数学摇滚常用 FACGCE 调弦？", "FACGCE 六根空弦本身就构成一个 Fmaj9 和弦，只需极少按弦即可让高音空弦持续共鸣，非常适合点弦与分解和弦。"),
        ],
    },
    "shoegaze": {
        "en_title": "Shoegaze Guitar Chords & Open-String Voicings — add9",
        "en_h1": "Shoegaze Guitar Chords & Voicings",
        "en_desc": "24 curated shoegaze guitar chord voicings in Standard tuning: ringing treble drones, wide sus2/add9 shapes, and hazy sevenths with clickable audio.",
        "en_kw": "shoegaze guitar chords,shoegaze chord voicings,dream pop guitar chords,open string guitar chords,add9 chords",
        "zh_title": "盯鞋（Shoegaze）吉他和弦与空弦指法 — add9",
        "zh_h1": "盯鞋吉他和弦与指法",
        "zh_desc": "精选 24 个标准调弦下的盯鞋（Shoegaze）吉他和弦指法：持续共鸣的高音空弦、宽音程挂留和弦与朦胧七和弦，支持在线试听。",
        "zh_kw": "盯鞋吉他和弦,Shoegaze和弦,盯鞋指法,空弦挂留和弦,梦幻流行吉他和弦",
        "en_faq": [
            ("What makes a guitar chord sound like shoegaze?", "Ringing open high strings (B and high E) against movable power-chord or maj7 roots, plus wide sus2 and add9 voicings that stay clear under reverb and fuzz."),
            ("Do I need alternate tunings for shoegaze chords?", "No. All 24 voicings on this page work in Standard tuning (EADGBE) by combining fretted bass shapes with open treble strings."),
        ],
        "zh_faq": [
            ("盯鞋（Shoegaze）和弦的核心色彩是什么？", "主要是让高音空弦（B 弦与高音 E 弦）持续共鸣，搭配可移动的低音把位与宽音程 sus2、add9，在混响与过载下依然通透。"),
            ("弹盯鞋和弦必须改特殊调弦吗？", "不需要。本页收录的 24 个盯鞋指法全部基于标准调弦（EADGBE），通过保留高音空弦即可获得宽广的音墙感。"),
        ],
    },
    "neo-soul-rnb": {
        "en_title": "Neo-Soul & R&B Guitar Chords & Ninth Voicings — add9",
        "en_h1": "Neo-Soul / R&B Guitar Chords & Voicings",
        "en_desc": "16 lush neo-soul and R&B guitar chord voicings: major and minor ninths, 11th grips, and altered dominants with fret diagrams and instant strum audio.",
        "en_kw": "neo soul guitar chords,r&b guitar chords,neo soul chord voicings,minor 9 guitar chord,guitar chord voicings",
        "zh_title": "新灵魂乐 / R&B 吉他和弦与九和弦指法 — add9",
        "zh_h1": "新灵魂乐 / R&B 吉他和弦与指法",
        "zh_desc": "精选 16 个新灵魂乐与 R&B 吉他和弦指法：大小九和弦、十一和弦与变化属和弦，附清晰指板图与一键试听。",
        "zh_kw": "新灵魂乐吉他和弦,Neo-soul和弦,R&B吉他和弦,小九和弦指法,吉他延伸和弦",
        "en_faq": [
            ("Which chords define neo-soul guitar?", "Minor 9 (m9), major 9 (maj9), minor 11 (m11), and altered dominant 7#5 / 7b9 voicings that leave room for hammer-ons and double-stops."),
            ("How do I voice neo-soul chords cleanly?", "Focus on 4-note middle-string grips (A-D-G-B or E-D-G-B) so chords glide smoothly without muddy low-mid intervals."),
        ],
        "zh_faq": [
            ("新灵魂乐（Neo-soul）最常用哪些吉他和弦？", "最核心的是小九和弦（m9）、大九和弦（maj9）、小十一和弦（m11）以及 7#5、7b9 等变化属和弦，便于衔接击勾弦与双音装饰。"),
            ("如何把 R&B 和弦弹得干净通透？", "多使用中音区四音指型，避开低音区浑浊的三度堆叠，让声部连接更顺滑。"),
        ],
    },
    "midwest-emo": {
        "en_title": "Midwest Emo Guitar Chords (Standard & FACGCE) — add9",
        "en_h1": "Midwest Emo Guitar Chords & Voicings",
        "en_desc": "21 Midwest emo guitar chords in Standard and FACGCE tuning: open treble pedals, bright maj7 and add9 extensions with playable fret diagrams and audio.",
        "en_kw": "midwest emo guitar chords,midwest emo chords,facgce chords,emo guitar voicings,twinkly guitar chords",
        "zh_title": "中西部 emo 吉他和弦与指法（标准调弦 & FACGCE）— add9",
        "zh_h1": "中西部 emo 吉他和弦与指法",
        "zh_desc": "精选 21 个中西部 emo（Midwest emo）吉他和弦，包含标准调弦与 FACGCE 调弦中的高音空弦持续音与明亮延伸和弦。",
        "zh_kw": "中西部emo吉他和弦,Midwest emo和弦,情绪摇滚吉他指法,FACGCE和弦,空弦延伸音",
        "en_faq": [
            ("What tunings are best for Midwest emo chords?", "FACGCE is the signature open tuning for sparkling arpeggios, while Standard tuning with a capo on frets 2–5 works well for open-string maj7 and add9 shapes."),
            ("What chord types give the classic Midwest emo sound?", "Major 7th, add9, and sus2 chords with ringing open strings on top create that bittersweet, open harmonic texture."),
        ],
        "zh_faq": [
            ("中西部 emo 常用什么调弦？", "FACGCE 是最经典的开放调弦，能轻松弹出闪亮的分解琶音；标准调弦配合变调夹（2–5 品）同样适合保留高音空弦。"),
            ("哪些和弦最有 Midwest emo 味道？", "带有高音空弦持续音的 maj7、add9 与 sus2 和弦，能营造出明亮又略带怀旧的情绪色彩。"),
        ],
    },
    "jazz": {
        "en_title": "Jazz Guitar Chords: Shells, Drop Voicings & Altered Dominants — add9",
        "en_h1": "Jazz Guitar Chords & Voicings",
        "en_desc": "19 essential jazz guitar chord voicings in Standard tuning: 3-note shells, Drop 2 & Drop 3 shapes, and altered dominants with note labels and audio.",
        "en_kw": "jazz guitar chords,jazz guitar chord voicings,shell voicings guitar,drop 2 guitar chords,altered dominant guitar",
        "zh_title": "爵士吉他和弦：Shell 指型、Drop 2 与变化属和弦 — add9",
        "zh_h1": "爵士吉他和弦与指法",
        "zh_desc": "精选 19 个标准调弦爵士吉他和弦：三音 Shell 指型、Drop 2 / Drop 3 声部排列与变化属和弦，清晰标注根音与每个发声音名。",
        "zh_kw": "爵士吉他和弦,Jazz和弦指法,Shell和弦,Drop 2指法,变化属和弦",
        "en_faq": [
            ("What are jazz shell voicings on guitar?", "Shell voicings use just three notes—root, 3rd, and 7th—dropping the 5th so you can comp cleanly through ii–V–I changes without clutter."),
            ("When should I use Drop 2 voicings?", "Drop 2 voicings put four close-harmony notes on adjacent strings, ideal for chord-melody arrangements and smooth voice leading."),
        ],
        "zh_faq": [
            ("什么是爵士吉他的 Shell 和弦指型？", "Shell 指型只保留根音、三音和七音（省略五音），仅需三根手指就能清晰交代和声功能，非常适合 ii–V–I 伴奏。"),
            ("什么时候使用 Drop 2 指型？", "Drop 2 将四音和弦紧凑分布在相邻四根弦上，声部线条清晰，非常适合爵士独奏与和弦旋律编配。"),
        ],
    },
    "jpop": {
        "en_title": "J-Pop Guitar Chords & Voicings (IV–iii–vi & Color Chords) — add9",
        "en_h1": "J-Pop Guitar Chords & Voicings",
        "en_desc": "21 curated J-pop guitar chords in Standard tuning: IV–iii–vi seventh moves, held-fifth voicings, and colored rock chords with interactive audio.",
        "en_kw": "j-pop guitar chords,japanese guitar chords,royal road progression chords,jpop chord voicings,anime guitar chords",
        "zh_title": "J-pop 日系吉他和弦与王道进行指法 — add9",
        "zh_h1": "J-pop 吉他和弦与指法",
        "zh_desc": "精选 21 个日系 J-pop 吉他和弦指法：IV–iii–vi 王道进行七和弦连接、保留五度指型与富有色彩的日系摇滚和弦，支持试听。",
        "zh_kw": "J-pop吉他和弦,日系吉他和弦,王道进行和弦,日摇和弦指法,add9和弦",
        "en_faq": [
            ("What is the classic J-pop chord progression?", "The Royal Road progression (IVmaj7 – V7 – iii7 – vi7) is a staple of J-pop and anime music, often colored with add9, sus4, and slash-bass inversions."),
            ("How do J-pop guitarists voice rock chords cleanly?", "By holding a common fifth or ninth on the top strings while moving the bass note underneath."),
        ],
        "zh_faq": [
            ("J-pop 最经典的和弦进行是什么？", "IVmaj7 – V7 – iii7 – vi7（常称“王道进行”）是 J-pop 与动漫音乐的核心骨架，常搭配 add9、sus4 与转位低音增强流动感。"),
            ("日系吉他如何让和弦连接更顺滑？", "常在高音弦保留共同音（如五音或九音），同时让低音线级进移动，形成明亮流畅的织体。"),
        ],
    },
    "city-pop": {
        "en_title": "City Pop Guitar Chords & Cutting Voicings — add9",
        "en_h1": "City Pop Guitar Chords & Voicings",
        "en_desc": "16 City pop guitar chord voicings in Standard tuning: compact sevenths, ninths, crisp upper-string cutting voicings, and altered dominants.",
        "en_kw": "city pop guitar chords,japanese city pop chords,funk guitar cutting voicings,city pop chord progression",
        "zh_title": "City pop 吉他和弦与高音弦切音指法 — add9",
        "zh_h1": "City pop 吉他和弦与指法",
        "zh_desc": "精选 16 个 City pop 吉他和弦指法：紧凑七、九和弦、清脆的高音弦切音（Cutting）指型与变化属和弦，点击即可试听。",
        "zh_kw": "City pop吉他和弦,城市流行吉他和弦,切音和弦指法,日系Funk吉他和弦,九和弦指法",
        "en_faq": [
            ("What chords give City pop its glossy sound?", "Tight maj7, m9, 13th, and slash chords (like F/G or G11) played on the top three or four strings for snappy rhythmic cutting."),
            ("Why use upper-string voicings in City pop?", "Skipping the low E and A strings leaves space for the synth bass and kick drum while making funky 16th-note strums crisp."),
        ],
        "zh_faq": [
            ("City pop 标志性的都市感来自哪些和弦？", "核心是紧凑的 maj7、m9、13 和弦以及挂留属和弦（如 F/G），常在高音三四根弦上做十六分音符切音。"),
            ("为什么 City pop 常用高音弦和弦指型？", "避开低音弦可以为贝斯与底鼓留出空间，同时让切音节奏更干脆明亮。"),
        ],
    },
    "bossa-nova": {
        "en_title": "Bossa Nova Guitar Chords (6/9, m6 & Flat-Five Dominants) — add9",
        "en_h1": "Bossa Nova Guitar Chords & Voicings",
        "en_desc": "10 authentic Bossa nova guitar chords in Standard tuning: 6/9 tonics, minor sixths and ninths, and 7b5 dominants voiced for thumb-led bass.",
        "en_kw": "bossa nova guitar chords,bossa nova chord voicings,6/9 guitar chord,brazilian guitar chords",
        "zh_title": "Bossa nova 吉他和弦与指弹声部指法 — add9",
        "zh_h1": "Bossa nova 吉他和弦与指法",
        "zh_desc": "精选 10 个经典 Bossa nova 吉他和弦指法：六九主和弦、小六与小九和弦，以及拇指低音上的降五属和弦，清晰直观。",
        "zh_kw": "Bossa nova吉他和弦,Bossa nova指法,六九和弦,小六和弦,巴西吉他和弦",
        "en_faq": [
            ("What are the most essential Bossa nova guitar chords?", "Major 6/9, maj7, minor 6 (m6), minor 9 (m9), and dominant 7b5 or 13b9 shapes voiced so the thumb alternates bass notes while fingers pluck the upper three strings."),
            ("Are Bossa nova chords playable without a pick?", "Yes—these 4-note voicings are specifically designed for fingerstyle thumb-and-three-finger comping."),
        ],
        "zh_faq": [
            ("Bossa nova 最核心的吉他和弦有哪些？", "大六九（6/9）、maj7、小六（m6）、小九（m9）以及 7b5、13b9 属和弦，非常适合拇指拨低音、其余三指齐奏高音声部。"),
            ("这些 Bossa nova 指法适合指弹吗？", "非常适合。这 10 个四音指型专门对应经典的拇指低音伴奏习惯，转换省力且声部平衡。"),
        ],
    },
    "lofi": {
        "en_title": "Lo-Fi Guitar Chords & Warm Seventh Voicings — add9",
        "en_h1": "Lo-Fi Guitar Chords & Voicings",
        "en_desc": "16 lo-fi guitar chord voicings in Standard tuning: soft sevenths, smooth inversions, and warm 6/9 shapes with clickable fretboard audio.",
        "en_kw": "lofi guitar chords,lo-fi chord voicings,chill guitar chords,lofi hip hop guitar chords",
        "zh_title": "Lo-fi 吉他和弦与温暖七和弦指法 — add9",
        "zh_h1": "Lo-fi 吉他和弦与指法",
        "zh_desc": "精选 16 个 Lo-fi 吉他和弦指法：柔和七和弦、顺滑转位与温暖六九和弦，适合 chill 节拍与卧室录音。",
        "zh_kw": "Lo-fi吉他和弦,Lofi和弦指法,治愈系吉他和弦,七和弦转位,卧室流行和弦",
        "en_faq": [
            ("What makes a chord progression sound lo-fi?", "Warm maj7, m7, and 6/9 voicings played softly in the mid-neck register, often using first or second inversions for gentle bass movement."),
            ("Do lo-fi guitar chords work on acoustic and electric?", "Yes—they sound great both on a clean neck-pickup electric and on a warm nylon or steel-string acoustic."),
        ],
        "zh_faq": [
            ("怎样弹出温暖松弛的 Lo-fi 和弦感？", "在中把位轻弹 maj7、m7 和 6/9 和弦，并善用第一、第二转位让低音平缓流动，避免过于尖锐的高频。"),
            ("这些 Lo-fi 和弦适合木吉他还是电吉他？", "两者皆宜。电吉他琴颈拾音器清音或木吉他轻拨都能呈现柔和的质感。"),
        ],
    },
    "indie": {
        "en_title": "Jangle Pop Guitar Chords (Standard, Open E & Whole Step Up) — add9",
        "en_h1": "Jangle Pop Guitar Chords & Voicings",
        "en_desc": "33 jangle pop and indie guitar chords across Standard, Open E, and Whole Step Up tunings: movable shapes ringing against open strings.",
        "en_kw": "jangle pop guitar chords,indie guitar chords,open e guitar chords,chimey guitar chords,smiths style chords",
        "zh_title": "Jangle pop 独立摇滚吉他和弦与空弦指法 — add9",
        "zh_h1": "Jangle pop 吉他和弦与指法",
        "zh_desc": "精选 33 个 Jangle pop 与独立摇滚吉他和弦，覆盖标准调弦、Open E 与升全音调弦，让可移动指型与清脆空弦交织共鸣。",
        "zh_kw": "Jangle pop吉他和弦,独立摇滚吉他和弦,Open E调弦和弦,空弦共鸣指法,英伦独立吉他",
        "en_faq": [
            ("Why do jangle pop players use Whole Step Up or Open E?", "Tuning a whole step up (or using a capo on fret 2) increases string tension and brightness, giving open-string arpeggios their signature chime."),
            ("Are Standard tuning jangle pop chords included?", "Yes—this guide covers Standard tuning alongside Open E and Whole Step Up shapes."),
        ],
        "zh_faq": [
            ("为什么 Jangle pop 吉他手常使用升全音调弦或变调夹？", "升高音高会增加琴弦张力并让泛音更清脆，使开放弦分解琶音呈现出标志性的钟鸣感。"),
            ("本页是否包含标准调弦的 Jangle pop 指法？", "包含。本页同时收录标准调弦、Open E 与升全音调弦的经典指法。"),
        ],
    },
    "bedroom-pop": {
        "en_title": "Bedroom Pop Guitar Chords (Standard & Open D) — add9",
        "en_h1": "Bedroom Pop Guitar Chords & Voicings",
        "en_desc": "24 bedroom pop guitar chords in Standard and Open D tuning: cozy barre and open sevenths plus dreamy Open D drone voicings with audio.",
        "en_kw": "bedroom pop guitar chords,indie bedroom pop chords,open d guitar chords,dreamy guitar chords",
        "zh_title": "Bedroom pop 卧室流行吉他和弦（标准调弦 & Open D）— add9",
        "zh_h1": "Bedroom pop 吉他和弦与指法",
        "zh_desc": "精选 24 个 Bedroom pop 吉他和弦指法，涵盖标准调弦的开放/横按七和弦，以及 Open D 调弦下的梦幻持续音指型。",
        "zh_kw": "Bedroom pop吉他和弦,卧室流行吉他和弦,Open D调弦和弦,梦幻吉他和弦,七和弦指法",
        "en_faq": [
            ("What chords are most common in bedroom pop?", "Relaxed maj7, m7, and add9 shapes in Standard tuning, plus lush Open D (DADF#AD) voicings where one or two fingers create full, shimmering chords."),
            ("Can beginners play these bedroom pop voicings?", "Yes—many Open D and open-position seventh shapes require only two or three fingers."),
        ],
        "zh_faq": [
            ("Bedroom pop 最常用的吉他和弦有哪些？", "标准调弦下轻松自然的 maj7、m7、add9，以及 Open D 调弦下只需一两根手指即可按出的梦幻持续音和弦。"),
            ("新手可以弹这些 Bedroom pop 指法吗？", "完全可以，其中不少开放七和弦与 Open D 指型按法简洁、手感轻松。"),
        ],
    },
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def chord_display_name(root_pc: int, quality: str) -> str:
    root = NOTE_NAMES[root_pc % 12]
    if quality in ("maj", "major", ""):
        return root
    return f"{root}{quality}"


def fret_code(frets: list[int | None]) -> str:
    parts = []
    for f in frets:
        if f is None:
            parts.append("x")
        else:
            parts.append(str(f))
    return " ".join(parts) if any(f is not None and f >= 10 for f in frets) else "".join(parts)


def sounding_midis(frets: list[int | None], tuning_midis: list[int]) -> list[int]:
    out = []
    for i, f in enumerate(frets):
        if f is not None and i < len(tuning_midis):
            out.append(tuning_midis[i] + f)
    return out


def render_fretboard_svg(
    frets: list[int | None],
    tuning_midis: list[int],
    root_pc: int,
    highlight_string: int | None = None,
    ghost_fret: tuple[int, int] | None = None,
) -> str:
    """
    Renders a clean, accessible SVG guitar chord diagram (low E -> high e).
    - Root notes get the brand rose-magenta square marker.
    - Non-root fretted notes get deep slate dots.
    - Open strings get outline circles; muted strings get crisp crosses.
    - Every sounding string displays its sounding note name below.
    """
    positive = [f for f in frets if f is not None and f > 0]
    min_f = min(positive) if positive else 1
    max_f = max(positive) if positive else 4
    base_fret = 1 if max_f <= 4 else min_f
    num_frets = max(4, (max_f - base_fret + 1) if positive else 4)
    num_frets = min(num_frets, 5)

    w = 196
    left = 34
    right = 176
    top = 34
    fret_h = 26
    h = top + num_frets * fret_h + 28
    step_x = (right - left) / 5.0

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="Chord diagram {esc(fret_code(frets))}">',
    ]

    # Nut or base fret label
    if base_fret == 1:
        lines.append(
            f'<line x1="{left}" y1="{top}" x2="{right}" y2="{top}" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>'
        )
    else:
        lines.append(
            f'<text x="{left - 10}" y="{top + fret_h * 0.65:.1f}" text-anchor="end" font-size="11" font-weight="700" fill="var(--muted)" font-family="var(--font-mono)">{base_fret}fr</text>'
        )

    # Horizontal fret wires
    for r in range(num_frets + 1):
        y = top + r * fret_h
        if r == 0 and base_fret == 1:
            continue
        lines.append(
            f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" stroke="var(--line)" stroke-width="1.4"/>'
        )

    # Vertical strings
    for s in range(6):
        x = left + s * step_x
        sw = 1.8 - s * 0.14
        lines.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + num_frets * fret_h}" stroke="var(--muted)" stroke-opacity="0.55" stroke-width="{sw:.2f}"/>'
        )

    # Optional ghost ring & trail (for hero C -> Cadd9 demo)
    if ghost_fret is not None:
        gs, gf = ghost_fret
        gx = left + gs * step_x
        gy = top + (gf - base_fret + 0.5) * fret_h
        if highlight_string == gs and frets[gs] is not None:
            ty = top + (frets[gs] - base_fret + 0.5) * fret_h
            lines.append(
                f'<line x1="{gx:.1f}" y1="{gy:.1f}" x2="{gx:.1f}" y2="{ty:.1f}" stroke="var(--accent-bright)" stroke-width="3" stroke-opacity="0.55" stroke-dasharray="3 3"/>'
            )
        lines.append(
            f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="7.5" fill="none" stroke="var(--muted)" stroke-width="2" stroke-opacity="0.7"/>'
        )

    # Dots, open/muted markers, and note labels
    label_y = top + num_frets * fret_h + 18
    for s in range(6):
        x = left + s * step_x
        f = frets[s]
        if f is None:
            cy = top - 14
            lines.append(
                f'<path d="M{x - 4:.1f} {cy - 4:.1f} L{x + 4:.1f} {cy + 4:.1f} M{x + 4:.1f} {cy - 4:.1f} L{x - 4:.1f} {cy + 4:.1f}" stroke="var(--muted)" stroke-width="1.8" stroke-linecap="round"/>'
            )
            continue

        midi = tuning_midis[s] + f
        pc = midi % 12
        note_name = NOTE_NAMES[pc]
        is_root = pc == (root_pc % 12)

        if f == 0:
            cy = top - 14
            stroke_c = "var(--accent)" if is_root else "currentColor"
            lines.append(
                f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="5.5" fill="none" stroke="{stroke_c}" stroke-width="2"/>'
            )
        else:
            row = f - base_fret
            cy = top + (row + 0.5) * fret_h
            if highlight_string == s:
                lines.append(
                    f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="9.5" fill="var(--accent-bright)"/>'
                )
            elif is_root:
                lines.append(
                    f'<rect x="{x - 8:.1f}" y="{cy - 8:.1f}" width="16" height="16" rx="4" fill="var(--accent)"/>'
                )
            else:
                lines.append(
                    f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="8" fill="var(--ink)"/>'
                )

        fill_lbl = "var(--accent)" if (is_root or highlight_string == s) else "var(--muted)"
        fw = "700" if (is_root or highlight_string == s) else "500"
        lines.append(
            f'<text x="{x:.1f}" y="{label_y}" text-anchor="middle" font-size="10.5" font-weight="{fw}" fill="{fill_lbl}">{esc(note_name)}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


PLAY_SVG = '<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M4.2 2.6a.8.8 0 0 1 1.22-.68l8.1 5.4a.8.8 0 0 1 0 1.36l-8.1 5.4A.8.8 0 0 1 4.2 13.4V2.6Z"/></svg>'
APPLE_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83ZM15.96 6.33c.68-.83 1.14-1.98 1.01-3.13-.98.04-2.17.65-2.87 1.48-.63.72-1.18 1.89-1.03 3.01 1.1.09 2.21-.55 2.89-1.36Z"/></svg>'


def head_html(
    *,
    lang: str,
    title: str,
    description: str,
    keywords: str,
    canonical_url: str,
    en_url: str,
    zh_url: str,
    rel_root: str,
    base_url: str,
    json_ld_list: list[dict],
) -> str:
    content_lang = "zh-CN" if lang == "zh-Hans" else "en-US"
    og_locale = "zh_CN" if lang == "zh-Hans" else "en_US"
    og_alt = "en_US" if lang == "zh-Hans" else "zh_CN"
    ld_scripts = "\n".join(
        f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'
        for obj in json_ld_list
    )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="content-language" content="{content_lang}">
  <meta name="applicable-device" content="pc,mobile">
  <meta http-equiv="Cache-Control" content="no-transform">
  <meta http-equiv="Cache-Control" content="no-siteapp">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="keywords" content="{esc(keywords)}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="apple-itunes-app" content="app-id={APP_ID}">
  <link rel="canonical" href="{esc(canonical_url)}">
  <link rel="alternate" hreflang="en" href="{esc(en_url)}">
  <link rel="alternate" hreflang="zh-Hans" href="{esc(zh_url)}">
  <link rel="alternate" hreflang="x-default" href="{esc(en_url)}">
  <link rel="icon" href="{rel_root}assets/icon.svg" type="image/svg+xml">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="add9">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical_url)}">
  <meta property="og:image" content="{esc(base_url)}/assets/icon.svg">
  <meta property="og:locale" content="{og_locale}">
  <meta property="og:locale:alternate" content="{og_alt}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(base_url)}/assets/icon.svg">
  <link rel="stylesheet" href="{rel_root}assets/style.css">
  {ld_scripts}
</head>"""


def header_html(lang: str, rel_root: str, switch_href: str, active: str) -> str:
    is_zh = lang == "zh-Hans"
    home_href = f"{rel_root}zh/" if is_zh else f"{rel_root}"
    chords_href = f"{rel_root}zh/chords/" if is_zh else f"{rel_root}chords/"
    privacy_href = f"{rel_root}zh/privacy/" if is_zh else f"{rel_root}privacy/"
    store_url = APP_STORE_CN if is_zh else APP_STORE_US
    chords_lbl = "和弦库" if is_zh else "Chords"
    privacy_lbl = "隐私" if is_zh else "Privacy"
    switch_lbl = "EN" if is_zh else "中文"
    cta_lbl = "下载 App" if is_zh else "App Store"
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{home_href}">
      <span class="brand-icon"><img src="{rel_root}assets/icon.svg" alt="add9" width="30" height="30"></span>
      <span>add9</span>
    </a>
    <nav class="nav-links" aria-label="{'主导航' if is_zh else 'Main navigation'}">
      <a href="{chords_href}"{' aria-current="page"' if active == 'chords' else ''}>{chords_lbl}</a>
      <a href="{privacy_href}"{' aria-current="page"' if active == 'privacy' else ''}>{privacy_lbl}</a>
      <a class="lang-switch" href="{switch_href}" hreflang="{'en' if is_zh else 'zh-Hans'}">{switch_lbl}</a>
      <a class="btn btn-primary btn-sm" href="{store_url}" target="_blank" rel="noopener">{cta_lbl}</a>
    </nav>
  </div>
</header>"""


def footer_html(lang: str, rel_root: str, switch_href: str) -> str:
    is_zh = lang == "zh-Hans"
    home_href = f"{rel_root}zh/" if is_zh else f"{rel_root}"
    chords_href = f"{rel_root}zh/chords/" if is_zh else f"{rel_root}chords/"
    privacy_href = f"{rel_root}zh/privacy/" if is_zh else f"{rel_root}privacy/"
    store_url = APP_STORE_CN if is_zh else APP_STORE_US
    note = "add9 · 离线吉他和弦与风格指法库（iPhone & iPad）" if is_zh else "add9 — Offline guitar chord & genre voicing library for iPhone and iPad."
    return f"""<footer class="site-footer">
  <div class="wrap footer-inner">
    <span>{note}</span>
    <div class="footer-links">
      <a href="{home_href}">{'首页' if is_zh else 'Home'}</a>
      <a href="{chords_href}">{'按风格浏览和弦' if is_zh else 'Chords by Genre'}</a>
      <a href="{privacy_href}">{'隐私政策' if is_zh else 'Privacy Policy'}</a>
      <a href="{switch_href}">{'English' if is_zh else '简体中文'}</a>
      <a href="{store_url}" target="_blank" rel="noopener">App Store</a>
    </div>
  </div>
</footer>
<script src="{rel_root}assets/audio.js" defer></script>
</body>
</html>"""


def md_to_simple_html(md_text: str) -> str:
    """Minimal deterministic Markdown-to-HTML converter for the privacy policies."""
    lines = md_text.strip().splitlines()
    out: list[str] = []
    in_ul = False

    def inline(txt: str) -> str:
        t = esc(txt)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(
            r"\[([^\]]+)\]\((https?://[^)]+|mailto:[^)]+)\)",
            r'<a href="\2" target="_blank" rel="noopener">\1</a>',
            t,
        )
        t = re.sub(
            r"\[([^\]]+@[^\]]+)\]\(([^)]+@[^)]+)\)",
            r'<a href="mailto:\2">\1</a>',
            t,
        )
        return t

    for raw in lines:
        line = raw.strip()
        if not line:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            continue
        if line.startswith("# "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(line[2:])}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{inline(line)}</p>")
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


def build_site(repo_root: Path, alt_chord_root: Path, base_url: str) -> None:
    base_url = base_url.rstrip("/")

    with open(alt_chord_root / "Packages/ChordKit/Sources/ChordKit/Resources/chord-atlas.json") as f:
        atlas = json.load(f)
    with open(alt_chord_root / "AlternativeChord/Resources/Localizable.xcstrings") as f:
        loc_strings = json.load(f).get("strings", {})

    def zh_text(en: str, fallback: str | None = None) -> str:
        val = (
            loc_strings.get(en, {})
            .get("localizations", {})
            .get("zh-Hans", {})
            .get("stringUnit", {})
            .get("value")
        )
        return val if val else (fallback if fallback is not None else en)

    tunings_by_id = {t["id"]: t for t in atlas["tunings"]}
    styles_by_id = {s["id"]: s for s in atlas["styles"]}
    families_by_style: dict[str, list[dict]] = {s["id"]: [] for s in atlas["styles"]}
    for fam in atlas["families"]:
        families_by_style[fam["styleID"]].append(fam)

    total_voicings = sum(len(f["voicings"]) for f in atlas["families"])
    sitemap_entries: list[tuple[str, str, str]] = []  # (en_url, zh_url, priority)

    def write_page(rel_path: str, content: str) -> None:
        dest = repo_root / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

    # Hero interactive voicing bench items (playable in browser!)
    std_midi = tunings_by_id["standard"]["midiNotes"]
    bench_items = [
        {
            "tab_en": "Cadd9",
            "tab_zh": "Cadd9",
            "chord": "Cadd9",
            "meta_en": "Move one finger from plain C (x32010 → x32030)",
            "meta_zh": "从普通 C 和弦移动一根手指（x32010 → x32030）",
            "frets": [None, 3, 2, 0, 3, 0],
            "root": 0,
            "hl": 4,
            "ghost": (4, 1),
        },
        {
            "tab_en": "Jazz",
            "tab_zh": "爵士",
            "chord": "Cmaj7 (Shell)",
            "meta_en": "Three-note shell voicing · 8 7 9 x x x",
            "meta_zh": "爵士三音 Shell 指型 · 8 7 9 x x x",
            "frets": [8, 7, 9, None, None, None],
            "root": 0,
            "hl": None,
            "ghost": None,
        },
        {
            "tab_en": "Shoegaze",
            "tab_zh": "盯鞋",
            "chord": "Eadd9",
            "meta_en": "Ringing open treble strings · 0 2 4 1 0 0",
            "meta_zh": "高音空弦持续共鸣 · 0 2 4 1 0 0",
            "frets": [0, 2, 4, 1, 0, 0],
            "root": 4,
            "hl": 2,
            "ghost": None,
        },
        {
            "tab_en": "Math rock",
            "tab_zh": "数学摇滚",
            "chord": "Fmaj7",
            "meta_en": "Compact Standard-tuning maj7 · 1 x 2 2 1 0",
            "meta_zh": "标准调弦紧凑大七指型 · 1 x 2 2 1 0",
            "frets": [1, None, 2, 2, 1, 0],
            "root": 5,
            "hl": 5,
            "ghost": None,
        },
        {
            "tab_en": "Neo-soul",
            "tab_zh": "新灵魂乐",
            "chord": "Am9",
            "meta_en": "Lush minor ninth grip · 5 x 5 5 5 7",
            "meta_zh": "丰满小九和弦指型 · 5 x 5 5 5 7",
            "frets": [5, None, 5, 5, 5, 7],
            "root": 9,
            "hl": 5,
            "ghost": None,
        },
    ]

    def render_bench(is_zh: bool) -> str:
        tabs = []
        panels = []
        for idx, b in enumerate(bench_items):
            pressed = "true" if idx == 0 else "false"
            tabs.append(
                f'<button type="button" class="bench-tab" data-bench-idx="{idx}" aria-pressed="{pressed}">{esc(b["tab_zh"] if is_zh else b["tab_en"])}</button>'
            )
            midis = ",".join(str(m) for m in sounding_midis(b["frets"], std_midi))
            svg = render_fretboard_svg(
                b["frets"], std_midi, b["root"], highlight_string=b["hl"], ghost_fret=b["ghost"]
            )
            hidden_attr = "" if idx == 0 else " hidden"
            strum_lbl = "试听" if is_zh else "Strum"
            panels.append(
                f"""<div data-bench-panel="{idx}"{hidden_attr}>
  <div class="bench-stage">
    <div>
      <p class="bench-chord-name">{esc(b['chord'])}</p>
      <p class="bench-chord-meta">{esc(b['meta_zh'] if is_zh else b['meta_en'])}</p>
    </div>
    <button type="button" class="strum-btn" data-midi="{midis}" aria-label="{strum_lbl} {esc(b['chord'])}">{PLAY_SVG}<span>{strum_lbl}</span></button>
  </div>
  <div class="bench-diagram">{svg}</div>
</div>"""
            )
        caption = (
            "点击上方风格切换指法并试听——方格标记根音，底部标注每根发声弦的音名。"
            if is_zh
            else "Click a style to switch voicings and hear the guitar strum. Squares mark the root."
        )
        return f"""<div class="bench" aria-label="{'交互式和弦试听' if is_zh else 'Interactive chord preview'}">
  <div class="bench-tabs" role="group" aria-label="{'选择风格和弦' if is_zh else 'Choose a voicing'}">{''.join(tabs)}</div>
  {''.join(panels)}
  <p class="bench-caption">{caption}</p>
</div>"""

    def render_genre_list(is_zh: bool, rel_prefix: str) -> str:
        rows = []
        for sid in STYLE_ORDER:
            s = styles_by_id[sid]
            slug = STYLE_SLUGS[sid]
            fams = families_by_style[sid]
            vcount = sum(len(f["voicings"]) for f in fams)
            name = zh_text(s["name"]) if is_zh else s["name"]
            summ = zh_text(s["summary"]) if is_zh else s["summary"]
            tunings_html = "".join(
                f'<span class="tag">{esc(zh_text(tunings_by_id[tid]["name"]) if is_zh else tunings_by_id[tid]["name"])}</span>'
                for tid in s["tuningIDs"]
            )
            count_lbl = f"{vcount} 个指法" if is_zh else f"{vcount} voicings"
            href = f"{rel_prefix}{slug}/"
            rows.append(
                f"""<a class="genre-row" href="{href}">
  <div>
    <div class="genre-row-top">
      <h3>{esc(name)}</h3>
      <span class="genre-count">{count_lbl}</span>
    </div>
    <p>{esc(summ)}</p>
  </div>
  <div class="genre-tunings">{tunings_html}</div>
</a>"""
            )
        return f'<div class="genre-list">{"".join(rows)}</div>'

    # 1. Home pages: / (EN) and /zh/ (ZH-Hans)
    for is_zh in (False, True):
        lang = "zh-Hans" if is_zh else "en"
        rel_root = "../" if is_zh else ""
        en_url = f"{base_url}/"
        zh_url = f"{base_url}/zh/"
        canonical = zh_url if is_zh else en_url
        switch_href = "../" if is_zh else "zh/"
        store_url = APP_STORE_CN if is_zh else APP_STORE_US

        if is_zh:
            title = "add9 — 吉他和弦、风格指法与和弦反查 App（iPhone / iPad）"
            desc = "告别无聊和弦。add9 是一款离线吉他和弦与指法 App，覆盖爵士、盯鞋、数学摇滚、中西部 emo、新灵魂乐、J-pop、City pop、Bossa nova 等 11 种风格，支持和弦反查、变调夹与和弦进行。"
            kw = "add9,吉他和弦,吉他和弦App,和弦指法,和弦反查,爵士吉他和弦,盯鞋吉他和弦,数学摇滚和弦,变调夹,和弦进行"
            h1 = "告别无聊和弦。"
            lead = "选一个基础和弦，立刻得到该音乐风格里吉他手真正会弹的精彩指法。覆盖 11 种风格、5 种调弦与离线原声试听。"
            cta_main = "在 App Store 免费下载"
            cta_sec = "浏览 11 种风格和弦库"
            hero_note = "适用于 iPhone 与 iPad · 离线可用 · 无广告 · 无订阅"
            sec1_h2 = "按音乐风格探索吉他和弦"
            sec1_sub = f"收录 {total_voicings} 个经过校对的真实可弹指法，点击任意风格即可在线查看指板图并试听。"
            sec2_h2 = "为认真练琴和写歌的人设计"
            caps = [
                ("按风格替换和弦", "输入普通 C 或 Am，立刻查看爵士、盯鞋、数学摇滚、新灵魂乐或 J-pop 中对应的精彩延伸与转位指法。"),
                ("按指型反查 + 可移动把位", "在指板上点出你偶然按到的怪和弦，立刻识别和弦名，并可整把位上下移动、保留空弦共鸣。"),
                ("真实音高的变调夹与特殊调弦", "支持标准调弦、FACGCE、Open D、Open E、升全音调弦以及 0–12 品变调夹，指板图与和弦名同步换算实际音高。"),
                ("收藏具体指法与创建进行", "将喜欢的具体指法归入自定义风格，自由串联和弦进行、调节速度并离线原声回放。"),
            ]
            cta_h2 = "把 11 种风格与完整和弦库装进口袋"
            cta_p = "无需登录，无广告，不追踪隐私。所有和弦图、反查引擎与吉他原声合成全部本地离线运行。"
            cta_btn = "前往 App Store 下载 add9"
        else:
            title = "add9 — Guitar Chord Voicing App & Finder by Genre (iOS)"
            desc = "No more boring chords. add9 is an offline guitar chord voicing app for iPhone and iPad covering Jazz, Shoegaze, Math rock, Midwest emo, Neo-soul, J-pop, City pop, and Bossa nova—with reverse chord finder, capo, and progressions."
            kw = "guitar chord voicing app,guitar chord finder,add9 app,genre guitar chords,reverse chord finder,math rock chords,shoegaze guitar chords,jazz guitar voicings"
            h1 = "No more boring chords."
            lead = "Ask for a plain chord and get the playable voicings players actually use in Jazz, Shoegaze, Math rock, Neo-soul, J-pop, and six more genres."
            cta_main = "Download Free on App Store"
            cta_sec = "Browse 11 Genre Guides"
            hero_note = "For iPhone & iPad · 100% offline · No ads · No subscription"
            sec1_h2 = "Explore guitar chords by genre"
            sec1_sub = f"{total_voicings} curated, playable voicings across 11 styles and 5 tunings. Open any guide to inspect fretboard notes and hear each chord."
            sec2_h2 = "Built for players writing beyond cowboy chords"
            caps = [
                ("Genre-aware chord alternatives", "Pick a root and quality, then compare standard shapes alongside curated Jazz, Shoegaze, Math rock, Midwest emo, and Neo-soul voicings."),
                ("Reverse chord finder with movable shapes", "Tap notes on the fretboard to identify unfamiliar shapes, then shift fretted notes up or down the neck while open strings keep ringing."),
                ("Accurate capo & alternate tunings", "Switch between Standard, FACGCE, Open D, Open E, Whole step up, and Capo 0–12—every diagram, sounding note label, and chord name updates live."),
                ("Save exact voicings & build progressions", "Organize favorite fingerings into custom genres, string chords into progressions, set tempo, and audition everything offline."),
            ]
            cta_h2 = "Carry all 11 genres and the full chord library offline"
            cta_p = "No account, no ads, no subscription. Built natively for iPhone and iPad with realistic offline acoustic guitar playback."
            cta_btn = "Get add9 on the App Store"

        app_ld = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "add9",
            "operatingSystem": "iOS 17.0+",
            "applicationCategory": "MusicApplication",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "url": canonical,
            "downloadUrl": store_url,
            "description": desc,
            "inLanguage": ["en", "zh-Hans"],
        }

        caps_html = "".join(
            f'<div class="cap-item"><h3>{esc(t)}</h3><p>{esc(p)}</p></div>'
            for t, p in caps
        )
        chords_prefix = "chords/"
        page_html = f"""{head_html(
            lang=lang,
            title=title,
            description=desc,
            keywords=kw,
            canonical_url=canonical,
            en_url=en_url,
            zh_url=zh_url,
            rel_root=rel_root,
            base_url=base_url,
            json_ld_list=[app_ld],
        )}
<body>
{header_html(lang, rel_root, switch_href, active="home")}
<main>
  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <h1>{esc(h1)}</h1>
        <p class="hero-lead">{esc(lead)}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{store_url}" target="_blank" rel="noopener">{APPLE_SVG}<span>{cta_main}</span></a>
          <a class="btn btn-secondary" href="{chords_prefix}">{cta_sec}</a>
        </div>
        <p class="hero-note">{hero_note}</p>
      </div>
      {render_bench(is_zh)}
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <div>
          <h2>{esc(sec1_h2)}</h2>
          <p class="section-sub">{esc(sec1_sub)}</p>
        </div>
      </div>
      {render_genre_list(is_zh, chords_prefix)}
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <h2>{esc(sec2_h2)}</h2>
      </div>
      <div class="cap-grid">{caps_html}</div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="cta-band">
        <div>
          <h2>{esc(cta_h2)}</h2>
          <p>{esc(cta_p)}</p>
        </div>
        <a class="btn btn-primary" href="{store_url}" target="_blank" rel="noopener">{APPLE_SVG}<span>{cta_btn}</span></a>
      </div>
    </div>
  </section>
</main>
{footer_html(lang, rel_root, switch_href)}"""
        write_page("zh/index.html" if is_zh else "index.html", page_html)

    sitemap_entries.append((f"{base_url}/", f"{base_url}/zh/", "1.0"))

    # 2. Chords Directory Index: /chords/ and /zh/chords/
    for is_zh in (False, True):
        lang = "zh-Hans" if is_zh else "en"
        rel_root = "../../" if is_zh else "../"
        en_url = f"{base_url}/chords/"
        zh_url = f"{base_url}/zh/chords/"
        canonical = zh_url if is_zh else en_url
        switch_href = "../../chords/" if is_zh else "../zh/chords/"
        home_href = "../" if is_zh else "../"

        if is_zh:
            title = "吉他和弦风格指法库（11 种风格、222 个精选指法）— add9"
            desc = "按音乐风格浏览 222 个精选吉他和弦指法：数学摇滚、盯鞋、新灵魂乐、中西部 emo、爵士、J-pop、City pop、Bossa nova、Lo-fi、Jangle pop 与 Bedroom pop。"
            kw = "吉他和弦库,吉他指法大全,风格和弦,爵士和弦,盯鞋和弦,数学摇滚和弦,add9"
            h1 = "吉他和弦风格指法库"
            lead = f"11 种音乐风格、5 种调弦、{total_voicings} 个经过校对的可弹吉他指法。所有和弦均可在线试听。"
            crumb_home, crumb_cur = "首页", "和弦库"
        else:
            title = "Guitar Chords by Genre — 11 Styles & 222 Playable Voicings | add9"
            desc = "Browse 222 curated guitar chord voicings across 11 genres: Math rock, Shoegaze, Neo-soul, Midwest emo, Jazz, J-pop, City pop, Bossa nova, Lo-fi, Jangle pop, and Bedroom pop."
            kw = "guitar chords by genre,guitar chord voicings chart,math rock chords,shoegaze chords,neo soul chords,jazz guitar voicings"
            h1 = "Guitar Chords by Genre"
            lead = f"11 curated music styles, 5 tunings, and {total_voicings} audited playable voicings—each with note labels and instant browser audio."
            crumb_home, crumb_cur = "Home", "Chords"

        crumb_ld = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": crumb_home, "item": f"{base_url}/zh/" if is_zh else f"{base_url}/"},
                {"@type": "ListItem", "position": 2, "name": crumb_cur, "item": canonical},
            ],
        }
        page_html = f"""{head_html(
            lang=lang,
            title=title,
            description=desc,
            keywords=kw,
            canonical_url=canonical,
            en_url=en_url,
            zh_url=zh_url,
            rel_root=rel_root,
            base_url=base_url,
            json_ld_list=[crumb_ld],
        )}
<body>
{header_html(lang, rel_root, switch_href, active="chords")}
<main>
  <section class="genre-hero">
    <div class="wrap">
      <ol class="breadcrumb">
        <li><a href="{home_href}">{crumb_home}</a></li>
        <li aria-current="page">{crumb_cur}</li>
      </ol>
      <h1>{esc(h1)}</h1>
      <p class="hero-lead">{esc(lead)}</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      {render_genre_list(is_zh, "")}
    </div>
  </section>
</main>
{footer_html(lang, rel_root, switch_href)}"""
        write_page("zh/chords/index.html" if is_zh else "chords/index.html", page_html)

    sitemap_entries.append((f"{base_url}/chords/", f"{base_url}/zh/chords/", "0.9"))

    # 3. 11 Genre Chord Pages (EN + ZH = 22 pages)
    for sid in STYLE_ORDER:
        style = styles_by_id[sid]
        slug = STYLE_SLUGS[sid]
        seo = GENRE_SEO[sid]
        fams = families_by_style[sid]
        en_url = f"{base_url}/chords/{slug}/"
        zh_url = f"{base_url}/zh/chords/{slug}/"
        sitemap_entries.append((en_url, zh_url, "0.85"))

        # Pick 4 neighboring genres for internal cross-linking
        idx = STYLE_ORDER.index(sid)
        related_ids = [STYLE_ORDER[(idx + offset) % len(STYLE_ORDER)] for offset in (1, 2, 3, 4)]

        for is_zh in (False, True):
            lang = "zh-Hans" if is_zh else "en"
            rel_root = "../../../" if is_zh else "../../"
            canonical = zh_url if is_zh else en_url
            switch_href = f"../../../chords/{slug}/" if is_zh else f"../../zh/chords/{slug}/"
            store_url = APP_STORE_CN if is_zh else APP_STORE_US
            home_href = "../../" if is_zh else "../../"
            chords_href = "../"

            style_name = zh_text(style["name"]) if is_zh else style["name"]
            style_summary = zh_text(style["summary"]) if is_zh else style["summary"]
            title = seo["zh_title"] if is_zh else seo["en_title"]
            h1 = seo["zh_h1"] if is_zh else seo["en_h1"]
            desc = seo["zh_desc"] if is_zh else seo["en_desc"]
            kw = seo["zh_kw"] if is_zh else seo["en_kw"]
            faqs = seo["zh_faq"] if is_zh else seo["en_faq"]

            tuning_pills = "".join(
                f'<span class="tag">{esc(zh_text(tunings_by_id[tid]["name"]) if is_zh else tunings_by_id[tid]["name"])}</span>'
                for tid in style["tuningIDs"]
            )

            family_blocks = []
            for fam in fams:
                tid = fam["tuningID"]
                tuning = tunings_by_id[tid]
                t_name = zh_text(tuning["name"]) if is_zh else tuning["name"]
                f_name = zh_text(fam["name"]) if is_zh else fam["name"]
                f_desc = fam["description"]

                cards = []
                for v in fam["voicings"]:
                    cname = chord_display_name(v["root"], v["quality"])
                    frets = v["frets"]
                    fcode = fret_code(frets)
                    midis = ",".join(str(m) for m in sounding_midis(frets, tuning["midiNotes"]))
                    movable = v.get("audit", {}).get("movable", False)
                    move_lbl = ("可移动" if movable else "固定把位") if is_zh else ("Movable" if movable else "Fixed")
                    svg = render_fretboard_svg(frets, tuning["midiNotes"], v["root"])
                    play_lbl = f"试听 {cname}" if is_zh else f"Play {cname}"
                    cards.append(
                        f"""<article class="voicing-card">
  <div class="voicing-top">
    <span class="voicing-name">{esc(cname)}</span>
    <button type="button" class="voicing-play" data-midi="{midis}" aria-label="{esc(play_lbl)}" title="{esc(play_lbl)}">{PLAY_SVG}</button>
  </div>
  <div class="voicing-svg">{svg}</div>
  <div class="voicing-foot">
    <span>{esc(fcode)}</span>
    <span>{move_lbl}</span>
  </div>
</article>"""
                    )
                desc_html = f'<p class="family-desc">{esc(f_desc)}</p>' if not is_zh else ""
                family_blocks.append(
                    f"""<section class="family-block">
  <div class="family-head">
    <div>
      <h2>{esc(f_name)}</h2>
      {desc_html}
    </div>
    <span class="tag">{esc(t_name)}</span>
  </div>
  <div class="voicing-grid">{"".join(cards)}</div>
</section>"""
                )

            faq_html = "".join(
                f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>'
                for q, a in faqs
            )

            related_html = "".join(
                f"""<a class="genre-row" href="../{STYLE_SLUGS[rid]}/">
  <div class="genre-row-top">
    <h3>{esc(zh_text(styles_by_id[rid]["name"]) if is_zh else styles_by_id[rid]["name"])}</h3>
    <span class="genre-count">{sum(len(f["voicings"]) for f in families_by_style[rid])} {'个指法' if is_zh else 'voicings'}</span>
  </div>
  <p>{esc(zh_text(styles_by_id[rid]["summary"]) if is_zh else styles_by_id[rid]["summary"])}</p>
</a>"""
                for rid in related_ids
            )

            crumb_home = "首页" if is_zh else "Home"
            crumb_chords = "和弦库" if is_zh else "Chords"

            ld_list = [
                {
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": crumb_home, "item": f"{base_url}/zh/" if is_zh else f"{base_url}/"},
                        {"@type": "ListItem", "position": 2, "name": crumb_chords, "item": f"{base_url}/zh/chords/" if is_zh else f"{base_url}/chords/"},
                        {"@type": "ListItem", "position": 3, "name": style_name, "item": canonical},
                    ],
                },
                {
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a},
                        }
                        for q, a in faqs
                    ],
                },
            ]

            cta_h2 = f"在 add9 中离线上手全部{style_name}和弦" if is_zh else f"Play every {style_name} voicing offline in add9"
            cta_p = (
                "自由切换 12 个根音、0–12 品变调夹与和弦进行，在 iPhone 和 iPad 上无广告免费使用。"
                if is_zh
                else "Transpose across all 12 roots, add a capo from 0–12, save favorite fingerings, and build chord progressions offline on iPhone and iPad."
            )
            cta_btn = "免费下载 add9" if is_zh else "Download add9 Free"

            page_html = f"""{head_html(
                lang=lang,
                title=title,
                description=desc,
                keywords=kw,
                canonical_url=canonical,
                en_url=en_url,
                zh_url=zh_url,
                rel_root=rel_root,
                base_url=base_url,
                json_ld_list=ld_list,
            )}
<body>
{header_html(lang, rel_root, switch_href, active="chords")}
<main>
  <section class="genre-hero">
    <div class="wrap">
      <ol class="breadcrumb">
        <li><a href="{home_href}">{crumb_home}</a></li>
        <li><a href="{chords_href}">{crumb_chords}</a></li>
        <li aria-current="page">{esc(style_name)}</li>
      </ol>
      <h1>{esc(h1)}</h1>
      <p class="hero-lead">{esc(style_summary)}</p>
      <div class="tuning-bar">{tuning_pills}</div>
    </div>
  </section>

  <div class="wrap">
    {"".join(family_blocks)}
  </div>

  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <h2>{'常见问题' if is_zh else 'Frequently asked questions'}</h2>
      </div>
      <div class="faq-list">{faq_html}</div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="cta-band">
        <div>
          <h2>{esc(cta_h2)}</h2>
          <p>{esc(cta_p)}</p>
        </div>
        <a class="btn btn-primary" href="{store_url}" target="_blank" rel="noopener">{APPLE_SVG}<span>{cta_btn}</span></a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <h2>{'继续探索其他风格' if is_zh else 'Explore more genres'}</h2>
      </div>
      <div class="genre-list">{related_html}</div>
    </div>
  </section>
</main>
{footer_html(lang, rel_root, switch_href)}"""
            out_rel = f"zh/chords/{slug}/index.html" if is_zh else f"chords/{slug}/index.html"
            write_page(out_rel, page_html)

    # 4. Privacy Policy Pages: /privacy/ and /zh/privacy/ (sourced directly from README.md & privacy-zh.md!)
    en_priv_md = (repo_root / "README.md").read_text(encoding="utf-8")
    zh_priv_md = (repo_root / "privacy-zh.md").read_text(encoding="utf-8")

    for is_zh, md_body in ((False, en_priv_md), (True, zh_priv_md)):
        lang = "zh-Hans" if is_zh else "en"
        rel_root = "../../" if is_zh else "../"
        en_url = f"{base_url}/privacy/"
        zh_url = f"{base_url}/zh/privacy/"
        canonical = zh_url if is_zh else en_url
        switch_href = "../../privacy/" if is_zh else "../zh/privacy/"
        title = "add9 隐私政策" if is_zh else "add9 Privacy Policy"
        desc = (
            "add9 是一款离线吉他和弦工具，无账户、无广告、无跟踪，你的收藏和弦与和弦进行仅保存在本地设备。"
            if is_zh
            else "add9 is an offline guitar chord app with no accounts, no ads, and no tracking. Your saved chords and progressions stay on your device."
        )
        kw = "add9隐私政策,吉他和弦App隐私" if is_zh else "add9 privacy policy,offline guitar chord app"
        page_html = f"""{head_html(
            lang=lang,
            title=title,
            description=desc,
            keywords=kw,
            canonical_url=canonical,
            en_url=en_url,
            zh_url=zh_url,
            rel_root=rel_root,
            base_url=base_url,
            json_ld_list=[],
        )}
<body>
{header_html(lang, rel_root, switch_href, active="privacy")}
<main class="prose">
  <div class="wrap-narrow">
    {md_to_simple_html(md_body)}
  </div>
</main>
{footer_html(lang, rel_root, switch_href)}"""
        write_page("zh/privacy/index.html" if is_zh else "privacy/index.html", page_html)

    sitemap_entries.append((f"{base_url}/privacy/", f"{base_url}/zh/privacy/", "0.4"))

    # 5. 404.html
    not_found_html = f"""{head_html(
        lang="en",
        title="Page Not Found — add9",
        description="The page you requested could not be found on add9.",
        keywords="add9",
        canonical_url=f"{base_url}/404.html",
        en_url=f"{base_url}/",
        zh_url=f"{base_url}/zh/",
        rel_root="./",
        base_url=base_url,
        json_ld_list=[],
    )}
<body>
<main class="prose">
  <div class="wrap-narrow">
    <h1>Page not found</h1>
    <p>That page does not exist. Head back to the chord library in English or Simplified Chinese.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="{base_url}/">English Home</a>
      <a class="btn btn-secondary" href="{base_url}/zh/">简体中文首页</a>
    </div>
  </div>
</main>
</body>
</html>"""
    write_page("404.html", not_found_html)

    # 6. sitemap.xml (with hreflang xhtml:link alternates for Google, Bing, and Baidu)
    url_blocks = []
    for en_u, zh_u, prio in sitemap_entries:
        for loc_u in (en_u, zh_u):
            url_blocks.append(
                f"""  <url>
    <loc>{esc(loc_u)}</loc>
    <lastmod>{TODAY}</lastmod>
    <priority>{prio}</priority>
    <xhtml:link rel="alternate" hreflang="en" href="{esc(en_u)}"/>
    <xhtml:link rel="alternate" hreflang="zh-Hans" href="{esc(zh_u)}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{esc(en_u)}"/>
  </url>"""
            )
    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(url_blocks)
        + "\n</urlset>\n"
    )
    write_page("sitemap.xml", sitemap_xml)

    # 7. robots.txt (explicitly welcoming Googlebot, Bingbot, and Baiduspider)
    robots_txt = f"""User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Baiduspider
Allow: /

User-agent: *
Allow: /
Disallow: /scripts/

Sitemap: {base_url}/sitemap.xml
"""
    write_page("robots.txt", robots_txt)

    print(f"Built {len(sitemap_entries) * 2} bilingual pages + 404.html + sitemap.xml + robots.txt for {base_url}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="https://jarvisrr.github.io/add9.com",
        help="Canonical site base URL (no trailing slash)",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    alt_chord_root = repo_root.parent / "alternative-chord"
    build_site(repo_root, alt_chord_root, args.base_url)


if __name__ == "__main__":
    main()
