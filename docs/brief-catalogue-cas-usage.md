# Brief — Catalogue des cas d'usage HOMEPEDIA

## 1. Contexte

**HOMEPEDIA** est un projet d'école (groupe d'étudiants) : une plateforme **big data** pour les
**entreprises de construction et de rénovation de bunkers** (abris enterrés, réhabilitation d'ouvrages
militaires, abris privés…). Le principe : croiser des **sources de données ouvertes** pour qualifier des
terrains et aider ces professionnels à décider.

L'utilisateur débute en data engineering. **Sois pédagogique** : définis le jargon, donne des exemples
concrets, explique tes choix. Réponds en français.

### Ce qui existe déjà (premier jet, fonctionnel)
- Pipeline complet : sources → Mage → HDFS → Spark → PostgreSQL/PostGIS → dbt → Superset.
  Mode d'emploi : `README.md`. Plan et écarts : `PLAN_PREMIER_JET.md`.
- **2 sources** croisées : cadastre (parcelles) et BD Cavités du BRGM (cavités souterraines).
  Fiches : `docs/fiches-sources/`.
- **1 cas d'usage** réalisé : « quelles parcelles sont à moins de 200 / 500 m d'une cavité connue ? »
  → dashboard Superset (carte parcelles + cavités, % de parcelles exposées par commune, chiffre clé).
- Périmètre de test : 6 communes de Moselle (ligne Maginot), 3 du Rhône (Monts d'Or).

### Matériau de départ à lire
ATTENTION ! Ne lire qu'à partir de l'étape 2 de la méthode (Partir des sources) pour ne pas être biaiser;
- **Recensement des sources potentielles** (fait par un autre agent) :
  - artefact en ligne : https://claude.ai/artifact/1A5jMcv9rfrp9qwPCyKmFt (le lire avec l'outil Artifact, action `read`)
  - notes détaillées dans `recherche/` : `bunkers-structures-militaires.md`, `geologie-nature-sol.md`,
    `risques-naturels.md`, `urbanisme-reglementation.md`, `isolement-accessibilite.md`,
    `decouvertes-exploratoires.md` (dont un répertoire historique des abris antiatomiques).
- Contrainte technique de la plateforme : Superset (cartes deck.gl, graphiques, filtres), PostGIS pour le
  spatial, MongoDB et un stockage de fichiers (images, PDF) en cours d'ajout.

---

## 2. Objectif

Produire un **catalogue de cas d'usage** : une liste structurée de **besoins métier** que la plateforme
pourrait couvrir, où chaque membre du groupe pourra **piocher** un sujet à développer.

Un **cas d'usage** = un besoin d'un professionnel + la valeur qu'il en tire + les données qui y répondent
+ la façon de le montrer. Exemple (déjà réalisé) :

> *« Avant d'acheter un terrain, je veux savoir s'il y a une cavité souterraine à proximité »*
> → risque d'effondrement ou opportunité de réhabilitation → cadastre + BD Cavités → carte + % par commune.

---

## 3. Méthode : trois axes de recherche, puis croisement

Mène les trois axes **séparément**, puis croise-les. Fais valider par l'utilisateur à la fin de chaque axe
avant de passer au suivant (il veut comprendre et participer, pas seulement recevoir un résultat).

1. **Partir du métier → les besoins.**
   Qui sont les utilisateurs ? (commercial qui prospecte, ingénieur structure, chef de chantier, dirigeant,
   client particulier, collectivité…). Quelles décisions prennent-ils, à quel moment du cycle
   (prospection, étude de faisabilité, permis, chantier, rénovation, revente) ? Qu'est-ce qui leur coûte
   du temps ou de l'argent aujourd'hui ?
2. **Partir des sources → ce qu'elles permettent.**
   Pour chaque source du recensement, quels besoins peut-elle servir, seule ou croisée avec d'autres ?
   Repérer les croisements à forte valeur (ex. nature du sol × risque inondation × accessibilité).
   Signaler les sources inaccessibles, payantes, ou à qualité douteuse.
3. **Partir des besoins → les meilleures visualisations.**
   Pour un besoin donné, quel affichage aide vraiment à décider ? (carte choroplèthe, carte de points,
   score / jauge, fiche terrain, comparateur de communes, classement, alerte, export PDF…).
   Tenir compte de ce que Superset sait faire, et dire quand il faudrait autre chose.

---

## 4. Livrable attendu

Une **page partageable** (artefact, comme le recensement des sources), avec :

1. Une courte **introduction** : personas / utilisateurs cibles, et méthode.
2. Le **catalogue**, une fiche par cas d'usage :

| Champ | Contenu |
|---|---|
| Nom court | ex. « Stabilité du sous-sol » |
| Qui / quand | persona + moment du cycle de vie du projet |
| Besoin | la question métier, dans les mots du professionnel |
| Valeur | ce que ça change (temps gagné, risque évité, argent) |
| Sources | lesquelles, accès, et si elles sont déjà intégrées |
| Traitements | croisements, calculs (ex. distance, score pondéré) |
| Visualisation | type de graphique / dashboard proposé |
| Difficulté | faible / moyenne / forte, avec la raison |
| Priorité suggérée | valeur ÷ difficulté |

3. Une **vue d'ensemble** : matrice cas d'usage × sources (quelles sources servent à plusieurs cas),
   et une proposition de **répartition** ou de **feuille de route** (quick wins d'abord).
4. Les **angles morts** : besoins sans source identifiée.

Vise **15 à 30 cas d'usage**, de qualité inégale assumée, mais chacun actionnable.

---

## 5. Ce qu'il ne faut PAS faire
- Ne pas modifier le code, les pipelines ni la stack Docker : c'est une phase de réflexion.
- Ne pas inventer de sources : si une donnée n'existe pas en open data, le dire.
- Ne pas lancer de sous-agents sans l'accord de l'utilisateur.
