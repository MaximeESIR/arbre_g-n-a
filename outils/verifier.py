"""Vérifications d'intégrité documentaire et de cohérence des références."""
import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'imports/v1.0-manifest.json').read_text())
for entry in manifest['files']:
    content = (root / 'imports/v1.0' / entry['path']).read_bytes()
    assert len(content) == entry['bytes'], entry['path']
    assert hashlib.sha256(content).hexdigest() == entry['sha256'], entry['path']
data = json.loads((root / 'donnees/arbre.json').read_text())
people = {p['sosa']: p for p in data['people']}
original = json.loads((root / 'imports/v1.0/Donnees genealogiques.json').read_text())
for person in original['people']:
    if person['sosa'] not in (3, 7):
        assert people[person['sosa']] == person, 'Personne hors périmètre modifiée'
assert data['sources'][:len(original['sources'])] == original['sources'], 'Sources historiques modifiées'
for family in original['families']:
    if family['id'] != 'F3':
        assert next(f for f in data['families'] if f['id'] == family['id']) == family, 'Famille hors périmètre modifiée'
assert len(people) == len(data['people']) == data['counts']['total_people']
sources = {s['id'] for s in data['sources']}
assert len(sources) == len(data['sources'])
for person in people.values():
    assert set(person['sources']) <= sources
    for event in ['birth', 'death']:
        if person.get(event): assert set(person[event].get('sources', [])) <= sources
    for occupation in person.get('occupations', []): assert set(occupation['sources']) <= sources
families = {f['id']: f for f in data['families']}
assert len(families) == len(data['families'])
for f in families.values():
    assert f['child'] in people
    assert set(f['sources']) <= sources
    for role, offset in [('father', 0), ('mother', 1)]:
        parent = f[role]
        if parent is not None:
            assert parent in people
            assert parent == f['child'] * 2 + offset
assert people[7]['birth']['date'] == '30 JAN 1949', 'Conserver la correction confirmée par Maxime'
ged = (root / 'donnees/arbre.ged').read_text()
records = re.findall(r'^0 @([^@]+)@ ', ged, re.M)
assert len(records) == len(set(records)), 'Identifiant GEDCOM dupliqué'
assert set(re.findall(r'(?m)^[1-9] (?:FAMC|FAMS|HUSB|WIFE|CHIL|SOUR|SUBM) @([^@]+)@', ged)) <= set(records)
assert {int(x) for x in re.findall(r'^0 @I(\d+)@ INDI$', ged, re.M)} == set(people)
assert set(re.findall(r'^0 @(F\d+)@ FAM$', ged, re.M)) == set(families)
for key, f in families.items():
    block = re.search(r'^0 @' + key + r'@ FAM\n(.*?)(?=^0 |\Z)', ged, re.M | re.S).group(1)
    assert f"1 CHIL @I{f['child']}@" in block
    for role, tag in [('father', 'HUSB'), ('mother', 'WIFE')]:
        if f[role] is not None:
            assert f"1 {tag} @I{f[role]}@" in block
            pb = re.search(r'^0 @I' + str(f[role]) + r'@ INDI\n(.*?)(?=^0 |\Z)', ged, re.M | re.S).group(1)
            assert f'1 FAMS @{key}@' in pb
    cb = re.search(r'^0 @I' + str(f['child']) + r'@ INDI\n(.*?)(?=^0 |\Z)', ged, re.M | re.S).group(1)
    assert f'1 FAMC @{key}@' in cb
assert ged.rstrip().endswith('0 TRLR')
for identifier in [3, 6, 7, 15]:
    block = re.search(r'^0 @I' + str(identifier) + r'@ INDI\n(.*?)(?=^0 |\Z)', ged, re.M | re.S).group(1)
    for event, tag in [('birth', 'BIRT'), ('death', 'DEAT')]:
        e = people[identifier].get(event)
        if e:
            eb = re.search(r'^1 ' + tag + r'\n(.*?)(?=^1 |\Z)', block, re.M | re.S).group(1)
            assert '2 DATE ' + e['date'] in eb
            if e.get('place'): assert '2 PLAC ' + e['place'] in eb
            for sid in e.get('sources', []): assert '2 SOUR @' + sid + '@' in eb
print(f"OK : {len(manifest['files'])} fichiers originaux intacts ; {len(people)} personnes ; {len(families)} familles ; références JSON/GEDCOM concordantes.")
assert people[6]['given'] == 'Claude Armand Gérard'
assert people[6]['birth']['place'] == 'Quesques, Pas-de-Calais, France'
assert people[7]['birth']['place'] == "Saint-Martin-d'Hardinghem, Pas-de-Calais, France"
assert 'M05' in families['F3']['sources']
assert families['F7']['sources'] == ['M04'], 'Le lien Jeanne–Marie-Paule reste déclaratif'
for sid in ['M05', 'M06', 'M07', 'M08', 'M09', 'M10', 'M11']:
    assert sid in sources
candidate_file = root / 'recherche/ascendances-candidates-v1.2.json'
if candidate_file.exists():
    candidates = json.loads(candidate_file.read_text())
    assert {l['id'] for l in candidates['lineages']} == {'hiette', 'noel', 'touret', 'joly'}
    assert len(people) == 60 and len(families) == 31, 'Ne pas rattacher les candidats sans preuve'
    for lineage in candidates['lineages']:
        assert lineage['missing_bridge'] and lineage['source_id'] in sources
        nodes = {p['relative_number']: p for p in lineage['persons']}
        assert len(nodes) == len(lineage['persons']) and 1 in nodes
        assert max(p['generation_from_nathalie_if_hypothesis_verified'] for p in nodes.values()) == 8
        for number, person in nodes.items():
            depth = number.bit_length()
            assert person['generation_from_candidate'] == depth
            assert person['generation_from_nathalie_if_hypothesis_verified'] == depth + 2
            assert person['evidence_level'] == 'Assertion d’un arbre collaboratif ; acte non consulté dans cette extraction'
            for parent in person['parents_relative_numbers']:
                assert parent in nodes and parent in (number * 2, number * 2 + 1)
for source in data['sources'][len(original['sources']):]:
    for name in source.get('files', []): assert (root / 'donnees' / name).is_file(), name
print('M05 conservée comme transcription de photographie ; filiation de Nathalie documentée, générations antérieures non raccordées par acte.')
