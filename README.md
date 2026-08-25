# Serializers & Validations DRF — Bloc 1

Support de cours niveau Mastère sur les serializers Django REST Framework :
slides, document de référence, 6 TP et un projet Django prêt à l'emploi.

## Contenu

| Fichier / dossier | Rôle |
|---|---|
| `slides.html` | Support de présentation (reveal.js). Volontairement épuré : c'est un support d'**oral**. |
| `reference_serializers_validations.md` | **Le polycopié détaillé.** Cas limites, pièges, ordre d'exécution de `is_valid()`. |
| `tps/` | Les 6 TP, format *I do / We do / You do*. |
| `tp_django/` | Projet Django barebone support des TP. |
| `bilan_bloc1_serializers_validations.md` | Synthèse courte (lexique + formulations clés). |
| `theme-ipssi.css` | Thème reveal.js clair/sombre. |

## Progression

Les 6 TP suivent la progression des slides, du plus simple au plus complexe :

1. **Validation de champ & d'objet** — `validate_<champ>`, `validate(attrs)`
2. **Mécanismes déclaratifs** — `validators=[...]`, `UniqueTogetherValidator`, validators custom
3. **Cycle de vie** — `save()` vs `create()`, hachage du mot de passe
4. **Champs avancés** — `source`, `SerializerMethodField`, `error_messages`, `partial=True`
5. **Contexte & représentation** — `context`, `to_representation()`
6. **Relations** — serializers imbriqués, `ListSerializer`, `HyperlinkedModelSerializer`

## Démarrer

```bash
cd tp_django
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test          # doit être vert côté boutique/
```

Ouvrir `slides.html` dans un navigateur pour la présentation
(connexion internet requise : reveal.js est chargé via CDN).

## Structure du projet Django

Deux applications, la même logique enseignée deux fois :

- **`boutique/`** — ressource **principale**, démo du prof. Implémentation
  complète et testée : c'est la référence montrée au tableau.
- **`formation/`** — ressource **miroir**, à compléter par les étudiants.
  Modèles fournis, serializers parsemés de `# TODO TPx`.

Chaque TP a son fichier de tests :

```bash
python manage.py test formation.tests.test_tp1   # TP1
python manage.py test formation                  # tous les TP
```

Un `NotImplementedError` dans la sortie signifie « TODO non fait » — c'est le
signal attendu, pas un bug.

## ⚠️ Avant de distribuer aux étudiants

`tp_django/corrige/` contient la **solution complète** de `formation/`.
Ne pas le distribuer avec le reste.

`formation/` doit être dans sa version stub. Pour la restaurer après avoir
consulté le corrigé :

```bash
cd tp_django
cp stubs/formation_serializers_stub.py formation/serializers.py
cp stubs/formation_validators_stub.py formation/validators.py
```

## Vérifié sur

Django 6.1 · djangorestframework 3.18 · Python 3.12
