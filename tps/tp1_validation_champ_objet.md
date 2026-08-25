# TP1 — Validation de champ & d'objet

**Fichiers concernés :** `boutique/serializers.py` (démo), `formation/serializers.py` (à toi de jouer)
**Concepts :** `validate_<champ>`, `validate(self, attrs)`

## Objectif

Distinguer une règle qui ne concerne **qu'un seul champ** (field-level)
d'une règle qui compare **plusieurs champs entre eux** (object-level), et
savoir écrire les deux sans les confondre.

---

## 🧑‍🏫 Modélisation / Démo prof (I do)

**Problème métier :** l'inscription à la boutique doit être rejetée si
l'email ne se termine pas par `@ipssi.fr` — et si `password` et
`password_confirm` ne correspondent pas.

Le prof ouvre `boutique/serializers.py` → `SignupSerializer` et explique,
ligne par ligne :

```python
def validate_email(self, value):
    if not value.endswith("@ipssi.fr"):
        raise serializers.ValidationError("Email IPSSI requis.")
    return value

def validate(self, attrs):
    if attrs["password"] != attrs["password_confirm"]:
        raise serializers.ValidationError(
            {"password_confirm": "Les mots de passe ne correspondent pas."}
        )
    return attrs
```

Points à faire ressortir à l'oral :
- `validate_email` est appelée **automatiquement** par `is_valid()`, par
  convention de nom (`validate_` + nom du champ) — personne ne l'appelle
  explicitement.
- Elle doit **retourner** `value` (jamais un booléen) : c'est cette valeur
  de retour qui atterrit dans `validated_data["email"]`.
- `validate(self, attrs)` s'exécute **après** tous les `validate_<champ>`
  — elle reçoit le dict complet déjà validé champ par champ.
- Elle doit retourner `attrs` en entier : sans `return`, DRF lève un
  `AssertionError: .validate() should return the validated data`.
  (Asymétrie à connaître : un `validate_<champ>` sans `return` ne lève rien
  du tout — il met silencieusement le champ à `None`.)
- `ValidationError("...")` → erreur globale (`non_field_errors`).
  `ValidationError({"champ": "..."})` → erreur ciblée sur ce champ.

Démo dans le terminal (`python manage.py shell`) :

```python
from boutique.serializers import SignupSerializer
s = SignupSerializer(data={"email": "a@gmail.com", "password": "x", "password_confirm": "x"})
s.is_valid()      # False
s.errors          # {'email': [...]}
```

---

## 👥 Pratique guidée (We do)

Dans `boutique/serializers.py`, commente temporairement le corps de
`validate_email` et de `validate` dans `SignupSerializer`, puis **retape-les
toi-même**, à l'identique, sans regarder le corrigé — en suivant le prof
au tableau.

Vérifie que tu retrouves le comportement attendu :

```bash
python manage.py test boutique.tests.SignupSerializerTests
```

Les 4 tests doivent passer.

---

## 🚀 Pratique autonome / Challenge (You do)

**Problème métier miroir :** un `Formateur` s'inscrit avec un `email`, un
`telephone` et un `password`/`password_confirm`. Le téléphone doit être un
numéro français : il doit commencer par `"0"` ou par `"+33"`. Les deux mots
de passe doivent correspondre.

Ouvre `formation/serializers.py` → `FormateurSignupSerializer` et complète :

- [ ] `validate_telephone(self, value)` — field-level, comme `validate_email`
      côté boutique, mais sur le téléphone.
- [ ] `validate(self, attrs)` — object-level, comme côté boutique, mais
      cible l'erreur sur `password_confirm`.

Valide ton travail :

```bash
python manage.py test formation.tests.test_tp1
```

### ✅ Critères de réussite

- Un téléphone qui ne commence ni par `0` ni par `+33` est rejeté, avec une
  erreur sur la clé `telephone`.
- Un téléphone valide (`0612345678` ou `+33612345678`) est accepté.
- Deux mots de passe différents sont rejetés, avec une erreur sur la clé
  `password_confirm`.
- Deux mots de passe identiques passent la validation.
