# Plan — Cluster multi-PC HOMEPEDIA (réseau privé virtuel Tailscale)

> Plan d'exécution destiné à un agent de code, à dérouler **avec** l'utilisateur et **un coéquipier**,
> les deux PC allumés côte à côte (ou à distance). Rédigé le 2026-09-26, à partir de l'état décrit dans
> `README.md` et `PLAN_PREMIER_JET.md` (premier jet + bonus + Rhône entier terminés).

---

## 0. Contexte à lire avant de commencer

- **Aujourd'hui :** toute la stack tourne sur **un seul PC** (« PC A », celui de l'utilisateur), dans
  **Docker Desktop pour Linux** (les conteneurs vivent dans une machine virtuelle ; ~7,8 Go de RAM alloués).
  Le « cluster » Spark / HDFS est une maquette : 1 worker, 1 DataNode, réplication 1.
- **Objectif :** en faire un **vrai cluster sur 2 machines** : le PC B (coéquipier) apporte un 2e worker
  Spark et un 2e DataNode HDFS. Le code des jobs ne doit **pas** changer : seulement la configuration.
- **Réseau :** les deux PC communiquent via **Tailscale** (réseau privé virtuel WireGuard). Chaque PC
  reçoit une adresse fixe `100.x.y.z`, joignable d'où qu'il soit (Wi-Fi d'école, 4G, domicile).
- L'utilisateur **débute** : chaque phase doit être expliquée simplement (voir mémoire « pédagogie »).

### Règles de conduite pour l'agent

1. **Une phase à la fois.** À la fin de chaque phase : vérification, résultat montré, explication en
   3-5 phrases, feu vert de l'utilisateur avant la suite.
2. **Pas de droits administrateur pour l'agent.** Toute commande `sudo` (installer Tailscale, Docker
   Engine…) est **donnée** à l'utilisateur ou au coéquipier, qui la lance lui-même. L'utilisateur a
   explicitement refusé de donner les droits root.
3. **Vérifier plutôt que supposer**, surtout pour le réseau : chaque connexion est testée (§ 4) avant d'y
   bâtir quoi que ce soit. Plusieurs points de ce plan sont des **hypothèses à confirmer** (§ 11).
4. **Si un point bloque plus de ~15 min**, s'arrêter et revenir avec le constat et 2 options.
5. **Réversible.** Tout ce qui concerne le cluster va dans des fichiers **séparés**
   (`docker-compose.cluster.yml` sur A, `docker-compose.worker.yml` sur B) : sans eux, la stack
   redémarre exactement comme avant (§ 10).
6. **Docker Desktop (PC A) : piège de synchronisation.** Un fichier monté remplacé (outils d'édition,
   `sed -i`) n'est pas vu par un conteneur démarré : comparer les `md5sum` hôte/conteneur et redémarrer
   le conteneur (voir `README.md`, Dépannage).

---

## 1. Objectif et périmètre

**Critère de réussite :** `homepedia_full` tourne en utilisant les **deux** PC :
- l'UI Spark montre **2 workers** et des tâches exécutées **sur les deux** ;
- HDFS montre **2 DataNodes vivants** et des blocs **répliqués sur les deux** (réplication 2) ;
- **démonstration de résilience** : on éteint un service du PC B pendant un job, et le travail aboutit quand même.

**Hors périmètre :** déplacer Postgres, Mage, Superset, MongoDB ou SeaweedFS (ils restent sur A) ;
plus de 2 PC (la recette est la même : répéter la phase 5 et la phase 6 par PC) ; haute disponibilité du
NameNode / du master Spark (ils restent des points uniques de défaillance, à expliquer à l'oral).

---

## 2. Architecture cible

```
            Tailscale (réseau privé 100.x.y.z, chiffré)
   ┌──────────────────────────────────┐        ┌──────────────────────────────┐
   │ PC A « tête » (utilisateur)       │        │ PC B « renfort » (coéquipier) │
   │  Docker Desktop (VM)              │        │  Docker (voir phase 1)        │
   │                                   │        │                               │
   │  mage (driver Spark) ◄────────────┼────────┼── spark-worker-b (executor)   │
   │  spark-master :7077 ◄─────────────┼────────┼── (s'enregistre)              │
   │  spark-worker (A)                 │        │                               │
   │  namenode :8020 ◄─────────────────┼────────┼── datanode-b (s'enregistre)   │
   │  datanode (A) :9866 ◄─────────────┼────────┼──► datanode-b :9866           │
   │  postgres, superset, mongo,       │        │   (réplication des blocs)     │
   │  seaweedfs, dbt-docs              │        │                               │
   └──────────────────────────────────┘        └──────────────────────────────┘
```

### Qui contacte qui (à ouvrir, **uniquement sur l'adresse Tailscale**)

| De | Vers | Port | Pourquoi |
|---|---|---|---|
| worker B | master (A) | 7077 | s'enregistrer, recevoir du travail |
| executor B | driver = Mage (A) | 7078 (`spark.driver.port`) | recevoir les tâches |
| executor B | driver (A) | 7079 (`spark.driver.blockManager.port`) | échanger des résultats |
| driver (A) | executor B | 7079 (`spark.blockManager.port`) | récupérer des résultats |
| executor A | executor B (et inverse) | 7079 | *shuffle* (échange de données entre ouvriers) |
| datanode B | namenode (A) | 8020 | s'enregistrer, signaler ses blocs |
| clients HDFS (Mage, executors) | datanodes A et B | 9866 (données), 9864 (WebHDFS) | lire / écrire des blocs |
| datanode A ↔ datanode B | | 9866 | réplication des blocs |
| navigateur (A) | UIs de B | 8081 (worker), 9864 (datanode) | observer |

---

## 3. Phase 0 — Sécuriser les ports existants (sur A seul, avant tout)

**Constat (2026-09-26) :** tous les ports sont publiés sur `0.0.0.0`, donc joignables depuis le Wi-Fi
(ex. Postgres 5432, MongoDB 27017). Avec Tailscale en plus, il faut maîtriser ce qu'on expose.

Tâches :
1. Dans `docker-compose.yml`, préfixer chaque port publié par `127.0.0.1:` (ex. `"127.0.0.1:5432:5432"`) :
   les interfaces restent accessibles depuis le PC A (navigateur, DBeaver), plus depuis le réseau.
2. Exception à étudier : l'API S3 (8333) doit rester lisible par **le navigateur de l'utilisateur**
   seulement → `127.0.0.1` suffit aussi.

**Vérification :** `docker compose ps` ne montre plus de `0.0.0.0` ; depuis un autre appareil du Wi-Fi,
`curl http://<IP Wi-Fi de A>:5432` échoue ; le dashboard et Mage marchent toujours sur `localhost`.

**À faire comprendre :** interface réseau, `0.0.0.0` vs `127.0.0.1`, surface d'attaque.

---

## 4. Phase 1 — Inventaire du PC B et choix de la méthode

**But :** savoir sur quoi on travaille avant d'écrire la moindre configuration.

Tâches (avec le coéquipier) :
1. Relever pour le PC B : système (Linux / macOS / Windows), RAM, nombre de cœurs, espace disque,
   **type de Docker** (`docker info --format '{{.OperatingSystem}}'` : « Docker Desktop » ou non).
2. Choisir la méthode selon ce tableau :

| PC B | Méthode | Pourquoi |
|---|---|---|
| **Linux + Docker Engine** (recommandé) | conteneurs en **`network_mode: host`** | Le conteneur utilise directement les interfaces du PC, dont `tailscale0` : Spark et HDFS annoncent l'adresse `100.x` sans traduction. Le plus simple et le plus fiable. |
| Linux + Docker Desktop, macOS, Windows | DataNode en conteneur avec **ports publiés** + adresse annoncée (`dfs.datanode.hostname`) ; **worker Spark installé nativement** (Java 17 + archive Spark 4.1.3, script `start-worker.sh`) | Docker Desktop fait tourner les conteneurs dans une VM : un worker Spark en conteneur annoncerait une adresse interne injoignable (Spark ne sépare pas « adresse d'écoute » et « adresse annoncée » pour les workers). |

3. Dimensionner B : laisser au moins 2 Go au système ; ex. PC de 8 Go → worker 2 cœurs / 3 Go.

**Vérification :** méthode choisie et notée en tête de `docker-compose.worker.yml` (commentaire).

---

## 5. Phase 2 — Tailscale : le réseau privé

Tâches (commandes **données** aux humains, qui les lancent) :
1. Créer un compte Tailscale (offre gratuite « Personal » : vérifier ses limites actuelles d'appareils
   et d'utilisateurs), installer Tailscale sur A et sur B (`https://tailscale.com/download`, nécessite
   les droits administrateur), se connecter (`tailscale up`).
2. Mettre les deux machines dans le **même tailnet** : soit le même compte, soit invitation du
   coéquipier, soit **partage** de la machine B vers le tailnet de A (fonction « Share »).
3. Noter les adresses : `tailscale ip -4` sur chaque PC → écrire dans `.env` de A :
   `TAILSCALE_IP_A=100.…` et `TAILSCALE_IP_B=100.…`.

**Vérifications (dans cet ordre, chacune doit passer) :**
1. `ping <IP B>` depuis A et `ping <IP A>` depuis B.
2. **Hôte B → conteneur A** : sur A, `docker run --rm -p <IP A>:8099:80 nginx` ; sur B, `curl http://<IP A>:8099`.
   *(Teste que Docker Desktop sait publier un port sur l'adresse Tailscale — hypothèse H1, § 11.)*
3. **Conteneur A → hôte B** : sur B, `python3 -m http.server 8099 --bind <IP B>` ; sur A,
   `docker run --rm curlimages/curl http://<IP B>:8099`.
   *(Teste qu'un conteneur de la VM Docker Desktop atteint le réseau Tailscale — hypothèse H2.)*
4. **Conteneur A → conteneur A via l'IP Tailscale** (le worker A devra joindre le driver par `100.x`) :
   refaire le test 2 avec le `curl` lancé dans un conteneur de A. *(Hypothèse H3 : « hairpin ».)*

**À faire comprendre :** VPN maillé, WireGuard, adresse `100.64.0.0/10`, pourquoi Tailscale évite
d'ouvrir des ports sur la box / le réseau de l'école.

**Pièges :** pare-feu du PC B (autoriser l'interface `tailscale0`) ; réseaux d'école qui bloquent l'UDP
(Tailscale passe alors par ses relais DERP : ça marche mais plus lentement) ; MTU (Tailscale ≈ 1280).

---

## 6. Phase 3 — Préparer le PC A (fichier `docker-compose.cluster.yml`)

**But :** exposer sur l'IP Tailscale de A **seulement** ce dont B a besoin, et apprendre aux services de A
à joindre ceux de B. Fichier **séparé**, utilisé ainsi :
`docker compose -f docker-compose.yml -f docker-compose.cluster.yml up -d`.

Tâches :
1. **Ports publiés sur `${TAILSCALE_IP_A}`** : `7077` (spark-master), `8020` (namenode), `9866` + `9864`
   (datanode A), `7078` + `7079` (mage = driver Spark).
2. **Noms des machines de B** pour les conteneurs de A : `extra_hosts: ["datanode-b:${TAILSCALE_IP_B}"]`
   sur `mage`, `spark-worker`, `namenode` (le client HDFS contacte les DataNodes par leur nom,
   cf. `dfs.client.use.datanode.hostname=true`).
3. **Driver Spark joignable depuis B** : rendre configurable dans `mage/homepedia/utils/spark.py`
   (variables d'environnement, valeurs actuelles par défaut) :
   `spark.driver.host=${TAILSCALE_IP_A}`, `spark.driver.port=7078`, `spark.driver.blockManager.port=7079`,
   `spark.blockManager.port=7079`, `spark.cores.max=` (cœurs A + cœurs B).
4. **Réplication HDFS 2** : `HDFS-SITE.XML_dfs.replication=2` (sur A et B).

**Vérification :** la stack redémarre ; `homepedia_full` passe **encore sur A seul** (le worker A doit
joindre le driver via `100.x` — hypothèse H3) ; `docker compose ps` ne montre des ports `100.x` que pour
la liste ci-dessus.

**Pièges :** si H3 échoue (le worker A ne joint pas le driver par `100.x`), option : `extra_hosts`
qui fait pointer un nom commun (ex. `driver-homepedia`) vers le conteneur `mage` sur A et vers
`${TAILSCALE_IP_A}` sur B, et `spark.driver.host=driver-homepedia`.

---

## 7. Phase 4 — Le DataNode du PC B (HDFS réparti)

Tâches :
1. Sur B : copier `docker/hadoop/` et `docker-compose.worker.yml` (ou cloner le dépôt).
2. Service `datanode-b` : même image `homepedia-hadoop:3.4.3` (reconstruite sur B), même
   `hadoop.env` avec en plus :
   - `CORE-SITE.XML_fs.defaultFS=hdfs://<IP A>:8020` (ou nom `namenode` → `extra_hosts` vers IP A),
   - `HDFS-SITE.XML_dfs.datanode.hostname=datanode-b` (nom **annoncé** au NameNode),
   - `HDFS-SITE.XML_dfs.replication=2`,
   - Linux + Engine : `network_mode: host` ; sinon ports `9866`, `9864`, `9867` publiés sur `<IP B>`.
   - `extra_hosts` : `namenode` et `datanode` → IP A (pour la réplication vers le DataNode A).
3. Répliquer l'existant : `hdfs dfs -setrep -w 2 /bronze` (sinon les anciens fichiers restent en 1 copie).

**Vérification :** `hdfs dfsadmin -report` → **Live datanodes (2)** ; UI 9870, onglet *Datanodes* ;
`hdfs fsck /bronze -files -blocks -locations | head` → chaque bloc listé sur **deux** DataNodes ;
nouvelle ingestion (`ingest_bronze`) sans erreur (écriture WebHDFS redirigée vers `datanode-b` — Mage
doit résoudre ce nom : `extra_hosts` de la phase 3).

**À faire comprendre :** placement des répliques, *heartbeat*, ce que fait le NameNode quand un DataNode
disparaît (re-réplication), pourquoi le NameNode reste un point unique de défaillance.

---

## 8. Phase 5 — Le worker Spark du PC B

Tâches :
1. **Linux + Engine :** service `spark-worker-b` (image `apache/spark:4.1.3-scala2.13-java17-python3-ubuntu`),
   `network_mode: host`, commande `spark-class org.apache.spark.deploy.worker.Worker spark://<IP A>:7077`,
   variables `SPARK_LOCAL_IP=<IP B>` (adresse d'écoute ET annoncée), `SPARK_WORKER_CORES`,
   `SPARK_WORKER_MEMORY`, `extra_hosts` (`namenode`, `datanode` → IP A ; lecture HDFS par les executors).
   **Autres cas :** installation native de Java 17 + Spark **4.1.3** (même version exacte que le cluster),
   `SPARK_LOCAL_IP=<IP B>`, `sbin/start-worker.sh spark://<IP A>:7077`, et `/etc/hosts` pour `namenode`, `datanode`, `datanode-b`.
2. Python : les jobs n'utilisent pas d'UDF Python, les executors n'ont donc pas besoin du même Python
   que le driver. **Si un jour une UDF est ajoutée** : même version de Python (3.10) exigée partout.

**Vérification :** UI Spark (A, http://localhost:8080) → **Alive Workers: 2**, cœurs et mémoire cumulés ;
lancer `run_spark_clean` → dans l'UI de l'application (onglet *Executors*), **2 executors** avec des
tâches terminées chacun ; comparer la durée de `clean_cadastre` (47 s sur A seul, Rhône entier).

**À faire comprendre :** répartition des tâches, *data locality* (Spark préfère lire un bloc sur la
machine qui le possède), coût du réseau dans un *shuffle* — **il est possible que ce soit plus lent**
qu'à une seule machine (réseau Wi-Fi + VPN) : c'est un résultat à expliquer, pas un échec.

**Pièges :** version de Spark ≠ 4.1.3 sur B → erreurs de sérialisation ; `SPARK_LOCAL_IP` oublié →
le worker annonce une adresse locale injoignable (tâches bloquées en *WAITING* ou connexions refusées) ;
horloges des deux PC décalées → logs difficiles à lire (activer la synchro NTP).

---

## 9. Phase 6 — Démonstration de bout en bout et résilience

Tâches :
1. Lancer `homepedia_full` ; relever les durées par étape (tableau avant / après dans le README).
2. **Résilience HDFS :** arrêter `datanode-b` → `hdfs dfs -cat` d'un fichier fonctionne toujours
   (réplique sur A) ; l'UI 9870 le marque *Dead* après ~10 min ; le relancer → retour à 2.
3. **Résilience Spark :** lancer `run_spark_clean`, arrêter `spark-worker-b` en plein job → Spark relance
   les tâches perdues sur le worker A ; le job aboutit (plus lentement). Montrer l'onglet *Executors* (*Dead*).
4. Préparer 3 captures d'écran pour la soutenance : UI Spark (2 workers), UI HDFS (2 DataNodes), fsck.

**Vérification :** critère de réussite du § 1 atteint.

---

## 10. Retour à un seul PC (après la séance)

1. Sur A : `hdfs dfs -setrep -w 1 /` **avant** d'éteindre B (sinon HDFS signale des blocs sous-répliqués
   et tente sans fin de recréer la 2e copie).
2. Sur A : relancer sans le fichier cluster : `docker compose up -d` (le compose de base est inchangé).
3. Sur B : `docker compose -f docker-compose.worker.yml down` (et `-v` pour effacer les blocs HDFS de B).

---

## 11. Hypothèses à vérifier (points incertains)

| # | Hypothèse | Testée en | Si elle est fausse |
|---|---|---|---|
| H1 | Docker Desktop (Linux) publie un port sur l'adresse Tailscale de A | phase 2, test 2 | publier sur `0.0.0.0` **et** filtrer avec le pare-feu de A (règle n'autorisant que `100.64.0.0/10`) |
| H2 | Un conteneur de A joint une adresse `100.x` de B | phase 2, test 3 | faire tourner le driver Spark hors conteneur, ou utiliser le conteneur Tailscale officiel en « sidecar » |
| H3 | Un conteneur de A joint un port publié sur l'IP Tailscale de A (hairpin) | phase 2, test 4 / phase 3 | nom commun résolu différemment sur A et B (`extra_hosts`, voir phase 3) |
| H4 | Le master Spark conteneurisé accepte un worker qui le contacte via `100.x:7077` | phase 5 | `SPARK_MASTER_HOST` / `SPARK_PUBLIC_DNS` ; en dernier recours master hors conteneur |
| H5 | Les réseaux utilisés (école, domicile) laissent passer Tailscale | phase 2 | relais DERP (automatique) ; tester depuis un partage de connexion 4G |

---

## 12. Ressources et ports (récapitulatif)

| Machine | Service | Ports exposés sur l'IP Tailscale | RAM indicative |
|---|---|---|---|
| A | spark-master | 7077 | 0,3 Go |
| A | mage (driver) | 7078, 7079 | 1–2 Go |
| A | namenode | 8020 | 0,5 Go |
| A | datanode | 9866, 9864 | 0,5 Go |
| B | datanode-b | 9866, 9864, 9867 | 0,5 Go |
| B | spark-worker-b | 7079 (+ UI 8081) | selon PC : 2–4 Go |

## 13. Définition de « terminé »

- [ ] Ports de A restreints à `127.0.0.1` + IP Tailscale (phase 0).
- [ ] UI Spark : 2 workers vivants, tâches exécutées sur les deux.
- [ ] UI HDFS : 2 DataNodes vivants, `fsck` montre 2 répliques par bloc.
- [ ] `homepedia_full` passe au vert en mode cluster ; durées comparées dans le README.
- [ ] Démonstration de résilience réalisée (HDFS et Spark).
- [ ] Retour à un seul PC testé (§ 10) ; README complété (section « Mode cluster »).
- [ ] L'utilisateur et son coéquipier savent expliquer : driver / master / worker / executor,
      NameNode / DataNode, réplication, et pourquoi le cluster n'est pas forcément plus rapide ici.
