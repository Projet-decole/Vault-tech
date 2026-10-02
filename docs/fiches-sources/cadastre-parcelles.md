# Fiche source — Cadastre Etalab : parcelles

| | |
|---|---|
| **Producteur** | DGFiP, diffusé par Etalab (cadastre.data.gouv.fr) |
| **Licence** | Licence Ouverte Etalab 2.0 |
| **Accès** | `https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/communes/{dep}/{insee}/cadastre-{insee}-parcelles.json.gz` |
| **Format** | GeoJSON `FeatureCollection`, gzippé |
| **Projection** | WGS84 (EPSG:4326) : aucun `crs` déclaré, c'est le défaut du GeoJSON |
| **Géométrie** | `Polygon` (100 % des 4 210 parcelles de Veckring) — prévoir quand même `MultiPolygon` ailleurs |
| **Mise à jour** | Millésimes datés, plusieurs fois par an. `latest` redirige (HTTP 302) vers le millésime courant : **2026-06-01** au 2026-09-25 |
| **Volume périmètre** | ~6 Mo gzippés pour les 6 communes (Metz 2,1 Mo, Thionville 2,0 Mo, Veckring 0,3 Mo) |

## Clé d'identification : `id` (14 caractères)

```
57704 000 01 0142
│     │   │  └── numéro de parcelle, complété à 4 chiffres
│     │   └───── section, complétée à 2 caractères
│     └───────── préfixe (000 sauf communes fusionnées/associées)
└─────────────── code INSEE de la commune (département 57 + commune 704)
```

Règle vérifiée sur les 4 210 parcelles de Veckring :
`id == commune + prefixe + lpad(section, 2, '0') + lpad(numero, 4, '0')`.

## Champs (`properties`)

| Champ | Type | Exemple | Retenu | Remarque |
|---|---|---|---|---|
| `id` | texte | `57704000010142` | ✅ | clé unique (4 210 / 4 210) |
| `commune` | texte | `57704` | ✅ | code INSEE, jointure avec le périmètre |
| `prefixe` | texte | `000` | ✅ | |
| `section` | texte | `1` | ✅ | **non complété** (≠ forme dans l'id) |
| `numero` | texte | `142` | ✅ | **non complété** |
| `contenance` | entier | `2322` | ✅ | surface cadastrale en m² (déclarative, ≠ surface géométrique) |
| `arpente` | booléen | `false` | ✅ | parcelle arpentée (19 / 4 210 à Veckring) |
| `created` / `updated` | date `AAAA-MM-JJ` | `2014-03-24` | ✅ | à caster en date |
| `geometry` | Polygon | | ✅ | conservée en texte GeoJSON jusqu'au silver |

## Pièges repérés

- **Un seul gros objet JSON.** Spark ne sait pas découper une `FeatureCollection` : il faut la convertir en JSON Lines (une feature par ligne) dès l'ingestion.
- **Codes en texte.** `commune`, `section`, `numero` et `id` sont des chaînes. Les lire en entier ferait perdre les zéros de tête : préfixe `000` → `0`, et dans l'Ain l'INSEE `01053` → `1053`.
- **Code INSEE ≠ code postal.** Thionville : INSEE `57672`, postal `57100`.
- **Tracer le millésime.** `latest` bouge dans le temps. Il faut enregistrer l'URL finale après redirection (`.../2026-06-01/...`) dans `_source_url`.
- **Paris, Lyon, Marseille : découpage par arrondissement.** Le fichier de la ville entière n'existe pas (`69123` → 404) ; il faut les codes des arrondissements municipaux (Lyon 1er = `69381` … 9e = `69389`), obtenus via `geo.api.gouv.fr/communes?codeDepartement=69&type=arrondissement-municipal`.
- **Communes nouvelles (fusions).** Ex. Oullins-Pierre-Bénite (`69149`, 2024) : vérifier que le code existe bien dans le millésime cadastral utilisé.
- **Résolution des noms.** `geo.api.gouv.fr?nom=Metz` renvoie *Metzing* en premier : ne jamais prendre le premier résultat à l'aveugle.
