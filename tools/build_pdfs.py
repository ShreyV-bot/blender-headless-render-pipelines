#!/usr/bin/env python3
"""Build the five method PDFs (docs/pdf/) from the Markdown guides (docs/method-*.md).

Requirements:  pip install reportlab   and the DejaVu fonts (DejaVuSans*.ttf, DejaVuSansMono*.ttf).
Font lookup:   $DEJAVU_DIR, tools/fonts/, then common system folders.
Usage:         python tools/build_pdfs.py
"""
import os, re, sys, textwrap
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Preformatted, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(DOCS, "pdf")

PDF_NAMES = {
    "method-1-gpu-only-eevee.md": "Method_1_GPU_Only_EEVEE.pdf",
    "method-2-cpu-capped-cycles.md": "Method_2_Low_RAM_Cycles.pdf",
    "method-3-parallel-eevee.md": "Method_3_Parallel_EEVEE.pdf",
    "method-4-hybrid-dual-engine.md": "Method_4_Hybrid_Dual_Engine.pdf",
    "method-5-universal-master-script.md": "Method_5_Universal_Master_Script.pdf",
}

NAVY = colors.HexColor("#1f2a44")
ORANGE = colors.HexColor("#e87d0d")
GREY = colors.HexColor("#5b6472")
CODE_BG = colors.HexColor("#f4f5f7")
LINE = colors.HexColor("#c9ced6")

# ------------------------------------------------------------------ fonts
def find_fonts():
    dirs = [os.environ.get("DEJAVU_DIR", ""), os.path.join(HERE, "fonts"),
            "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "/usr/share/fonts/TTF",
            "/Library/Fonts", os.path.expanduser("~/Library/Fonts"), "C:/Windows/Fonts"]
    for d in dirs:
        if d and os.path.exists(os.path.join(d, "DejaVuSans.ttf")):
            return d
    sys.exit("DejaVu fonts not found. Download them from https://dejavu-fonts.github.io/ and put the "
             ".ttf files in tools/fonts/ (or set DEJAVU_DIR).")

def register_fonts():
    d = find_fonts()
    for name, fn in [("DejaVuSans", "DejaVuSans.ttf"), ("DejaVuSans-Bold", "DejaVuSans-Bold.ttf"),
                     ("DejaVuSans-Oblique", "DejaVuSans-Oblique.ttf"),
                     ("DejaVuSans-BoldOblique", "DejaVuSans-BoldOblique.ttf"),
                     ("DejaVuSansMono", "DejaVuSansMono.ttf"), ("DejaVuSansMono-Bold", "DejaVuSansMono-Bold.ttf")]:
        pdfmetrics.registerFont(TTFont(name, os.path.join(d, fn)))
    pdfmetrics.registerFontFamily("DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold",
                                  italic="DejaVuSans-Oblique", boldItalic="DejaVuSans-BoldOblique")

# ------------------------------------------------------------------ styles
def make_styles():
    base = dict(fontName="DejaVuSans", fontSize=8.8, leading=12.4, textColor=colors.HexColor("#1b1f27"))
    S = {}
    S["p"] = ParagraphStyle("p", spaceAfter=5, **base)
    S["title"] = ParagraphStyle("title", fontName="DejaVuSans-Bold", fontSize=19, leading=23,
                                textColor=NAVY, spaceAfter=3)
    S["sub"] = ParagraphStyle("sub", fontName="DejaVuSans-Oblique", fontSize=9.6, leading=13,
                              textColor=GREY, spaceAfter=8)
    S["h2"] = ParagraphStyle("h2", fontName="DejaVuSans-Bold", fontSize=11.5, leading=15, textColor=colors.white,
                             backColor=NAVY, borderPadding=(3, 5, 3, 5), spaceBefore=14, spaceAfter=8,
                             keepWithNext=1)
    S["h3"] = ParagraphStyle("h3", fontName="DejaVuSans-Bold", fontSize=10, leading=13.5, textColor=ORANGE,
                             spaceBefore=9, spaceAfter=4, keepWithNext=1)
    S["li"] = ParagraphStyle("li", leftIndent=15, bulletIndent=4, spaceAfter=2.5, **base)
    S["cell"] = ParagraphStyle("cell", fontName="DejaVuSans", fontSize=7.5, leading=9.8)
    S["cellh"] = ParagraphStyle("cellh", fontName="DejaVuSans-Bold", fontSize=7.5, leading=9.8, textColor=colors.white)
    S["callout"] = ParagraphStyle("callout", fontName="DejaVuSans", fontSize=8, leading=11, textColor=colors.HexColor("#3a2a10"))
    S["code"] = ParagraphStyle("code", fontName="DejaVuSansMono", fontSize=7.3, leading=9.2)
    return S

# ------------------------------------------------------------------ inline markdown
def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline(text, header=False):
    codes = []
    def grab(m):
        codes.append(m.group(1)); return "\x00%d\x00" % (len(codes) - 1)
    t = re.sub(r"`([^`]+)`", grab, text)
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])", r"<i>\1</i>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", t)
    def back(m):
        if header:  # white text on the dark header row: no tinted background
            return '<font face="DejaVuSansMono" size="7.2" color="white">%s</font>' % esc(codes[int(m.group(1))])
        return '<font face="DejaVuSansMono" size="7.6" backColor="#eceff3">%s</font>' % esc(codes[int(m.group(1))])
    return re.sub(r"\x00(\d+)\x00", back, t)

def plain_len(s):
    return len(re.sub(r"[`*]", "", s))

# ------------------------------------------------------------------ markdown parsing
def parse(md):
    lines = md.splitlines()
    meta, blocks, i = {}, [], 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"<!--\s*(\w+):\s*(.*?)\s*-->", ln)
        if m:
            meta[m.group(1)] = m.group(2); i += 1; continue
        if ln.startswith("```"):
            j, code = i + 1, []
            while j < len(lines) and not lines[j].startswith("```"):
                code.append(lines[j]); j += 1
            blocks.append(("code", code)); i = j + 1; continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i]); i += 1
            blocks.append(("table", rows)); continue
        if ln.startswith(">"):
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i].lstrip(">").strip()); i += 1
            blocks.append(("callout", q)); continue
        m = re.match(r"(#{1,3}) (.*)", ln)
        if m:
            blocks.append(("h%d" % len(m.group(1)), m.group(2))); i += 1; continue
        if re.match(r"\s*[-*] ", ln):
            blocks.append(("li", ("•", re.sub(r"^\s*[-*] ", "", ln)))); i += 1; continue
        m = re.match(r"\s*(\d+)\. (.*)", ln)
        if m:
            blocks.append(("li", (m.group(1) + ".", m.group(2)))); i += 1; continue
        if ln.strip() == "---":
            blocks.append(("hr", None)); i += 1; continue
        if ln.strip() == "":
            i += 1; continue
        para = [ln.strip()]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"(```|\||>|#|\s*[-*] |\s*\d+\. |<!--)", lines[i]):
            para.append(lines[i].strip()); i += 1
        blocks.append(("p", " ".join(para)))
    return meta, blocks

# ------------------------------------------------------------------ flowables
CONTENT_W = A4[0] - 32 * mm
WRAP = 104

def wrap_code_line(line):
    if len(line) <= WRAP:
        return [line]
    indent = len(line) - len(line.lstrip())
    is_comment = line.lstrip().startswith("#")
    prefix = " " * indent + ("# " if is_comment else "    ")
    body = line.strip()[2:].strip() if is_comment else line.strip()
    chunks = textwrap.wrap(body, width=WRAP - len(prefix), break_long_words=True, break_on_hyphens=False)
    first = (" " * indent + ("# " if is_comment else "")) + chunks[0]
    return [first] + [prefix + c for c in chunks[1:]]

def code_flowable(code, S):
    out = []
    for ln in code:
        out.extend(wrap_code_line(ln.replace("\t", "    ")))
    # Split into ~10-line rows so long code can break across pages. Never cut next to a blank line:
    # Preformatted strips leading/trailing blank lines, which would swallow the spacing.
    chunks, cur = [], []
    for idx, ln in enumerate(out):
        cur.append(ln)
        nxt = out[idx + 1] if idx + 1 < len(out) else None
        if len(cur) >= 10 and ln.strip() and nxt is not None and nxt.strip():
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    chunks = chunks or [[""]]
    rows = [[Preformatted("\n".join(c), S["code"])] for c in chunks]
    t = Table(rows, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CODE_BG), ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                           ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (0, 0), 5), ("BOTTOMPADDING", (0, -1), (-1, -1), 5)]))
    return t

def table_flowable(rows, S):
    cells = []
    for r in rows:
        if re.match(r"^\|[\s:|-]+\|$", r.strip()):
            continue
        cells.append([c.strip() for c in r.strip().strip("|").split("|")])
    n = max(len(r) for r in cells)
    for r in cells:
        r += [""] * (n - len(r))
    weights = []
    for c in range(n):
        col = [row[c] for row in cells]
        avg = sum(plain_len(x) for x in col) / len(col)
        longest = max((len(w) for x in col for w in re.sub(r"[`*]", "", x).split()), default=4)
        weights.append(max(min(avg, 48), longest * 0.95, 7))
    total = sum(weights)
    widths = [max(w / total * CONTENT_W, 13 * mm) for w in weights]
    k = CONTENT_W / sum(widths)
    widths = [w * k for w in widths]
    data = []
    for ri, row in enumerate(cells):
        data.append([Paragraph(inline(x, header=(ri == 0)), S["cellh"] if ri == 0 else S["cell"]) for x in row])
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), 0.4, LINE),
          ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4),
          ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for ri in range(1, len(cells)):
        if ri % 2 == 0:
            st.append(("BACKGROUND", (0, ri), (-1, ri), colors.HexColor("#f6f7f9")))
    t.setStyle(TableStyle(st))
    return t

def callout_flowable(lines, S):
    paras = [Paragraph(inline(l), S["callout"]) for l in lines if l]
    t = Table([[paras]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff3e0")),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, ORANGE), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t

# ------------------------------------------------------------------ page furniture
class NumberedCanvas(canvas.Canvas):
    series = ""; footer = ""
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self._saved = []
    def showPage(self):
        self._saved.append(dict(self.__dict__)); self._startPage()
    def save(self):
        total = len(self._saved)
        for st in self._saved:
            self.__dict__.update(st); self._furniture(total); super().showPage()
        super().save()
    def _furniture(self, total):
        w, h = A4
        self.setFont("DejaVuSans-Bold", 6.8); self.setFillColor(ORANGE)
        self.drawString(16 * mm, h - 11 * mm, self.series)
        self.setStrokeColor(LINE); self.setLineWidth(0.5); self.line(16 * mm, h - 13 * mm, w - 16 * mm, h - 13 * mm)
        self.line(16 * mm, 13 * mm, w - 16 * mm, 13 * mm)
        self.setFont("DejaVuSans", 7); self.setFillColor(GREY)
        self.drawString(16 * mm, 9 * mm, self.footer)
        self.drawRightString(w - 16 * mm, 9 * mm, "Page %d of %d" % (self._pageNumber, total))

def build_pdf(md_path, pdf_path, S):
    meta, blocks = parse(open(md_path, encoding="utf-8").read())
    story, seen_title = [], False
    for kind, data in blocks:
        if kind == "h1":
            story.append(Paragraph(inline(data), S["title"])); seen_title = True
        elif kind == "p" and seen_title and len(story) == 1 and data.startswith("*") and data.endswith("*"):
            story.append(Paragraph(inline(data.strip("*")), S["sub"]))
            story.append(HRFlowable(width="100%", thickness=1.2, color=ORANGE, spaceAfter=8))
        elif kind == "p":
            story.append(Paragraph(inline(data), S["p"]))
        elif kind == "h2":
            story.append(Paragraph(inline(data), S["h2"]))
        elif kind == "h3":
            story.append(Paragraph(inline(data), S["h3"]))
        elif kind == "li":
            story.append(Paragraph(inline(data[1]), S["li"], bulletText=data[0]))
        elif kind == "code":
            story.append(code_flowable(data, S)); story.append(Spacer(1, 6))
        elif kind == "table":
            story.append(table_flowable(data, S)); story.append(Spacer(1, 7))
        elif kind == "callout":
            story.append(callout_flowable(data, S)); story.append(Spacer(1, 7))
        elif kind == "hr":
            story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=4, spaceAfter=6))
    NumberedCanvas.series = meta.get("series", ""); NumberedCanvas.footer = meta.get("footer", "")
    doc = BaseDocTemplate(pdf_path, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=20 * mm,
                          bottomMargin=17 * mm, title=re.sub(r"[`*]", "", next(d for k, d in blocks if k == "h1")),
                          author="Blender Headless Render Pipelines")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f", leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame])])
    doc.build(story, canvasmaker=NumberedCanvas)

def main():
    register_fonts()
    S = make_styles()
    os.makedirs(OUT, exist_ok=True)
    for md_name, pdf_name in PDF_NAMES.items():
        md_path = os.path.join(DOCS, md_name)
        if not os.path.exists(md_path):
            print("skip (missing):", md_name); continue
        build_pdf(md_path, os.path.join(OUT, pdf_name), S)
        print("built", pdf_name)

if __name__ == "__main__":
    main()
