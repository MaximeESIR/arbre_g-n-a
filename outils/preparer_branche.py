"""Régénère la première itération maternelle sans modifier l'import v1.0."""
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
data['scope'] = 'Dossier v1.0 préservé ; première itération sur la branche de Nathalie HIETTE. Filiations maternelles ajoutées sur déclaration, sans acte.'
data['research_status'] = '25 octobre 2026 : Claude HIETTE et Jeanne TOURET ajoutés sur déclaration familiale. Marie-Paule JOLY née le 30 janvier 1949 selon Maxime. Décès de Claude confirmé par Maxime au 11 janvier 2001 à « Vandringhem » ; la notice M02 du ZIP indique Vaudringhem pour Claude Armand Gérard HIETTE, né le même jour. Graphie communale et prénoms supplémentaires à vérifier. Aucun acte relu dans cette itération. Recherches externes bloquées par la politique réseau. Aucun ascendant plus ancien confirmé.'
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

i3 = re.search(r'^0 @I3@ .*?(?=^0 |\Z)', ged, re.M | re.S).group()
i3 = re.sub(r'^1 NOTE .*?(?=^1 |\Z)', '1 NOTE ' + people[3]['note'] + '\n', i3, flags=re.M | re.S)
replace_record('I3', i3.rstrip() + '\n1 SOUR @M04@')
replace_record('I7', '''0 @I7@ INDI
1 NAME Marie-Paule /JOLY/
1 SEX F
1 _SOSA 7
1 BIRT
2 DATE 30 JAN 1949
2 NOTE Date corrigée et confirmée par Maxime ; acte non consulté. Lieu possible : Saint-Martin-d'Hardinghem.
2 SOUR @M04@
1 FAMC @F7@
1 FAMS @F3@
1 NOTE ''' + people[7]['note'] + '''
1 SOUR @M01@
1 SOUR @M04@''')
replace_record('F3', '''0 @F3@ FAM
1 HUSB @I6@
1 WIFE @I7@
1 CHIL @I3@
1 NOTE Parents déclarés par Maxime ; aucun acte consulté.
1 SOUR @M01@
1 SOUR @M04@''')
new_records = '''0 @I6@ INDI
1 NAME Claude /HIETTE/
1 SEX M
1 _SOSA 6
1 BIRT
2 DATE 6 JAN 1940
2 PLAC Quesque [lieu déclaré ; piste Quesques à confirmer]
2 NOTE Déclaration familiale ; acte non consulté.
2 SOUR @M04@
1 DEAT
2 DATE 11 JAN 2001
2 PLAC Vandringhem
2 NOTE Graphie de Maxime ; la notice M02 indique Vaudringhem. Commune à vérifier dans l'acte.
2 SOUR @M04@
1 FAMS @F3@
1 NOTE ''' + people[6]['note'] + '''
1 SOUR @M04@
0 @I15@ INDI
1 NAME Jeanne /TOURET/
1 SEX F
1 _SOSA 15
1 FAMS @F7@
1 NOTE ''' + people[15]['note'] + '''
1 SOUR @M04@
0 @F7@ FAM
1 WIFE @I15@
1 CHIL @I7@
1 NOTE Lien mère-fille déclaré par Maxime ; aucun acte consulté.
1 SOUR @M04@
0 @M04@ SOUR
1 TITL Précisions familiales de Maxime sur la branche Nathalie, 25 octobre 2026
1 NOTE ''' + data['sources'][-1]['reading'] + '\n'
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
