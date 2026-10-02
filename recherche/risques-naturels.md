# Recensement des données ouvertes — Domaine : Risques naturels

> Rapport de recherche pour la plateforme HOMEPEDIA (évaluation de terrains à vocation bunker/abri).
> Domaine assigné : risques naturels — sismicité réglementaire, inondation, mouvement de terrain (angle réglementaire), submersion marine/érosion côtière, volcanisme, feux de forêt, historique CatNat.
> Date de recherche : 2026-09-16.

---

## PARTIE 1 — Données pertinentes

| Donnée | Utilité pour l'évaluation d'un terrain bunker |
|---|---|
| **Zonage sismique réglementaire (5 zones, code de l'environnement)** | Impose des règles de construction parasismique (Eurocode 8 / CPMI-EC8) ; un ouvrage enterré en zone 4-5 nécessite un dimensionnement renforcé |
| **Catalogue de sismicité instrumentale récente (séismes réels observés)** | Complète le zonage réglementaire (figé depuis 2011) par l'activité sismique effective et récente d'un secteur |
| **PPRI — Plan de Prévention du Risque Inondation (zonage réglementaire)** | Interdit ou contraint fortement la construction souterraine en zone inondable (remontée de nappe, submersion de l'ouvrage) |
| **Données hydrométriques temps réel/historique (hauteurs d'eau, débits)** | Permet de vérifier objectivement la fréquence et l'intensité des crues d'un cours d'eau à proximité |
| **PPRN mouvement de terrain (zonage réglementaire officiel)** | Distinct de l'inventaire brut BDMVT (volet géologie) : donne la contrainte constructible opposable sur la parcelle |
| **PPR submersion marine (zonage réglementaire littoral)** | Un terrain immergeable lors de tempêtes/grandes marées est disqualifiant pour un bunker enterré proche du littoral |
| **Indicateur de recul du trait de côte / érosion côtière** | La loi Climat et Résilience impose des cartographies de recul à horizon 30/100 ans : un terrain menacé d'érosion perd toute pérennité |
| **Zonage de l'aléa volcanique (DOM : Guadeloupe, Martinique, Réunion, Mayotte)** | Exclut certaines zones de tout projet enterré (coulées pyroclastiques, lahars) |
| **Historique et zonage du risque feu de forêt** | Un feu de forêt n'affecte pas directement un ouvrage enterré mais impacte l'accès, les infrastructures de surface et la végétation de camouflage/isolement |
| **Historique des arrêtés CatNat par commune (depuis 1982)** | Proxy de la sinistralité réelle et récurrente d'un secteur (inondation, mouvement de terrain, sécheresse...) toutes causes confondues |
| **Procédures administratives GASPAR (PPRN/PPRT/PPRM en cours, approuvés, prescrits)** | Vue d'ensemble agrégée de toutes les procédures réglementaires de prévention des risques sur une commune |
| **Rapport de risque multi-aléas par point géolocalisé** | Permet d'interroger un terrain précis en une requête et d'obtenir la synthèse de tous les risques réglementaires |
| **Carte de Localisation des Phénomènes d'Avalanche (CLPA, zones de montagne)** | Pertinent uniquement pour les terrains de montagne, exclut certaines parcelles de tout projet permanent |

---

## PARTIE 2 — Sources trouvées

### 🇫🇷 Sources françaises

**1. API Géorisques — Rapport de risque par point géolocalisé**
- Organisme : Ministère chargé de l'environnement / BRGM
- URL : https://www.georisques.gouv.fr/doc-api et https://www.data.gouv.fr/dataservices/api-georisques
- Format : API REST (JSON) ; endpoint `GET /api/v1/resultats_rapport_risque?latlon=<lon>,<lat>` renvoyant en un appel les 12 risques naturels (inondation, séisme, RGA, radon...) et 6 risques technologiques d'un point
- Granularité : point géolocalisé (parcelle par géocodage inverse)
- Fréquence : continue, agrège les bases sources
- Licence : Ouverte (Etalab), v1 sans jeton, v2 avec jeton gratuit
- Statut : ✅ Active — **point d'entrée le plus efficace pour l'architecture de la plateforme**

**2. GASPAR — Procédures administratives relatives aux risques**
- Organisme : Ministère chargé de l'environnement, diffusé via Géorisques
- URL : https://www.georisques.gouv.fr/donnees/bases-de-donnees/procedures-administratives-relatives-aux-risques
- Format : CSV, export SIG ; dictionnaire de données publié en PDF
- Granularité : commune × type de risque (PPRN, PPRT, PPRM, radon, CatNat)
- Fréquence : alimentation continue par les services déconcentrés (DDT/DREAL)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active

**3. Géoportail de l'urbanisme (GPU) — Zonage réglementaire des PPR**
- Organisme : Ministère chargé de l'urbanisme / IGN
- URL : https://www.geoportail-urbanisme.gouv.fr/
- Format : consultation cartographique web, téléchargement des pièces écrites en PDF, flux WMS pour le zonage
- Granularité : parcelle cadastrale (génération de fiche parcelle)
- Fréquence : mise à jour continue par les collectivités/DDT
- Licence : Ouverte, consultation publique sans compte
- Statut : ✅ Active — source de référence pour le zonage PPRI/PPRN opposable

**4. Base des arrêtés de catastrophe naturelle (CatNat)**
- Organisme : Ministère chargé de l'environnement (GASPAR), diffusé via data.gouv.fr
- URL : https://www.data.gouv.fr/datasets/arretes-de-catastrophe-naturelle-par-commune et https://www.data.gouv.fr/datasets/arretes-de-catastrophe-naturelle-en-france-metropolitaine-2
- Format : CSV, jointures territoriales (EPCI, département, région)
- Granularité : commune, historique depuis 1982
- Fréquence : mise à jour régulière (dernière connue : septembre 2025)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active
- Alternative communautaire : https://www.catnat.net/ (297 240 arrêtés, mise à jour quasi immédiate après publication au Journal Officiel, mais source associative à recouper avec la donnée officielle)

**5. Zonage sismique de la France**
- Organisme : Ministère chargé de l'environnement / BRGM
- URL : https://www.data.gouv.fr/datasets/zonage-sismique-de-la-france-1 et https://www.geoportail.gouv.fr/donnees/zones-de-sismicite
- Format : Shapefile, WMS
- Granularité : commune (5 zones de sismicité, de très faible à forte)
- Fréquence : réglementaire, en vigueur depuis le 1er mai 2011, source communale non révisée récemment (dernière version connue : janvier 2015)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active mais figée réglementairement — à croiser avec la sismicité instrumentale récente (source suivante)

**6. BCSF-RéNaSS — Catalogue de sismicité instrumentale**
- Organisme : EOST (École et Observatoire des Sciences de la Terre, Strasbourg) / CNRS-INSU
- URL : https://www.franceseisme.fr/ et https://renass.unistra.fr/
- Format : catalogue consultable en ligne, export de données sismologiques
- Granularité : événement sismique ponctuel (épicentre, magnitude, intensité macrosismique)
- Fréquence : quasi temps réel (détection et localisation continues)
- Licence : CC BY 4.0
- Statut : ✅ Active

**7. Hub'Eau — API Hydrométrie (données Vigicrues)**
- Organisme : Service Central Vigicrues (ex-SCHAPI) / Eaufrance
- URL : https://hubeau.eaufrance.fr/page/api-hydrometrie et https://www.vigicrues.gouv.fr/
- Format : API REST (JSON/CSV), interrogation quasi temps réel + historique
- Granularité : station hydrométrique ponctuelle (~1700 à 3000 stations selon réseau)
- Fréquence : rafraîchissement source toutes les 5 à 60 min, requêtage Hub'Eau toutes les 2 min, profondeur d'historique d'1 mois glissant pour le temps réel (archives plus anciennes disponibles séparément)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active

**8. Géolittoral — Portail de la mer et du littoral**
- Organisme : Ministère chargé de la mer et du littoral
- URL : https://www.geolittoral.developpement-durable.gouv.fr/ (téléchargement : page "Téléchargement et flux de données")
- Format : Shapefile / GeoDataFiles (zip), flux OGC conformes INSPIRE
- Granularité : variable selon couche (façade maritime à local)
- Fréquence : mise à jour par projet/campagne
- Licence : Ouverte
- Statut : ✅ Active — contient notamment les atlas d'aléas littoraux (submersion marine + érosion) réalisés avec le BRGM sur certaines façades (ex. Bretagne)

**9. Indicateur National de l'Érosion Côtière (INEC)**
- Organisme : Cerema / Ministère chargé de l'environnement
- URL : https://www.data.gouv.fr/datasets/indicateur-national-de-lerosion-cotiere/ et https://www.geolittoral.developpement-durable.gouv.fr/indicateur-national-de-l-erosion-cotiere-premiers-a1511.html
- Format : SIG (Shapefile), couvre France métropolitaine + Guadeloupe, Martinique, Guyane, Mayotte, Réunion
- Granularité : linéaire côtier, évolution sur au moins 50 ans, analyse multi-périodes
- Fréquence : mise à jour périodique (refonte majeure récente intégrant des données locales plus fines)
- Licence : Ouverte, réutilisation libre avec mention de la source
- Statut : ✅ Active

**10. BRGM — Visualiseur d'élévation du niveau marin (sealevelrise)**
- Organisme : BRGM
- URL : https://sealevelrise.brgm.fr/slr/
- Format : viewer cartographique interactif
- Granularité : zone littorale basse
- Fréquence : projections basées sur scénarios climatiques (GIEC)
- Licence : à vérifier (consultation libre, réutilisation des données sous-jacentes non confirmée)
- Statut : ⚠️ Active — utile en complément qualitatif, pas une base téléchargeable structurée

**11. Dossier expert Volcanisme — Géorisques**
- Organisme : Ministère chargé de l'environnement / BRGM, en lien avec IPGP (OVSG, OVSM, OVPF, REVOSIMA)
- URL : https://www.georisques.gouv.fr/consulter-les-dossiers-thematiques/volcanisme
- Format : dossier documentaire, cartes d'aléa via PPRN volcaniques consultables sur le GPU (source n°3) pour Guadeloupe, Martinique, Réunion
- Granularité : commune (DOM concernés uniquement)
- Fréquence : mise à jour lors de révision des PPRN volcaniques
- Licence : Ouverte pour les zonages PPR diffusés via GPU
- Statut : ⚠️ Active mais dispersée entre le dossier documentaire national et les PPRN spécifiques à chaque DOM — pas de couche SIG nationale unique identifiée

**12. BDIFF — Base de Données sur les Incendies de Forêt en France**
- Organisme : IGN, sous pilotage des ministères chargés de la forêt et de l'intérieur (fusion 2023 avec la base Prométhée du pourtour méditerranéen)
- URL : https://bdiff.agriculture.gouv.fr/ et https://www.data.gouv.fr/datasets/base-de-donnees-sur-les-incendies-de-forets-en-france-bdiff
- Format : consultation web, export CSV/SIG
- Granularité : événement ponctuel géolocalisé + agrégation communale, historique depuis 2006
- Fréquence : mise à jour annuelle (données consolidées jusqu'à l'année précédente)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active

**13. CLPA — Carte de Localisation des Phénomènes d'Avalanche**
- Organisme : ONF (service RTM — Restauration des Terrains en Montagne), ex-Cemagref
- URL : https://www.avalanches.fr/ (portail dédié historique) — données également mobilisées dans les PPR avalanche via le GPU (source n°3)
- Format : cartes numérisées, fiches de témoignage
- Granularité : massif montagneux / phénomène ponctuel observé
- Fréquence : mise à jour continue depuis 1971, mais couverture et fraîcheur hétérogènes selon massifs
- Licence : à vérifier (consultation publique, réutilisation des données brutes non confirmée en open data structuré)
- Statut : ⚠️ Active mais uniquement pertinent pour les terrains de montagne, format peu structuré pour intégration automatisée

---

## Synthèse — Données non couvertes par une source identifiée à ce stade

- **Zonage PPR national consolidé en un jeu de données SIG unique** : le zonage réglementaire (PPRI, PPRN mouvement de terrain, PPR submersion, PPR avalanche) reste consultable commune par commune sur le Géoportail de l'urbanisme, mais aucun export national agrégé et prêt à l'emploi (type Shapefile national unique) n'a été identifié — une agrégation via scraping/API du GPU serait nécessaire côté plateforme.
- **Cartographie volcanique structurée en SIG national** : les zonages d'aléa volcanique existent (PPRN des DOM) mais sont dispersés par territoire, sans couche nationale unifiée équivalente au zonage sismique.
- **Aléa avalanche en open data structuré** : la CLPA existe depuis 1971 mais son exploitation reste largement cartographique/documentaire, sans API ni export SIG national clairement disponible en open data.
- **Historique fin de submersion marine événementielle (type CatNat mais dédié tempêtes/submersions)** : les arrêtés CatNat couvrent bien cet aléa administrativement, mais une base dédiée avec hauteurs d'eau observées lors des événements de submersion (comparable à Hub'Eau pour les crues fluviales) n'a pas été localisée à l'échelle nationale.
- **Projection du recul du trait de côte à horizon réglementaire 2050/2100 par commune (cartes L.121-22-2 du code de l'urbanisme)** : les listes de communes concernées existent, mais les cartes de recul elles-mêmes sont publiées commune par commune sans jeu de données national consolidé identifié à ce stade.
