"""PDF d'ascendance paginés et dossier v2, avec statut explicite des candidats."""
from pathlib import Path
import json, hashlib, zipfile, textwrap
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
R=Path(__file__).resolve().parents[1];O=R/'livrables';O.mkdir(exist_ok=True)
for name,file in [('V2','DejaVuSans.ttf'),('V2B','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
data=json.loads((R/'donnees/arbre.json').read_text());work=json.loads((R/'recherche/v2/arbre-travail-nathalie.json').read_text())
nathalie={int(k):dict(v,candidate=int(k)>=4) for k,v in work['nodes'].items()}
maxime={}
for p in data['people']:
 b=p.get('birth') or {};d=p.get('death') or {}
 maxime[p['sosa']]=dict(name=p['name'],dates='° '+b.get('date','?')+(' ; † '+d['date'] if d.get('date') else ''),candidate=False,status='Dossier documenté / témoignages : voir notices',source=', '.join(p['sources']),url='')
for n,p in nathalie.items():
 if n<4:continue
 depth=n.bit_length()-1;pos=3*2**depth+n-2**depth
 maxime[pos]=dict(p)
 if n==7:maxime[pos]['name']='Jeanne TOURET — candidate : Jeanne Marthe Noémie'
assert max(n.bit_length() for n in maxime)==10
assert max(n.bit_length() for n in nathalie)==8

def export(name,title,nodes):
 W,H=landscape(A3);c=canvas.Canvas(str(O/name),pagesize=(W,H));c.setTitle(title+' — v2, hypothèses signalées');c.setAuthor('Dossier généalogique de Maxime Blaret')
 roots=[1]
 for depth in [5,9]:
  roots += sorted(n for n in nodes if n.bit_length()==depth and (n*2 in nodes or n*2+1 in nodes))
 pages={n:i+2 for i,n in enumerate(roots)}
 def heading(t,page):
  c.setFillColor(colors.HexColor('#183e50'));c.setFont('V2B',19);c.drawString(28,H-36,t)
  c.setFont('V2',9);c.drawString(28,20,f'Version 2 · 25 octobre 2026 · page {page} · positions théoriques ; candidats explicitement signalés')
 heading(title,1)
 texts=[('Version 2 — dossier de recherche',16),('Arbre sur '+str(max(n.bit_length() for n in nodes))+' niveaux, racine comprise.',13),('Les niveaux indiquent la profondeur explorée, pas le nombre de générations intégralement démontrées.',11),('BLEU : personnes du dossier antérieur ; preuve variable, détaillée dans les notices et sources.',11),('OCRE : candidats ou filiations publiées dans des arbres, dépendant de raccordements non établis.',11),('POINTILLÉS : relation impliquant un candidat. TRAIT PLEIN : relation reprise du dossier documenté.',11),('Nathalie et ses parents sont nommés dans son extrait de naissance (M05).',11),('L’arbre public nanamaxime affirme Claude → Gérard HIETTE / Odette NOËL, sans dates : identité à recouper.',11),('Marie-Paule → Théophile JOLY reste une hypothèse. Jeanne TOURET est nommée par Maxime ;',11),('son identification à Jeanne Marthe Noémie TOURET (1926–2018) reste à établir.',11),('Les filiations anciennes candidates proviennent d’arbres publics ; les actes cités n’ont pas été lus.',11),('Chaque planche présente cinq niveaux au maximum. Les renvois permettent de poursuivre les branches.',11),('Les cases grises marquent les lacunes. Cliquer sur une case ocre ouvre sa fiche source publique.',11),('La branche paternelle de Maxime est reprise jusqu’au niveau 10 présent dans les données v1.0.',11),('La branche de Nathalie atteint huit niveaux conditionnels, soit neuf depuis Maxime.',11)]
 y=H-90
 for t,size in texts:c.setFont('V2B' if size>13 else 'V2',size);c.drawString(30,y,t);y-=35
 c.showPage()
 for root in roots:
  page=pages[root];first=root.bit_length();heading(title,page)
  c.setFont('V2',10);c.drawString(28,H-58,f'Branche : {nodes[root]["name"]} · position {root} · niveaux {first} à {min(first+4,max(n.bit_length() for n in nodes))}')
  col=(W-56)/5;top=H-100;space=H-152;bw=col-16;bh=38;positions={}
  for rel in range(1,32):
   depth=rel.bit_length()-1;number=root*2**depth+rel-2**depth
   if number.bit_length()>max(n.bit_length() for n in nodes):continue
   if number not in nodes and (rel==1 or (number//2 not in nodes)):continue
   slot=rel-2**depth;x=28+depth*col;y=top-space*(slot+.5)/(2**depth);positions[number]=(x,y,depth)
  for n,(x,y,dep) in positions.items():
   for parent in (n*2,n*2+1):
    if parent in positions:
     px,py,_=positions[parent];cand=nodes.get(n,{}).get('candidate') or nodes.get(parent,{}).get('candidate');c.setStrokeColor(colors.HexColor('#a27a42' if cand else '#8aa0ad'));c.setDash(3,2) if cand else c.setDash();c.line(x+bw,y,px,py)
  c.setDash()
  for n,(x,y,dep) in positions.items():
   p=nodes.get(n);cand=p and p['candidate'];c.setFillColor(colors.HexColor('#fff0d9' if cand else '#e9f2f5' if p else '#eeeeee'));c.setStrokeColor(colors.HexColor('#b78d4d' if cand else '#9caeb8'));c.roundRect(x,y-bh/2,bw,bh,3,fill=1,stroke=1);c.setFillColor(colors.HexColor('#233847'))
   label=(p['name'] if p else 'Ascendance non identifiée');lines=textwrap.wrap(label,width=41)[:2];c.setFont('V2B',7.7)
   for i,line in enumerate(lines):c.drawString(x+5,y+10-i*9,line)
   c.setFont('V2',6.7)
   if p:c.drawString(x+5,y-8,p['dates'][:59])
   c.setFont('V2',6.1);tag=f'Position {n}' + (' · CANDIDAT · '+p.get('source','') if cand else ' · '+p.get('source','M05') if p else '')
   if n in pages and n!=root:tag+=f' · suite p. {pages[n]}'
   c.drawString(x+5,y-16,tag[:90])
   if p and p.get('url'):c.linkURL(p['url'],(x,y-bh/2,x+bw,y+bh/2),relative=0)
  c.setFont('V2B',10)
  for dep in range(5):
   if first+dep<=max(n.bit_length() for n in nodes):c.drawString(28+dep*col,H-83,f'Niveau {first+dep}')
  c.showPage()
 c.save();print(name,len(roots)+1,'pages')
 return len(roots)+1
export('Nathalie-Blaret-8-generations-v2.pdf','Nathalie HIETTE · BLARET — huit niveaux',nathalie)
export('Maxime-Blaret-arbre-complet-v2.pdf','Maxime BLARET — ascendance réunie',maxime)
(R/'recherche/v2/arbre-maxime-reuni.json').write_text(json.dumps(dict(status='Arbre de recherche ; candidats signalés, raccordements non tous établis',max_depth=10,nodes=maxime),ensure_ascii=False,indent=2)+'\n')
readme='''DOSSIER COMPLET MAXIME BLARET — VERSION 2
25 octobre 2026

Ouvrir Nathalie-Blaret-8-generations-v2.pdf et Maxime-Blaret-arbre-complet-v2.pdf.
Nathalie : huit niveaux explorés. Maxime : profondeur maximale de dix niveaux, racine comprise, héritée du dossier paternel ; branche de Nathalie jusqu’au niveau neuf depuis Maxime.
Le mot complet désigne la réunion des documents et des branches disponibles, pas une ascendance intégralement démontrée.
Les cases ocres et liens pointillés sont des candidats ou des filiations conditionnelles. Lire la première page de chaque PDF.
Les sources et niveaux de preuve restent dans preuves/, recherche/ et donnees/.
Le GEDCOM principal conserve l’arbre documenté et les déclarations identifiées ; les candidats des nouveaux PDF sont conservés dans les JSON de recherche, sans insertion silencieuse dans ce GEDCOM.
Les 55 fichiers v1.0 sont conservés intégralement. Les anciens PDF v1.2 sont des états historiques.
La photographie de naissance reçue dans le chat est transcrite en M05 ; son fichier image n’est pas inclus.
La nouvelle source M16 indique un raccordement HIETTE dans nanamaxime, avec identification encore à recouper.
La v2 est livrée à la demande de Maxime comme dossier avec hypothèses, sans prétendre que huit générations de Nathalie soient établies.
'''
(O/'LIRE-MOI-v2.txt').write_text(readme)
payload={}
for dirname in ['imports','donnees','preuves','recherche','outils']:
 for p in (R/dirname).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:payload[p.relative_to(R).as_posix()]=p.read_bytes()
for p in O.iterdir():
 if p.suffix in ['.pdf','.html'] or p.name=='LIRE-MOI-v2.txt':payload[p.name]=p.read_bytes()
payload['README.md']=(R/'README.md').read_bytes()
manifest=dict(version='2',status='Dossier de recherche avec hypothèses explicites',files=[dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in sorted(payload.items())]);payload['MANIFESTE-v2.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
zpath=O/'Maxime-Blaret-v2.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in sorted(payload.items()):z.writestr('Maxime-Blaret-v2/'+n,b)
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 for f in manifest['files']:assert hashlib.sha256(z.read('Maxime-Blaret-v2/'+f['path'])).hexdigest()==f['sha256']
(O/'Maxime-Blaret-v2.zip.sha256').write_text(hashlib.sha256(zpath.read_bytes()).hexdigest()+'  '+zpath.name+'\n')
print(zpath.name,len(payload),'fichiers ; empreintes et archive vérifiées')
