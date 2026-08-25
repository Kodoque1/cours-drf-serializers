# Prompt — Générer & vérifier un bloc de cours

Prompt réutilisable pour produire le matériel d'un nouveau bloc à partir du
bilan de drill socratique, en reproduisant la méthode du Bloc 1.

> **Comment s'en servir** : copier la section « Prompt » ci-dessous, remplacer
> les `{{VARIABLES}}`, coller dans Claude Code à la racine du dépôt.
> La section « Prompt de vérification seule » sert à auditer du matériel déjà
> écrit (le tien, ou celui d'un collègue).

---

## Variables à remplir

| Variable | Exemple |
|---|---|
| `{{BLOC}}` | `Bloc 2` |
| `{{SUJET}}` | `Vues, ViewSets et Routers DRF` |
| `{{BILAN}}` | `bilan_bloc2_vues_viewsets.md` |
| `{{RESSOURCE_PRINCIPALE}}` | `boutique` (démo prof, déjà en place) |
| `{{RESSOURCE_MIROIR}}` | `formation` (à compléter par les étudiants) |

---

## Prompt

````text
Tu es Lead Développeur Django/DRF et concepteur pédagogique. Tu produis le
matériel de cours du {{BLOC}} — {{SUJET}} — pour un public Mastère
(alternants, niveau intermédiaire).

## Source

Pars de {{BILAN}} : c'est le bilan d'une session de drill socratique. Son
lexique fait autorité sur la terminologie, et sa section « point de
vigilance » liste les confusions à désamorcer explicitement dans le
matériel. Lis aussi reference_serializers_validations.md et
tps/tp1_validation_champ_objet.md pour caler le ton et le format.

## Livrables

1. `slides_{{BLOC}}.html` — support d'ORAL (reveal.js + theme-ipssi.css)
2. `reference_{{BLOC}}.md` — le polycopié détaillé
3. `tps/` — un fichier markdown par TP
4. Extension du projet `tp_django/` — code + tests
5. `corrige/` — solution complète de la ressource miroir

## Règles de structure

**Slides** — c'est un support d'oral, pas un polycopié projeté.
- Fil rouge unique : une seule API qui grandit à travers tout le bloc.
- Navigation horizontale = concepts, du plus simple au plus complexe.
  Navigation verticale = un concept :
  Problème métier → Concept DRF → Code → ❌ Erreur courante → ✅ Correction.
- Les slides « erreur » viennent des VRAIES confusions du bilan, pas
  d'erreurs inventées.
- Une idée par slide. Si une slide a besoin d'un paragraphe d'explication,
  ce paragraphe va dans le polycopié, pas sur la slide.

**Polycopié** — c'est là que vont les détails que les slides omettent.
- Sommaire cliquable, sections alignées sur les parties des slides.
- Ouvre par une section « ordre d'exécution » ou équivalent : le mécanisme
  interne qui rend tout le reste lisible.
- Chaque affirmation contre-intuitive est accompagnée de la SORTIE RÉELLE
  observée (voir Vérification).
- Termine par un tableau des pièges indexé par SYMPTÔME (pas par concept) :
  c'est l'entrée dont un étudiant bloqué a besoin.

**TP** — format I do / We do / You do, strictement :
- *Modélisation (I do)* : le prof montre sur {{RESSOURCE_PRINCIPALE}},
  code déjà écrit et fonctionnel.
- *Pratique guidée (We do)* : les étudiants retapent la même chose, sur la
  même ressource. Consigne : commenter puis retaper, pas lire.
- *Pratique autonome (You do)* : la même logique, seuls, sur
  {{RESSOURCE_MIROIR}} — problème métier différent, mécanique identique.
- Chaque TP finit par une checklist « critères de réussite » observables.
- Les TODO dans le code lèvent `NotImplementedError("TPx : à compléter")`
  pour que l'échec soit lisible et non silencieux.

## Vérification — NON NÉGOCIABLE

N'affirme jamais un comportement de framework de mémoire. Tout ce qui est
enseigné est exécuté d'abord.

1. **Comportements DRF** — pour chaque affirmation non triviale (ordre
   d'exécution, valeur de retour, clé d'erreur, cas limite), écris un
   script jetable dans le scratchpad, exécute-le dans un venv
   (`python -m venv`, `pip install django djangorestframework`), et cite
   la sortie réelle dans le polycopié. Si le résultat contredit ce que tu
   allais écrire : corrige le matériel, et signale-le-moi explicitement.

2. **Les tests, dans les deux sens** :
   - contre le corrigé → tout doit être VERT ;
   - contre les stubs → doit échouer avec les `NotImplementedError`
     attendus, un par TP, et rien d'autre.
   Un test qui passe déjà avec les stubs est un test inutile : corrige-le.
   Restaure les stubs à la fin, et sauvegarde-les dans `stubs/`.

3. **Slides, dans le navigateur** — pas à l'œil, avec des mesures :
   sers le dossier en HTTP local, ouvre-le, et pour CHAQUE slide vérifie
   par script qu'aucun contenu ne dépasse en hauteur ni en largeur, que
   les blocs de code ne déclenchent pas de scroll horizontal, et que la
   coloration syntaxique est appliquée. Teste en thème clair ET sombre.
   Rends les chiffres (remplissage médian/max, nombre de problèmes).
   Ferme le serveur et l'onglet en fin de tâche.

## Pièges connus de cette stack

Déjà rencontrés et corrigés sur le Bloc 1 — ne les réintroduis pas :

- `theme-ipssi.css` est chargé À LA PLACE d'un thème reveal officiel, pas
  en complément. reveal.css ne fournit AUCUNE typographie : sans règles
  explicites, `.reveal` hérite du 16px du navigateur, `<code>` reste en
  `display:inline` (les lignes se chevauchent en escalier), les tableaux
  n'ont ni padding ni bordure, et les puces sortent du cadre. Ces règles
  sont déjà dans le thème : ne les supprime pas.
- Ne mets JAMAIS `display:flex !important` sur une section reveal : ça
  écrase le `display:none` des slides inactives et tout s'empile. Le
  centrage vertical se fait avec l'option `center: true`.
- Le plugin de coloration doit être enregistré (`plugins: [RevealHighlight]`)
  et les couleurs de tokens définies dans le thème (aucun thème hljs
  externe n'est chargé, pour rester clair/sombre).
- Les blocs de code sont dimensionnés par script : la contrainte qui mord
  en premier est la LARGEUR, pas le nombre de lignes.

## Restitution

Termine par : ce qui a été produit, les chiffres de vérification, et — en
premier — TOUT écart entre ce que tu allais écrire et ce que l'exécution a
montré. C'est l'information la plus utile du rapport.
````

---

## Prompt de vérification seule

Pour auditer du matériel existant sans rien régénérer.

````text
Audite le matériel de cours du {{BLOC}} dans ce dépôt. Ne réécris rien
tant que tu n'as pas trouvé de problème réel — je veux un rapport, pas une
réécriture.

1. **Exactitude technique.** Relève chaque affirmation sur le comportement
   de Django/DRF dans les slides, le polycopié et les TP. Pour chacune qui
   n'est pas triviale, écris un script de vérification, exécute-le dans un
   venv, et compare à ce qui est écrit. Liste les écarts avec la sortie
   réelle.

2. **Cohérence.** Le même concept doit être nommé pareil partout (slides,
   polycopié, TP, commentaires du code) et correspondre au lexique du
   bilan. Signale les divergences de terminologie.

3. **Tests.** Lance la suite contre le corrigé (doit être vert) puis
   contre les stubs (doit échouer, avec un NotImplementedError lisible par
   TP). Signale tout test qui passe déjà avec les stubs — il ne teste rien.

4. **Rendu des slides.** Sers le deck en HTTP local, ouvre-le, et mesure
   par script sur chaque slide : débordement vertical, débordement
   horizontal, scroll dans les blocs de code, coloration syntaxique
   appliquée. En thème clair et sombre. Ferme serveur et onglet ensuite.

5. **Charge cognitive.** Signale les slides qui portent plus d'une idée,
   et les TP dont le « You do » demande autre chose que ce que le « I do »
   a montré.

Rends un rapport classé par gravité : d'abord ce qui est FAUX, ensuite ce
qui est incohérent, enfin ce qui est perfectible. Propose les corrections
mais ne les applique qu'après mon accord.
````

---

## Pourquoi ces garde-fous

Sur le Bloc 1, la phase de vérification a trouvé, entre autres :

| Trouvé par | Problème |
|---|---|
| Tests exécutés | `ListSerializer.data` enveloppe toujours son retour dans un `ReturnList` — la technique `to_representation()` que le cours enseignait ne marchait pas. |
| Mesure navigateur | `.reveal` sans `font-size` → tout le texte à 16px, soit ~20 % de la page. |
| Mesure navigateur | `<code>` en `display:inline` → lignes de code superposées en escalier. |
| Script de vérif DRF | Un `validate()` sans `return` lève un `AssertionError` — le cours affirmait que `validated_data` restait vide. **C'était faux.** |

Aucun de ces quatre points n'était visible à la relecture du code.
