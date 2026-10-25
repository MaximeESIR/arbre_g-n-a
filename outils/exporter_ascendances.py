"""Dessine les lignées candidates, sans les rattacher au GEDCOM établi."""
import json
import math
import pathlib
import textwrap

from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = pathlib.Path(__file__).resolve().parents[1]

def exporter():
    dataset = json.loads((ROOT / 'recherche/ascendances-candidates-v1.2.json').read_text())
    out = ROOT / 'livrables/Ascendances explorees - hypotheses.pdf'
    out.parent.mkdir(exist_ok=True)
    pdfmetrics.registerFont(TTFont('Hypotheses', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('HypothesesBold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    page_width, page_height = landscape(A3)
    c = canvas.Canvas(str(out), pagesize=(page_width, page_height))
    c.setTitle('Ascendances de candidats — raccordements à Nathalie non établis')
    c.setAuthor('Recherche pour Maxime Blaret')
    for lineage in dataset['lineages']:
        c.setFillColor(colors.HexColor('#873c20'))
        c.setFont('HypothesesBold', 15)
        c.drawString(25, page_height - 28, 'HYPOTHÈSES — CES LIGNÉES NE SONT PAS RATTACHÉES À NATHALIE')
        c.setFont('HypothesesBold', 11)
        c.drawString(25, page_height - 49, lineage['candidate'])
        c.setFont('Hypotheses', 9)
        c.drawString(25, page_height - 65, lineage['missing_bridge'] + '.')
        c.setFillColor(colors.HexColor('#263f4c'))
        c.setFont('Hypotheses', 8)
        c.drawString(25, page_height - 80, 'Huit colonnes exploratoires : seules Nathalie et ses parents sont documentés par M05 ; les autres relations sont des assertions d’arbres publiés.')
        c.drawString(25, page_height - 93, 'Les traits pleins dans la partie ancienne reproduisent ces assertions et ne signalent pas une validation par acte.')
        top = page_height - 125
        usable_height = page_height - 180
        col_width = (page_width - 50) / 8
        box_width, box_height = col_width - 9, 19.5
        centers = {}
        for person in lineage['persons']:
            depth = person['generation_from_candidate'] - 1
            slot = person['relative_number'] - 2 ** depth
            centers[person['relative_number']] = (25 + (depth + 2) * col_width, top - usable_height * (slot + .5) / (2 ** depth))
        for number, (x, y) in centers.items():
            for parent in [number * 2, number * 2 + 1]:
                if parent in centers:
                    px, py = centers[parent]
                    c.setStrokeColor(colors.HexColor('#9aa9ae'))
                    c.setLineWidth(.4)
                    c.line(x + box_width, y, px, py)
        def box(x, y, name, dates='', tentative=True, url=None):
            c.setFillColor(colors.HexColor('#f7f2e7') if tentative else colors.HexColor('#e8f1f5'))
            c.setStrokeColor(colors.HexColor('#ae9671') if tentative else colors.HexColor('#567484'))
            c.roundRect(x, y - box_height / 2, box_width, box_height, 2.5, fill=1, stroke=1)
            c.setFillColor(colors.HexColor('#223744'))
            c.setFont('Hypotheses', 5.5)
            lines = textwrap.wrap(name, width=37, break_long_words=True)[:2]
            if len(lines) == 1:
                c.drawString(x + 3, y + 2, lines[0])
                if dates: c.drawString(x + 3, y - 5, dates)
            else:
                c.drawString(x + 3, y + 4, lines[0])
                c.drawString(x + 3, y - 2, lines[1])
                if dates:
                    c.setFont('Hypotheses', 4.5)
                    c.drawString(x + 3, y - 7.5, dates)
            if url: c.linkURL(url, (x, y - box_height/2, x + box_width, y + box_height/2), relative=0, thickness=0)
        for person in lineage['persons']:
            x, y = centers[person['relative_number']]
            box(x, y, person['name'], person['dates_displayed'], url=person['url'])
        root_x, root_y = centers[1]
        parent_name = 'Claude Armand Gérard HIETTE' if lineage['id'] in ('hiette', 'noel') else 'Marie-Paule JOLY'
        parent_dates = '1940–2001 [M05 / M06]' if lineage['id'] in ('hiette', 'noel') else '30 janvier 1949 [M05]'
        box(25, root_y, 'Nathalie HIETTE', '19 novembre 1969 [M05]', False)
        box(25 + col_width, root_y, parent_name, parent_dates, False)
        c.setStrokeColor(colors.HexColor('#567484'))
        c.line(25 + box_width, root_y, 25 + col_width, root_y)
        c.setStrokeColor(colors.HexColor('#a44823'))
        c.setDash(3, 2)
        c.line(25 + col_width + box_width, root_y, root_x, root_y)
        c.setDash()
        c.setFillColor(colors.HexColor('#a44823'))
        c.setFont('HypothesesBold', 6)
        c.drawString(25 + col_width, root_y - 22, 'Raccordement non établi →')
        c.setFont('Hypotheses', 8)
        for column in range(8):
            c.drawString(25 + column * col_width, top + 12, f'Niveau {column + 1}' + (' *' if column > 1 else ''))
        c.setFillColor(colors.HexColor('#263f4c'))
        c.setFont('Hypotheses', 7)
        c.drawString(25, 38, '* Numérotation conditionnelle depuis Nathalie ; ne pas compter les candidats comme ses ascendants établis. Les noms sont cliquables vers leurs fiches sources.')
        c.drawString(25, 25, 'Source : ' + lineage['source'])
        c.showPage()
    c.save()
    print(out.name, ':', len(dataset['lineages']), 'planches A3, toutes explicitement conditionnelles.')
    return out

if __name__ == '__main__':
    exporter()
