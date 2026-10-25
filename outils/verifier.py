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
assert data['sources'][:-1] == original['sources'], 'Sources historiques modifiées'
assert len(people) == len(data['people']) == data['counts']['total_people']
sources = {s['id'] for s in data['sources']}
assert len(sources) == len(data['sources'])
for person in people.values():
    assert set(person['sources']) <= sources
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
print(f"OK : {len(manifest['files'])} fichiers originaux intacts ; {len(people)} personnes ; {len(families)} familles ; références JSON/GEDCOM concordantes.")
print('Vérification documentaire uniquement : aucune nouvelle filiation certifiée par acte.')
