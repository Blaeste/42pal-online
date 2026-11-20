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
- **Affichage** : un site web (classements, stats, connexion, revue) et un menu LEADERBOARD dans 42pal.
- **Vie privée** : mode classé sur consentement explicite ; le leaderboard montre le login et le campus ; le code et les instantanés sont effacés après 90 jours (les notes et les temps restent) ; chacun peut supprimer son compte.
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

## Étapes

Chaque étape se fait en TDD dans son dépôt, puis les tests utilisateur (commandes à copier et sortie attendue).

### Phase 0 — Préalables (sans code, par le propriétaire)

- **0.1** Lire la doc de l'API 42 en étant connecté (endpoints OAuth, champs de `/v2/me`, limites de requêtes, règles des apps) et demander à 42 l'accord pour un leaderboard public avec les logins (CGU de l'intra, article 6). *Vérif* : réponse écrite de 42, champs confirmés notés ici.
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
- **2.5** Client et site : écran de consentement (ce qui est envoyé, ce qui est public, 90 jours). *Vérif* : refuser ne crée pas de compte.

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
- **7.2** Pages web. **7.3** Menu LEADERBOARD dans le client. *Vérif* : tests, essai à la main.

### Phase 8 — Vie privée et mise en ligne

- **8.1** Effacement à 90 jours, suppression de compte (site et `./42pal online delete-account`), page de confidentialité. *Vérif* : tests.
- **8.2** Déploiement Docker Compose (Caddy pour le HTTPS, l'app, les workers, PostgreSQL), sauvegardes quotidiennes hors du VPS, surveillance. *Vérif* : restauration réussie d'une sauvegarde, test de charge à 100 grademe simultanés.
- **8.3** Bêta fermée, puis ouverture campus par campus après l'accord de 42.

## Risques

- **CGU de l'intra (article 6)** : interdiction de collecter les données des autres utilisateurs (login, campus…) pour un autre usage que l'intra, notamment des « annuaires » publics. Sans accord de 42 : leaderboard visible seulement par les gens connectés, ou pseudos.
- **Exécuter du code d'inconnus** : évasion de conteneur possible. Parades : gVisor, aucun secret dans les workers, idéalement une VM à part pour eux.
- **La détection d'IA est peu fiable** : jamais de refus sur le style seul.
- **Un client modifié peut simuler une frappe en temps réel** : coûteux, et les valeurs aberrantes partent en revue. Aucun anticheat côté client n'est parfait.
- **Charge** : tous les campus, chaque grademe recompilé. File, limites, VPS qu'on peut agrandir.
- **Coupures réseau en exam** : trous, donc revue, pas refus.
- **La v1 figée ne reçoit plus de nouveaux exercices.**
- **RGPD** : le propriétaire est responsable du traitement. Hébergement en Europe, page de confidentialité, registre des traitements.

## Questions ouvertes (avec la recommandation)

1. **Pile serveur** : Python 3.12, FastAPI, PostgreSQL, templates côté serveur, pour réutiliser le grader tel quel.
2. **Saisons** : le mois calendaire.
3. **Langue du site** : l'anglais, comme le programme.
4. **VPS** : réutiliser le VPS OVH du plan de la v1, s'il a la place pour des conteneurs (gVisor demande un noyau qui le permet).

## Hors périmètre

- Toute modification de la v1.
- Les vrais sujets de 42.
- La surveillance par webcam ou capture d'écran, un anticheat au niveau du noyau.
- Une app mobile, tout paiement.
