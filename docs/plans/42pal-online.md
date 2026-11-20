# Plan — 42pal online : mode classé, connexion 42, leaderboard et anticheat

## Objectif

Ajouter à 42pal un **mode classé** : l'étudiant se connecte avec son compte 42, passe un exam dont le serveur tire le sujet, regrade le code et fait foi pour la note, puis apparaît dans un leaderboard par exam, global et par saison, avec des stats par exercice. Un anticheat repère le code collé, copié (d'une ref, d'un oracle ou d'un autre étudiant), écrit par une IA ou rendu dans un temps impossible.

**Le plan est fini quand** un étudiant de n'importe quel campus 42 se connecte depuis `./42pal`, passe un exam classé, voit sa note validée par le serveur et sa place sur le site, et qu'un exam truqué (collé, copié d'une ref, validé en 2 s) est refusé ou mis en revue.

## Décisions

- **La v1 ne bouge plus.** `Blaeste/42pal` (tag v1.0.0) reste la version standalone, sans aucun commit. Les clones existants s'y mettent à jour par `git pull` et n'en reçoivent plus rien.
- **Deux nouveaux dépôts** :
  - `Blaeste/42pal-online`, **public** : le client, parti d'un seul commit d'import de la v1 (l'état de `6c8dea8`). Il garde tous les modes hors ligne de la v1 et ajoute le mode classé. Client en stdlib (urllib, json, threading), compatible Python 3.10.
  - `Blaeste/42pal-server`, **privé** : la connexion OAuth 42, les exams classés, le regrade, l'anticheat, la revue, le leaderboard et le site. Les seuils de l'anticheat y restent secrets. Il importe le cœur de `42pal-online` à une version épinglée, pour regrader exactement comme le client.
- **Le serveur fait foi** pour le tirage du sujet (graine serveur), l'heure, les attentes entre grademe, la progression de niveau et la note. Il refuse les clients d'une autre version que la sienne.
- **Le client garde son grading local** pour la trace immédiate ; le serveur regrade avec les tests du variant **plus des tests tirés d'une graine secrète**, nouvelle à chaque grademe (un code qui recopie les sorties attendues des tests visibles échoue).
- **Mêmes exercices** que le mode hors ligne : l'anticheat vérifie qu'il n'y a ni copier-coller, ni trace d'IA, et que le temps de réalisation est crédible.
- **Instantanés en direct** : pendant un exam classé, le client envoie toutes les ~10 s les fichiers de `rendu/` modifiés, horodatés par le serveur.
- **Suspicion** : les cas nets sont refusés automatiquement ; les cas douteux restent hors du leaderboard, « en vérification », jusqu'à la décision d'un relecteur.
- **Relecteurs** : l'admin (le propriétaire) et des logins de confiance qu'il nomme. Chaque décision garde qui l'a prise, quand et pourquoi.
- **Public** : tous les campus 42, leaderboard par campus et global.
- **Hébergement** : un VPS payant en Europe, conteneurs isolés pour chaque grademe.
- **Leaderboard** : par exam (meilleure note validée, puis le temps), score global (somme des meilleures notes), saisons qui repartent à zéro avec archive, stats publiques par exercice et par thème, points faibles personnels privés.
- **Affichage** : un site web (classements, stats, connexion, revue) et un menu LEADERBOARD dans 42pal. **Le site est réservé aux membres du réseau 42 connectés** : aucune page publique, aucune indexation (CGU de l'API, art. 3 et 4.1).
- **Vie privée** : mode classé sur consentement écrit (case à cocher, preuve gardée, retrait possible à tout moment) ; le leaderboard montre le login et le campus aux seuls membres 42 connectés ; le code et les instantanés sont effacés après 90 jours (les notes et les temps restent) ; chacun peut voir, exporter et supprimer ses données.
- **Ce que le programme et le site affichent est en anglais**, comme la v1.

## Architecture

**Connexion** : `./42pal login` demande un code d'appairage au serveur et ouvre le navigateur sur le serveur, qui passe par l'OAuth 42 (le secret de l'app ne quitte jamais le serveur). Le serveur lit `/v2/me` : login, campus principal, type de compte ; seuls les étudiants actifs passent. Le client récupère un jeton (aléatoire, stocké haché côté serveur, révocable) dans `~/.42pal/online.json`, en droits 600.

**Exam classé** (mode exam seulement : durée réelle, attentes longues) :

1. Le client démarre une session ; le serveur vérifie la version, tire le variant et le renvoie. Le client affiche le sujet depuis le même catalogue. Le menu cheat est désactivé.
2. Un thread envoie les instantanés (fichiers changés seulement, tailles limitées, chaque instantané contient le hash du précédent).
3. Au grademe, le client grade en local et montre la trace, puis envoie le code. Le serveur met le travail en file, regrade dans un conteneur, et son verdict décide du niveau suivant.
4. À la fin ou au temps écoulé, le serveur calcule la note et la durée, puis lance l'anticheat : **validé**, **refusé** ou **en vérification**.

**Bac à sable** : un conteneur neuf par grademe, image Ubuntu 22.04 avec clang, valgrind, Python 3.10 et le cœur épinglé ; `--network none`, système de fichiers en lecture seule, dossier de travail en tmpfs, utilisateur non root, limites de CPU, de mémoire et de processus, durée maximale ; runtime gVisor. File de travaux dans PostgreSQL, un worker par cœur.

**Anticheat** (dépôt privé) :

- **Temps** : plancher par exercice (le code final ne peut pas être tapé plus vite que N caractères par seconde), puis comparaison avec la distribution des étudiants validés.
- **Collé** : saut de caractères entre deux instantanés, solution qui apparaît d'un coup.
- **Copie** : empreintes du code normalisé (winnowing sur les tokens, AST pour Python) comparées aux `ref.c`/`ref.py`, aux oracles des `exercise.py` et aux autres rendus du même exercice.
- **Style IA** : signaux faibles (commentaires et docstrings parfaits, annotations de type rares à ce niveau, formatage parfait dès le premier jet). **Jamais un refus à lui seul** : il envoie en revue.
- **Trous** dans les instantanés (client coupé) : revue, pas refus.
- L'IP compte peu : tout un cluster sort par la même IP au campus.

## API 42 (doc lue le 2026-11-20)

- **OAuth « Authorization Code »** : `GET https://api.intra.42.fr/oauth/authorize` avec `client_id`, `redirect_uri`, `response_type=code`, `scope=public` et un `state` aléatoire ; puis `POST https://api.intra.42.fr/oauth/token` avec `grant_type=authorization_code`, `client_id`, `client_secret`, `code` et `redirect_uri`, **côté serveur seulement**. Le jeton s'envoie dans `Authorization: Bearer <jeton>`.
- **Redirections** : l'app en accepte plusieurs, une par ligne → la vraie (`https://<domaine>/auth/callback`) et une locale pour le développement.
- **Scope** : `public` suffit pour lire `/v2/me`. Aucun autre.
- **`GET /v2/me`** donne `id`, `login`, `kind`, `staff?`, `alumni?`, `active?`, `pool_month`, `pool_year`, `cursus_users` (cursus `piscine-c`, `42cursus`…, avec `blackholed_at`), `campus` et `campus_users` (avec `is_primary`). Il donne aussi l'e-mail, les noms, le téléphone et la photo : **le serveur ne les garde pas**.
- **Ce que le serveur garde** : l'`id` 42, le `login`, le campus principal (id, nom), le type de compte, `active?` et les cursus. Le jeton 42 ne sert qu'à la connexion (un seul appel à `/v2/me`), puis le serveur donne son propre jeton : aucun appel à l'API 42 pendant un exam.
- **Limites** : 2 requêtes par seconde et 1200 par heure pour toute l'app. Une connexion coûte 2 requêtes, soit environ 600 connexions par heure. Le rôle « Official App », demandé par mail à 42 quand l'app est prête et publique, relève ces limites.
- **Jetons** : valables 2 heures ; `GET https://api.intra.42.fr/oauth/token/info` donne le temps restant.
- **Secret de l'app** : il change automatiquement tous les mois (CGU de l'API, art. 3.2). Le serveur le lit dans sa configuration ; un échange de code refusé signale qu'il faut le remplacer.
- **App créée** : « 42PAL », type « 42 Pedagogical Project ». Restent à régler : la vraie redirection (pour l'instant un placeholder) et le scope `public` à cocher.

## CGU de l'API (version du 08.01.2025, lues le 2026-11-20)

- **Art. 1** : une app doit être bénéfique au réseau 42 (pédagogie, outils) ; 42 peut la contrôler, au hasard ou sur signalement, et couper l'accès. Les candidats à l'entrée et les anciens étudiants qui ne sont pas alumni n'ont pas accès à l'API ; les alumni, si.
- **Art. 3** : les données de l'API restent dans le réseau 42 ; les garder en local demande le consentement préalable de la personne.
- **Art. 4.1** : interdit de mettre les données dans un annuaire, un moteur de recherche ou hors de l'environnement 42 ; interdit de les collecter ou de les garder sans consentement écrit préalable. Les données « anonymisées, agrégées ou dérivées » comptent aussi.
- **Art. 4.2** : consentement explicite, libre et éclairé ; politique de confidentialité (selon les recommandations de la CNIL) ; preuve du consentement gardée ; retrait possible à tout moment ; politique fournie à 42 sur demande.
- **Art. 4.3** : sécurité : confidentialité et intégrité, sauvegardes, gestion des accès, protection des serveurs, chiffrement en transit et au repos, pseudonymisation.
- **Art. 4.4 et 4.5** : un moyen simple de demander l'accès, la modification ou la suppression ; tout supprimer quand ce n'est plus utile, quand le service s'arrête, quand 42 le demande ou quand la personne le demande.
- **Art. 6** : un risque de sécurité ou une fuite de clés se signale à security@42.fr ; les clés compromises se révoquent tout de suite.

## Étapes

Chaque étape se fait en TDD dans son dépôt, puis les tests utilisateur (commandes à copier et sortie attendue).

**Avancement (2026-11-20)** : phases 1 à 7 faites, et 8.1 ; 8.2 en local seulement. Restent : ce qui attend le propriétaire (phase 0), la relecture du protocole (2.1), la calibration (5.3), le VPS (8.2) et la bêta (8.3).

- 1.1, 1.2 : les deux dépôts, CI verte ; le serveur teste sur SQLite et PostgreSQL.
- 2.1 à 2.5 : `docs/protocol.md` ; connexion 42 (faux intra dans les tests), consentement avant tout compte, politique de confidentialité (nom et contact du responsable par `PAL42_CONTROLLER` et `PAL42_CONTACT`), suppression du compte ; `./42pal login` et `logout` ; un test bloque le réseau et vérifie que les modes hors ligne n'y touchent pas.
- 3.1 à 3.5 : tirage à graine secrète, durée, attentes « hard », niveaux, fin au temps écoulé ; file de grademe et worker ; bac à sable Docker (pas de réseau, lecture seule, nobody, limites) ; **valgrind marche sous gVisor** (job de la CI avec `runsc`) ; tests à graine secrète (`extra_seeds` dans le cœur) ; `./42pal ranked` ; un test de bout en bout fait passer un niveau au client du sous-module contre le serveur lancé.
- 4.1, 4.2 : instantanés toutes les 10 s et juste avant chaque grademe, chaînés par hash, horodatés par le serveur, envois ratés comptés.
- 5.1, 5.2 : un module par signal (timing, collé, copie par empreintes, style, trous) ; refus des seuls cas nets (niveau validé en quelques secondes, ref recopiée avec ses `#if` de variants), le reste en vérification. 5.3 attend de vraies sessions.
- 6.1 : file de revue, replay (signaux, instantanés et diffs, grademe), décision avec motif, journal ; admins par `PAL42_ADMINS`, relecteurs nommés sur le site.
- 7.1 à 7.3 : classements par exam, global, par saison (mois) et par campus ; stats par exercice et par thème ; points faibles personnels ; pages derrière la connexion ; `./42pal leaderboard`.
- 8.1 : code et instantanés effacés après 90 jours, ménage des lignes expirées, export JSON de toutes ses données, `./42pal delete-account`.
- 8.2 (local) : `deploy/` du serveur, Docker Compose (PostgreSQL, web sur 127.0.0.1:8000, worker qui lance le bac à sable par le socket, sans secret de l'app 42). Pour le VPS : Caddy, domaine, gVisor, chiffrement au repos, sauvegardes, migrations.

### Phase 0 — Préalables (sans code, par le propriétaire)

- **0.1** ~~Lire la doc et les CGU de l'API~~ (fait le 2026-11-20, voir plus haut). Reste : présenter le projet à la pédagogie du campus avant l'ouverture (42 peut contrôler les apps), puis demander le rôle « Official App » quand l'app sera prête. *Vérif* : réponse écrite.
- **0.2** Créer l'app sur l'intra (redirection `https://<domaine>/auth/callback`, plus une redirection locale pour le développement). Le secret va dans un gestionnaire de mots de passe, jamais dans un dépôt.
- **0.3** Le VPS en Europe (celui d'OVH prévu dans le plan de la v1 ?) et le nom de domaine. *Vérif* : ssh, puis une page « hello » en HTTPS.

### Phase 1 — Les dépôts

- **1.1** Créer `42pal-online` : commit d'import de la v1, version 2.0.0-dev, README de la version online, ce plan. *Vérif* : les 712 tests passent en 3.10 et 3.13, CI verte, `./42pal` marche hors ligne comme la v1.
- **1.2** Créer `42pal-server` (privé) : squelette FastAPI avec `/health`, pytest, CI, `42pal-online` en sous-module épinglé. *Vérif* : un test regrade la ref de `char_filter` par le cœur importé et obtient `passed`.

### Phase 2 — Protocole et connexion

- **2.1** `docs/protocol.md` dans le client : endpoints, JSON, erreurs, règle de version. *Vérif* : relecture ensemble.
- **2.2** Serveur : OAuth 42, table des utilisateurs (login, campus principal, type), refus des comptes non étudiants ou inactifs. *Vérif* : tests contre un faux serveur 42.
- **2.3** Serveur : appairage du terminal, jetons hachés et révocables. *Vérif* : test d'un appairage complet.
- **2.4** Client : `./42pal login` et `logout`. *Vérif* : tests contre un faux serveur local ; un test bloque le réseau et vérifie que les modes hors ligne n'ouvrent aucune connexion.
- **2.5** Client et site : écran de consentement (ce qui est envoyé, qui le voit, 90 jours), case à cocher, preuve gardée (date et version de la politique), retrait possible à tout moment ; page de politique de confidentialité selon les recommandations de la CNIL. *Vérif* : refuser ne crée pas de compte ; la preuve du consentement est enregistrée ; le retrait efface le compte.

### Phase 3 — Exam classé, sans anticheat

- **3.1** Serveur : démarrage de session (tirage serveur, contrôle de version), machine d'états (niveaux, attentes, durée). *Vérif* : tests.
- **3.2** Serveur : image du bac à sable, file de travaux, workers. *Vérif* : un rendu juste passe, un faux échoue ; pas de réseau dans le conteneur, bombe fork stoppée, boucle infinie coupée, **valgrind marche sous gVisor** (à vérifier tôt).
- **3.3** Serveur : grademe par la file, verdict avec les tests à graine secrète. *Vérif* : un rendu qui code en dur les sorties des tests visibles échoue sur le serveur.
- **3.4** Client : `RankedShell` dérivée de `Shell`, trace locale puis verdict serveur, attentes du serveur, cheat désactivé. *Vérif* : tests « les deux OK » et « OK en local, KO sur le serveur ».
- **3.5** Fin d'exam et temps écoulé : note finale et durée. *Vérif* : tests.

### Phase 4 — Instantanés

- **4.1** Client : thread d'instantanés (fichiers changés, tailles limitées, chaîne de hash, reprise après coupure). *Vérif* : contre un faux serveur, des modifications donnent des instantanés ; une coupure laisse un trou signalé, puis ça reprend.
- **4.2** Serveur : stockage horodaté, limites par session. *Vérif* : tests.

### Phase 5 — Anticheat

- **5.1** Un module par signal : temps, collé, copie, style, trous. *Vérif* : cas faits à la main (frappe honnête progressive, collage, copie d'une ref, copie renommée d'un autre étudiant).
- **5.2** Décision : validé, refusé, en vérification. *Vérif* : un test par règle.
- **5.3** Calibrage sur des sessions du propriétaire et une bêta fermée. *Vérif* : aucun refus automatique d'un honnête sur la bêta.

### Phase 6 — Revue

- **6.1** Site : connexion, rôles admin et relecteur, file des exams en vérification, replay de la frappe (frise et diff), décision avec motif, journal des décisions. *Vérif* : tests, essai à la main.

### Phase 7 — Leaderboard et stats

- **7.1** Serveur : classement par exam, score global, saisons avec archive, filtre par campus, stats par exercice et par thème, points faibles personnels. *Vérif* : tests sur des jeux de données.
- **7.2** Pages web, réservées aux membres 42 connectés (pas de page publique, `noindex`, `robots.txt` qui interdit tout). **7.3** Menu LEADERBOARD dans le client. *Vérif* : une page de classement ouverte sans connexion renvoie vers la connexion ; tests, essai à la main.

### Phase 8 — Vie privée et mise en ligne

- **8.1** Effacement à 90 jours ; voir, exporter, modifier et supprimer ses données, depuis un lien facile à trouver (site et `./42pal online delete-account`) ; tout effacer si 42 le demande ou si le service s'arrête. *Vérif* : tests.
- **8.2** Déploiement Docker Compose (Caddy pour le HTTPS, l'app, les workers, PostgreSQL), chiffrement au repos (disque ou base) et des sauvegardes, sauvegardes quotidiennes hors du VPS, accès au serveur par clé SSH seulement, surveillance, rappel mensuel pour le secret de l'app. *Vérif* : restauration réussie d'une sauvegarde, test de charge à 100 grademe simultanés.
- **8.3** Bêta fermée, puis ouverture campus par campus après l'accord de 42.

## Risques

- **Règles de 42** (CGU de l'intra art. 6, CGU de l'API art. 1, 3 et 4) : les données ne sortent pas du réseau 42 → tout le classement est derrière la connexion 42, avec consentement écrit. 42 peut contrôler l'app et couper l'accès : présenter le projet à la pédagogie avant d'ouvrir.
- **Secret de l'app renouvelé chaque mois** : oublié, plus personne ne peut se connecter. Rappel mensuel et alerte au premier échange refusé.
- **Exécuter du code d'inconnus** : évasion de conteneur possible. Parades : gVisor, aucun secret dans les workers, idéalement une VM à part pour eux.
- **La détection d'IA est peu fiable** : jamais de refus sur le style seul.
- **Un client modifié peut simuler une frappe en temps réel** : coûteux, et les valeurs aberrantes partent en revue. Aucun anticheat côté client n'est parfait.
- **Charge** : tous les campus, chaque grademe recompilé. File, limites, VPS qu'on peut agrandir.
- **Coupures réseau en exam** : trous, donc revue, pas refus.
- **La v1 figée ne reçoit plus de nouveaux exercices.**
- **Un rendu Python peut lire l'oracle** (`exercise.py`) dans le bac à sable pendant l'exécution, s'il a le droit d'ouvrir des fichiers : l'anticheat (5.1) signale `open`, `exec`, `importlib` dans un rendu Python. Les ref ne sont pas dans l'image.
- **Docker rootless** (cette machine) ne sait pas limiter le CPU : `PAL42_SANDBOX_CPUS` vide ; sur le VPS, Docker normal avec gVisor.
- **Avant la première mise en ligne** : des migrations de base (Alembic), la remise en file des grademe d'un worker tombé, une taille maximale des requêtes (Caddy), une limite de requêtes par compte, les comptes staff comme relecteurs (aujourd'hui refusés à la connexion).
- **RGPD** : le propriétaire est responsable du traitement. Hébergement en Europe, page de confidentialité, registre des traitements.

## Questions ouvertes (avec la recommandation)

1. **Pile serveur** : Python 3.12, FastAPI, PostgreSQL, templates côté serveur, pour réutiliser le grader tel quel.
2. **Saisons** : le mois calendaire.
3. **Langue du site** : l'anglais, comme le programme.
4. **VPS** : réutiliser le VPS OVH du plan de la v1, s'il a la place pour des conteneurs (gVisor demande un noyau qui le permet).
5. **Qui peut jouer en classé** : `/v2/me` distingue les étudiants actifs, les piscineux (cursus `piscine-c`), les alumni et le staff. Les CGU de l'API (art. 1) refusent l'accès aux candidats à l'entrée et aux anciens étudiants qui ne sont pas alumni. Recommandation : étudiants actifs et alumni ; les piscineux seulement si 42 le confirme par écrit (le mode hors ligne reste ouvert à tous) ; le staff seulement comme relecteur.

## Hors périmètre

- Toute modification de la v1.
- Les vrais sujets de 42.
- La surveillance par webcam ou capture d'écran, un anticheat au niveau du noyau.
- Une app mobile, tout paiement.
