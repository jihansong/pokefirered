#!/usr/bin/env python3
"""Make the next walkthrough docx from the previous one and a markdown chapter.

    python3 tools/make_walkthrough_docx.py \
        docs/Thunder_Yellow_Walkthrough_v0.8.0.docx docs/v0.9.0-chapter.md 0.9.0 \
        -o docs/Thunder_Yellow_Walkthrough_v0.9.0.docx

The chapter is inserted before the "알아두면 좋은 점" chapter (--before), which
is renumbered +1. Everything is copied from the old document's own XML so the
new chapter looks like the ones before it:

  # N. title        Heading1 (N becomes the tips chapter's number; " (vX)" added)
  ## N.m title      Heading2          ### title   Heading3
  | a | b |         table: C8A415 header row, F3F1E7 striped rows, 60/90 margins
  - item / "  - "   ListParagraph bullets, levels 0 and 1
  ![caption](path)  picture (path relative to the markdown) and italic caption
  **bold**          bold run; `code` loses its backticks
  <!-- ... -->      left out

A ### section made only of "- **label**: text" bullets becomes an event table
(항목 | 내용) like the v0.8.0 chapter; unlabeled bullets go in a 참고 row and
sub-bullets become extra lines of the row above. --no-event-tables keeps them
as bullets.

Also updated: the cover version line and summary line, a new row in the
version table and in the event index, the "v0.1.0~vX" save-compatibility lines
of chapter 1 and the tips chapter (X = the previous version), and the title in
docProps/core.xml. The rows come from a <!-- walkthrough ... --> block in the
markdown (subtitle:, summary: or summary-add:, version-row: per line,
index-row: place | events); the options of the same names override it.
"""

import argparse
import datetime
import os
import re
import struct
import sys
import zipfile
from xml.dom import minidom

FONT = ('<w:rFonts w:ascii="Malgun Gothic" w:cs="Malgun Gothic" '
        'w:eastAsia="Malgun Gothic" w:hAnsi="Malgun Gothic"/>')
TCMAR = ('<w:tcMar><w:top w:type="dxa" w:w="60"/><w:left w:type="dxa" w:w="90"/>'
         '<w:bottom w:type="dxa" w:w="60"/><w:right w:type="dxa" w:w="90"/></w:tcMar>')
TBLPR = ('<w:tblPr><w:tblW w:type="dxa" w:w="9360"/><w:tblBorders>'
         '<w:top w:val="single" w:color="auto" w:sz="4"/>'
         '<w:left w:val="single" w:color="auto" w:sz="4"/>'
         '<w:bottom w:val="single" w:color="auto" w:sz="4"/>'
         '<w:right w:val="single" w:color="auto" w:sz="4"/>'
         '<w:insideH w:val="single" w:color="auto" w:sz="4"/>'
         '<w:insideV w:val="single" w:color="auto" w:sz="4"/>'
         '</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr>')
TABLE_W = 9360
HEAD_FILL = 'C8A415'
STRIPE_FILL = 'F3F1E7'
IMG_W = 3657600  # EMU, 4 in: what the older chapters use for a 240x160 shot
REL_IMAGE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'


# ---------------------------------------------------------------- XML pieces

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rpr(size, bold=False, italic=False, color=None):
    s = FONT
    if bold:
        s += '<w:b/><w:bCs/>'
    if italic:
        s += '<w:i/><w:iCs/>'
    if color:
        s += '<w:color w:val="%s"/>' % color
    return '<w:rPr>%s<w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr>' % (s, size, size)


def run(text, size, bold=False, italic=False, color=None):
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (
        rpr(size, bold, italic, color), esc(text))


def inline_runs(text, size, bold=False, color=None):
    """**bold** spans become bold runs; `code` just loses its backticks."""
    text = text.replace('`', '')
    out = []
    for i, part in enumerate(re.split(r'\*\*', text)):
        if part:
            out.append(run(part, size, bold or i % 2 == 1, color=color))
    return ''.join(out) or run('', size, bold, color=color)


def para(text, ppr='<w:spacing w:after="120" w:line="300"/>', size=21):
    return '<w:p><w:pPr>%s</w:pPr>%s</w:p>' % (ppr, inline_runs(text, size))


def heading(level, text):
    before, color, size = {1: (360, '2F3640', 30), 2: (260, '55606E', 24),
                           3: (260, '55606E', 24)}[level]
    return ('<w:p><w:pPr><w:pStyle w:val="Heading%d"/><w:spacing w:after="140" '
            'w:before="%d"/></w:pPr>%s</w:p>'
            % (level, before, run(text.replace('`', '').replace('**', ''),
                                  size, True, color=color)))


def bullet(text, level):
    # The book's bullet list (numId 2) has one level; a sub-item is the same
    # bullet indented one step further.
    ind = '<w:ind w:left="720" w:hanging="240"/>' if level else ''
    return ('<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/>'
            '<w:numId w:val="2"/></w:numPr><w:spacing w:after="80" w:line="300"/>%s</w:pPr>'
            '%s</w:p>' % (ind, inline_runs(text, 21)))


def blank():
    return para('')


def cell(width, paras, header=False, stripe=False):
    fill = HEAD_FILL if header else (STRIPE_FILL if stripe else None)
    tcpr = '<w:tcW w:type="dxa" w:w="%d"/>' % width
    if fill:
        tcpr += '<w:shd w:fill="%s" w:val="clear"/>' % fill
    ps = []
    for i, text in enumerate(paras):
        last = i == len(paras) - 1
        if header:
            ppr = '<w:spacing w:after="0"/>'
            runs = inline_runs(text, 19, bold=True, color='20242B')
        else:
            ppr = '<w:spacing w:after="%d" w:line="280"/>' % (0 if last else 60)
            runs = inline_runs(text, 19)
        ps.append('<w:p><w:pPr>%s</w:pPr>%s</w:p>' % (ppr, runs))
    return '<w:tc><w:tcPr>%s%s</w:tcPr>%s</w:tc>' % (tcpr, TCMAR, ''.join(ps))


def row(widths, cells, header=False, stripe=False):
    """cells: one list of paragraphs per column."""
    trpr = '<w:trPr><w:tblHeader/></w:trPr>' if header else ''
    return '<w:tr>%s%s</w:tr>' % (trpr, ''.join(
        cell(w, c, header, stripe) for w, c in zip(widths, cells)))


def table(widths, head, rows):
    grid = ''.join('<w:gridCol w:w="%d"/>' % w for w in widths)
    body = row(widths, [[h] for h in head], header=True)
    for i, r in enumerate(rows):
        body += row(widths, r, stripe=i % 2 == 1)
    return '<w:tbl>%s<w:tblGrid>%s</w:tblGrid>%s</w:tbl>' % (TBLPR, grid, body)


def text_width(s):
    s = re.sub(r'\*\*|`', '', s)
    return sum(2 if ord(c) > 0x2e7f else 1 for c in s)


def column_widths(head, rows):
    """Each column gets at least its longest word, then the rest of the
    width goes where the text is longest (about 120 dxa per half-width char
    at 9.5 pt, 260 for the cell margins)."""
    ncol = len(head)
    cols = [[head[c]] + [p for r in rows for p in r[c]] for c in range(ncol)]
    least = [max(text_width(w) for t in col for w in (t.split() or [''])) * 120 + 260
             for col in cols]
    want = [max(text_width(t) for t in col) * 120 + 260 for col in cols]
    spare = TABLE_W - sum(least)
    extra = [w - l for w, l in zip(want, least)]
    if spare > 0 and sum(extra):
        least = [l + spare * e // sum(extra) for l, e in zip(least, extra)]
    widths = [TABLE_W * l // sum(least) for l in least]
    widths[-1] += TABLE_W - sum(widths)
    return widths


def picture(path, caption, pic_id, rid):
    with open(path, 'rb') as f:
        head = f.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        sys.exit('%s: only PNG pictures are supported' % path)
    w, h = struct.unpack('>II', head[16:24])
    cx, cy = IMG_W, IMG_W * h // w
    name = 'pic_%d.png' % pic_id
    a = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    pic = 'http://schemas.openxmlformats.org/drawingml/2006/picture'
    drawing = (
        '<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="%d" cy="%d"/><wp:docPr id="%d" name="%s" descr="%s"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="%s" noChangeAspect="1"/>'
        '</wp:cNvGraphicFramePr><a:graphic xmlns:a="%s"><a:graphicData uri="%s">'
        '<pic:pic xmlns:pic="%s"><pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/>'
        '</pic:nvPicPr><pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/>'
        '</a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        '<a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        '</pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing>'
        % (cx, cy, pic_id, name, esc(caption), a, a, pic, pic, pic_id, name, rid, cx, cy))
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60"/>'
            '<w:jc w:val="center"/></w:pPr><w:r>%s</w:r></w:p>' % drawing
            + '<w:p><w:pPr><w:spacing w:after="200"/><w:jc w:val="center"/></w:pPr>%s</w:p>'
            % run(caption, 18, italic=True, color='55606E'))


# ---------------------------------------------------------------- markdown

def parse_markdown(src):
    """Returns (settings, blocks). Blocks: ('h', level, text), ('p', text),
    ('li', level, text), ('table', head, rows), ('img', caption, path)."""
    settings = {}
    for m in re.finditer(r'<!--\s*walkthrough\s*\n(.*?)-->', src, re.S):
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                settings.setdefault(k.strip(), []).append(v.strip())
    src = re.sub(r'<!--.*?-->', '', src, flags=re.S)

    blocks = []
    lines = src.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r'(#{1,3}) +(.*)', line)
        if m:
            blocks.append(('h', len(m.group(1)), m.group(2).strip()))
            i += 1
            continue
        m = re.match(r'!\[(.*)\]\((.*)\)\s*$', line.strip())
        if m:
            blocks.append(('img', m.group(1), m.group(2)))
            i += 1
            continue
        if line.lstrip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(('table', rows[0], [[[c] for c in r] for r in rows[1:]]))
            continue
        m = re.match(r'( *)- +(.*)', line)
        if m:
            text = m.group(2)
            i += 1
            while (i < len(lines) and lines[i].strip() and not re.match(r' *- ', lines[i])
                   and not lines[i].lstrip().startswith(('|', '#', '!['))):
                text += ' ' + lines[i].strip()
                i += 1
            blocks.append(('li', min(len(m.group(1)) // 2, 1), text))
            continue
        text = line.strip()
        i += 1
        while (i < len(lines) and lines[i].strip()
               and not re.match(r'(#{1,3} | *- |\||!\[)', lines[i].lstrip())):
            text += ' ' + lines[i].strip()
            i += 1
        blocks.append(('p', text))
    return settings, blocks


def event_tables(blocks):
    """### sections of "- **label**: text" bullets become 항목|내용 tables."""
    out = []
    i = 0
    while i < len(blocks):
        out.append(blocks[i])
        if blocks[i][0] != 'h' or blocks[i][1] != 3:
            i += 1
            continue
        j = i + 1
        while j < len(blocks) and blocks[j][0] in ('li', 'img'):
            j += 1
        items = [b for b in blocks[i + 1:j] if b[0] == 'li']
        labeled = [b for b in items if b[1] == 0 and re.match(r'\*\*[^*]+\*\*:', b[2])]
        if not labeled or (j < len(blocks) and blocks[j][0] != 'h'):
            i += 1
            continue
        rows = []
        for b in items:
            m = re.match(r'\*\*([^*]+)\*\*: *(.*)', b[2])
            if b[1] == 0 and m:
                rows.append([[m.group(1)], [m.group(2)]])
            elif b[1] == 0:
                if rows and rows[-1][0] == ['참고']:
                    rows[-1][1].append(b[2])
                else:
                    rows.append([['참고'], [b[2]]])
            else:
                rows[-1][1].append('· ' + b[2])
        label_w = max(1200, max(text_width(r[0][0]) for r in rows) * 190 + 240)
        out.append(('table', ['항목', '내용'], rows, [label_w, TABLE_W - label_w]))
        out.extend(b for b in blocks[i + 1:j] if b[0] == 'img')
        i = j
    return out


# ---------------------------------------------------------------- document

def split_body(doc):
    """Top-level <w:p>/<w:tbl>/<w:sectPr> elements of <w:body>, as strings."""
    start = doc.index('<w:body>') + len('<w:body>')
    end = doc.rindex('</w:body>')
    body = doc[start:end]
    elems = []
    pos = 0
    tag_re = re.compile(r'<(/?)(w:p|w:tbl|w:sectPr)(?=[ >/])[^>]*?(/?)>')
    depth = 0
    for m in tag_re.finditer(body):
        closing, selfclosing = m.group(1), m.group(3)
        if depth == 0:
            begin = m.start()
        if selfclosing:
            pass
        elif closing:
            depth -= 1
        else:
            depth += 1
        if depth == 0:
            elems.append(body[begin:m.end()])
            pos = m.end()
    assert not body[pos:].strip(), 'unparsed tail in <w:body>'
    return doc[:start], elems, doc[end:]


def plain(x):
    return ''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)', x))


def set_text(x, old, new):
    """Replace text inside a paragraph's <w:t> runs (must sit in one run)."""
    n = x.count('>%s' % esc(old))
    if not n:
        raise SystemExit('cannot find %r in %r' % (old, plain(x)))
    return x.replace('>%s' % esc(old), '>%s' % esc(new))


def append_row(tbl, cells):
    rows = re.findall(r'<w:tr>.*?</w:tr>', tbl, re.S)
    widths = [int(w) for w in re.findall(r'<w:gridCol w:w="(\d+)"/>', tbl)]
    stripe = STRIPE_FILL not in rows[-1]
    return tbl.replace('</w:tbl>', row(widths, cells, stripe=stripe) + '</w:tbl>')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('old_docx')
    ap.add_argument('chapter_md')
    ap.add_argument('version', help='new version, e.g. 0.9.0')
    ap.add_argument('-o', '--output', required=True)
    ap.add_argument('--before', default='알아두면 좋은 점',
                    help='title of the Heading1 chapter the new one goes before')
    ap.add_argument('--subtitle', help='cover line after "버전 vX —"')
    ap.add_argument('--summary', help='whole cover summary line')
    ap.add_argument('--summary-add', help='appended to the cover summary line')
    ap.add_argument('--version-row', action='append',
                    help='paragraph of the new version-table row (repeatable)')
    ap.add_argument('--index-row', action='append',
                    help='"place | events" row for the event index (repeatable)')
    ap.add_argument('--no-event-tables', action='store_true')
    args = ap.parse_args()

    ver = args.version.lstrip('v')
    md_dir = os.path.dirname(os.path.abspath(args.chapter_md))
    with open(args.chapter_md, encoding='utf-8') as f:
        settings, blocks = parse_markdown(f.read())

    def opt(name, cli):
        if cli is not None:
            return cli
        return settings.get(name)

    subtitle = opt('subtitle', args.subtitle)
    summary = opt('summary', args.summary)
    summary_add = opt('summary-add', args.summary_add)
    version_row = opt('version-row', args.version_row)
    index_rows = opt('index-row', args.index_row)
    one = lambda v: v[0] if isinstance(v, list) else v

    zin = zipfile.ZipFile(args.old_docx)
    doc = zin.read('word/document.xml').decode('utf-8')
    rels = zin.read('word/_rels/document.xml.rels').decode('utf-8')
    core = zin.read('docProps/core.xml').decode('utf-8')

    old_ver = re.search(r'Thunder Yellow 공략집 v([\d.]+)', core).group(1)
    head, elems, tail = split_body(doc)

    # the chapter the new one goes before, and its number
    tips = next(i for i, x in enumerate(elems)
                if 'w:val="Heading1"' in x and re.match(r'\d+\. ' + re.escape(args.before),
                                                        plain(x)))
    num = int(re.match(r'(\d+)\.', plain(elems[tips])).group(1))
    elems[tips] = set_text(elems[tips], '%d. %s' % (num, args.before),
                           '%d. %s' % (num + 1, args.before))

    # new chapter XML
    if not args.no_event_tables:
        blocks = event_tables(blocks)
    pic_base = (max([int(n) for n in re.findall(r'docPr id="(\d+)"', doc)] + [0]) // 100 + 1) * 100
    rid_next = max(int(n) for n in re.findall(r'Id="rId(\d+)"', rels)) + 1
    media, new_rels = [], []
    out = []
    for b in blocks:
        kind = b[0]
        if kind == 'h':
            text = b[2]
            if b[1] == 1:
                text = re.sub(r'^\d+\.', '%d.' % num, text)
                if '(v' not in text:
                    text += ' (v%s)' % ver
            elif b[1] == 2:
                text = re.sub(r'^\d+\.(\d+)', r'%d.\1' % num, text)
            out.append(heading(b[1], text))
        elif kind == 'p':
            out.append(para(b[1]))
        elif kind == 'li':
            out.append(bullet(b[2], b[1]))
        elif kind == 'table':
            widths = b[3] if len(b) > 3 else column_widths(b[1], b[2])
            out.append(table(widths, b[1], b[2]))
            out.append(blank())
        elif kind == 'img':
            path = os.path.join(md_dir, b[2])
            if not os.path.exists(path):
                path = b[2]
            pic_id = pic_base + len(media)
            rid = 'rId%d' % (rid_next + len(media))
            target = 'media/v%s_%d.png' % (ver.replace('.', ''), pic_id)
            media.append((target, path))
            new_rels.append('<Relationship Id="%s" Type="%s" Target="%s"/>'
                            % (rid, REL_IMAGE, target))
            out.append(picture(path, b[1], pic_id, rid).replace(
                'pic_%d.png' % pic_id, os.path.basename(target)))
    if not any(b[0] == 'p' and b[1].startswith('세이브 호환') for b in blocks):
        out.append(para('세이브 호환: v0.1.0~v%s 세이브를 그대로 이어서 할 수 있습니다.' % old_ver))
    elems[tips:tips] = out

    # cover: version line and summary line (before the first Heading1, 목차)
    first_h1 = next(i for i, x in enumerate(elems) if 'w:val="Heading1"' in x)
    for i in range(first_h1):
        t = plain(elems[i])
        if t.startswith('버전 v'):
            new = '버전 v%s' % ver + (' — %s' % one(subtitle) if subtitle else
                                     t[len('버전 v' + old_ver):])
            elems[i] = set_text(elems[i], t, new)
        elif t.startswith('v0.1.0 ') and (summary or summary_add):
            new = one(summary) if summary else t + ' · ' + one(summary_add)
            elems[i] = set_text(elems[i], t, new)

    # save compatibility: chapter 1's line and the tips chapter's first bullet
    tips = elems.index(next(x for x in elems[tips:] if 'w:val="Heading1"' in x
                            and args.before in plain(x)))
    compat = re.compile(r'v0\.1\.0~v\d+\.\d+\.(?:\d+|x)')
    ch1 = next(i for i, x in enumerate(elems)
               if 'w:val="Heading1"' in x and plain(x).startswith('1. '))
    ch2 = next(i for i in range(ch1 + 1, len(elems)) if 'w:val="Heading1"' in elems[i])
    targets = [i for i in range(ch1, ch2) if '세이브 호환' in plain(elems[i])]
    targets += [i for i in range(tips + 1, len(elems))
                if 'ListParagraph' in elems[i] and compat.search(plain(elems[i]))][:1]
    for i in targets:
        elems[i] = compat.sub('v0.1.0~v%s' % old_ver, elems[i])

    # version table (the one whose header is 버전 | 추가된 것) and event index
    for i, x in enumerate(elems):
        if not x.startswith('<w:tbl>'):
            continue
        hdr = [plain(c) for c in re.findall(r'<w:tc>.*?</w:tc>',
                                           re.search(r'<w:tr>.*?</w:tr>', x, re.S).group(0), re.S)]
        if hdr == ['버전', '추가된 것'] and version_row:
            elems[i] = append_row(x, [['v' + ver], version_row])
        elif hdr == ['장소', '이벤트'] and index_rows:
            for r in index_rows:
                place, events = [s.strip() for s in r.split('|', 1)]
                elems[i] = append_row(elems[i], [[place], [events]])

    doc = head + ''.join(elems) + tail
    rels = rels.replace('</Relationships>', ''.join(new_rels) + '</Relationships>')
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    core = core.replace('공략집 v%s' % old_ver, '공략집 v%s' % ver)
    core = re.sub(r'(<dcterms:modified[^>]*>)[^<]*', r'\g<1>' + now, core)

    for name, data in (('document.xml', doc), ('rels', rels), ('core.xml', core)):
        minidom.parseString(data.encode('utf-8'))  # fail here, not in Word

    tmp = args.output + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == 'word/document.xml':
                data = doc.encode('utf-8')
            elif item.filename == 'word/_rels/document.xml.rels':
                data = rels.encode('utf-8')
            elif item.filename == 'docProps/core.xml':
                data = core.encode('utf-8')
            else:
                data = zin.read(item.filename)
            zout.writestr(item, data)
        for target, path in media:
            with open(path, 'rb') as f:
                zout.writestr('word/' + target, f.read())
    os.replace(tmp, args.output)
    print('%s: chapter %d "%s" before %d. %s; %d pictures; v%s -> v%s'
          % (args.output, num, plain(out[0]), num + 1, args.before, len(media), old_ver, ver))


if __name__ == '__main__':
    main()
