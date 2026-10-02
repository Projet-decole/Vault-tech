# Recensement des données ouvertes — Domaine : Urbanisme et réglementation de construction

> Rapport de recherche pour la plateforme HOMEPEDIA (évaluation de terrains à vocation bunker/abri).
> Domaine assigné : urbanisme et réglementation foncière — PLU/zonage, règles de construction enterrée, servitudes d'utilité publique, permis de construire, zonage agricole, cadastre.
> Date de recherche : 2026-09-16.

---

## PARTIE 1 — Données pertinentes

| Donnée | Utilité pour l'évaluation d'un terrain bunker |
|---|---|
| **Zonage PLU/PLUi (zones U, AU, A, N)** | Détermine si le terrain est constructible (zone U/AU) ou soumis à de fortes restrictions (zone A agricole, zone N naturelle) |
| **Règlement écrit du PLU (article applicable à la zone)** | Précise les règles de hauteur, d'emprise au sol, de distance aux limites séparatives — y compris pour les ouvrages enterrés, souvent traités différemment des constructions hors-sol |
| **Seuils réglementaires permis de construire / déclaration préalable (Code de l'urbanisme)** | Un abri enterré de plus de 20 m² de surface de plancher (ou emprise au sol si applicable) nécessite un permis de construire ; entre 5 et 20 m², une déclaration préalable suffit ; en-deçà et sous 1,80 m sous plafond, aucune formalité |
| **Servitudes d'utilité publique (SUP) toutes catégories** | Une servitude (ligne électrique, canalisation de gaz, périmètre de monument historique, zone de défense/militaire) peut interdire ou fortement contraindre un creusement |
| **Servitudes relatives aux monuments historiques (périmètre de 500 m)** | Impose l'avis de l'Architecte des Bâtiments de France (ABF) pour toute construction visible depuis ou vers le monument, y compris les accès et superstructures d'un bunker |
| **Servitudes militaires / zones de défense (Code de la défense)** | Peut interdire toute construction ou creusement à proximité d'installations militaires classées |
| **Cadastre (limites parcellaires, superficie, section)** | Base indispensable pour identifier la parcelle exacte, ses limites et vérifier la conformité aux règles de distance |
| **Zonage agricole protégé (RPG, ZAP, terres à usage agricole déclaré)** | Une parcelle en zone agricole exploitée peut être grevée d'un bail rural, limitant la libre disposition du terrain même si le PLU l'autorise en zone A sous conditions |
| **Historique des transactions foncières (DVF)** | Permet d'évaluer le marché local et la cohérence du prix d'un terrain proposé à la vente |
| **Document d'urbanisme applicable et son historique de révision** | Un PLU en cours de révision peut annoncer un changement de zonage à court terme, impactant la constructibilité future |

---

## PARTIE 2 — Sources trouvées

### 🇫🇷 Sources françaises

**1. Géoportail de l'urbanisme (GPU)**
- Organisme : Ministère chargé de l'urbanisme / IGN
- URL : https://www.geoportail-urbanisme.gouv.fr/
- Format : consultation cartographique web, téléchargement du règlement écrit en PDF, données géographiques (zonage) en GML/Shapefile
- Granularité : parcelle cadastrale (fiche parcelle générée à la demande)
- Fréquence : mise à jour continue par les collectivités (numérisation progressive, couverture non exhaustive pour les communes n'ayant pas encore dématérialisé leur document)
- Licence : Ouverte, consultation publique sans compte
- Statut : ✅ Active — source de référence nationale pour le zonage PLU/PLUi et les SUP

**2. API Carto — module Géoportail de l'Urbanisme (GPU)**
- Organisme : IGN, en lien avec le Ministère chargé de l'urbanisme
- URL : https://apicarto.ign.fr/api/doc/ (module Urbanisme) et https://www.data.gouv.fr/dataservices/api-carto-module-geoportail-de-lurbanisme-gpu
- Format : API REST (GeoJSON), permet d'interroger en temps réel le document d'urbanisme applicable à une parcelle, ses zonages et ses SUP
- Granularité : parcelle (via coordonnées ou identifiant cadastral)
- Fréquence : reflète l'état de la base GPU, mise à jour continue
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — **recommandée pour une intégration automatisée à la plateforme** (interrogation programmatique d'une parcelle)

**3. API Carto — module Cadastre (IGN)**
- Organisme : IGN
- URL : https://apicarto.ign.fr/api/doc/pdf/docUser_moduleCadastre.pdf
- Format : API REST, données issues du PCI Express (Plan Cadastral Informatisé)
- Granularité : parcelle, section, commune (recherche par coordonnées GPS ou identifiant)
- Fréquence : mise à jour selon les mises à jour cadastrales de la DGFiP
- Licence : Ouverte (Etalab)
- Statut : ✅ Active

**4. Cadastre Etalab (cadastre.data.gouv.fr)**
- Organisme : Etalab / DGFiP
- URL : https://cadastre.data.gouv.fr/
- Format : téléchargement direct en GeoJSON (compressé ou non) et Shapefile, par commune, département ou France entière
- Granularité : parcelle, bâtiment, section cadastrale — couverture de 34 700 communes (PCI Vecteur) + Eurométropole de Strasbourg
- Fréquence : mise à jour périodique suivant les millésimes DGFiP
- Licence : Ouverte (Licence Ouverte / Etalab)
- Statut : ✅ Active — alternative pratique à l'API pour un traitement de masse (import direct en base)

**5. Servitudes d'utilité publique (SUP) — fiches et données GPU**
- Organisme : Ministère chargé de l'urbanisme, gestionnaires de réseaux (RTE, GRTgaz, opérateurs), Ministère de la Culture, Ministère des Armées
- URL : https://www.geoportail-urbanisme.gouv.fr/infos_sup/ et fiches par commune sur data.geopf.fr (ex. `data.geopf.fr/annexes/gpu/documents/DU_<code_commune>/...`)
- Format : PDF (liste et fiches descriptives par catégorie), données géographiques via l'API GPU (source n°2)
- Granularité : commune, avec géométrie précise par servitude (ligne, périmètre, polygone)
- Fréquence : mise à jour continue par les gestionnaires de servitude
- Licence : Ouverte
- Statut : ✅ Active — couvre notamment les catégories pertinentes : **AC1** (monuments historiques, périmètre 500 m), **AR5/AR6** (servitudes militaires/défense nationale), **I3/I4** (canalisations de gaz/hydrocarbures), **PM1** (risques technologiques), **I1bis/T** (lignes électriques)
- Référence réglementaire complémentaire (texte de loi, non géodonnée) : Code de la défense, articles R5111-1 à R5114-11 (servitudes militaires) — https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006071307/LEGISCTA000023752983/

**6. Code de l'urbanisme — seuils autorisations d'urbanisme (Légifrance)**
- Organisme : Légifrance / Ministère chargé de l'urbanisme
- URL : https://www.legifrance.gouv.fr/codes/id/LEGITEXT000006074075/ (Code de l'urbanisme, articles R.421-1 et suivants) ; synthèse pratique sur https://www.service-public.fr/
- Format : texte juridique consultable en ligne (HTML), pas une géodonnée mais une référence normative structurante
- Granularité : nationale (règles générales, modulées localement par le PLU)
- Fréquence : mise à jour au gré des réformes du code
- Licence : Domaine public / Licence Ouverte (Légifrance / data.gouv.fr propose aussi des exports du code)
- Statut : ✅ Active — seuils clés identifiés : **< 5 m² et hauteur < 1,80 m** = aucune formalité ; **5 à 20 m²** = déclaration préalable ; **> 20 m²** = permis de construire (le critère de hauteur sous plafond de 1,80 m est déterminant pour qualifier une construction enterrée comme surface de plancher)

**7. RPG — Registre Parcellaire Graphique**
- Organisme : ASP (Agence de Services et de Paiement) / Ministère de l'Agriculture
- URL : https://www.data.gouv.fr/datasets/rpg et https://agriculture.gouv.fr (actualités des millésimes annuels)
- Format : Shapefile/GeoPackage, téléchargeable par département ou France entière
- Granularité : îlot cultural (résolution 1/5000 sur fond BD Ortho IGN)
- Fréquence : mise à jour annuelle
- Licence : Ouverte (Licence Ouverte v2.0), réutilisation libre y compris commerciale
- Statut : ✅ Active — permet d'identifier si une parcelle est déclarée en exploitation agricole (donc potentiellement sous bail rural) indépendamment du zonage PLU

**8. Demandes de Valeurs Foncières (DVF) / DVF+**
- Organisme : DGFiP, diffusé via data.gouv.fr et Etalab
- URL : https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres et https://cadastre.data.gouv.fr/dvf
- Format : CSV, base géolocalisée (DVF+ enrichie avec la parcelle)
- Granularité : mutation (transaction) géolocalisée à la parcelle
- Fréquence : mise à jour semestrielle, historique sur 5 ans glissants
- Licence : Ouverte (Etalab)
- Statut : ✅ Active — ⚠️ non disponible en Alsace-Moselle (régime du Livre foncier) ni à Mayotte

**9. Atlas des patrimoines / base Mérimée**
- Organisme : Ministère de la Culture
- URL : https://atlas.patrimoines.culture.fr/ et https://culture.data.gouv.fr/datasets/immeubles-proteges-au-titre-des-monuments-historiques-2/
- Format : visualiseur cartographique, export SIG des périmètres de protection (AC1), base Mérimée consultable/téléchargeable
- Granularité : monument ponctuel + périmètre de protection (rayon de 500 m ou périmètre délimité des abords - PDA)
- Fréquence : mise à jour continue par les Directions Régionales des Affaires Culturelles (DRAC)
- Licence : Ouverte (Etalab / Licence Ouverte)
- Statut : ✅ Active — recoupe et détaille la servitude AC1 déjà signalée dans le GPU

---

## Synthèse — Données non couvertes par une source identifiée à ce stade

- **Règlement détaillé propre aux constructions enterrées par commune** : le GPU donne accès au règlement écrit complet du PLU (PDF), mais aucune base structurée ne recense spécifiquement, à l'échelle nationale, les dispositions particulières aux ouvrages souterrains (elles sont noyées dans le texte réglementaire général et varient fortement d'une commune à l'autre) — une extraction automatisée par mots-clés dans les PDF réglementaires serait nécessaire côté plateforme.
- **PLU non dématérialisés** : les communes n'ayant pas encore numérisé leur document d'urbanisme (couverture GPU incomplète, notamment petites communes rurales) ne sont consultables qu'en mairie ou en intercommunalité — pas de solution nationale automatisée pour ces cas.
- **Existence et statut d'un bail rural sur une parcelle agricole** : le RPG signale l'usage agricole déclaré, mais l'information juridique du bail rural lui-même (locataire, durée, clauses) n'est pas en open data (protégée, relève des actes notariés/SAFER).
- **Zones agricoles protégées (ZAP) et périmètres de protection des espaces agricoles et naturels périurbains (PAEN)** : ces classements existent par arrêté préfectoral ou délibération locale mais aucun jeu de données SIG national consolidé n'a été identifié — seulement des arrêtés dispersés consultables préfecture par préfecture.
- **Cartographie nationale unifiée des servitudes militaires (AR5/AR6)** : les fiches SUP par commune existent sur le GPU, mais un export SIG national consolidé de ces zones (souvent sensibles) n'a pas été trouvé en accès libre direct — cohérent avec leur nature de sécurité nationale.
