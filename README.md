# Statistiques publiques Trackdéchets

**version 1.1.0**

> Application basée sur Plotly Dash consacrée à la publication d'un tableau de bord illustrant l'activité de [l'application
> Trackdéchets](https://app.trackdechets.beta.gouv.fr/). Ce tableau de bord vise à donner au grand public aux
> professionnels du déchet un aperçu du cycle de vie des déchets en France.

### Pré-requis

- python 3.9
- pip
- [pipenv](https://pipenv.pypa.io/en/latest/)

### Déploiement

1. Faites une copie du fichier de déclaration des variables d'environnement :

```
cp sample.env .env
```

2. Configurez les variables d'environnement dans `.env` (vous pouvez aussi les déclarer directement dans votre système)  
3. Créez l'environnement

```bash
pipenv shell
pipenv install
```

4. Démarrez l'application

```bash
python app.py
```

### Notes de versions

**1.1.0 09/03/2022**

- améliorations esthétiques
- correction d'aberrations dans le volume de déchets traités

**1.0.0 01/02/2022**

- première publication
