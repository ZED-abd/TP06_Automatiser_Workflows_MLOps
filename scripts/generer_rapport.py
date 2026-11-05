"""Genere le rapport PDF a partir des sources Markdown et des captures reelles.

Dependance de mise en page : python -m pip install reportlab
Lancer depuis la racine du clone : python scripts/generer_rapport.py
"""

from html import escape, unescape
from pathlib import Path
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, NextPageTemplate, PageBreak, PageTemplate,
    Paragraph, Preformatted, Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'
OUTPUT = REPORTS / 'Abdelbaki_Zakaria_5IASDR_G6.pdf'
NAVY = colors.HexColor('#15334D')
TEAL = colors.HexColor('#087F8C')
PALE = colors.HexColor('#EEF5F8')
GREY = colors.HexColor('#566573')

font_dir = Path('C:/Windows/Fonts')
if (font_dir / 'arial.ttf').exists():
    for name, filename in [('Rapport', 'arial.ttf'), ('Rapport-Bold', 'arialbd.ttf'), ('Rapport-Italic', 'ariali.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
    pdfmetrics.registerFontFamily('Rapport', normal='Rapport', bold='Rapport-Bold', italic='Rapport-Italic', boldItalic='Rapport-Bold')
    FONT = 'Rapport'
    BOLD = 'Rapport-Bold'
else:
    FONT, BOLD = 'Helvetica', 'Helvetica-Bold'

styles = getSampleStyleSheet()
styles.add(ParagraphStyle('Texte', fontName=FONT, fontSize=9.5, leading=13, spaceAfter=6, textColor=NAVY, allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle('TitreRapport', parent=styles['Texte'], fontName=BOLD, fontSize=24, leading=29, spaceBefore=15, spaceAfter=16))
styles.add(ParagraphStyle('SectionRapport', parent=styles['Texte'], fontName=BOLD, fontSize=14, leading=18, spaceBefore=12, spaceAfter=8, keepWithNext=True, textColor=TEAL))
styles.add(ParagraphStyle('QuestionRapport', parent=styles['Texte'], fontName=BOLD, fontSize=11, leading=15, spaceBefore=10, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle('Cellule', parent=styles['Texte'], fontSize=8, leading=11, spaceAfter=0))
styles.add(ParagraphStyle('CelluleEntete', parent=styles['Cellule'], fontName=BOLD, textColor=colors.white))
styles.add(ParagraphStyle('TitreCapture', parent=styles['Texte'], fontName=BOLD, fontSize=14, leading=18, spaceAfter=8, textColor=TEAL))
styles.add(ParagraphStyle('Legende', parent=styles['Texte'], fontSize=8, leading=11, alignment=TA_CENTER, textColor=GREY))


def clean(text):
    return text.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')


def inline(text):
    text = escape(clean(text))
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<link href="{m[2]}" color="#087F8C">{m[1]}</link>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)
    return text


def footer(canvas, doc):
    width, height = canvas._pagesize
    canvas.saveState()
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(1.1)
    canvas.line(36, height - 27, width - 36, height - 27)
    canvas.setFont(FONT, 7)
    canvas.setFillColor(GREY)
    canvas.drawString(36, 22, 'TP06 | Abdelbaki Zakaria | 5IASDR-G6')
    canvas.drawRightString(width - 36, 22, str(doc.page))
    canvas.restoreState()


doc = BaseDocTemplate(str(OUTPUT), title='TP06 - Automatiser les workflows MLOps', author='Abdelbaki Zakaria',
                      subject='5IASDR-G6 - Prefect, DVC et GitHub Actions', leftMargin=42, rightMargin=42,
                      topMargin=40, bottomMargin=40)
portrait_width = A4[0] - 84
wide = landscape(A4)
doc.addPageTemplates([
    PageTemplate(id='texte', pagesize=A4, frames=[Frame(42, 40, portrait_width, A4[1] - 80, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=footer),
    PageTemplate(id='capture', pagesize=wide, frames=[Frame(36, 40, wide[0] - 72, wide[1] - 80, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=footer),
])

source = (REPORTS / 'rapport_tp6.md').read_text(encoding='utf-8')
synthesis = (REPORTS / 'tp6_synthese.md').read_text(encoding='utf-8')
synthesis = synthesis[synthesis.index('| Critère'):].replace('## Conclusion (5 lignes)', '### Conclusion (5 lignes)')
source = source.replace('Le tableau complet et la conclusion en cinq lignes figurent dans\n[tp6_synthese.md](tp6_synthese.md) et sont intégrés au PDF.', synthesis)
# Regrouper les captures en annexe evite des pages de texte presque vides.
body_lines = []
annexes = []
caption = None
for source_line in source.splitlines():
    if source_line.startswith('**Capture '):
        caption = source_line
    elif source_line.startswith('!['):
        annexes.append((caption, source_line))
        caption = None
    else:
        body_lines.append(source_line)
source = '\n'.join(body_lines) + '\n\n' + '\n\n'.join(
    (label + '\n\n' if label else '') + picture for label, picture in annexes
)
source = source.replace('## 1. Contexte et environnement',
    'Les captures réelles sont regroupées en annexe, après les réponses et la synthèse.\n\n## 1. Contexte et environnement')
lines = source.splitlines()
story = []
paragraph = []


def flush():
    if paragraph:
        story.append(Paragraph(inline(' '.join(paragraph)).replace('[[BR]]', '<br/>'), styles['Texte']))
        paragraph.clear()


index = 0
while index < len(lines):
    line = lines[index].strip()
    if not line:
        flush()
        index += 1
        continue
    if line.startswith('```'):
        flush()
        block = []
        index += 1
        while index < len(lines) and not lines[index].startswith('```'):
            block.extend(textwrap.wrap(clean(lines[index]), width=83, replace_whitespace=False, drop_whitespace=False) or [''])
            index += 1
        story.append(Preformatted('\n'.join(block), ParagraphStyle('CodeRapport', fontName='Courier', fontSize=8, leading=10, backColor=PALE, borderPadding=8, spaceBefore=6, spaceAfter=10)))
        index += 1
        continue
    image_match = re.fullmatch(r'!\[([^\]]+)\]\(([^)]+)\)', line)
    if image_match:
        flush()
        title = image_match.group(1)
        if story and isinstance(story[-1], Paragraph) and story[-1].text.startswith('<b>Capture '):
            title = unescape(re.sub('<[^>]+>', '', story.pop().text))
        # Deux captures consecutives n'ont pas besoin d'une page de texte vide.
        if len(story) >= 2 and isinstance(story[-1], PageBreak) and isinstance(story[-2], NextPageTemplate):
            story.pop()
            story.pop()
        story.extend([NextPageTemplate('capture'), PageBreak(), Paragraph(inline(title), styles['TitreCapture'])])
        image_path = REPORTS / image_match.group(2)
        picture = Image(str(image_path))
        scale = min((wide[0] - 72) / picture.imageWidth, 455 / picture.imageHeight)
        picture.drawWidth = picture.imageWidth * scale
        picture.drawHeight = picture.imageHeight * scale
        picture.hAlign = 'CENTER'
        story.extend([picture, Spacer(1, 6), Paragraph(inline('Capture réelle - ' + image_path.name), styles['Legende']), NextPageTemplate('texte'), PageBreak()])
        index += 1
        continue
    if line.startswith('|'):
        flush()
        rows = []
        while index < len(lines) and lines[index].strip().startswith('|'):
            row = [cell.strip() for cell in lines[index].strip().strip('|').split('|')]
            if not all(re.fullmatch(r'[: -]+', cell) for cell in row):
                rows.append(row)
            index += 1
        columns = len(rows[0])
        if columns == 3:
            widths = [portrait_width * .20, portrait_width * .40, portrait_width * .40]
        else:
            widths = [portrait_width / columns] * columns
        cells = [[Paragraph(inline(cell), styles['CelluleEntete' if row_no == 0 else 'Cellule']) for cell in row] for row_no, row in enumerate(rows)]
        table = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [PALE, colors.white]),
            ('GRID', (0, 0), (-1, -1), .4, colors.HexColor('#D4E0E5')),
            ('LEFTPADDING', (0, 0), (-1, -1), 7), ('RIGHTPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))
        story.extend([table, Spacer(1, 10)])
        continue
    heading = re.match(r'^(#{1,3}) (.+)$', line)
    if heading:
        flush()
        level = len(heading.group(1))
        if level == 2 and heading.group(2).startswith(('3.', '6.', '7.')):
            if not isinstance(story[-1], PageBreak):
                story.append(PageBreak())
        story.append(Paragraph(inline(heading.group(2)), styles[{1: 'TitreRapport', 2: 'SectionRapport', 3: 'QuestionRapport'}[level]]))
    elif line.startswith('- '):
        flush()
        bullet = line[2:]
        index += 1
        while index < len(lines) and lines[index].startswith('  '):
            bullet += ' ' + lines[index].strip()
            index += 1
        story.append(Paragraph(inline(bullet), styles['Texte'], bulletText='-'))
        continue
    else:
        paragraph.append(line + (' [[BR]]' if lines[index].endswith('  ') else ''))
    index += 1
flush()
while story and isinstance(story[-1], (PageBreak, NextPageTemplate)):
    story.pop()
doc.build(story)
print(OUTPUT)
