"""Produit les PDF et le ZIP v1.2 avec inventaire SHA-256 de son contenu."""
import hashlib
import html
import json
import pathlib
import re
import zipfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, Line, String

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'livrables'
OUT.mkdir(exist_ok=True)
data = json.loads((ROOT / 'donnees/arbre.json').read_text())
font_dir = pathlib.Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('Dossier', str(font_dir / 'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DossierBold', str(font_dir / 'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('Dossier', normal='Dossier', bold='DossierBold', italic='Dossier', boldItalic='DossierBold')
styles = getSampleStyleSheet()
for key in ['Normal', 'Title', 'Heading1', 'Heading2', 'Heading3']:
    styles[key].fontName = 'Dossier'
styles['Normal'].fontSize = 9
styles['Normal'].leading = 13
styles.add(ParagraphStyle(name='SmallDossier', parent=styles['Normal'], fontSize=7.2, leading=10))
styles.add(ParagraphStyle(name='CoverDossier', parent=styles['Title'], alignment=TA_CENTER, textColor=colors.HexColor('#173949')))

def para(text, style='Normal'):
    return Paragraph(html.escape(str(text)).replace('\n', '<br/>'), styles[style])

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Dossier', 7)
    canvas.setFillColor(colors.HexColor('#52606a'))
    canvas.drawString(40, 23, 'Maxime BLARET • v1.2 • état de recherche du 25 octobre 2026')
    canvas.drawRightString(A4[0] - 40, 23, str(doc.page))
    canvas.restoreState()

def pdf(name, flow):
    doc = SimpleDocTemplate(str(OUT / name), pagesize=A4, leftMargin=42, rightMargin=42, topMargin=42, bottomMargin=40)
    doc.build(flow, onFirstPage=footer, onLaterPages=footer)

def title(text):
    return [para(text, 'CoverDossier'), Spacer(1, 14), para('Version 1.2 — état de recherche, ascendance maternelle incomplète'), Spacer(1, 16)]

def markdown(path):
    # Rendu documentaire simple et lisible ; les URL restent imprimées.
    lines = path.read_text().splitlines()
    flow = []
    fenced = False
    for line in lines:
        if line.startswith('```'):
            fenced = not fenced
            continue
        if not line.strip():
            flow.append(Spacer(1, 6)); continue
        line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', line)
        line = line.replace('**', '').replace('`', '')
        if line.startswith('# '): flow.append(para(line[2:], 'Heading1'))
        elif line.startswith('## '): flow.append(para(line[3:], 'Heading2'))
        elif line.startswith('### '): flow.append(para(line[4:], 'Heading3'))
        else: flow.append(para(line, 'SmallDossier' if fenced or line.startswith('|') else 'Normal'))
    return flow

flow = title('Arbre généalogique de Maxime Blaret')
flow += [para('La branche paternelle de la v1.0 est conservée. L’extrait de naissance de Nathalie documente ses parents ; aucune génération antérieure supplémentaire n’est présentée comme établie.'), Spacer(1, 12)]
tree = Drawing(510, 285)
def box(x, y, lines):
    tree.add(Rect(x, y, 230, 57, rx=5, ry=5, fillColor=colors.HexColor('#edf4f5'), strokeColor=colors.HexColor('#355869')))
    for i, line in enumerate(lines):
        tree.add(String(x + 9, y + 41 - i * 14, line, fontName='Dossier', fontSize=8.5))
tree.add(Line(255, 217, 135, 167, strokeColor=colors.HexColor('#355869')))
tree.add(Line(255, 217, 375, 167, strokeColor=colors.HexColor('#355869')))
tree.add(Line(375, 110, 375, 72, strokeColor=colors.HexColor('#ad7637'), strokeDashArray=[4, 3]))
box(140, 217, ['Nathalie HIETTE — Sosa 3', '19 novembre 1969, Wavrans-sur-l’Aa', 'Parents nommés dans M05'])
box(20, 110, ['Claude Armand Gérard HIETTE — Sosa 6', '6 janvier 1940, Quesques [M05]', '11 janvier 2001, Vaudringhem [M04/M06]'])
box(270, 110, ['Marie-Paule JOLY — Sosa 7', '30 janvier 1949 [M05]', 'Saint-Martin-d’Hardinghem [M05]'])
box(270, 15, ['Jeanne TOURET — Sosa 15', 'Mère de Marie-Paule selon Maxime [M04]', 'Dates et lieux non établis'])
tree.add(String(20, 14, 'Trait plein : M05 ; pointillés : témoignage M04.', fontName='Dossier', fontSize=7.5))
flow += [tree, Spacer(1, 12)]
people = {p['sosa']: p for p in data['people']}
for identifier in [3, 6, 7, 15]:
    p = people[identifier]
    flow += [para(f"Sosa {identifier} — {p['name']}", 'Heading2')]
    for label, event in [('Naissance', p['birth']), ('Décès', p['death'])]:
        if event:
            flow += [para(f"{label} : {event.get('date', '')} — {event.get('place', '')}"), para(event.get('quality', ''), 'SmallDossier')]
    flow += [para(p['note']), Spacer(1, 8)]
flow += [PageBreak(), para('Index complet des personnes raccordées', 'Heading1'), para('Les candidats des pistes sont exclus de cet index et du GEDCOM. Le statut de preuve varie : consulter les notices et les sources de chaque personne.'), Spacer(1, 10)]
families = {f['child']: f for f in data['families']}
rows = [[para(t, 'SmallDossier') for t in ['Sosa', 'Personne', 'Naissance / décès', 'Parents / sources']]]
for p in data['people']:
    f = families.get(p['sosa'], {})
    parents = ', '.join(str(f[k]) for k in ['father', 'mother'] if f.get(k) is not None) or 'Non identifiés'
    b, d = p.get('birth') or {}, p.get('death') or {}
    dates = f"° {b.get('date', '?')}\n{b.get('place', '')}\n† {d.get('date', '?')}" if d else f"° {b.get('date', '?')}\n{b.get('place', '')}"
    rows.append([para(p['sosa'], 'SmallDossier'), para(p['name'], 'SmallDossier'), para(dates, 'SmallDossier'), para(parents + '\n' + ', '.join(p['sources']), 'SmallDossier')])
t = Table(rows, colWidths=[35, 158, 180, 137], repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e4eef2')), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('GRID', (0, 0), (-1, -1), .3, colors.HexColor('#b6c7ce')), ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
flow.append(t)
pdf('Arbre genealogique v1.2.pdf', flow)

flow = title('Journal de recherche')
for name in ['nathalie.md', 'pistes-v1.2.md', 'pieces-a-obtenir.md']:
    flow += markdown(ROOT / 'recherche' / name) + [PageBreak()]
pdf('Journal de recherche v1.2.pdf', flow[:-1])

flow = title('Notices et catalogue des sources')
flow += [para('Les sources S01–S36 et M01–M03 sont reprises de la v1.0, sans revendiquer leur relecture. M04 est le témoignage actuel ; M05 est la photographie transcrite ; M06–M11 sont des pages lues durant la recherche v1.2.'), Spacer(1, 10)]
for s in data['sources']:
    flow += [para(s['id'] + ' — ' + s['title'], 'Heading2'), para(s.get('kind', '')), para(s.get('reference', '')), para(s.get('reading', ''))]
    if s.get('url'): flow.append(para(s['url'], 'SmallDossier'))
    flow.append(Spacer(1, 8))
pdf('Notices et sources v1.2.pdf', flow)

readme = """Dossier généalogique de Maxime BLARET — v1.2, état de recherche
25 octobre 2026

La branche maternelle est incomplète : ne pas présenter les candidats comme des ascendants établis.
Lire les trois PDF v1.2, puis recherche/nathalie.md et recherche/pistes-v1.2.md.
Les données courantes figurent dans donnees/arbre.json et donnees/arbre.ged.
Les 55 fichiers de la v1.0 sont préservés dans imports/v1.0 ; leurs PDF sont historiques.
Les preuves nouvelles et les extraits textuels de sources sont dans preuves/.
M05 est une transcription de la photographie reçue ; son fichier binaire n'était pas accessible dans l'espace téléchargé et n'est pas inclus.
Le journal d'accès est conservé dans recherche/acces-v1.2.json. Une erreur réseau n'est pas un résultat négatif de généalogie.
Aucun message à une mairie ou à un propriétaire d'arbre n'a été envoyé.
Le manifeste interne contrôle les empreintes du contenu, pas sa vérité généalogique.
"""
(OUT / 'LIRE-MOI-v1.2.txt').write_text(readme)

payload = {}
for directory in ['imports', 'donnees', 'preuves', 'recherche', 'outils']:
    for p in sorted((ROOT / directory).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            payload[p.relative_to(ROOT).as_posix()] = p.read_bytes()
payload['README.md'] = (ROOT / 'README.md').read_bytes()
for p in sorted(OUT.iterdir()):
    if p.suffix == '.pdf' or p.name == 'LIRE-MOI-v1.2.txt': payload[p.name] = p.read_bytes()
manifest = dict(version='1.2', status='état de recherche ; ascendance maternelle incomplète', files=[dict(path=n, bytes=len(b), sha256=hashlib.sha256(b).hexdigest()) for n, b in sorted(payload.items())])
payload['MANIFESTE-v1.2.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
archive = OUT / 'Maxime-Blaret-v1.2.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for n, b in sorted(payload.items()):
        zi = zipfile.ZipInfo('Maxime-Blaret-v1.2/' + n, date_time=(2026, 10, 25, 12, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, b)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for f in manifest['files']:
        b = z.read('Maxime-Blaret-v1.2/' + f['path'])
        assert len(b) == f['bytes'] and hashlib.sha256(b).hexdigest() == f['sha256']
(OUT / 'Maxime-Blaret-v1.2.zip.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name + '\n')
print(f'{archive.name} : {len(payload)} fichiers, {archive.stat().st_size} octets ; contenu vérifié.')
