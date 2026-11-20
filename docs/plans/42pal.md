# Plan — 42pal : réviser les exams 42 avec des variantes

## Objectif

Un outil pour les étudiants de 42 Mulhouse qui simule tous les exams (piscine et cursus, C, C++ et Python). Chaque sujet tiré est une **variante paramétrée** d'un modèle d'exo écrit sur le même thème que le vrai exam, et il est corrigé automatiquement.

- **Phase 1 (ce plan)** : un outil terminal qui reproduit l'examshell.
- **Phase 2 (plan séparé)** : une interface web, hébergée d'abord sur le VPS OVH, puis probablement sur un serveur de l'école.

**La phase 1 est finie quand** un étudiant du campus lance `./42pal` sans rien installer, passe un rank 02 complet avec des variantes qu'il n'a jamais vues, et que tout le catalogue passe `check-catalog`.

## Décisions

- **Langage** : Python 3.10 minimum (à confirmer sur un poste du campus), bibliothèque standard uniquement pour le cœur et les tests (`unittest`), car personne n'a le droit d'installer quoi que ce soit sur les postes.
- **Affichage** : `rich` (licence MIT) est embarqué dans `vendor/` avec `typing_extensions`, soit environ 1,2 Mo, sans `pygments` ni `markdown_it`. Il n'y a rien à installer et pas besoin de sudo. Seul `pal42/cli/` s'en sert : le cœur reste en bibliothèque standard, sans affichage. Vérifié sur le Python 3.10.12 du système, sans aucun paquet : console, couleurs, tableaux, panneaux, affichage en direct, prompt et barres de progression marchent.
- **Exo** : un modèle composé de paramètres (avec des combinaisons interdites possibles), d'un sujet à trous, d'un **oracle** Python, d'un générateur de tests, et d'une solution de référence `ref.c` paramétrée par `-D`.
- **Variante** : identifiée par `exo#seed`, donc reproductible.
- **Les exams pointent vers des thèmes.** Au tirage, on prend un thème du niveau, puis un modèle de ce thème, puis une seed.
- **Aucun sujet réel dans le dépôt.** Les sujets réels servent seulement à repérer les thèmes. Chaque modèle a son propre nom, son propre énoncé et ses propres exemples, et peut interdire la combinaison qui redonnerait le sujet réel.
- **Correction locale**, sur la machine de l'étudiant.
- **Compilation par défaut** : `cc -Wall -Wextra -Werror`, comme la moulinette.
- **Après un échec**, on retente le même sujet, avec une attente qui augmente à chaque échec.

## Structure visée

```
42pal/
├── 42pal                # script de lancement (python3 -m pal42)
├── pal42/               # le cœur, sans aucun affichage, réutilisé par le web
│   ├── model.py variant.py subject.py catalog.py
│   ├── grader.py trace.py harness.py checks.py exam.py session.py
│   ├── runners/         # base.py c.py cpp.py python.py
│   └── cli/             # shell.py practice.py check.py display.py
├── exercises/c/char_filter/   # exercise.py, ref.c
├── themes.json
├── exams/               # rank02.json, piscine_*.json
├── vendor/              # rich et typing_extensions, embarqués (rien à installer)
└── tests/
```

## Étapes

**Ordre de réalisation** : les étapes 1 à 8 sont faites. On fait ensuite l'interface d'abord (étapes 16 et 18), avec un `grademe` qui répond « pas encore branché », pour voir l'outil de bout en bout au plus tôt. Puis on reprend le correcteur (étapes 9 à 15), on le branche, et on continue avec les étapes 17, 19 et suivantes.

### Jalon 0 : squelette

**1. Initialiser le dépôt.** `git init`, `.gitignore`, le paquet `pal42/` avec `__main__.py` (option `--version`) et le script `./42pal`, qui marche depuis n'importe quel dossier. Lancer `python3 --version` sur un poste du campus pour fixer la version minimale.
- Vérifier : `./42pal --version` affiche la version, et `python3 -m unittest -v` passe.

### Jalon 1 : modèle d'exo et variantes

**2. Modèle de données.** `Param`, `Exercise` (langage, type programme ou fonction, fichiers attendus, fonctions autorisées, thèmes, paramètres, combinaisons interdites, sujet, oracle, tests) et `TestCase`, dans `pal42/model.py`.
- Test d'abord : un sujet qui utilise un paramètre inexistant lève une erreur dès la création de l'exo.

**3. Tirage d'une variante.** `draw(exo, seed)` renvoie une `Variant`. Le nom peut dépendre des paramètres. Fichier : `variant.py`.
- Test : la même seed donne la même variante.
- Test : sur 200 seeds, chaque valeur autorisée sort au moins une fois, et une combinaison interdite ne sort jamais.

**4. Sujet au format 42.** On produit les lignes Assignment name, Expected files et Allowed functions, une ligne de tirets, l'énoncé, puis les exemples `| cat -e` calculés par l'oracle. Fichier : `subject.py`.
- Test : l'en-tête suit bien le format 42.
- Test : un instantané de notre sujet, relu une fois à la main puis enregistré dans `tests/golden/`, ne change pas d'un lancement à l'autre.

**5. Premier modèle : `char_filter`**, un modèle original sur le thème « ensembles de caractères ». Paramètres : `mode` (communs, seulement dans le 1er, seulement dans le 2e), `ordre` et `séparateur`. La combinaison identique au sujet réel est interdite. Fichier : `exercises/c/char_filter/exercise.py`.
- Test : l'oracle donne les sorties de nos propres exemples, y compris pour un mauvais nombre d'arguments.

**6. Catalogue.** On découvre les exos dans `exercises/` et on les indexe par langage et par thème. Fichier : `catalog.py`.
- Test : `char_filter` est trouvé sous le thème `char_sets`.
- Test : un dossier sans `exercise.py` est ignoré avec un avertissement.

**7. Liste des thèmes : `themes.json`.** Pour chaque thème : son id, la compétence testée, et les exams et niveaux où il apparaît. Pour l'instant, seulement la piscine et le rank 02 : un premier jet écrit de mémoire (l'inventaire de 42_EXAM n'est plus en ligne), à faire relire par des étudiants qui ont passé ces exams.
- Test : un modèle qui cite un thème inconnu donne une erreur.
- Test : un thème sans compétence, sans exam ou avec un niveau qui n'est pas un nombre, ou un thème écrit deux fois, donne une erreur.

### Jalon 2 : correcteur C

**8. Compilation.** `cc -Wall -Wextra -Werror` dans un dossier temporaire, avec une commande configurable par exam. Fichiers : `runners/base.py` et `runners/c.py`.
- Test : un `.c` valide compile.
- Test : une variable inutilisée fait échouer la compilation, et l'erreur est capturée.

**9. Exécution.** On lance le programme avec des arguments ou une entrée standard, sous timeout, et on récupère stdout, le code de retour et le signal éventuel. L'entrée et la sortie passent par des fichiers temporaires, le programme tourne dans son propre groupe de processus, et tout le groupe est tué à la fin : aucun enfant lancé avec `fork()` ne reste en vie. La sortie est limitée à 1 Mo (au-delà, le système arrête le programme avec `SIGXFSZ`).
- Test : une boucle infinie donne TIMEOUT, et `*(volatile int *)0 = 0` donne SEGFAULT.
- Test : un enfant qui boucle est arrêté, que le programme finisse seul ou par timeout ; une sortie sans fin est coupée.

**10. Correcteur d'exos « programme ».** Chaque test compare la sortie à l'oracle, et on s'arrête au premier échec avec une **trace** comme celle de la moulinette : la commande du test, puis un diff en `cat -e` entre la sortie de l'étudiant (lignes `-`) et la sortie attendue (lignes `+`), et `Diff KO`. Un crash, un timeout ou une erreur de compilation donnent leur propre message à la place du diff. Le cœur renvoie le texte de la trace, et le shell l'écrit dans `traces/` (étape 18). Fichiers : `grader.py` et `trace.py`.

```
= Test 2 =======================================================================
$> ./repeat_twice "ab c" | cat -e
--- student
+++ moulinette
-ab c$
+ab c ab c$

Diff KO
```

- Test : une solution juste écrite par nous passe.
- Test : une solution sans `\n` échoue, et sa trace montre `-hello` contre `+hello$`, avec la commande du test.

**11. Exos « fonction ».** Un `main` de test est généré pour chaque variante. Le contrôle des fonctions interdites (étape 12, déjà faite) ne doit alors regarder que le code de l'étudiant, pas ce `main` de test (par exemple avec `nm -u` sur l'objet de l'étudiant seul). Fait : la compilation passe par des objets (`cc -c`), puis l'édition de liens avec le `main` de test. Fait aussi : un exo « fonction » peut donner `call` (un test écrit comme un appel C, `ft_x("abc", 'a')`), utilisé par les traces et par les exemples automatiques de son sujet. Les rendus en plusieurs fichiers (un header + un `.c`) marchent : seuls les `.c` sont compilés, les headers sont copiés. Un exo peut aussi fournir des fichiers (`provided_files`, un header avec une structure par exemple), écrits à côté du sujet et ajoutés à la compilation. Fait aussi : quand l'étudiant rend aussi un header, `check-catalog` prend le header de référence à côté de `ref.c`, sous son nom (`exercises/c/list_drop/node.h`). Fichier : `harness.py`, avec un modèle « fonction » original sur le thème « parcours de chaîne ».
- Test : une fonction juste passe, une fonction décalée de 1 échoue.
- Test : un rendu qui contient un `main` donne une erreur claire.

**12. Fonctions interdites.** On liste les fonctions utilisées avec `nm -u` et on les compare aux fonctions autorisées. Fichier : `checks.py`.
- Test : `printf`, alors que seul `write` est autorisé, échoue avec « Forbidden function: printf ».

**13. Fuites mémoire (activable exo par exo).** Avec valgrind s'il est présent.
- Test : un malloc sans free échoue.
- Test : sans valgrind dans le PATH, on affiche un avertissement et rien ne plante.

### Jalon 3 : garantir que la correction est juste

**14. `ref.c` paramétrée.** Un seul fichier C avec des `#if MODE == …`, compilé avec `-D…` pour chaque variante. Fichier : `exercises/c/char_filter/ref.c`.
- Vérifier : il compile sans erreur sous `-Werror` pour toutes les combinaisons autorisées.

**15. Commande `./42pal check-catalog`.** Pour chaque exo, on teste toutes les combinaisons de paramètres (ou 50 seeds s'il y en a trop) en comparant `ref.c` et l'oracle sur tous les tests. Fichier : `cli/check.py`.
- Test : avec un oracle volontairement faux, la commande échoue en nommant `exo#seed` et le test.
- Test : sur le vrai catalogue, la commande passe.

### Jalon 4 : le mode exam en terminal

**16. Définition d'un exam.** Un fichier par exam (`exams/rank02.json`, `exams/piscine.json`) donne le titre, le langage, le nombre de niveaux, la durée et la commande de compilation ; les durées d'attente après un échec viendront à l'étape 19. Les thèmes de chaque niveau viennent de `themes.json`, pour ne pas les écrire deux fois. Un niveau dont aucun thème n'a encore de modèle est signalé par un avertissement et ne peut pas être joué. Au tirage : un thème du niveau, puis un modèle de ce thème, puis une seed. Fichier : `exam.py`.
- Test : le rank 02 a 4 niveaux, et `char_filter` est jouable au niveau 2.
- Test : un niveau sans aucun modèle donne un avertissement.
- Test : un fichier d'exam mal écrit donne une erreur dès le chargement.
- Fait : la note suit 42_EXAM : chaque niveau réussi vaut 100 / nombre de niveaux (25 au rank 02), la note est sur 100, et l'exam est réussi à 100. Si les niveaux jouables s'arrêtent avant, l'exam s'arrête sous 100 et le dit. La note est affichée après chaque OK, dans `status`, dans le panneau du sujet (ce que vaut le niveau), dans le résumé et dans l'historique.

**17. Session.** On garde l'exam, le niveau, le sujet en cours (`exo#seed`), le début de l'exam, les tentatives et l'heure de la prochaine correction possible dans `~/.42pal/session.json`, pour pouvoir reprendre. On garde aussi, à part, l'historique des exams terminés (exam, niveau atteint, note, tentatives, durée) : c'est la base du futur score (voir « Plus tard : gamification »). Fichier : `session.py`.
- Test : sauvegarder puis recharger donne le même état (l'horloge est injectée pour les tests).
- Test : un exam terminé s'ajoute à l'historique, qui survit à une nouvelle session.
- Fait : au lancement, « Resume your exam? … (y/n) » reprend le même sujet (`exo#seed`), au même niveau, avec le même mode, le temps ayant continué de courir ; `n` garde l'ancien exam dans l'historique comme « abandoned » ; un exam expiré pendant l'absence y va comme « time » sans question. Ctrl-C garde la session ; `finish`, Ctrl-D, la fin du temps ou l'exam réussi la terminent. Le chronomètre de l'exam ne repart plus de zéro à chaque niveau (bug corrigé au passage).

**18. Le shell examshell.** D'abord un faux login comme à l'exam : le login est prérempli avec le nom d'utilisateur, et le mot de passe est masqué, accepte n'importe quoi, n'est jamais vérifié ni gardé. Puis le choix de l'exam et du niveau de départ (parmi les niveaux jouables), et tout se passe dans `~/42pal_exam/` (pas `~/42pal`, qui est souvent le dépôt cloné), avec les commandes `status`, `grademe`, `finish` et `help`. Au tirage : un thème du niveau, puis un modèle, puis une seed. L'affichage passe par `rich` (couleurs, tableau des résultats, minuteur en direct), et le prompt utilise `readline` pour l'historique et la complétion des commandes. C'est à cette étape qu'on copie `rich` dans `vendor/` et que `./42pal` l'ajoute au chemin de Python. Fichiers : `cli/shell.py` et `cli/display.py`. Fait aussi : avant le choix de l'exam, un premier menu demande qui l'on est, piscine (piscineux) ou étudiant (cursus), d'après le champ `audience` de chaque `exams/*.json` ; seuls les exams de ce public sont proposés, et un exam seul est pris sans question. Chaque menu dit ce que valent ses choix : les niveaux et la durée de chaque exam, les attentes de chaque mode, les points d'un niveau. Le dernier choix de chaque menu revient au menu d'avant (Quit dans le premier menu affiché, et dans le menu des thèmes de `practice`). En mode exam, le niveau de départ n'est plus demandé : on commence au niveau 1, comme à l'examen. Fait aussi : une interface plein écran avec textual (copié dans `vendor/`, comme rich), dans le style de la démo fournie : login, menus au clavier et à la souris avec le logo animé, puis un écran d'exam (en-tête avec le minuteur en direct et la note, sujet défilant avec PgUp/PgDn, journal des commandes, ligne `examshell>`, raccourcis g, s, f, ?). Les shells texte font tout le travail : l'écran leur envoie chaque commande (`handle`) et montre ce qu'ils affichent ; la correction tourne dans un thread. `--plain`, ou une entrée qui n'est pas un terminal, donne l'interface texte. Fichiers : `cli/tui.py` et `cli/tui.tcss`, tests dans `tests/test_tui.py` (pilote de textual). Fait aussi : au lancement, un `git fetch` en tâche de fond cherche une nouvelle version pendant le login ; après le login, 42pal propose la mise à jour (`git pull --ff-only`) puis redémarre (`os.execv`). Jamais de mot de passe demandé, abandon silencieux sans réseau, `PAL42_NO_UPDATE=1` pour couper (les tests le mettent). Fichier : `pal42/update.py`.

```
~/42pal_exam/
├── subjects/<exo>/subject.en.txt   le sujet tiré
├── rendu/<exo>/                    l'étudiant code ici
└── traces/                         une trace par grademe raté
```

`rendu/` est un simple dossier : `grademe` corrige les fichiers présents, commités ou non. Pour garder les réflexes du vrai exam, c'est aussi un dépôt git local relié à un dépôt nu caché dans `~/.42pal/rendu.git`, donc `git add`, `git commit` et `git push` marchent, sans être obligatoires. Si git manque, ce n'est qu'un dossier.

`grademe` affiche un spinner pendant la correction (« test 3/18 »), puis OK ou KO avec le chemin cliquable du journal (`traces/01_<nom>.trace`, écrit à chaque grademe), puis la trace elle-même dans le terminal, coupée après 25 lignes (entière dans le fichier).
- Vérifier à la main : une bonne solution fait passer au niveau suivant, une mauvaise écrit une trace dans `traces/`.
- Vérifier à la main : `git add . && git commit -m test && git push` marche dans `rendu/`.
- Fait : `rendu/` est un dépôt git qui pousse vers `~/.42pal/rendu.git` (`push.default=current`, identité locale seulement si aucune n'existe), et Tab complète les commandes de l'examshell. Fait aussi, en plein écran : un minuteur affiché en direct dans l'en-tête ; en mode texte, le temps reste vérifié à chaque commande. Fait aussi, pour le propriétaire seul : une commande cachée `cheat` (ni dans l'aide, ni dans la complétion) demande une phrase de passe, puis ouvre un menu du même style que les autres. Le code de ce menu est chiffré dans `pal42/cheat.pack` (clé tirée de la phrase par PBKDF2-HMAC-SHA256, chiffrement HMAC-SHA256 en mode compteur, puis HMAC d'intégrité, bibliothèque standard seulement) : sans la phrase, lire ou modifier 42pal n'en donne rien. Sa source en clair reste sur la machine du propriétaire, dans `cheat/` (ignoré par git), avec ses tests (`python3 -m unittest discover -s cheat`) ; `python3 -m pal42.cheat seal` la chiffre dans le pack, `python3 -m pal42.cheat open` la rend. Un exam où le menu a servi est marqué `"cheat": true` dans l'historique.

**19. Temps et nouvel essai.** L'exam s'arrête à la durée maximale. Après un échec, on retente le même sujet, et l'attente avant le prochain `grademe` augmente à chaque échec. Fait : le premier nouvel essai est gratuit, puis deux modes, choisis dans un menu après l'exam : **exam** (attente hard de 42_EXAM, 0,5 · 2,5 · 3 · 5,5 · 8,5 · 14 · 22,5 · 36,5 · 59 min, et la vraie durée) ou **révision** (attente soft 0, 1, 2, 3, 5 min, premier essai gratuit, sans limite de temps ; Entrée par défaut), réglable dans `retry_minutes` du fichier de l'exam ; l'attente repart de zéro après un sujet réussi. L'étudiant est prévenu : « If KO: next grademe in … » avant chaque correction, « Next grademe in … · if KO again: … » après un KO, et dans `status`. Fait aussi : l'exam s'arrête à la durée maximale (le temps est vérifié à chaque commande tapée : une commande trop tardive n'est pas exécutée, un `grademe` trop tardif n'est pas corrigé), avec un avertissement unique quand il reste moins de 10 minutes, et un résumé à la fin (niveaux réussis, `grademe` OK et KO, temps passé). Fait en plein écran : à la fin du temps, l'exam s'arrête de lui-même, sans attendre une commande.
- Test avec une horloge simulée : l'attente grandit d'un échec à l'autre, le sujet ne change pas, et l'exam se termine avec la note.

**20. Révision par thème.** `./42pal practice --theme <id>` enchaîne des variantes du même thème, sans timer. Fichier : `cli/practice.py`.
- Vérifier : 5 tirages donnent 5 seeds différentes, toutes du même thème.
- Fait : pas de login, pas de minuteur ni d'attente ; `grademe` (un OK passe au sujet suivant), `next`, `help`, `finish` (avec un bilan). Sans `--theme`, un menu des thèmes qui ont un exo ; un thème sans exo donne la liste des thèmes et le code de sortie 1.

**21. Installation au campus.** Un `README.md` (`git clone … && ./42pal`).
- Vérifier : sur un poste du campus, avec le `python3` du système, ça se lance sans pip ni sudo.
- Fait : `README.md` écrit (installation, exam, révision, catalogue, contribution). Vérifié depuis un clone neuf, avec `PATH=/usr/bin:/bin` (Python 3.10.12 du système) : exam, `practice`, `check-catalog` et les tests passent, sans rien installer.

### Jalon 5 : remplir le catalogue

Chaque exo est une étape : un thème, un modèle original, sa `ref.c`, et `check-catalog` qui passe.

**22. ~~Guide de contribution.~~ Abandonné** : les exos sont écrits par nous seulement, pas de guide ni de dossier modèle pour d'autres. Ancien texte : `CONTRIBUTING.md` et un dossier modèle `exercises/_template/`. La règle n°1 : décris le thème, écris ton propre nom, ton propre énoncé et tes propres exemples, et ne copie jamais un sujet réel.
- Vérifier : ajouter un deuxième modèle du thème `char_sets` en suivant uniquement le guide.

**23. Rank 02 jouable de bout en bout.** Un modèle par niveau d'abord, puis compléter les thèmes. Fait : tous les niveaux sont jouables. En cours : un exo par thème qui n'en a pas encore, dans l'ordre `bits` (`byte_rotate`, fait), `allocation` (`sequence_array`, fait), `list_changes` (`list_drop`, fait, l'étudiant rend aussi le header), `case_style` (`name_style`, fait), `number_parse` (`number_read`, fait), `int_arrays` (`tab_index`, fait), `int_sort` (`tab_sort`, fait), `stack_parsing` (`nest_report`, fait, niveau 4 de la finale), `string_search` (`longest_span`, fait, niveau 4 de la finale), puis les autres thèmes de la finale. Un thème doit garder une difficulté proche d'un niveau à l'autre, puisque chacun de ses exos peut être tiré à chacun de ses niveaux : `number_print`, `words` et `linked_lists` ont été coupés en deux pour que les modèles proches de `ft_itoa`, `rev_wstr` ou `ft_list_remove_if` (niveau 4 du rank 02) ne tombent plus au niveau 1 (`number_string`, `reorder_words`, `list_changes`). Fait ensuite : des modèles faciles pour `words` (`word_pick`), `number_print` (`base_print`) et `linked_lists` (`list_measure`, avec `cell.h` donné à côté du sujet, l'autre style des vrais sujets) ; le niveau 1 du rank 02 a de nouveau quatre exos. `check-catalog` note les variantes d'un exo en parallèle, pour que la suite de tests reste rapide. Audit de tous les exams : `themes.json` découle maintenant d'une table des vrais sujets de chaque niveau de 42_EXAM (des noms seulement) et du thème de chaque vrai sujet, gardée par un test (`tests/test_themes.py`). Les thèmes qui mêlaient un sujet facile et un sujet dur sont coupés : `program_args` / `option_flags`, `words` / `clean_words`, `number_parse` / `base_parse`, `number_print` / `print_in_base`, `arithmetic` / `primes`, `allocation` / `int_ranges`, `int_arrays` / `int_sort`. Restent sans exo, à remplir : `allocation` (comme `ft_strdup`), `number_parse` (`ft_atoi`), `number_print` (`fizzbuzz`), `arithmetic` (`do_op`), `clean_words`, `option_flags` et les thèmes durs de la finale. Ensuite, à la demande : autant d'exercices différents que dans les vrais exams, chacun dans le style d'un vrai sujet (le style de `rot_13` donne du rot-2, rot-3, rot-5…, jamais rot-13). Chaque thème est maintenant le style d'un seul vrai sujet (75 thèmes, nommés d'après le style, jamais d'après le sujet) : un niveau tire un style, puis un exercice de ce style, comme le vrai exam tire un des sujets du niveau. 33 styles sur 75 ont un exercice : le niveau 1 du rank 02 a ses 12 styles (`bip_bop`, `put_filter`, `copy_shape`, `pointer_pair`, `repeat_rule`, `rev_part`, `letter_step`, `replace_pick` ajoutés). Puis le niveau 2 du rank 02 a ses 15 styles (`mirror_group`, `word_from_end`, `merge_chars`, `sentence_case`, `bit_check`, `byte_show`, `dup_shape`, `compare_rule`, `read_int`, `span_set`). Puis le niveau 3 du rank 02 a ses 15 styles (`word_join`, `word_spread`, `caps_start`, `caps_end`, `prime_facts`, `divisor_facts`, `multiple_facts`, `arg_measure`, `op_table`, `hop_range`, `hidden_trace`). Puis le niveau 4 (`int_to_text`, `word_rotate`, `list_sort_by`, `zone_fill`) : **le rank 02 a tous ses styles** (49). Puis les 10 styles propres aux piscines (`letter_find`, `set_first`, `char_only`, `char_line`, `say_message`, `count_down`, `param_from_end`, `rev_inplace`, `bit_flip`, `match_trace`). 68 styles sur 75 : il reste les 7 styles de la finale (`ft_list_foreach`, `check_mate`, `brainfuck`, `cycle_detector`, `print_memory`, `options`, `rpn_calc`). Puis `list_loop` (style de `cycle_detector`, `ring.h` donné) et `list_each` (style de `ft_list_foreach`, `box.h` donné). Le rank 02 suit maintenant la liste des vrais sujets (57, noms seulement, contre 49 dans 42_EXAM) : `ft_strrev`, `reverse_bits` et `wdmatch` passent aussi au niveau 2, `ft_list_foreach`, `ft_list_remove_if` et `sort_int_tab` au niveau 4, et deux nouveaux styles ont leur exo, `set_run` (style de `ft_strspn`) et `set_find` (style de `ft_strpbrk`). 72 styles sur 77 : il reste les 5 styles de la finale (`check_mate`, `brainfuck`, `print_memory`, `options`, `rpn_calc`). Puis les 5 derniers : `board_threat` (style de `check_mate`, des pièces à nous), `tape_script` (`brainfuck`, avec d'autres boucles), `byte_dump` (`print_memory`, 8 ou 12 octets par ligne), `flag_mask` (`options`) et `expr_eval` (`rpn_calc`, en notation préfixe, postfixe compacte ou avec parenthèses). **Les 77 styles ont leur exercice.** Les énoncés sont maintenant remis en forme à 80 colonnes, paragraphe par paragraphe, après la substitution (`subject.reflow`) : plus de retour à la ligne avant chaque morceau variable ; les blocs de code (prototype, header) restent tels quels. À l'écran, les morceaux propres à la variante ressortent en gras violet (`display.subject_text`) ; le fichier du sujet reste en texte brut. Relecture de tous les énoncés : une dizaine de tournures corrigées.
- Vérifier : un exam complet terminé à la main. Fait, et automatisé : `tests/test_whole_exams.py` joue chacun des 9 exams du niveau 1 au dernier, en rendant à chaque niveau la solution de référence du sujet tiré (une `ref.c` reçoit ses `-D` en `#define` en tête de fichier, comme un vrai rendu) ; chaque exam doit finir à 100/100 et entrer dans l'historique comme réussi.

**24. Correcteur Python** (exos programme et fonction), dans `runners/python.py`. Il est d'abord testé sur un modèle simple d'un thème déjà connu. Les vrais modèles Python viendront quand les sujets auront été fournis. Dans le nouveau cursus, les ranks 03 à 06 sont en Python (14, 7, 7 et 9 sujets) ; on n'y prend que les notions, jamais les énoncés. Fait : `runners/python.py` (vérification de la syntaxe avec `py_compile`, puis `python3` sur un main de test qui importe la fonction de l'étudiant et affiche `repr()` de son résultat), `checks.python_violations` (imports et appels interdits, lus avec `ast`), un `ref.py` par exo vérifié par `check-catalog`, le runner choisi selon le langage du sujet, et `$prototype` pour une déclaration qui change avec la variante. Les 37 styles Python sont dans `themes.json`. **Le rank 03 est jouable** (`exams/rank03.json`, 6 niveaux, 3 h, durée à confirmer) avec ses 14 styles : `nest_check`, `key_sort`, `mirror_word`, `grid_turn`, `trace_letters`, `char_mix`, `base_shift`, `digit_steps`, `letter_bag`, `merge_twist`, `char_balance`, `case_wave`, `shift_list`, `key_shift`. Menus : le menu « Student » propose le rank 02 et le rank 03 (avec le langage de chaque exam), et la révision demande d'abord le langage (C ou Python). Puis les ranks 04 (`turn_find`, `star_chart`, `common_sorted`, `merge_many`, `mirror_parts`, `need_order`, `window_stat`), 05 (`run_pack`, `path_fill`, `slot_share`, `loop_seek`, `zone_count`, `grid_seek`, `word_chain`) et 06 (`word_tree`, `string_pack`, `task_plan`, `edge_spare`, `word_complete`, `set_groups`, `value_keeper`, `top_heap`, `cut_find`), avec un main de test pour les classes (`class_harness` : le test donne les arguments du constructeur et une liste d'appels de méthodes). **Les 37 styles Python ont leur exercice** ; les ranks 03 à 06 sont jouables (durée de 3 h à confirmer ; le rank 06 a 2 niveaux, les seuls dont on connaît les sujets). Ensuite, à la demande : la révision est un choix du premier menu (« What do you want to do? » : exams de la piscine, exams des étudiants, ou Practice), dans le terminal et en plein écran ; Back dans le menu des langages revient au premier menu. Le README a une image d'en-tête et deux captures du plein écran (`docs/images/`), prises avec un login générique.
- Test : une solution juste passe, une fausse échoue avec une trace.

**25. ~~Correcteur C++~~ Abandonné** : dans le nouveau cursus, les ranks 03 à 06 sont en Python, et seul le nouveau cursus compte. Ancien texte : `c++ -std=c++98 -Wall -Wextra -Werror` et un premier modèle sur un thème du rank 05.

**26. ~~Gros sujets~~ Abandonné** pour la même raison : ces sujets (shell et pipes, serveur réseau, printf, lecture ligne par ligne) sont ceux de l'ancien cursus. Ancien texte : un sujet original par thème, avec peu ou pas de paramètres et un correcteur sur mesure.

**27. Exams de la piscine** (`exams/piscine_*.json`), en réutilisant les thèmes C. Fait : 4 exams comme dans 42_EXAM, `piscine_01` (8 niveaux, 4 h), `piscine_02` (8, 4 h), `piscine_03` (4, 4 h) et `piscine_final` (4, 8 h), avec les niveaux des thèmes repris des noms d'exos de 42_EXAM (thèmes seulement) et 4 nouveaux thèmes pour la finale (`stack_parsing`, `interpreters`, `memory_dump`, `string_search`). Tous les niveaux des 5 exams sont jouables.

### Jalon 6 : web (plan séparé, après les premiers retours du campus)

FastAPI importe le même cœur. La correction tourne dans un conteneur Docker sans réseau, avec des limites de CPU, de mémoire et de processus, et un système de fichiers en lecture seule. On y ajoute un éditeur dans le navigateur, la connexion 42 et le suivi de la progression.

Le déploiement doit pouvoir changer de serveur : tout passe par Docker Compose et un fichier `.env`, sans rien de propre au VPS OVH. Passer au serveur de l'école reviendra à copier le compose et le `.env`.

### Plus tard : gamification (phase 2, seulement pour ceux qui le veulent)

Un score et des classements, **uniquement sur la base du volontariat** : c'est désactivé par défaut, on peut s'inscrire et se retirer à tout moment, et se retirer efface ses données du classement.

- **Score** : calculé à partir des exams terminés (niveau atteint, note, temps, nombre de tentatives) et des révisions par thème. La formule reste à définir.
- **Classements** : par promo (piscine ou année d'entrée en cursus), par campus et par exam. La promo et le campus viennent de la connexion 42.
- **Ce qui est visible** : le login (ou un pseudo), le score et le rang, jamais le code rendu.

**Ce qu'on prépare dès la phase 1**, pour ne pas tout refaire :
- La session (étape 17) garde l'historique des exams terminés, en local. Rien ne quitte la machine en phase 1.
- Le cœur renvoie les résultats sous forme de données (note, tentatives, durées) et non de texte, pour qu'on puisse les compter plus tard.
- Seules les corrections faites sur le serveur (jalon 6) compteront pour le classement : en local, l'étudiant peut modifier le correcteur, donc un score local n'est pas fiable.

## Risques

- **Un oracle faux donne des corrections fausses.** C'est le risque n°1. La parade est la double implémentation (oracle et `ref.c`), avec `check-catalog` obligatoire avant d'ajouter un exo.
- **Pas de sujets publics.** Le catalogue dépendra des thèmes que les étudiants décriront, d'où la liste des thèmes tôt (étape 7) et un guide de contribution clair (étape 22).
- **Une variante trop proche du sujet réel.** Les combinaisons interdites, et des noms et énoncés écrits par nous, limitent ce risque.
- **Une variante plus dure que son niveau.** Il faut garder des paramètres de même difficulté et relire chaque modèle.
- **La version de Python sur les postes du campus est inconnue.** On vise 3.10 et on vérifie dès l'étape 1.
- **valgrind peut manquer sur certains postes.** Dans ce cas, le contrôle des fuites est désactivé avec un avertissement.
- **Le cœur doit rester sans affichage**, sinon le web ne pourra pas s'y brancher.
- **Un classement pousse à tricher.** En local, le correcteur et l'oracle sont modifiables : seuls les exams corrigés sur le serveur comptent pour le classement.

## Questions ouvertes

- Sujets Python : à fournir plus tard, uniquement comme source de thèmes.
- Au vrai exam, après un échec, retente-t-on le même sujet ? C'est le comportement par défaut ici, et c'est réglable.
- Gamification : quelle formule de score ? Classement par login ou par pseudo ?

## Hors périmètre (phase 1)

- Le web, les comptes, la connexion 42, le score et le classement (phase 2, voir « Plus tard : gamification »).
- La génération de sujets par IA.
- L'anti-triche.
- Le support macOS testé (le vrai exam est sous Linux).
- La traduction des sujets.
