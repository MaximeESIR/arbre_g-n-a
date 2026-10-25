from pathlib import Path
import json,html
r=Path(__file__).resolve().parents[1];d=json.loads((r/'recherche/ascendances-candidates-v1.2.json').read_text())
nodes={1:dict(name='Nathalie HIETTE, nom d’usage BLARET',dates='19 novembre 1969',status='Documenté par M05',url=''),2:dict(name='Claude Armand Gérard HIETTE',dates='6 janvier 1940 – 11 janvier 2001',status='Père nommé dans M05',url=''),3:dict(name='Marie-Paule JOLY',dates='30 janvier 1949',status='Mère nommée dans M05',url='')}
for line in d['lineages']:
 root={'hiette':4,'noel':5,'joly':6,'touret':7}[line['id']]
 for p in line['persons']:
  rel=p['relative_number'];dep=rel.bit_length()-1;n=root*2**dep+rel-2**dep
  status='Filiation publiée dans un arbre ; acte non consulté. Dépend du raccordement initial.'
  if rel==1:status=('Parent de Claude selon l’arbre nanamaxime ; identité à recouper.' if root in (4,5) else 'Candidat : lien avec Marie-Paule non établi.' )
  nodes[n]=dict(name=p['name'],dates=p['dates_displayed'],status=status,url=p['url'],source=line['source_id'])
obj=dict(title='Nathalie — arbre de travail sur huit niveaux',status='Recherche incomplète : ce document n’est pas la v2 achevée. Les raccordements et filiations non documentés restent des hypothèses.',numbering='Numéros de positions théoriques depuis Nathalie, pas attribution de Sosa établis aux candidats.',nodes=nodes)
(r/'recherche/v2/arbre-travail-nathalie.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def branch(n):
 level=n.bit_length()
 if level>8:return ''
 p=nodes.get(n)
 if p is None:return f'<li class="unknown"><span>Niveau {level} · position {n} : ascendance non identifiée</span></li>'
 cls='known' if n<4 else 'candidate';link=f'<a target="_blank" rel="noopener" href="{html.escape(p["url"],quote=True)}">Fiche source {p.get("source", "")}</a>' if p['url'] else 'Source : photographie M05'
 body=f'<p>{html.escape(p["status"])}</p>{link}'
 children=('<ul>'+branch(n*2)+branch(n*2+1)+'</ul>') if level<8 else ''
 return f'<li class="{cls}"><details '+('open' if level<4 else '')+f'><summary><small>Niveau {level} · position {n}</small><strong>{html.escape(p["name"])}</strong><span>{html.escape(p["dates"])}</span></summary><div class="source">{body}</div>{children}</details></li>'
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nathalie — arbre de travail sur huit niveaux</title><style>
body{font:16px system-ui,sans-serif;margin:0;background:#f6f7f8;color:#233343}header{padding:25px;background:#213e50;color:white}main{max-width:1100px;margin:25px auto;padding:0 18px}.notice{padding:18px;background:#fff0d9;border-left:5px solid #a26019;line-height:1.5}button{padding:10px 18px;margin:14px 10px 14px 0;border:1px solid #456;border-radius:5px;cursor:pointer}ul{list-style:none;padding-left:25px;border-left:1px solid #aab8bd}li{margin:10px 0}summary{padding:12px;background:#fff;border:1px solid #aab8bd;border-left:5px solid #a26019;border-radius:5px;cursor:pointer}summary strong,summary span,summary small{display:block;margin:3px 0}summary small{color:#5b6771}.known>details>summary{border-left-color:#238174}.source{padding:10px 15px;font-size:14px;background:#f2e8d8}.known>details>.source{background:#e2efeb}.source p{margin:0 0 8px}.unknown{color:#67747b;padding:9px}a{color:#165984}footer{padding:25px;font-size:14px}@media print{button{display:none}summary,.source{break-inside:avoid}body{background:white}}
</style><header><h1>Nathalie HIETTE · BLARET</h1><p>Arbre de travail sur huit niveaux — recherche du 25 octobre 2026</p></header><main><div class="notice"><b>Recherche incomplète — ce document n’est pas la v2 achevée.</b><p>Les deux premiers niveaux sont documentés par l’extrait de naissance de Nathalie. L’arbre public « nanamaxime » affirme le lien Claude–Gérard/Odette, mais ne donne pas les dates permettant de confirmer l’identité de cette famille. Les raccordements Marie-Paule–Théophile et Marie-Paule–Jeanne Marthe Noémie restent à établir. Le nom Jeanne TOURET vient du témoignage de Maxime ; son identification précise à la candidate n’est pas acquise.</p><p>Vert : relation documentée par M05. Ocre : candidat ou filiation déclarée dans un arbre public, dépendant des raccordements incertains. Une source publiée n’est pas une lecture d’acte. Les positions numérotent le plan de recherche.</p></div><button onclick="document.querySelectorAll('details').forEach(x=>x.open=true)">Déployer les huit niveaux</button><button onclick="document.querySelectorAll('details').forEach(x=>x.open=false)">Replier</button><button onclick="window.print()">Imprimer</button><ul>'''+branch(1)+'''</ul><footer>Les fiches sources sont cliquables. Les lacunes restent visibles. Le dossier v1.0 et l’arbre documenté restent conservés séparément.</footer></main></html>'''
(r/'livrables/Nathalie-arbre-de-travail.html').write_text(page)
assert max(n.bit_length() for n in nodes)==8
assert len(nodes)==123
print(len(nodes),'positions renseignées ; huit niveaux ; toutes les hypothèses signalées')
