"""성경 참조 인식·정규화 (한국어/영어 → USFM 코드, 예: ROM.8.28)."""
import re

# code, english, [english abbrs], korean full, korean abbr, testament
BOOKS = [
    ("GEN", "Genesis", ["Gen", "Gn"], "창세기", "창", "OT"),
    ("EXO", "Exodus", ["Exod", "Exo", "Ex"], "출애굽기", "출", "OT"),
    ("LEV", "Leviticus", ["Lev", "Lv"], "레위기", "레", "OT"),
    ("NUM", "Numbers", ["Num", "Nm"], "민수기", "민", "OT"),
    ("DEU", "Deuteronomy", ["Deut", "Dt"], "신명기", "신", "OT"),
    ("JOS", "Joshua", ["Josh", "Jos"], "여호수아", "수", "OT"),
    ("JDG", "Judges", ["Judg", "Jdg"], "사사기", "삿", "OT"),
    ("RUT", "Ruth", ["Ruth", "Ru"], "룻기", "룻", "OT"),
    ("1SA", "1 Samuel", ["1 Sam", "1Sam", "1 Sa"], "사무엘상", "삼상", "OT"),
    ("2SA", "2 Samuel", ["2 Sam", "2Sam", "2 Sa"], "사무엘하", "삼하", "OT"),
    ("1KI", "1 Kings", ["1 Kgs", "1Kgs", "1 Ki"], "열왕기상", "왕상", "OT"),
    ("2KI", "2 Kings", ["2 Kgs", "2Kgs", "2 Ki"], "열왕기하", "왕하", "OT"),
    ("1CH", "1 Chronicles", ["1 Chr", "1Chr"], "역대상", "대상", "OT"),
    ("2CH", "2 Chronicles", ["2 Chr", "2Chr"], "역대하", "대하", "OT"),
    ("EZR", "Ezra", ["Ezra", "Ezr"], "에스라", "스", "OT"),
    ("NEH", "Nehemiah", ["Neh"], "느헤미야", "느", "OT"),
    ("EST", "Esther", ["Esth", "Est"], "에스더", "에", "OT"),
    ("JOB", "Job", ["Job"], "욥기", "욥", "OT"),
    ("PSA", "Psalms", ["Psalm", "Ps", "Psa"], "시편", "시", "OT"),
    ("PRO", "Proverbs", ["Prov", "Pr"], "잠언", "잠", "OT"),
    ("ECC", "Ecclesiastes", ["Eccl", "Ecc"], "전도서", "전", "OT"),
    ("SNG", "Song of Songs", ["Song", "SoS"], "아가", "아", "OT"),
    ("ISA", "Isaiah", ["Isa", "Is"], "이사야", "사", "OT"),
    ("JER", "Jeremiah", ["Jer"], "예레미야", "렘", "OT"),
    ("LAM", "Lamentations", ["Lam"], "예레미야애가", "애", "OT"),
    ("EZK", "Ezekiel", ["Ezek", "Eze"], "에스겔", "겔", "OT"),
    ("DAN", "Daniel", ["Dan", "Dn"], "다니엘", "단", "OT"),
    ("HOS", "Hosea", ["Hos"], "호세아", "호", "OT"),
    ("JOL", "Joel", ["Joel"], "요엘", "욜", "OT"),
    ("AMO", "Amos", ["Amos", "Am"], "아모스", "암", "OT"),
    ("OBA", "Obadiah", ["Obad", "Ob"], "오바댜", "옵", "OT"),
    ("JON", "Jonah", ["Jonah", "Jon"], "요나", "욘", "OT"),
    ("MIC", "Micah", ["Mic"], "미가", "미", "OT"),
    ("NAM", "Nahum", ["Nah"], "나훔", "나", "OT"),
    ("HAB", "Habakkuk", ["Hab"], "하박국", "합", "OT"),
    ("ZEP", "Zephaniah", ["Zeph", "Zep"], "스바냐", "습", "OT"),
    ("HAG", "Haggai", ["Hag"], "학개", "학", "OT"),
    ("ZEC", "Zechariah", ["Zech", "Zec"], "스가랴", "슥", "OT"),
    ("MAL", "Malachi", ["Mal"], "말라기", "말", "OT"),
    ("MAT", "Matthew", ["Matt", "Mt"], "마태복음", "마", "NT"),
    ("MRK", "Mark", ["Mark", "Mk"], "마가복음", "막", "NT"),
    ("LUK", "Luke", ["Luke", "Lk"], "누가복음", "눅", "NT"),
    ("JHN", "John", ["John", "Jn"], "요한복음", "요", "NT"),
    ("ACT", "Acts", ["Acts", "Ac"], "사도행전", "행", "NT"),
    ("ROM", "Romans", ["Rom", "Ro"], "로마서", "롬", "NT"),
    ("1CO", "1 Corinthians", ["1 Cor", "1Cor"], "고린도전서", "고전", "NT"),
    ("2CO", "2 Corinthians", ["2 Cor", "2Cor"], "고린도후서", "고후", "NT"),
    ("GAL", "Galatians", ["Gal"], "갈라디아서", "갈", "NT"),
    ("EPH", "Ephesians", ["Eph"], "에베소서", "엡", "NT"),
    ("PHP", "Philippians", ["Phil", "Php"], "빌립보서", "빌", "NT"),
    ("COL", "Colossians", ["Col"], "골로새서", "골", "NT"),
    ("1TH", "1 Thessalonians", ["1 Thess", "1Thess"], "데살로니가전서", "살전", "NT"),
    ("2TH", "2 Thessalonians", ["2 Thess", "2Thess"], "데살로니가후서", "살후", "NT"),
    ("1TI", "1 Timothy", ["1 Tim", "1Tim"], "디모데전서", "딤전", "NT"),
    ("2TI", "2 Timothy", ["2 Tim", "2Tim"], "디모데후서", "딤후", "NT"),
    ("TIT", "Titus", ["Titus", "Tit"], "디도서", "딛", "NT"),
    ("PHM", "Philemon", ["Phlm", "Phm"], "빌레몬서", "몬", "NT"),
    ("HEB", "Hebrews", ["Heb"], "히브리서", "히", "NT"),
    ("JAS", "James", ["Jas"], "야고보서", "약", "NT"),
    ("1PE", "1 Peter", ["1 Pet", "1Pet"], "베드로전서", "벧전", "NT"),
    ("2PE", "2 Peter", ["2 Pet", "2Pet"], "베드로후서", "벧후", "NT"),
    ("1JN", "1 John", ["1 Jn", "1Jn"], "요한일서", "요일", "NT"),
    ("2JN", "2 John", ["2 Jn", "2Jn"], "요한이서", "요이", "NT"),
    ("3JN", "3 John", ["3 Jn", "3Jn"], "요한삼서", "요삼", "NT"),
    ("JUD", "Jude", ["Jude"], "유다서", "유", "NT"),
    ("REV", "Revelation", ["Rev", "Rv"], "요한계시록", "계", "NT"),
]

BY_CODE = {b[0]: b for b in BOOKS}
_NAME2CODE = {}
for code, en, abbrs, ko, koa, _ in BOOKS:
    for n in [en, ko, koa, *abbrs, code]:
        _NAME2CODE[n.lower().replace(".", "")] = code

_ko_names = sorted({n for b in BOOKS for n in (b[3], b[4])}, key=len, reverse=True)
_en_names = sorted({n for b in BOOKS for n in (b[1], *b[2])}, key=len, reverse=True)

# 한국어: 로마서 8장 28절 / 로마서 8:28 / 롬 8:28-30 / 롬8:28 / 로마서 8장
_KO = re.compile(
    r"(?<![가-힣A-Za-z])(" + "|".join(map(re.escape, _ko_names)) + r")\s?"
    r"(\d{1,3})(?:\s?(?:장|편)(?:\s?(\d{1,3})\s?절)?|:(\d{1,3}))"
    r"(?:\s?[-~–]\s?(\d{1,3})\s?절?)?"
)
# 영어: Romans 8:28 / Rom. 8:28-30 / 1 Cor 13:4
_EN = re.compile(
    r"(?<![A-Za-z])(" + "|".join(re.escape(n).replace(r"\ ", r"\s?") for n in _en_names) + r")\.?\s"
    r"(\d{1,3})(?::(\d{1,3}))?(?:\s?[-–]\s?(\d{1,3}))?(?![\d:])"
)


def code_for(name):
    return _NAME2CODE.get(re.sub(r"\s+", " ", name).lower().replace(".", "")) or \
        _NAME2CODE.get(re.sub(r"\s+", "", name).lower().replace(".", ""))


def _fmt(code, ch, v=None, v2=None):
    s = f"{code}.{int(ch)}"
    if v:
        s += f".{int(v)}"
        if v2 and int(v2) > int(v):
            s += f"-{int(v2)}"
    return s


def extract(text):
    """텍스트에서 성경 참조를 찾아 정규화된 코드 목록(순서 유지·중복 제거)을 반환."""
    out = []
    for m in _KO.finditer(text):
        code = code_for(m.group(1))
        if code:
            out.append((m.start(), _fmt(code, m.group(2), m.group(3) or m.group(4), m.group(5))))
    for m in _EN.finditer(text):
        code = code_for(m.group(1))
        if code and m.group(3):  # 영어는 장:절 형태만 인정(오탐 방지)
            out.append((m.start(), _fmt(code, m.group(2), m.group(3), m.group(4))))
    seen, refs = set(), []
    for _, r in sorted(out):
        if r not in seen:
            seen.add(r)
            refs.append(r)
    return refs


def korean_label(ref):
    """ROM.8.28 → '로마서 8장 28절' (Obsidian 노트 제목으로 사용)."""
    m = re.match(r"^([1-3]?[A-Z]{2,3})\.(\d+)(?:\.(\d+)(?:-(\d+))?)?$", ref)
    if not m or m.group(1) not in BY_CODE:
        return ref
    ko = BY_CODE[m.group(1)][3]
    s = f"{ko} {m.group(2)}" + ("편" if m.group(1) == "PSA" else "장")
    if m.group(3):
        s += f" {m.group(3)}절" if not m.group(4) else f" {m.group(3)}-{m.group(4)}절"
    return s


def parent_refs(ref):
    """ROM.8.28-30 → [ROM.8.28-30, ROM.8] (장 단위 상위 참조 포함)."""
    parts = ref.split(".")
    return [ref] + ([".".join(parts[:2])] if len(parts) > 2 else [])


def normalize_query(q):
    refs = extract(q)
    if refs:
        return refs
    c = q.strip().upper()
    return [c] if re.match(r"^[1-3]?[A-Z]{2,3}\.\d+(\.\d+(-\d+)?)?$", c) and c.split(".")[0] in BY_CODE else []
