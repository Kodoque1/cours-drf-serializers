# TP3 — Cycle de vie de l'objet

**Fichiers concernés :** `boutique/serializers.py` (démo), `formation/serializers.py` (à toi de jouer)
**Concepts :** `ModelSerializer`/`extra_kwargs`, `save()` vs `create()`, hachage du mot de passe

## Objectif

Comprendre que `save()` est un **dispatcher générique** qu'on ne touche
jamais, et que le hachage du mot de passe se fait dans `create()`, jamais
dans `save()` — pour éviter un mot de passe stocké en clair.

---

## 🧑‍🏫 Modélisation / Démo prof (I do)

**Problème métier :** après inscription, le mot de passe ne doit **jamais**
être lisible en base de données.

```python
class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "password_confirm"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
        }

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        email = validated_data["email"]
        return User.objects.create_user(
            username=email, email=email, password=validated_data["password"]
        )
```

Points à faire ressortir à l'oral :
- `save()` (héritée, jamais réécrite) décide "création ou update ?" puis
  délègue à `create()` ou `update()` — c'est **ces deux méthodes** qu'on
  override, jamais `save()`.
- `User.objects.create_user()` hache le mot de passe (`set_password()` en
  interne) ; `User.objects.create()` le stockerait tel quel, en clair.
- `extra_kwargs` permet d'ajuster une option (ici `write_only`,
  `min_length`) sur un champ déjà généré par `ModelSerializer`, sans le
  redéclarer entièrement.

Piège à montrer explicitement :

```python
def save(self, **kwargs):                    # ❌ override du dispatcher
    data = self.validated_data
    data.pop("password_confirm")
    return User.objects.create(**data)       # ❌ mot de passe en clair
```

Démo :

```python
from boutique.serializers import SignupSerializer
s = SignupSerializer(data={"email": "demo@ipssi.fr", "password": "abcdefgh", "password_confirm": "abcdefgh"})
s.is_valid()
user = s.save()
user.password   # un hash, jamais "abcdefgh"
```

---

## 👥 Pratique guidée (We do)

Dans `boutique/serializers.py`, enlève temporairement le corps de
`SignupSerializer.create()` et retape-le toi-même, en suivant le prof.

Vérifie :

```bash
python manage.py test boutique.tests.SignupSerializerTests.test_inscription_valide_hache_le_mot_de_passe
```

---

## 🚀 Pratique autonome / Challenge (You do)

**Problème métier miroir :** `Formateur` n'est pas un compte Django
(pas de `create_user()` disponible) — il stocke lui-même son mot de passe
haché dans `Formateur.password_hash`. Utilise
`django.contrib.auth.hashers.make_password()` (même idée que
`create_user()`, mais explicite).

Complète `formation/serializers.py` → `FormateurSignupSerializer.create()` :

- [ ] Retire `password_confirm` et `password` de `validated_data`.
- [ ] Crée le `Formateur` avec `password_hash=make_password(<le mot de passe>)`.

Valide ton travail :

```bash
python manage.py test formation.tests.test_tp3
```

### ✅ Critères de réussite

- `Formateur.password_hash` n'est jamais égal au mot de passe en clair.
- `django.contrib.auth.hashers.check_password("motdepasse123", formateur.password_hash)`
  renvoie `True`.
- Un seul `Formateur` est créé en base (pas d'erreur si `password_confirm`
  n'a pas été retiré avant l'appel à `Formateur.objects.create(...)`).
