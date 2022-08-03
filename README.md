# Statistiques publiques Trackdéchets

**version 1.6**

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

**1.6 12/07/2022**
- Ajout des données sur les autres bordereaux
- Revue du layout avec le design system de l'état

**1.5.1 12/07/2022**
- Suppression de toute mention de cache


**1.5.0 07/07/2022**
- Refactoring complet de l'application
- Changement de la logique d'actualisation des données

**1.4.0 13/06/2022**

- correction de la récupération des données (variables globales => fonction)
- stats internes BSDD
- modularisation du code

**1.3.0 29/03/2022**

- ajout du [design système de l'État](https://gouvfr.atlassian.net/wiki/spaces/DB/overview?homepageId=145359476)

**1.2.0 15/03/2022**

- utilisation de gunicorn comme Web server
- séparation des requêtes BSDD créés et BSDD générés pour des résultats plus précis

**1.1.2 10/03/2022**

- filtrage des BSDD dont la date de traitement `processedAt` est en l'an 0001 ([#3](https://github.com/MTES-MCT/trackdechets-public-stats/issues/3))

**1.1.1 10/03/2022**

- ajout du support des fuseaux horaires (lié à [ceci](https://github.com/MTES-MCT/trackdechets/commit/cef32f2bcddbf60a4a214c243c149bf6e4f32c8b) et [cela](https://github.com/MTES-MCT/trackdechets/blob/34785171b8495b707b9339d2e14d2e211f0d4777/back/prisma/migrations/56_fix_timestamp_zone.sql))

**1.1.0 09/03/2022**

- améliorations esthétiques
- correction d'aberrations dans le volume de déchets traités

**1.0.0 01/02/2022**

- première publication
