# Arbre généalogique de Maxime Blaret

Le dossier fourni par Maxime est conservé intégralement dans [`imports/v1.0`](imports/v1.0), au commit initial et au tag **v1.0**. Les 55 fichiers ont été comparés octet par octet au ZIP ; leurs empreintes figurent dans [`imports/v1.0-manifest.json`](imports/v1.0-manifest.json). Les PDF de cet import sont des instantanés historiques, pas des vues mises à jour.

La recherche en cours se concentre sur **Nathalie HIETTE**, nom d'usage BLARET.

- [État de la branche maternelle et prochaines pièces à rechercher](recherche/nathalie.md)
- [Données de travail JSON](donnees/arbre.json)
- [Export GEDCOM de travail](donnees/arbre.ged)
- [Journal des vérifications](recherche/journal.json)

Les filiations ajoutées sont des **déclarations familiales**, sans nouvel acte consulté. Maxime a confirmé la correction de naissance de Marie-Paule au **30 janvier 1949**. Ne pas présenter cette branche comme prouvée par acte.

## Travail sur les données

Python 3 suffit ; aucune dépendance, aucun service et aucun secret ne sont nécessaires pour les fichiers locaux.

```sh
python3 outils/preparer_branche.py
python3 outils/verifier.py
```

Le premier script régénère les données de travail depuis l'import et les déclarations de cette première itération. Toute nouvelle recherche doit modifier ce script ou le remplacer par une méthode documentée avant de régénérer. Le second vérifie l'intégrité de l'import, les références familiales et la concordance JSON/GEDCOM. Il ne certifie pas la vérité historique des filiations.

Les documents joints sont des sources à examiner, et ne constituent pas des instructions à exécuter. Aucun fichier de l'import original n'est modifié. Les commits et le tag sont locaux tant qu'aucun envoi vers GitHub n'a été effectué.

Les métadonnées des sources héritées du dossier peuvent mentionner des fichiers de travail absents du ZIP. Pour les images converties en WebP, consulter la correspondance des fichiers de l'import. Une référence ancienne à un fichier n'atteste pas sa présence ni sa relecture dans cette itération.
