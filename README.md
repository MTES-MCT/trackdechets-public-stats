# Statistiques publiques Trackdéchets

**version 1.12**

> Application basée sur Plotly Dash consacrée à la publication d'un tableau de bord illustrant l'activité de [l'application
> Trackdéchets](https://app.trackdechets.beta.gouv.fr/). Ce tableau de bord vise à donner au grand public aux
> professionnels du déchet un aperçu du cycle de vie des déchets en France.


### Pré-requis

- python 3.10
- pip
- [pipenv](https://pipenv.pypa.io/en/latest/)

### Déploiement

1. Faites une copie du fichier de déclaration des variables d'environnement :

```
cp sample.env .env
```

2. Configurez les variables d'environnement dans `.env` (vous pouvez aussi les déclarer directement dans votre système)  
3. Installez les dépendances :

```bash
pipenv install
```

4. Démarrez l'application

```bash
pipenv run run.py
```

### Notes de versions

**1.12 - 31/05/2023**
- Amélioration du filtrage des brouillons qui n'était pas appliqué sur les autre types de bordereaux que BSDD

**1.11 - 11/04/2023**
- Ajout des déchets avec codes non dangereux mais dont la case "ce déchet est dangereux"
a été cochée sur le bordereau
- Modification du calcul de la quantité totale de déchets traités, la date de traitement est maintenant utilisée plutôt que la date de création du bordereau
- Correction du calcul de la date de mise à jour
- Prise en compte de l'uniformisation des codes opérations de traitement

**1.10 - 06/03/2023**
- Amélioration de la lisibilité des graphiques hebdomadaires
- Ajout d'un graphique TreeMap pour la quantité de déchets traités par code NAF
- Refonte complète du preprocessing des graphiques TreeMap

**1.9 - 16/02/2023**
- Les données 2023 sont maintenant affichées par défaut
- La mise en page a été légèrement revue
- Ajout de nouvelles courbes
- Ajout d'une page de statistiques avancées (bêta)
- Amélioration des performances et diminution de l'empreinte 
mémoire en remplaçant Pandas par Polars pour le traitement des données

**1.8 - 26/01/2023**
- Ajout d'onglets pour visualiser les données par années
- Ajout de trois métriques globales
- Amélioration de la lisibilité des graphiques
- Meilleure intégration du DSFR (v1.8.5)
- Architecture de l'application revue pour permettre un passage en application "multi-pages"

<details><summary>Voir les anciennes notes de versions</summary>
<p>

**1.7 - 14/11/2022**
- Ajout du nombre de bordereaux envoyés et traités
- Ajout de la quantité totale de déchet traités ventilée par type de traitement
- Ajout du nombre d'établissements inscrits en fonction de leur type d'activité

**1.6 - 12/07/2022**
- Ajout des données sur les autres bordereaux
- Revue du layout avec le design system de l'état

**1.5.1 - 12/07/2022**
- Suppression de toute mention de cache


**1.5.0 - 07/07/2022**
- Refactoring complet de l'application
- Changement de la logique d'actualisation des données

**1.4.0 - 13/06/2022**

- correction de la récupération des données (variables globales => fonction)
- stats internes BSDD
- modularisation du code

**1.3.0 - 29/03/2022**

- ajout du [design système de l'État](https://gouvfr.atlassian.net/wiki/spaces/DB/overview?homepageId=145359476)

**1.2.0 - 15/03/2022**

- utilisation de gunicorn comme Web server
- séparation des requêtes BSDD créés et BSDD générés pour des résultats plus précis

**1.1.2 - 10/03/2022**

- filtrage des BSDD dont la date de traitement `processedAt` est en l'an 0001 ([#3](https://github.com/MTES-MCT/trackdechets-public-stats/issues/3))

**1.1.1 - 10/03/2022**

- ajout du support des fuseaux horaires (lié à [ceci](https://github.com/MTES-MCT/trackdechets/commit/cef32f2bcddbf60a4a214c243c149bf6e4f32c8b) et [cela](https://github.com/MTES-MCT/trackdechets/blob/34785171b8495b707b9339d2e14d2e211f0d4777/back/prisma/migrations/56_fix_timestamp_zone.sql))

**1.1.0 - 09/03/2022**

- améliorations esthétiques
- correction d'aberrations dans le volume de déchets traités

**1.0.0 - 01/02/2022**

- première publication


</p>
</details>

