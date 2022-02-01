# Statistiques publiques Trackdéchets

**version 1.0.0**

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
cp sample.env.sh env.sh
```

2. Configurez les variables d'environnement dans `env.sh` 
3. Créez l'environnement

```bash
pipenv shell
pipenv install
```

4. Démarrez l'application

```bash
./start.sh
```
