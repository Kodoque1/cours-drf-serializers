# TP2 — Mécanismes déclaratifs

**Fichiers concernés :** `boutique/serializers.py`, `boutique/validators.py` (démo),
`formation/serializers.py`, `formation/validators.py` (à toi de jouer)
**Concepts :** `validators=[...]`, `UniqueValidator`, `Meta.validators`,
`UniqueTogetherValidator`, validator custom réutilisable

## Objectif

Comprendre que `validators=[...]` est un mécanisme **indépendant** de
`validate_<champ>`/`validate()` — orchestré par `is_valid()`, mais jamais
imbriqué dedans — et savoir écrire un validator réutilisable entre
plusieurs serializers.

---

## 🧑‍🏫 Modélisation / Démo prof (I do)

**Problème métier n°1 :** deux comptes ne doivent jamais partager le même
email. `User.email` n'est **pas** unique en base par défaut dans Django —
il faut donc l'imposer nous-mêmes.

```python
email = serializers.EmailField(
    validators=[UniqueValidator(queryset=User.objects.all())]
)
```

Piège à montrer explicitement (et pourquoi c'est un piège) :

```python
def validate_email(self, value):
    if User.objects.filter(email=value).exists():   # double travail !
        raise serializers.ValidationError("Email déjà utilisé.")
    return value
```

**Problème métier n°2 :** une salle ne peut pas être réservée deux fois au
même créneau — une contrainte sur **deux champs combinés**, donc
object-level et déclarative :

```python
class Meta:
    model = Booking
    validators = [
        UniqueTogetherValidator(queryset=Booking.objects.all(), fields=["room", "date"])
    ]
```

**Problème métier n°3 :** la règle « email `@ipssi.fr` » doit être
réutilisable sur plusieurs serializers, sans copier-coller
(`boutique/validators.py`) :

```python
class CompanyEmailValidator:
    def __init__(self, domain):
        self.domain = domain          # état d'instance, fixé à la construction

    def __call__(self, value):
        if not value.endswith(self.domain):
            raise serializers.ValidationError(f"Domaine {self.domain} requis.")
```

Point à faire ressortir : DRF appelle un validator avec **un seul argument**
(`validator(value)`) — toute configuration (ici, `domain`) doit donc être
fixée à la construction (`__init__`), pas à l'appel. Et on ne nomme jamais
sa classe `EmailValidator` : collision avec `django.core.validators`.

---

## 👥 Pratique guidée (We do)

1. Dans `boutique/serializers.py`, enlève temporairement le
   `validators=[UniqueValidator(...)]` du champ `email` de `SignupSerializer`,
   puis retape-le toi-même.
2. Dans `BookingSerializer`, enlève `Meta.validators`, puis retape-le.
3. Dans `boutique/validators.py`, retape `CompanyEmailValidator` toi-même
   (sans le corrigé sous les yeux).

Vérifie :

```bash
python manage.py test boutique.tests.BookingSerializerTests
python manage.py test boutique.tests.CompanyEmailValidatorTests
```

---

## 🚀 Pratique autonome / Challenge (You do)

**Problème métier miroir n°1 :** deux `Formateur` ne doivent pas partager
le même email (`Formateur.email` n'est pas unique non plus, exprès).

**Problème métier miroir n°2 :** deux `Creneau` ne peuvent pas partager la
même `salle` au même `horaire`.

**Problème métier miroir n°3 :** un numéro de téléphone doit être
réutilisable comme règle sur plusieurs serializers (préfixe configurable :
`"0"` ou `"+33"` selon le contexte).

Complète :

- [ ] `formation/serializers.py` → `FormateurSignupSerializer.email` :
      ajoute `validators=[UniqueValidator(queryset=Formateur.objects.all())]`.
- [ ] `formation/serializers.py` → `CreneauSerializer.Meta` : ajoute
      `validators = [UniqueTogetherValidator(queryset=Creneau.objects.all(), fields=["salle", "horaire"])]`.
- [ ] `formation/validators.py` → `FrenchPhoneValidator` : implémente
      `__init__(self, prefix)` (attribut d'instance) et
      `__call__(self, value)` (lève une erreur si `value` ne commence pas
      par `self.prefix`).

Valide ton travail :

```bash
python manage.py test formation.tests.test_tp2
```

### ✅ Critères de réussite

- Un email déjà utilisé par un `Formateur` existant est rejeté.
- Deux `Creneau` sur la même salle et le même horaire : le second est rejeté.
- Le même horaire sur une **autre** salle est accepté.
- `FrenchPhoneValidator(prefix="0")("0612345678")` ne lève rien.
- `FrenchPhoneValidator(prefix="0")("+33612345678")` lève une `ValidationError`.
