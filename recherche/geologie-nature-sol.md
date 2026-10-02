# Recensement des données ouvertes — Domaine : Géologie et nature du sol

> Rapport de recherche pour la plateforme HOMEPEDIA (évaluation de terrains à vocation bunker/abri).
> Domaine assigné : géologie et nature du sol — nature du sous-sol, nappe phréatique, portance, risques de mouvement de terrain, cavités, hydrogéologie.
> Date de recherche : 2026-09-14.

---

## PARTIE 1 — Données pertinentes

| Donnée | Utilité pour l'évaluation d'un terrain bunker |
|---|---|
| **Nature lithologique du sous-sol** (roche massive, argile, sable, limon, craie, alluvions...) | Détermine la faisabilité technique et le coût de creusement (roche dure = protection mais forage coûteux ; argile/sable = creusement facile mais soutènement nécessaire) |
| **Carte géologique structurale** (failles, pendage des couches, épaisseur des formations) | Identifie les zones de faiblesse structurelle, risques d'infiltration le long des failles |
| **Profondeur du toit rocheux / substratum** | Conditionne la profondeur maximale exploitable avant d'atteindre la roche mère |
| **Niveau piézométrique et battement de nappe (min/max saisonnier)** | Une nappe affleurante interdit ou complique fortement un ouvrage enterré (étanchéité, pompage permanent) |
| **Perméabilité / porosité du sol** | Risque d'infiltration d'eau dans l'ouvrage, drainage nécessaire |
| **Portance et résistance mécanique (essais pressiométriques, pénétrométriques, CBR)** | Dimensionnement des fondations et voûtes de l'abri |
| **Aléa retrait-gonflement des argiles (RGA)** | Risque de fissuration des structures enterrées par mouvement saisonnier du sol |
| **Aléa mouvements de terrain** (glissements, effondrements, coulées, érosion) | Risque d'instabilité rendant le terrain dangereux à long terme |
| **Cavités souterraines connues** (naturelles : grottes/karst ; artificielles : carrières, mines, sapes de guerre) | Risque d'effondrement, mais aussi opportunité de réemploi d'une cavité existante |
| **Anciennes concessions minières et risques après-mine** | Risque d'affaissement minier, remontée de nappe dans galeries noyées |
| **Sondages/forages géotechniques archivés (BSS)** | Données directes de coupe de sol déjà réalisées à proximité, évite un forage neuf |
| **Référentiel pédologique (nature et profondeur des sols agricoles)** | Complète la géologie profonde par la nature des horizons de surface |
| **Zonage sismique** | Pertinent pour le dimensionnement antisismique d'un ouvrage enterré |
| **Potentiel radon** | Gaz radioactif naturel issu du sous-sol granitique/volcanique, critique pour un espace confiné et peu ventilé comme un bunker |
| **Karst et infiltration rapide (zones calcaires)** | Risque de dissolution et d'effondrement différé (fontis) |
| **Qualité chimique des eaux souterraines** | Utile si le bunker prévoit un captage d'eau autonome |

---

## PARTIE 2 — Sources trouvées

### 🇫🇷 Sources françaises

**1. Cartes géologiques de France (harmonisées)**
- Organisme : BRGM (Bureau de Recherches Géologiques et Minières)
- URL : https://infoterre.brgm.fr/ (visualiseur) + https://infoterre.brgm.fr/page/geoservices-ogc (services OGC)
- Format : WMS, WMS-C, WFS, KML (standards OGC) ; export vectoriel possible
- Granularité : de 1/1 000 000 à 1/50 000 (échelle départementale à locale)
- Fréquence : mise à jour continue par feuilles géologiques
- Licence : Ouverte (Etalab / Licence Ouverte, accès gratuit depuis la politique de science ouverte du BRGM)
- Statut : ✅ Active

**2. Banque du Sous-Sol (BSS)**
- Organisme : BRGM
- URL : https://infoterre.brgm.fr/page/banque-sol-bss et https://www.data.gouv.fr/datasets/bss-ouvrages-de-la-banque-du-sous-sol-brgm
- Format : téléchargement par département (CSV/SIG), consultation web, fiches PDF de sondages
- Granularité : ouvrage ponctuel (forage/sondage), +800 000 ouvrages référencés
- Fréquence : alimentation continue (déclarations de sondages)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — donnée géotechnique brute très utile (coupes de sondages réels)

**3. Inventaire des cavités souterraines (BD Cavités)**
- Organisme : BRGM / GEODERIS / Université Gustave Eiffel / INERIS / Cerema / Fédération française de spéléologie — diffusé via Géorisques
- URL : https://www.georisques.gouv.fr/donnees/bases-de-donnees/inventaire-des-cavites-souterraines et https://www.data.gouv.fr/datasets/inventaire-des-cavites-souterraines
- Format : CSV, GPX, SIG (Shapefile), téléchargeable par département/région/national
- Granularité : cavité ponctuelle (coordonnées + type + statut)
- Fréquence : mise à jour continue par signalements
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — ⚠️ lacune connue sur la petite couronne parisienne (75/78/91/92/93/94/95, gérée par l'Inspection Générale des Carrières)

**4. Base de données Mouvements de Terrain (BDMVT)**
- Organisme : BRGM, diffusé via Géorisques
- URL : https://www.georisques.gouv.fr/donnees/bases-de-donnees
- Format : SIG (Shapefile), CSV
- Granularité : événement ponctuel géolocalisé (glissement, effondrement, coulée, érosion de berge)
- Fréquence : mise à jour continue
- Licence : Ouverte (Etalab)
- Statut : ✅ Active

**5. Carte d'exposition au retrait-gonflement des argiles (RGA)**
- Organisme : BRGM / Géorisques
- URL : https://www.georisques.gouv.fr/donnees/bases-de-donnees/retrait-gonflement-des-argiles et https://www.data.gouv.fr/datasets/carte-des-risques-retrait-gonflement-des-argiles
- Format : Shapefile (Lambert 93 / RGF93), PMTiles
- Granularité : nationale, découpage départemental, résolution fine (zonage jaune/orange/rouge)
- Fréquence : révision majeure — nouvel arrêté du 9 janvier 2026 mettant à jour la carte de 2020 (nouveau zonage applicable depuis le 1er juillet 2026)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active, récemment mise à jour

**6. ADES / Hub'Eau — API Piézométrie (niveaux des nappes)**
- Organisme : BRGM / Sandre / Eaufrance (portail national ADES)
- URL : https://hubeau.eaufrance.fr/page/api-piezometrie
- Format : API REST (JSON, GeoJSON, CSV)
- Granularité : station piézométrique ponctuelle (+23 000 stations), certaines en quasi temps réel (horaire)
- Fréquence : intégration quotidienne, certaines stations en temps quasi-réel
- Licence : Ouverte (Etalab, via Eaufrance)
- Statut : ✅ Active, vérifiée accessible

**7. Hub'Eau — Qualité des nappes d'eau souterraine**
- Organisme : BRGM / Eaufrance
- URL : https://hubeau.eaufrance.fr/page/api-qualite-nappes
- Format : API REST (JSON/CSV)
- Granularité : point de prélèvement
- Fréquence : continue
- Licence : Ouverte (Etalab)
- Statut : ✅ Active (utile en complément, moins directement pour la géotechnique)

**8. Référentiel Régional Pédologique (RRP) — GisSol**
- Organisme : INRAE / GIS Sol (programme IGCS)
- URL : https://gissol.hub.inrae.fr/donnees-et-outils (portail) + diffusion via Géoportail/cartes.gouv.fr (couche "Carte des sols")
- Format : base DoneSol (norme AFNOR NF X31-560), export SIG, visualisation Géoportail
- Granularité : 1/250 000, par département/région ; certains RRP plus fins existent localement
- Fréquence : mise à jour par campagne régionale (variable selon régions, certaines datant de plusieurs années)
- Licence : à vérifier au cas par cas (une partie ouverte, une partie sur demande/convention selon les régions)
- Statut : ⚠️ Active mais couverture inégale selon les départements

**9. GEODERIS — Risques miniers résiduels / après-mine**
- Organisme : GEODERIS (BRGM + INERIS)
- URL : https://geoderis.fr/ (site institutionnel) ; données également intégrées dans Géorisques (rubrique risques miniers) et data.gouv.fr (recherche "GEODERIS")
- Format : rapports PDF, SIG pour certains bassins, cartes d'aléas miniers
- Granularité : bassin minier / concession
- Fréquence : ponctuelle, par étude de bassin
- Licence : Ouverte pour les données diffusées sur Géorisques ; rapports parfois sur demande
- Statut : ⚠️ Active mais dispersée — pas un jeu de données unique et homogène au niveau national

**10. Zonage sismique de la France**
- Organisme : Ministère chargé de l'environnement / Géorisques / Géoportail
- URL : https://www.data.gouv.fr/datasets/zonage-sismique-de-la-france-1 et https://www.geoportail.gouv.fr/donnees/zones-de-sismicite
- Format : Shapefile, WMS
- Granularité : commune (5 zones de sismicité)
- Fréquence : réglementaire, en vigueur depuis le 1er mai 2011 (peu révisée depuis)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — pertinent pour dimensionnement antisismique d'un ouvrage enterré

**11. API Géorisques (agrégateur multirisque)**
- Organisme : Ministère chargé de l'environnement / BRGM
- URL : https://www.georisques.gouv.fr/doc-api et https://www.data.gouv.fr/dataservices/api-georisques
- Format : API REST (JSON), endpoint clé `GET /api/v1/resultats_rapport_risque?latlon=<lon>,<lat>` renvoyant en un seul appel 12 risques naturels (dont RGA, cavités, radon, séisme) pour un point donné
- Granularité : point géolocalisé (parcelle par géocodage inverse)
- Fréquence : continue, agrège les bases sources
- Licence : Ouverte, v1 sans jeton, v2 avec jeton gratuit (FranceConnect/Cerbère)
- Statut : ✅ Active — **la plus efficace pour interroger un terrain précis en une requête**, très recommandée pour l'architecture de la plateforme

**12. Cartographie du potentiel radon**
- Organisme : IRSN / Géorisques
- URL : intégrée dans https://www.georisques.gouv.fr/ (rubrique radon) et accessible via l'API Géorisques ci-dessus
- Format : SIG / API
- Granularité : commune (classement en 3 catégories de potentiel)
- Fréquence : cartographie stable, révisée occasionnellement
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — pertinent car un espace confiné souterrain concentre le radon, enjeu de ventilation du bunker

**13. OpenStreetMap — cavités, carrières, sites militaires**
- Organisme : communauté OpenStreetMap (via API Overpass)
- URL : https://overpass-api.de/ ; tags `natural=cave_entrance`, `landuse=quarry`, `military=bunker`, `landuse=military` (wiki : https://wiki.openstreetmap.org/wiki/Tag:natural=cave_entrance, etc.)
- Format : API Overpass QL, export GeoJSON/OSM XML
- Granularité : objet ponctuel/polygone déclaratif (couverture hétérogène, dépend des contributeurs)
- Fréquence : temps réel (édition continue)
- Licence : ODbL (Open Database License)
- Statut : ✅ Active — complément utile mais **non exhaustif et non validé scientifiquement**, à croiser avec les sources institutionnelles

### 🇪🇺 Équivalents européens / internationaux

**14. EGDI — European Geological Data Infrastructure**
- Organisme : EuroGeoSurveys (réseau des services géologiques nationaux européens)
- URL : https://www.europe-geology.eu/ (portail) et https://newegdi.geus.dk/
- Format : WMS/WFS OGC, visualiseur cartographique, +800 couches (cartes géologiques, hydrogéologie, géorisques, forages)
- Granularité : variable selon pays, généralement 1/1 000 000 harmonisé
- Fréquence : mise à jour par service géologique national contributeur
- Licence : Ouverte (majoritairement), certaines couches nationales restreintes
- Statut : ✅ Active — pertinent si le projet s'étend à d'autres pays européens

**15. OneGeology**
- Organisme : consortium international des services géologiques (initiative mondiale)
- URL : intégré désormais dans EGDI pour l'Europe (https://www.europe-geology.eu/project/onegeology-europe/) ; portail mondial historique http://www.onegeology.org/
- Format : WMS
- Granularité : 1/1 000 000 à l'échelle mondiale
- Fréquence : variable selon pays contributeur
- Licence : Ouverte selon les pays
- Statut : ⚠️ À vérifier — portail historique, activité de maintenance ralentie ces dernières années, EGDI est le point d'entrée européen actif à privilégier

---

## Synthèse — Données non couvertes par une source identifiée à ce stade

- **Portance et résistance mécanique des sols (essais géotechniques normalisés type G1-G5, pressiométrie, CBR) à l'échelle nationale** : aucune base ouverte homogène trouvée. Le Cerema produit des données géotechniques mais aucun jeu de données national structuré et librement téléchargeable n'a été localisé (à recontacter directement, ou passer par les études géotechniques ponctuelles archivées dans la BSS du BRGM, qui reste la meilleure approximation disponible).
- **Carte nationale unifiée des anciennes carrières à ciel ouvert (hors mines)** : les carrières actives sont bien couvertes par les bases ICPE/DREAL, mais un inventaire nationalisé et open data des *anciennes* carrières abandonnées non minières reste fragmenté entre BD Cavités, GEODERIS et archives départementales (Inspections des Carrières locales, notamment en Île-de-France).
- **Cartographie fine de la perméabilité/infiltration des sols** : les données hydrogéologiques disponibles (ADES, Hub'Eau) concernent surtout les niveaux de nappe et la qualité de l'eau, pas directement des coefficients de perméabilité cartographiés à l'échelle parcellaire — il faut les déduire indirectement des cartes géologiques/pédologiques ou des sondages BSS.
- **Référentiel pédologique homogène et récent sur tout le territoire** : le RRP (GisSol) a une couverture et une fraîcheur inégales selon les départements, certains n'ayant pas encore de RRP finalisé.
- **Données GEODERIS structurées en open data national** : les informations après-mine existent mais sont dispersées par bassin minier plutôt que centralisées dans un jeu de données SIG unique et téléchargeable.
