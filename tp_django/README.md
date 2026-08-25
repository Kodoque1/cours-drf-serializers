# Projet barebone — TP Serializers & Validations DRF

Deux apps, une seule logique enseignée deux fois :

- **`boutique/`** — ressource **principale**, démo du prof (I do). Solution
  complète et fonctionnelle : `Utilisateur` (inscription), `Booking`
  (réservation de salle), `Order`/`OrderItem` (commande).
- **`formation/`** — ressource **miroir**, à compléter par les étudiants
  (We do / You do). Modèles déjà écrits, serializers à moitié faits
  (`# TODO TPx` un peu partout) : `Formateur` (inscription), `Creneau`
  (réservation de salle), `Session`/`Inscription` (commande).

Les 6 TP correspondants sont dans `../tps/`.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## Lancer les tests d'un TP

```bash
python manage.py test formation.tests.test_tp1   # TP1
python manage.py test formation.tests.test_tp2   # TP2
python manage.py test formation.tests.test_tp3   # TP3
python manage.py test formation.tests.test_tp4   # TP4
python manage.py test formation.tests.test_tp5   # TP5
python manage.py test formation.tests.test_tp6   # TP6

python manage.py test formation                  # tous les TP
python manage.py test boutique                   # vérifie la démo prof
```

Tant qu'un TODO n'est pas résolu, son test échoue avec un
`NotImplementedError` explicite (pas un échec silencieux) : c'est le signal
que le TP n'est pas terminé, pas un bug.

## Lancer le serveur pour tester à la main

```bash
python manage.py runserver
```

Endpoints (voir `boutique/urls.py` / `formation/urls.py`), par ex. :
`POST /api/formation/signup/`, `POST /api/formation/creneaux/`,
`GET/PATCH /api/formation/formateurs/<id>/`,
`GET/POST /api/formation/sessions/`, `GET /api/formation/sessions/<id>/`.

## `corrige/`

Solution complète de `formation/` — réservée au formateur, ne pas
distribuer avec le reste du projet (voir `corrige/README.md`).
