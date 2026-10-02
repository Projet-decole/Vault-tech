# Fiche source — BD Cavités (inventaire des cavités souterraines)

| | |
|---|---|
| **Producteur** | BRGM (avec Univ. Gustave Eiffel, INERIS, CEREMA, FFS), diffusé par Géorisques |
| **Licence** | Données publiques Géorisques (Licence Ouverte) — non précisée sur la fiche data.gouv, **à confirmer** |
| **Accès retenu** | Export CSV par département : `https://www.georisques.gouv.fr/webappReport/ws/cavites/departements/{dep}/fiches.csv?` |
| **Liste des exports** | `https://www.georisques.gouv.fr/webappReport/ws/telechargement/cavites?anneemin=2003` (JSON) |
| **Format** | CSV `;`, UTF-8 **avec BOM**, fins de ligne CRLF, `;` final (colonne vide en trop) |
| **Volume** | Moselle (57) : 1 263 cavités, 0,5 Mo — Rhône (69) : 425 cavités, 0,2 Mo |
| **Mise à jour** | Continue (`dateMajCavite` par fiche) ; pas de millésime global |

## Accès testés le 2026-09-25

| Accès | État |
|---|---|
| API Géorisques v1 `/api/v1/cavites` | ❌ 503 (tout `/api/`, doc OpenAPI v1 et v2 comprises) |
| WFS BRGM `mapsref.brgm.fr/wxs/georisques/risques` (lien data.gouv) | ❌ erreur MapServer côté serveur |
| `files.georisques.fr/...` | ❌ 403 / 404 |
| **Export CSV `webappReport`** | ✅ 200 — endpoint non documenté, **fragile** |

À retester plus tard : l'API v1/v2 (JSON paginé, plus propre). Le pipeline doit isoler l'accès dans un seul bloc pour pouvoir changer de méthode sans toucher au reste.

## Clé d'identification

`id` (ex. `149042`) et `numCavite` (ex. `LORAW0003856`) sont tous deux uniques (1 263 / 1 263). **On retient `numCavite`** : c'est l'identifiant métier BRGM, stable et lisible.

## Coordonnées — ⚠ le piège principal

Les coordonnées brutes `xOuvrage/yOuvrage` sont **dans des systèmes différents selon les lignes**, indiqués par `lambertOuvrage` :

| `lambertOuvrage` | Système | EPSG | Lignes (57) |
|---|---|---|---|
| `5` | Lambert II étendu | 27572 | 1 211 |
| `7` | Lambert-93 | 2154 | 38 |
| `1` | Lambert I | 27571 | 8 |
| `6` | WGS84 (degrés) | 4326 | 1 |
| vide | — (cavités confidentielles) | — | 5 |

La colonne **`xouvl2e/youvl2e`** donne la même position **harmonisée en Lambert II étendu (EPSG:27572)** pour toutes les lignes sauf 6. Vérifié dans PostGIS : L93 brut et `l2e` tombent au même point, à moins de 1 mm près.

**Règle retenue :**
1. si `xouvl2e` est renseigné → point EPSG:27572 ;
2. sinon si `lambertOuvrage = 6` → `xOuvrage/yOuvrage` en EPSG:4326 ;
3. sinon → pas de géométrie (on garde la ligne, sans coordonnées).

La reprojection se fait dans PostGIS (`ST_Transform`), pas à la main.

## Champs retenus

| Champ | Exemple | Remarque |
|---|---|---|
| `numCavite` | `LORAW0003856` | clé |
| `nomCavite` | `Hackenberg` | |
| `typeCavite` | `ouvrage militaire` | 622 ouvrages militaires, 471 naturelles, 52 carrières, 47 ouvrages civils, 12 caves, 59 indéterminés |
| `typeCaviteAppauvri` | `ouvrage militaire` | même chose sans accents : utile pour les tests `accepted_values` |
| `natureCavite` | `puits-galeries` | |
| `statut` | `abandon` | `abandon` / `indéterminé` |
| `numInsee` | `57704` | code INSEE, toujours renseigné → filtre sur le périmètre |
| `positionnement` | `précis` | précis 1 078 / approché 163 / imprécis 18 / **centroïde de commune 4** (à exclure des calculs de distance) |
| `precisionXY` | `10` | incertitude en mètres (5 à 500) |
| `reperageGeographique` | `orifice visible` | |
| `xouvl2e`, `youvl2e` | `893204`, `2490862` | EPSG:27572 |
| `lambertOuvrage`, `xOuvrage`, `yOuvrage` | | repli (voir règle) |
| `confidentialite` | `public` | Moselle : 5 confidentielles ; Rhône : **184 sur 425** — toujours sans coordonnées |
| `dateMajCavite` | `2020-10-08` | |
| `commentaires` | | texte libre (candidat MongoDB en phase bonus) |

Écartés : champs de saisie/validation (`cUser*`, `userValidation*`, e-mails d'agents BRGM → données personnelles, à ne pas propager), `dangerosite` (vide sur 100 % des lignes).

## Comparaison des départements (2026-09-26)

| | Moselle (57) | Rhône (69) |
|---|---|---|
| Cavités | 1 263 | 425 |
| **Localisées** (utilisables sur une carte) | 1 258 | **241** |
| Confidentielles, sans position | 5 | **184 (43 %)** |
| Type dominant | ouvrage militaire (622, ligne Maginot) | ouvrage civil (291), naturelle (81) |
| Systèmes de coordonnées | 27572, 2154, 27571, 4326 | 27572, 2154 |

**Lyon (69123) : les 66 cavités sont TOUTES confidentielles** (idem la plupart de celles de
Sainte-Foy-lès-Lyon, Oullins-Pierre-Bénite, Saint-Genis-Laval). Le BRGM ne diffuse pas leur position.
Conséquence : Lyon n'apporterait aucune cavité sur la carte. Le nombre de cavités par commune reste
utilisable (compte), mais pas la distance aux parcelles.

## Cavités dans le périmètre

| Commune | INSEE | Cavités |
|---|---|---|
| Metz | 57463 | 24 |
| Hettange-Grande | 57323 | 22 |
| Veckring | 57704 | 9 (dont ouvrage du Hackenberg, casemates, blockhaus, carrières Helling) |
| Thionville | 57672 | 4 |
| Hayange | 57306 | 4 |
| Algrange | 57012 | 1 |
| Saint-Romain-au-Mont-d'Or | 69233 | 20 (18 localisées : grottes, ouvrages civils) |
| Fontaines-Saint-Martin | 69087 | 11 (ouvrages civils) |
| Poleymieux-au-Mont-d'Or | 69153 | 9 |

## Pièges repérés

- **Plusieurs projections dans une seule colonne** (voir ci-dessus).
- **Retours à la ligne dans les textes** : 11 lignes ont un saut de ligne dans un champ entre guillemets. Un lecteur ligne à ligne, ou Spark sans `multiLine`, les couperait en deux. Encore une raison de convertir en JSON Lines à l'ingestion.
- **BOM UTF-8** en tête de fichier : le premier nom de colonne devient `﻿id` si on ne lit pas en `utf-8-sig`.
- **Le fichier est départemental.** On télécharge le fichier de chaque département du périmètre (déduit du code INSEE des communes), contrairement au cadastre, qui est téléchargé commune par commune.
- **Une cavité en bordure de commune** peut être proche de parcelles de la commune voisine. Décision phase 2 : on ne filtre pas, on garde tout le département. Sur la carte Superset, une cavité est rattachée à la commune de sa parcelle la plus proche (≤ 500 m).
- **Confidentialité très variable selon le département** (5 cavités sans position en Moselle, 184 dans le Rhône) : à vérifier avant de choisir un territoire de démonstration.
- **Texte libre (`commentaires`) très inégal** : 461 fiches en Moselle en ont un (dimensions, « effondrement », « en eau », « gypse »…), **aucune** dans le Rhône (2026-09-26). La recherche plein texte (MongoDB) ne porte donc que sur les noms pour le Rhône.
