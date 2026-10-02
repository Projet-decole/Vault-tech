# Recensement des données ouvertes — Domaine : Accessibilité et discrétion du terrain

> Rapport de recherche pour la plateforme HOMEPEDIA (évaluation de terrains à vocation bunker/abri).
> Domaine assigné : isolement, confidentialité et accessibilité pratique — densité de population, distance aux axes/villes, discrétion visuelle, trafic aérien/zones réglementées, infrastructures de crise, couverture réseau, occupation du sol.
> Date de recherche : 2026-09-16.

---

## PARTIE 1 — Données pertinentes

| Donnée | Utilité pour l'évaluation d'un terrain bunker |
|---|---|
| **Densité de population fine (carroyage 200 m)** | Mesure directe de l'isolement réel autour du terrain, plus précise que la densité communale moyenne |
| **Population légale par commune / IRIS** | Complète le carroyage pour une vision socio-démographique du secteur (âge, revenu, structure des ménages) |
| **Zonage en aires d'attraction des villes (pôle / couronne / hors attraction)** | Indique la distance fonctionnelle à une agglomération et le niveau de dépendance à un pôle urbain |
| **Réseau routier hiérarchisé (autoroutes, nationales, départementales, chemins)** | Calcule la distance et le temps d'accès réels aux axes principaux ; un accès discret nécessite un chemin secondaire mais praticable |
| **Boisement et couvert forestier (BD Forêt)** | Le boisement dense est le principal facteur de dissimulation visuelle d'un terrain |
| **Relief et modèle numérique de terrain (MNT/RGE ALTI)** | Une topographie encaissée (vallon, dépression) renforce la discrétion visuelle et acoustique |
| **Occupation du sol détaillée (BD TOPO, Corine Land Cover)** | Distingue zones urbaines, agricoles, forestières, naturelles — cadre la nature de l'environnement immédiat |
| **Couverture réseau mobile (2G/3G/4G/5G) et localisation des antennes-relais** | Un usage occasionnel du bunker nécessite une couverture minimale, mais une zone totalement non couverte accroît la discrétion (compromis à arbitrer) |
| **Zones réglementées/interdites de l'espace aérien (P/R/D)** | Une zone militaire ou réglementée à proximité peut impliquer une surveillance aérienne accrue à éviter, ou au contraire un no-fly zone civil protecteur |
| **Carte des restrictions de vol pour drones** | Indique si le terrain est survolable par des drones de loisir/photographie (enjeu de discrétion vis-à-vis d'une observation aérienne informelle) |
| **Localisation des aérodromes, aéroports et hélistations** | Un aérodrome proche augmente le trafic aérien (visibilité) mais offre aussi une infrastructure d'évacuation/accès rapide en cas de crise |
| **Points d'eau incendie / bornes incendie** | Infrastructure de sécurité utile en cas de crise, indicateur indirect du niveau d'équipement du secteur |
| **Présence de caméras de surveillance publiques (voie publique, bâtiments publics)** | Un secteur vidéosurveillé réduit fortement la discrétion d'accès au terrain |
| **Trafic aérien commercial/militaire réel (couloirs aériens, statistiques de survol)** | Complète le zonage réglementaire par la fréquentation effective de l'espace aérien local |

---

## PARTIE 2 — Sources trouvées

### 🇫🇷 Sources françaises

**1. INSEE — Données carroyées à 200 m (Filosofi)**
- Organisme : INSEE
- URL : https://www.insee.fr/fr/statistiques/2520034 (page de référence) et exports sur https://www.data.gouv.fr/datasets/anciennes-donnees-carroyees-a-200-m-sur-la-population
- Format : Shapefile/GeoPackage, grille de carreaux 200 m (agrégeable en carreaux 1 km)
- Granularité : carreau de 200 m × 200 m — la plus fine disponible en population sur tout le territoire
- Fréquence : mise à jour par millésime (dernier jeu basé sur Filosofi, périodicité pluriannuelle)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — ⚠️ certaines cellules à faible population sont imputées/masquées pour raison de confidentialité statistique (indicateur `I_est_cr`)

**2. INSEE — Contours IRIS**
- Organisme : INSEE / IGN (co-édition)
- URL : https://www.data.gouv.fr/datasets/contours-iris-insee-ign/
- Format : Shapefile/GeoJSON
- Granularité : IRIS (îlot d'environ 2 000 habitants ; communes de moins de 10 000 habitants non subdivisées)
- Fréquence : mise à jour annuelle
- Licence : Ouverte (Etalab)
- Statut : ✅ Active

**3. INSEE — Zonage en aires d'attraction des villes (AAV 2020)**
- Organisme : INSEE
- URL : https://www.data.gouv.fr/datasets/aires-dattraction-des-villes-2020-aav-par-communes et version enrichie https://www.data.gouv.fr/datasets/zonage-en-aires-dattraction-des-villes-france-entiere-enrichi-zaav-2020
- Format : CSV, jointure par code commune (INSEE)
- Granularité : commune, classée par pôle/couronne/hors attraction et par taille d'aire (Paris, +700 000 hab., +200 000 hab., +50 000 hab.)
- Fréquence : refonte décennale (dernière : 2020, méthode harmonisée Eurostat/OCDE)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — bon proxy de l'éloignement fonctionnel à une ville

**4. ANFR / Arcep — Cartoradio et Mon Réseau Mobile**
- Organisme : ANFR (Agence Nationale des Fréquences) / Arcep
- URL : https://www.data.gouv.fr/datasets/cartographie-nationale-des-antennes-relais-de-telephonie-mobile (antennes) et https://monreseaumobile.arcep.fr/ (couverture par opérateur)
- Format : CSV/SIG pour les antennes (coordonnées, altitude, opérateur, technologies 2G/3G/4G/5G, bande de fréquence) ; carte interactive + open data pour la couverture simulée et mesurée
- Granularité : site radioélectrique ponctuel (base BNIR) ; couverture par petite maille pour Mon Réseau Mobile
- Fréquence : mise à jour continue (autorisations ANFR) et périodique pour les mesures de qualité de service Arcep
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — permet de croiser isolement géographique et niveau de couverture réseau

**5. IGN — BD TOPO**
- Organisme : IGN
- URL : https://geoservices.ign.fr/bdtopo (téléchargement) et https://cartes.gouv.fr/
- Format : Shapefile/GeoPackage, modélisation 2D/3D du territoire (routes hiérarchisées, bâti, hydrographie, réseaux)
- Granularité : objet vectoriel précis (échelle infra-métrique pour le réseau routier)
- Fréquence : mise à jour continue, livraisons régulières
- Licence : Ouverte et gratuite depuis le 1er janvier 2021 (Licence Ouverte Etalab)
- Statut : ✅ Active — source de référence pour calculer précisément les distances aux axes routiers

**6. IGN — BD Forêt (V2)**
- Organisme : IGN
- URL : https://geoservices.ign.fr/bdforet
- Format : Shapefile
- Granularité : peuplement forestier (essence dominante, structure), unité minimale de quelques ares selon les zones
- Fréquence : mise à jour par département, cycle pluriannuel
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — indicateur clé de dissimulation visuelle par la végétation

**7. IGN — RGE ALTI (Modèle Numérique de Terrain)**
- Organisme : IGN
- URL : https://geoservices.ign.fr/rgealti
- Format : raster (GeoTIFF/ASCII grid), résolution 1 m ou 5 m selon les zones
- Granularité : pixel de 1 à 5 m — permet de calculer pentes, encaissement, lignes de vue (analyse de visibilité/viewshed)
- Fréquence : mise à jour par campagne de levé (LiDAR HD en cours de généralisation)
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — essentiel pour une analyse de discrétion visuelle par modélisation de visibilité (viewshed analysis)

**8. CORINE Land Cover (CLC)**
- Organisme : Copernicus (programme européen), déclinaison française diffusée par le Ministère chargé de l'environnement
- URL : https://www.data.gouv.fr/datasets/corine-land-cover-occupation-des-sols-en-france et portail Copernicus Land Monitoring Service
- Format : raster (GeoTIFF), vecteur (Shapefile/SQLite), flux WMS/WMTS/WFS
- Granularité : résolution 20 m, unité cartographique minimale de 25 ha (44 postes de nomenclature) ; nouvelle génération CLC+ en cours à 10 m
- Fréquence : millésimes 1990, 2000, 2006, 2012, 2018 (CLC+ vise un cycle de 3 ans)
- Licence : Ouverte (Copernicus / Etalab)
- Statut : ✅ Active — utile pour une vision européenne comparable si le projet s'étend hors de France

**9. SIA — Données d'espace aérien (zones P/R/D)**
- Organisme : Service de l'Information Aéronautique (SIA), DGAC
- URL : https://www.data.gouv.fr/datasets/donnees-despace-aerien-de-la-base-aeronautique-du-sia et https://www.sia.aviation-civile.gouv.fr/ (eAIP France, section ENR 5.1)
- Format : XML_SIA et AIXM 4.5 (norme Eurocontrol)
- Granularité : zone d'espace aérien (polygone 3D avec plafond/plancher)
- Fréquence : cycle AIRAC de 28 jours (mise à jour et validité de 4 semaines)
- Licence : Ouverte, réservée à un usage non aéronautique de sécurité (les usages opérationnels de navigation doivent utiliser la donnée à jour officielle)
- Statut : ✅ Active — identifie les zones interdites (P), réglementées (R) ou dangereuses (D), notamment militaires

**10. Géoportail / DGAC — Carte des restrictions UAS (drones)**
- Organisme : DGAC, en collaboration avec l'IGN
- URL : couche "Restrictions UAS — catégorie Ouverte et Aéromodélisme" sur https://www.geoportail.gouv.fr/ ou https://cartes.gouv.fr/
- Format : couche cartographique interactive (WMS), consultable en ligne
- Granularité : zone de restriction (0 à 150 m d'altitude en métropole)
- Fréquence : mise à jour par arrêté, ⚠️ ne couvre pas les restrictions temporaires ni certains arrêtés préfectoraux locaux (survol de plages, monuments historiques)
- Licence : Ouverte
- Statut : ⚠️ Active mais incomplète (limitations explicitement signalées par la DGAC elle-même)

**11. DGAC — Aéroports et aérodromes régionaux**
- Organisme : DGAC
- URL : https://www.data.gouv.fr/fr/datasets/aeroports-et-aerodromes-regionaux/ et organisation DGAC sur data.gouv.fr
- Format : CSV/SIG
- Granularité : aérodrome ponctuel (coordonnées, statut, code OACI)
- Fréquence : mise à jour occasionnelle
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — à croiser avec le tag OSM `aeroway=helipad` (voir source suivante) pour les hélisurfaces non répertoriées officiellement

**12. OpenStreetMap — Overpass API (routes, POI, points d'eau incendie, hélisurfaces)**
- Organisme : communauté OpenStreetMap France
- URL : https://overpass.openstreetmap.fr/api/interpreter (instance française) ou https://overpass-api.de/
- Format : Overpass QL, export GeoJSON/OSM XML
- Granularité : objet ponctuel/linéaire déclaratif (`emergency=fire_hydrant` pour les points d'eau incendie, `aeroway=helipad` pour les hélisurfaces, réseau routier complet avec classification)
- Fréquence : temps réel (édition continue communautaire)
- Licence : ODbL
- Statut : ✅ Active — très riche pour les points d'eau incendie et hélisurfaces informelles, mais couverture hétérogène et non garantie exhaustive (dépend des contributeurs locaux)

---

## Synthèse — Données non couvertes par une source identifiée à ce stade

- **Localisation des caméras de vidéosurveillance publiques** : aucune base nationale ouverte n'a été identifiée, et c'est attendu — ce type de donnée relève de la sécurité publique et n'est pas publié en open data pour des raisons évidentes de prévention (seules des initiatives citoyennes locales et non exhaustives existent parfois sur OpenStreetMap avec le tag `man_made=surveillance`, à couverture très partielle et non fiable).
- **Trafic de drones civils en temps réel ou statistiques de survol par zone** : aucune source ouverte identifiée ; seule la réglementation (zones autorisées/interdites) est disponible, pas la fréquentation réelle.
- **Restrictions de vol temporaires et arrêtés préfectoraux locaux (drones, survols)** : explicitement absents de la couche Géoportail/DGAC — nécessitent une consultation préfecture par préfecture, non centralisée.
- **Qualité de service réseau mesurée en un point précis hors zones déjà testées** : Mon Réseau Mobile fournit une simulation de couverture et des mesures de qualité sur les axes/lieux fréquentés, mais pas une garantie de mesure réelle pour un point isolé quelconque — une mesure terrain resterait nécessaire pour un terrain très reculé.
- **Cartographie nationale consolidée des hélisurfaces privées/agricoles non officielles** : partiellement couvertes par OpenStreetMap de façon non exhaustive, sans registre officiel équivalent aux aérodromes DGAC.
- **Trafic aérien militaire réel (couloirs d'entraînement, fréquentation effective des zones R/D)** : le zonage réglementaire est public, mais les données de fréquentation opérationnelle réelle relèvent du secret défense et ne sont pas publiées.
