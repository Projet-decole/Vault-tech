# Recherche exploratoire (hors domaine assigné) — Pistes de données nouvelles

> Rapport de recherche libre pour la plateforme HOMEPEDIA. Objectif : repérer des sources ou des axes non anticipés par les 5 domaines déjà traités (géologie, risques naturels, urbanisme, isolement/accessibilité, bunkers existants).
> Date de recherche : 2026-09-16.
> Méthode : recherches croisées sur des thématiques adjacentes non explicitement demandées, pour identifier des angles d'analyse manquants au découpage actuel du projet.

---

## Découverte la plus significative : un répertoire historique des abris antiatomiques existe déjà

**Bâtiments susceptibles d'être utilisés comme abri atomique (1964-1973)**
- Organisme : ancienne Direction de la Sécurité Civile (Ministère de l'Intérieur), archives conservées aux Archives Nationales
- URL : https://francearchives.gouv.fr/findingaid/49e76783d91bd9cfd9fc519c08b9e51aef89688a
- Format : fonds d'archives papier (inventaire consultable en ligne, pas de SIG numérique)
- Granularité : bâtiment recensé, classé par département et arrondissement, distinction zones urbaines/rurales
- Fréquence : figé (recensement historique 1964-1973, non réactualisé depuis)
- Licence : archives publiques consultables (conditions de consultation/reproduction à vérifier auprès des Archives Nationales)
- Statut : ⚠️ Source historique non numérisée en SIG — **piste à fort potentiel** pour le domaine "Bunkers et structures militaires existantes" : ce recensement d'époque a identifié des bâtiments (souvent des caves, parkings ou sous-sols d'immeubles publics) pressentis pour un usage d'abri, dont certains pourraient toujours exister et être documentés
- Complément : selon le Sénat, environ 600 structures recensées comme abris sont de nature militaire, ce qui limite leur accessibilité publique — un rapport sénatorial sur le sujet serait à identifier précisément pour compléter cette piste

**Pourquoi c'est une découverte utile** : ce fonds n'apparaît dans aucune des pistes de recherche initiales données pour le domaine "bunkers existants" — il constitue une source historique complémentaire à Wikimaginot et aux inventaires du Mur de l'Atlantique, orientée cette fois sur le patrimoine de la Guerre Froide plutôt que de la Seconde Guerre mondiale.

---

## Autres pistes découvertes par thème

### 1. Réseaux souterrains existants — donnée manquante critique avant tout creusement

**Guichet unique des réseaux et canalisations**
- Organisme : INERIS, pour le compte de l'État (Ministère chargé de l'environnement)
- URL : https://www.reseaux-et-canalisations.gouv.fr/ (portail public) et https://www.reseaux-et-canalisations.ineris.fr/ (plateforme technique)
- Format : plateforme de déclaration DT-DICT, consultation cartographique en ligne
- Granularité : réseau ponctuel/linéaire (aérien, souterrain, subaquatique), tous exploitants confondus
- Fréquence : mise à jour continue par les exploitants de réseaux (obligation réglementaire)
- Licence : accès public pour la consultation de zone, mais les données précises de tracé restent réservées aux déclarants DT-DICT (maîtres d'ouvrage/exécutants de travaux) pour des raisons de sécurité
- Statut : ✅ Active — **angle totalement absent des 5 domaines précédents** : avant tout creusement de bunker, il est réglementairement obligatoire de vérifier l'absence de réseaux enterrés (gaz, électricité, fibre, eau) sur l'emprise du projet ; pourrait justifier un domaine ou sous-axe dédié "compatibilité technique du sous-sol avec les réseaux existants"

### 2. Sites et sols pollués — angle absent du domaine géologie (qui traite la nature du sol, pas sa contamination)

**BASIAS / CASIAS — anciens sites industriels et activités de service**
- Organisme : BRGM, diffusé via Géorisques
- URL : https://www.georisques.gouv.fr/donnees/bases-de-donnees/inventaire-historique-de-sites-industriels-et-activites-de-service et export sur data.gouv.fr
- Format : fichier "léger" (tous sites, informations restreintes) et fichiers régionaux complets, GeoJSON
- Granularité : site industriel ponctuel, historique (activités passées, pas nécessairement pollution avérée)
- Fréquence : recensement historique par enquêtes départementales, mise à jour ponctuelle
- Licence : Ouverte (Etalab)
- Statut : ✅ Active

**BASOL — pollution suspectée ou avérée**
- Organisme : Ministère chargé de l'environnement / DREAL
- URL : https://www.data.gouv.fr/datasets/information-de-ladministration-concernant-une-pollution-suspectee-ou-averee-ex-basol et https://www.georisques.gouv.fr/articles-risques/pollutions-sols-sis-anciens-sites-industriels/basol
- Format : CSV/SIG
- Granularité : site ponctuel nécessitant une action de l'administration (pas exhaustif — ne couvre que les cas remontés)
- Fréquence : mise à jour continue
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — pertinent pour vérifier qu'un terrain n'a pas d'antécédent industriel/pollution avant creusement d'un ouvrage habité en permanence

### 3. Risques technologiques — angle distinct des risques naturels (non couvert par le domaine "Risques naturels")

**Base des installations classées (ICPE) et sites SEVESO**
- Organisme : Ministère chargé de l'environnement, diffusé via Géorisques
- URL : https://www.georisques.gouv.fr/donnees/bases-de-donnees et https://www.data.gouv.fr/datasets/base-des-installations-classees-icpe ; portail dédié SEVESO : https://seveso3.din.developpement-durable.gouv.fr/
- Format : GeoJSON/CSV
- Granularité : établissement ponctuel (précision de géolocalisation variable, parfois seulement à la commune)
- Fréquence : mise à jour continue
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — un terrain trop proche d'un site Seveso "seuil haut" est exposé à un risque d'accident industriel majeur (explosion, nuage toxique), pertinent en négatif (à éviter) mais aussi potentiellement en positif si le projet s'intéresse aux terrains militaires/industriels désaffectés reconvertis

**PPI — Plans Particuliers d'Intervention (nucléaire civil et sites industriels majeurs)**
- Organisme : Préfectures / ASNR (Autorité de sûreté nucléaire et de radioprotection)
- URL : exemples par centrale sur data.gouv.fr (ex. https://www.data.gouv.fr/datasets/carte-ppi-paluel-et-penly-2025), pas de jeu de données national unique identifié
- Format : SIG par site (Shapefile/PDF), périmètres concentriques (2 km, 5 km, 20 km depuis 2019 pour les centrales nucléaires)
- Granularité : zone concentrique autour de chaque site à risque
- Fréquence : mise à jour lors des révisions de plan (extension récente à 20 km)
- Licence : Ouverte, mais diffusion dispersée site par site
- Statut : ⚠️ Active mais **non centralisée nationalement** — nécessiterait une agrégation manuelle des PPI publiés préfecture par préfecture pour toutes les centrales nucléaires et sites Seveso seuil haut

### 4. Espaces naturels protégés — contrainte de constructibilité non couverte par le domaine urbanisme (qui couvre le PLU/SUP mais pas les zonages environnementaux)

**INPN — Natura 2000, réserves naturelles, espaces protégés**
- Organisme : MNHN (Muséum National d'Histoire Naturelle) — Inventaire National du Patrimoine Naturel
- URL : https://inpn.mnhn.fr/telechargement/cartes-et-information-geographique/cons/natura et exports data.gouv.fr (ex. https://www.data.gouv.fr/datasets/inpn-donnees-du-programme-natura-2000, https://www.data.gouv.fr/datasets/espaces-naturels-proteges)
- Format : Shapefile/GeoJSON, flux WMS/WFS
- Granularité : zone protégée (ZPS, ZSC, réserve naturelle nationale/régionale, parc national, arrêté de protection de biotope...)
- Fréquence : mise à jour continue
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — un terrain en zone Natura 2000 ou réserve naturelle est soumis à évaluation environnementale et fortement contraint pour tout terrassement, information absente des fiches SUP classiques du GPU (les zonages environnementaux ne sont pas toujours répertoriés comme SUP)

### 5. Potentiel géothermique — nouvel axe "autonomie énergétique" non anticipé

**Cartographie du potentiel géothermique (BRGM / géothermies.fr)**
- Organisme : BRGM / ADEME
- URL : https://www.geothermies.fr/ et outils cartographiques régionaux du BRGM (ex. cartographie du potentiel à l'échelle de la parcelle)
- Format : cartes interactives web, données sous-jacentes partiellement en SIG selon les régions
- Granularité : variable, certaines cartographies vont jusqu'à l'échelle parcellaire pour la géothermie de surface (sondes verticales)
- Fréquence : mise à jour par campagne régionale
- Licence : à vérifier selon la région (portail national géothermies.fr en accès libre pour la consultation)
- Statut : ⚠️ Active mais couverture et niveau de détail hétérogènes — pertinent si le projet veut valoriser l'autonomie énergétique d'un bunker (chauffage/climatisation géothermique), axe non demandé jusqu'ici mais potentiellement attractif pour la clientèle visée

### 6. Sécurité et accès aux services — enrichit le domaine "isolement/accessibilité" sous un angle non couvert

**Statistiques de délinquance communale (SSMSI)**
- Organisme : Service Statistique Ministériel de la Sécurité Intérieure (Ministère de l'Intérieur)
- URL : https://www.data.gouv.fr/datasets/bases-statistiques-communale-departementale-et-regionale-de-la-delinquance-enregistree-par-la-police-et-la-gendarmerie-nationales
- Format : CSV
- Granularité : commune, depuis 2016
- Fréquence : mise à jour annuelle
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — ⚠️ couverture partielle selon les catégories d'infraction (30 à 91 % des communes selon le type de délit en 2025) ; complète la notion de "discrétion" par celle de "sécurité perçue du secteur", un critère probablement recherché par la clientèle visée

**Base Permanente des Équipements (BPE) — INSEE**
- Organisme : INSEE
- URL : https://www.data.gouv.fr/datasets/base-permanente-des-equipements
- Format : CSV, géolocalisé
- Granularité : équipement/service ponctuel, 235 types classés en 7 grands domaines (dont santé et secours), échelle commune/IRIS
- Fréquence : mise à jour annuelle
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — beaucoup plus riche et structurée que les pistes envisagées initialement pour "l'accès aux infrastructures en cas de crise" : permet de calculer précisément la distance aux hôpitaux, casernes de pompiers, gendarmeries, commerces essentiels

---

## Recommandation

Deux pistes ressortent comme suffisamment riches et distinctes pour mériter d'être formalisées en **domaines à part entière** plutôt que de rester des ajouts dispersés dans les domaines existants :

1. **Compatibilité technique du sous-sol (réseaux enterrés + pollution des sols)** — regrouperait le guichet unique des réseaux et BASIAS/BASOL/CASIAS, aujourd'hui à cheval entre le domaine géologie et le domaine urbanisme sans être couvert par aucun des deux.
2. **Risques technologiques et nucléaires** — regrouperait ICPE/SEVESO et les PPI, actuellement absents du domaine "Risques naturels" qui, comme son nom l'indique, exclut le risque d'origine industrielle ou nucléaire civile.

Les autres découvertes (Natura 2000, géothermie, délinquance, BPE) peuvent en revanche être **intégrées comme enrichissements** aux domaines déjà traités (urbanisme pour Natura 2000, isolement/accessibilité pour délinquance et BPE) sans nécessiter de domaine séparé.

La découverte du répertoire d'abris antiatomiques 1964-1973 mérite d'être signalée en priorité à l'agent en charge du domaine "Bunkers et structures militaires existantes" pour enrichir son rapport avec cette piste patrimoniale de la Guerre Froide, absente de sa liste de pistes initiale.
