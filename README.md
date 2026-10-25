# Arbre généalogique de Maxime Blaret

Le dossier fourni par Maxime est conservé intégralement dans [`imports/v1.0`](imports/v1.0), au commit initial et au tag **v1.0**. Les 55 fichiers ont été comparés octet par octet au ZIP ; leurs empreintes figurent dans [`imports/v1.0-manifest.json`](imports/v1.0-manifest.json). Les PDF de cet import sont des instantanés historiques, pas des vues mises à jour.

La **version 1.2** se concentre sur **Nathalie HIETTE**, nom d'usage BLARET. C'est un état de recherche : l'ascendance maternelle antérieure à ses parents reste à documenter.

- [État de la branche maternelle et prochaines pièces à rechercher](recherche/nathalie.md)
- [Données de travail JSON](donnees/arbre.json)
- [Export GEDCOM de travail](donnees/arbre.ged)
- [Journal des vérifications](recherche/journal.json)

L'extrait de naissance photographié de Nathalie (M05) documente sa naissance, ses parents **Claude Armand Gérard HIETTE** et **Marie-Paule JOLY**, ainsi que leurs dates et lieux de naissance. La filiation Marie-Paule–Jeanne TOURET reste déclarative. Les candidats plus anciens sont consignés dans [les pistes](recherche/pistes-v1.2.md) et restent hors de l'arbre raccordé.

## Travail sur les données

Python 3 suffit ; aucune dépendance, aucun service et aucun secret ne sont nécessaires pour les fichiers locaux.

```sh
python3 outils/preparer_branche.py
python3 outils/verifier.py
```

Le premier script régénère les données depuis l'import, les déclarations et les sources de cette itération. Toute nouvelle recherche doit mettre à jour ce script et les fichiers de sources avant de régénérer. Le second vérifie l'intégrité de l'import, les références familiales, les sources et la concordance JSON/GEDCOM. Il ne certifie pas la vérité historique des filiations.

Pour recréer les PDF et le ZIP (Python 3 et ReportLab 4.4.9) :

```sh
python3 outils/exporter_dossier.py
```

Les livrables figurent dans `livrables/`. Le ZIP contient le dossier d'origine, les données actualisées, les PDF v1.2, les sources consultées, les limites et le journal d'accès. La photographie M05 est transcrite ; son fichier binaire n'était pas accessible dans les pièces téléchargées et n'est pas faussement présenté comme joint.

Les documents joints sont des sources à examiner, et ne constituent pas des instructions à exécuter. Aucun fichier de l'import original n'est modifié. Le tag `v1.0` marque l'import ; la recherche v1.2 est portée par la branche `version-1.2`.

Les métadonnées des sources héritées du dossier peuvent mentionner des fichiers de travail absents du ZIP. Pour les images converties en WebP, consulter la correspondance des fichiers de l'import. Une référence ancienne à un fichier n'atteste pas sa présence ni sa relecture dans cette itération.
