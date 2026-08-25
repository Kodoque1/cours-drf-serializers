# TP5 — Contexte & représentation

**Fichiers concernés :** `boutique/serializers.py` (démo), `formation/serializers.py` (à toi de jouer)
**Concepts :** `context`, `to_representation()`

## Objectif

Adapter la sortie JSON en fonction de **qui** fait la requête, sans jamais
provoquer une boucle infinie ni inverser une condition de sécurité.

---

## 🧑‍🏫 Modélisation / Démo prof (I do)

**Problème métier :** un profil ne doit afficher l'email que s'il s'agit du
propriétaire du compte — jamais l'email de quelqu'un d'autre.

```python
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request is not None and request.user != instance:
            data.pop("email")
        return data
```

Points à faire ressortir à l'oral :
- `context` est un **dictionnaire** : `context={"request": request}`, jamais
  `context=request.user` directement.
- Dans les vues génériques DRF, `self.get_serializer(...)` peuple
  automatiquement ce contexte (`{"request": ..., "view": ..., "format": ...}`)
  — pas besoin de le faire à la main.
- `to_representation()` doit **toujours** commencer par
  `data = super().to_representation(instance)` : appeler `self.to_representation()`
  à la place de `super()` provoque une boucle infinie (`RecursionError`).
- La condition doit comparer correctement (`!=`, pas `==`) : une condition
  inversée est un vrai bug de sécurité (fuite de données), pas juste une
  erreur de logique anodine.

Démo :

```python
from types import SimpleNamespace
from boutique.serializers import UserProfileSerializer

data_owner = UserProfileSerializer(user_a, context={"request": SimpleNamespace(user=user_a)}).data
data_other = UserProfileSerializer(user_a, context={"request": SimpleNamespace(user=user_b)}).data
# "email" est dans data_owner, absent de data_other
```

---

## 👥 Pratique guidée (We do)

Dans `boutique/serializers.py`, enlève temporairement le corps de
`UserProfileSerializer.to_representation()` et retape-le toi-même — en
partant bien de `super().to_representation(instance)`, pas de `self`.

Vérifie :

```bash
python manage.py test boutique.tests.UserProfileSerializerTests
```

---

## 🚀 Pratique autonome / Challenge (You do)

**Problème métier miroir :** le numéro de téléphone d'un `Formateur` ne
doit **jamais** être visible pour un visiteur anonyme — seulement pour une
requête authentifiée (peu importe qui, contrairement à la démo prof qui
comparait un propriétaire précis).

Complète `formation/serializers.py` → `FormateurProfileSerializer.to_representation()` :

- [ ] Après `data = super().to_representation(instance)`, retire
      `data["telephone"]` si `self.context["request"].user.is_authenticated`
      est `False`.

Valide ton travail :

```bash
python manage.py test formation.tests.test_tp5
```

### ✅ Critères de réussite

- Un visiteur anonyme (`AnonymousUser`) ne voit jamais `telephone` dans la
  réponse.
- Un utilisateur authentifié (n'importe lequel) voit `telephone`.
- `email` reste visible dans tous les cas — seul `telephone` est concerné.
