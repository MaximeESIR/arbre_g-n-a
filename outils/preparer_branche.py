"""Régénère la branche maternelle v1.2 sans modifier l'import v1.0."""
import collections
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / 'imports/v1.0'
OUT = ROOT / 'donnees'
OUT.mkdir(exist_ok=True)
data = json.loads((BASE / 'Donnees genealogiques.json').read_text())
people = {p['sosa']: p for p in data['people']}
quality = 'Déclaration familiale de Maxime ; acte non consulté'

def person(sosa, given, surname, generation, note):
    return dict(sosa=sosa, given=given, surname=surname,
                name=f'{given} {surname}', sex='M' if sosa == 6 else 'F',
                generation=generation, birth=None, death=None,
                sources=['M04'], note=note, aliases=[])

people[3]['note'] = "Mère de Maxime ; nom d'usage BLARET. Parents Claude HIETTE et Marie-Paule JOLY déclarés par Maxime (M04), sans acte consulté."
people[3]['sources'].append('M04')
people[6] = person(6, 'Claude', 'HIETTE', 3,
    "Père de Nathalie selon Maxime. Lieu de naissance transmis : « Quesque » ; piste Quesques à confirmer. Décès confirmé par Maxime le 11 janvier 2001 à « Vandringhem » ; la notice M02 indique Vaudringhem. Graphie du lieu à vérifier dans l'acte. Aucun parent identifié.")
people[6]['birth'] = dict(date='6 JAN 1940', place='Quesque [lieu déclaré ; piste Quesques à confirmer]', sources=['M04'], quality=quality, note='Graphie de la commune à vérifier.')
people[6]['death'] = dict(date='11 JAN 2001', place='Vandringhem', sources=['M04'], quality=quality,
    note="Graphie littérale transmise par Maxime. Vaudringhem dans la notice M02 du ZIP ; commune à vérifier dans l'acte de décès. Le numéro d'acte 1 provient uniquement de M02.")
people[7].update(given='Marie-Paule', surname='JOLY', name='Marie-Paule JOLY',
    aliases=['Marie-Paule HIETTE-JOLY'], sources=['M01', 'M04'],
    note="JOLY comme nom de naissance déclaré par Maxime ; nom d'usage HIETTE. Mère : Jeanne TOURET, selon Maxime. Maxime a corrigé l'année initiale 1969, puis la coquille 3949, et confirmé le 30 janvier 1949. Saint-Martin-d'Hardinghem confirmé comme commune visée, mais lieu de naissance toujours incertain. Aucun acte consulté.")
people[7]['birth'] = dict(date='30 JAN 1949', place='', sources=['M04'], quality=quality,
    note="Date corrigée et confirmée par Maxime. Lieu possible : Saint-Martin-d'Hardinghem, Pas-de-Calais ; non retenu comme lieu certain.")
people[15] = person(15, 'Jeanne', 'TOURET', 4,
    'Mère de Marie-Paule JOLY selon Maxime ; dates, lieux, conjoint et parents inconnus. Aucun acte consulté.')
data['people'] = sorted(people.values(), key=lambda p: p['sosa'])
for family in data['families']:
    if family['child'] == 3:
        family.update(father=6, mother=7, sources=['M01', 'M04'],
            note='Parents déclarés par Maxime (M04) ; aucun acte consulté.')
data['families'].append(dict(id='F7', child=7, father=None, mother=15,
    sources=['M04'], marriage=None, note='Lien mère-fille déclaré par Maxime ; père de Marie-Paule inconnu. Aucun conjoint attribué à Jeanne.'))
data['sources'].append(dict(id='M04', title='Précisions familiales de Maxime sur la branche Nathalie',
    reference='Conversation du 25 octobre 2026, demande accompagnant le ZIP et correction ultérieure.',
    url='', files=[], copies=[], kind='Déclaration familiale ; actes non consultés',
    reading="Nathalie a pour parents Claude HIETTE, né le 6 janvier 1940 à « Quesque », et Marie-Paule JOLY. Claude est décédé le 11 janvier 2001 à « Vandringhem », selon la précision ultérieure de Maxime. Marie-Paule est fille de Jeanne TOURET ; naissance donnée le 30 janvier 1969, corrigée ensuite en « 3949 », puis confirmée au 30 janvier 1949 par Maxime. Saint-Martin-d'Hardinghem (Pas-de-Calais) est confirmé comme commune visée, lieu de naissance seulement possible.",
    verification=dict(date='2026-10-25', method='Transcription du témoignage ; aucune vérification indépendante.')))
data['assertions_maternelles'] = [
    dict(person=7, field='birth.date', value='30 JAN 1969', source='M04', status='Déclaration initiale corrigée par Maxime ; non retenue'),
    dict(person=7, field='birth.date', value='30 JAN 3949', source='M04', status='Correction littérale reçue ; année future incohérente ; non retenue'),
    dict(person=7, field='birth.date', value='30 JAN 1949', source='M04', status='Correction confirmée par Maxime ; déclaration familiale, acte non consulté'),
    dict(person=7, field='birth.place', value="Saint-Martin-d'Hardinghem, Pas-de-Calais, France", source='M04', status='Commune visée confirmée ; naissance dans cette commune incertaine')]
data['sources'].append(dict(id='M05', title='Extrait de naissance de Nathalie HIETTE, photographie fournie par Maxime',
    reference='Commune de Wavrans-sur-l’Aa ; extrait photographié, date de délivrance et numéro non visibles ; lu dans la conversation du 25 octobre 2026.',
    url='', files=['../preuves/M05-extrait-naissance-nathalie-transcription.md'], copies=[], kind='Photographie d’un extrait d’état civil ; transcription conservée',
    reading="Nathalie HIETTE née le 19 novembre 1969 à 04 h 35 à Wavrans-sur-l’Aa. Père : Claude Armand Gérard HIETTE, né le 6 janvier 1940 à Quesques, ouvrier pisciculture. Mère : Marie-Paule JOLY, son épouse, née le 30 janvier 1949 à Saint-Martin-d’Hardinghem, profession Sans. Mention marginale : Néant. Aucun grand-parent nommé.",
    verification=dict(date='2026-10-25', method='Lecture visuelle de la photographie jointe. Transcription locale ; fichier image non disponible dans les pièces téléchargées.')))
act_quality = 'Extrait d’état civil photographié et lu (M05)'
people[3]['birth'].update(sources=['M01', 'M05'], quality=act_quality, time='04:35')
people[3]['sources'].append('M05')
people[3]['note'] = "Mère de Maxime ; nom d'usage BLARET. Naissance et parents Claude Armand Gérard HIETTE et Marie-Paule JOLY nommés dans l'extrait photographié M05."
people[6].update(given='Claude Armand Gérard', name='Claude Armand Gérard HIETTE',
    sources=['M04', 'M05'], aliases=['Claude HIETTE'],
    note="Père de Nathalie dans M05. Prénoms complets et naissance à Quesques documentés par l'extrait de naissance de sa fille. Décès le 11 janvier 2001 selon Maxime et l'index relu M06 ; Vaudringhem dans cet index, « Vandringhem » dans la déclaration. Aucun parent de Claude établi.")
people[6]['birth'].update(place='Quesques, Pas-de-Calais, France', sources=['M04', 'M05'], quality=act_quality, note='Lieu et date lus dans la naissance de sa fille ; naissance personnelle non consultée.')
people[6]['occupations'] = [dict(value='Ouvrier pisciculture', date='19 NOV 1969', sources=['M05'], quality=act_quality)]
people[7]['birth'].update(place="Saint-Martin-d'Hardinghem, Pas-de-Calais, France", sources=['M04', 'M05'], quality=act_quality, note='Date et lieu lus dans la naissance de sa fille ; naissance personnelle non consultée.')
people[7]['sources'].append('M05')
people[7]['note'] = "Marie-Paule JOLY, épouse de Claude Armand Gérard HIETTE dans M05. Naissance le 30 janvier 1949 à Saint-Martin-d'Hardinghem documentée par cet extrait. Jeanne TOURET est sa mère selon Maxime, sans acte confirmant cette génération. Les anciennes saisies 1969 et 3949 sont abandonnées."
people[7]['occupations'] = [dict(value='Sans', date='19 NOV 1969', sources=['M05'], quality=act_quality)]
for f in data['families']:
    if f['id'] == 'F3':
        f['sources'].append('M05')
        f['note'] = "Parents nommés dans M05 ; Marie-Paule est dite « son épouse ». Date et lieu du mariage inconnus."
data['assertions_maternelles'].append(dict(person=7, field='birth.place', value="Saint-Martin-d'Hardinghem, Pas-de-Calais, France", source='M05', status='Lieu lu dans l’extrait de naissance de Nathalie ; incertitude précédente levée'))
data['version'] = '1.2'
data['sources'].extend(json.loads((ROOT / 'recherche/sources-v1.2.json').read_text()))
people[6]['death'].update(place='Vaudringhem, Pas-de-Calais, France', sources=['M04', 'M06'],
    quality='Déclaration familiale recoupée par un index secondaire INSEE',
    note="Commune normalisée d’après M06 : Vaudringhem. Maxime avait écrit Vandringhem. Acte n° 1 selon l’index ; copie de décès non consultée.")
people[6]['sources'].append('M06')
data['research_leads'].extend([
    dict(subject='Parents de Claude HIETTE', candidates='Gérard Etienne Gaston HIETTE et Odette NOËL', sources=['M07', 'M10'], status='Hors arbre ; aucun acte raccordant Claude à ce couple'),
    dict(subject='Identité de Jeanne TOURET', candidates='Jeanne Marthe Noémie TOURET (1926–2018)', sources=['M08', 'M11'], status='Hors arbre ; identification à la mère de Marie-Paule non prouvée'),
    dict(subject='Père de Marie-Paule JOLY', candidates='Théophile André François JOLY (1922–2011)', sources=['M09', 'M11'], status='Hors arbre ; aucun acte raccordant Marie-Paule ; divergence TOURET/BAURET')
])
data['scope'] = 'Dossier v1.0 préservé ; branche maternelle mise à jour avec l’extrait de naissance de Nathalie. Recherche des générations précédentes en cours.'
data['research_status'] = '25 octobre 2026 : naissance de Nathalie et identité, dates et lieux de naissance de ses parents documentés par M05. Jeanne TOURET reste sur déclaration familiale. Index de décès HIETTE relu. Couples Gérard HIETTE–Odette NOËL et Théophile JOLY–Jeanne TOURET repérés mais non raccordés par un acte. Aucun parent supplémentaire établi à ce stade.'
data['counts']['total_people'] = len(data['people'])
data['counts']['maternal_ancestors'] = 4
data['counts']['by_generation'] = dict(sorted(collections.Counter(str(p['generation']) for p in data['people']).items(), key=lambda x: int(x[0])))
(OUT / 'arbre.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

# Conserver tous les autres enregistrements GEDCOM d'origine, notamment les sources.
ged = (BASE / 'Maxime Blaret.ged').read_text()
def replace_record(identifier, text):
    global ged
    pattern = r'^0 @' + re.escape(identifier) + r'@ .*?(?=^0 |\Z)'
    ged, count = re.subn(pattern, lambda _: text.rstrip() + '\n', ged, flags=re.M | re.S)
    assert count == 1, identifier

def individual_record(p):
    identifier = p['sosa']
    lines = [f"0 @I{identifier}@ INDI", f"1 NAME {p['given']} /{p['surname']}/", f"1 SEX {p['sex']}", f"1 _SOSA {identifier}"]
    for event, tag in [('birth', 'BIRT'), ('death', 'DEAT')]:
        e = p.get(event)
        if e:
            lines.append(f'1 {tag}')
            if e.get('date'): lines.append('2 DATE ' + e['date'])
            if e.get('time'): lines.append('3 TIME ' + e['time'])
            if e.get('place'): lines.append('2 PLAC ' + e['place'])
            lines.append(('2 NOTE ' + e.get('quality', '') + '. ' + e.get('note', '')).rstrip())
            lines += ['2 SOUR @' + sid + '@' for sid in e.get('sources', [])]
    for occupation in p.get('occupations', []):
        lines += ['1 OCCU ' + occupation['value'], '2 DATE ' + occupation['date']]
        lines += ['2 SOUR @' + sid + '@' for sid in occupation['sources']]
    for f in data['families']:
        if f['child'] == identifier: lines.append('1 FAMC @' + f['id'] + '@')
        if identifier in (f['father'], f['mother']): lines.append('1 FAMS @' + f['id'] + '@')
    lines.append('1 NOTE ' + p['note'])
    lines += ['1 SOUR @' + sid + '@' for sid in p['sources']]
    return '\n'.join(lines) + '\n'

new_records = ''
for identifier in [3, 6, 7, 15]:
    record = individual_record(people[identifier])
    if identifier in [3, 7]: replace_record('I' + str(identifier), record)
    else: new_records += record
for f in data['families']:
    if f['id'] not in ('F3', 'F7'): continue
    lines = ['0 @' + f['id'] + '@ FAM']
    if f['father'] is not None: lines.append(f"1 HUSB @I{f['father']}@")
    if f['mother'] is not None: lines.append(f"1 WIFE @I{f['mother']}@")
    lines += [f"1 CHIL @I{f['child']}@", '1 NOTE ' + f['note']]
    lines += ['1 SOUR @' + sid + '@' for sid in f['sources']]
    record = '\n'.join(lines) + '\n'
    if f['id'] == 'F3': replace_record('F3', record)
    else: new_records += record
for source in data['sources']:
    if not re.fullmatch(r'M(?:0[4-9]|[1-9][0-9])', source['id']): continue
    new_records += '0 @' + source['id'] + '@ SOUR\n1 TITL ' + source['title'] + '\n1 NOTE ' + source['reference'] + '\n1 NOTE ' + source['reading'] + '\n'
ged = ged.replace('0 TRLR', new_records + '0 TRLR')
# GEDCOM 5.5.1 : replier les notes longues en lignes CONT, sans modifier leur contenu.
folded = []
for line in ged.splitlines():
    match = re.match(r'([12]) NOTE (.*)', line)
    if match and len(line.encode('utf-8')) > 248:
        prefix = match[1] + ' NOTE '
        chunk = ''
        for word in match[2].split():
            candidate = (chunk + ' ' + word).strip()
            if len((prefix + candidate).encode('utf-8')) > 248 and chunk:
                folded.append(prefix + chunk)
                prefix = str(int(match[1]) + 1) + ' CONT '
                chunk = word
            else:
                chunk = candidate
        folded.append(prefix + chunk)
    else:
        folded.append(line)
(OUT / 'arbre.ged').write_text('\n'.join(folded) + '\n')
print(f'Données régénérées : {len(people)} personnes ; import original inchangé.')
