# TP — Serializers & Validations DRF

6 TP, à faire dans l'ordre, sur le projet `../tp_django/`.

## Format de chaque TP

- **Modélisation / Démo prof (I do)** — le prof montre le code sur la
  ressource **principale** (`boutique/`) et explique le concept.
- **Pratique guidée (We do)** — vous retapez la même logique, à l'identique,
  toujours sur `boutique/`, en suivant le prof.
- **Pratique autonome / Challenge (You do)** — vous appliquez la même
  logique, seuls, sur votre ressource **miroir** (`formation/`). Un jeu de
  tests valide votre travail.

## Installation (une seule fois)

```bash
cd tp_django
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## Se situer

| Ressource principale (prof, déjà écrite) | Ressource miroir (vous, à compléter) |
|---|---|
| `Utilisateur` (inscription) | `Formateur` (inscription) |
| `Booking` (réservation de salle) | `Creneau` (réservation de salle) |
| `Order` / `OrderItem` (commande) | `Session` / `Inscription` (commande) |

## Valider un TP

```bash
python manage.py test formation.tests.test_tp1   # remplacer 1 par le numéro du TP
```

Un `NotImplementedError` dans la sortie du test veut juste dire « TODO non
fait » — ce n'est pas un bug du projet.
