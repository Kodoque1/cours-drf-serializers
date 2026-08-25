# TP4 — Champs avancés

**Fichiers concernés :** `boutique/serializers.py` (démo), `formation/serializers.py` (à toi de jouer)
**Concepts :** `source`, `error_messages`, `SerializerMethodField`, `partial=True`

## Objectif

Manipuler des champs qui ne collent pas exactement au modèle : un champ
renommé/traversant une relation (`source`), un champ calculé
(`SerializerMethodField`), un message d'erreur sur mesure
(`error_messages`), et une mise à jour partielle (`partial=True`).

---

## 🧑‍🏫 Modélisation / Démo prof (I do)

**Problème métier :** sur une réservation, on veut afficher le nom de la
salle (`room.name`) sous la clé `room_name`, et le nombre de jours restants
avant la réservation — deux informations qui ne sont pas des colonnes
directes de `Booking`.

```python
class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    jours_restants = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ["id", "room", "room_name", "user", "date", "jours_restants"]

    def get_jours_restants(self, obj):
        return (obj.date - timezone.now().date()).days
```

Points à faire ressortir à l'oral :
- `source="room.name"` traverse la relation (chemin à points) — le champ
  exposé s'appelle `room_name`, l'attribut réel est `room.name`.
- `SerializerMethodField` est **toujours en lecture seule** ; sa méthode
  compagnon s'appelle `get_<nom_du_champ>` et reçoit l'**instance
  complète** (`obj`), pas juste le nom du champ.
- `error_messages` (ici via `extra_kwargs`) permet un message clair plutôt
  que le message générique DRF :

```python
extra_kwargs = {
    "email": {"error_messages": {"required": "L'email est obligatoire."}},
}
```

- `partial=True` désactive **uniquement** le check "required" sur les
  champs **absents** de la requête — un champ présent (même vide/invalide)
  est toujours validé normalement. C'est ce que `RetrieveUpdateAPIView`
  utilise automatiquement pour un PATCH (jamais pour un PUT).

Démo :

```python
from boutique.serializers import UserProfileSerializer
s = UserProfileSerializer(some_user, data={}, partial=True)
s.is_valid()   # True : aucun champ requis, car aucun n'est présent
```

---

## 👥 Pratique guidée (We do)

Dans `boutique/serializers.py`, enlève temporairement `room_name`,
`jours_restants` et `get_jours_restants` de `BookingSerializer`, et
`extra_kwargs` de `UserProfileSerializer`, puis retape-les toi-même.

Vérifie :

```bash
python manage.py test boutique.tests.BookingSerializerTests.test_room_name_et_jours_restants_sont_exposes
```

---

## 🚀 Pratique autonome / Challenge (You do)

**Problème métier miroir :** sur un `Creneau`, on veut afficher l'email du
formateur (`formateur.email`) sous la clé `formateur_email`, et le nombre
d'**heures** restantes avant le créneau. Sur le profil d'un `Formateur`, un
téléphone manquant doit afficher un message clair.

Complète `formation/serializers.py` :

- [ ] `CreneauSerializer.formateur_email` — remplace la déclaration actuelle
      par un champ utilisant `source="formateur.email"` (regarde comment
      `salle_nom` est fait juste au-dessus, c'est la même mécanique).
- [ ] `CreneauSerializer.get_heures_restantes(self, obj)` — retourne le
      nombre d'heures (entier) entre maintenant et `obj.horaire`
      (`django.utils.timezone.now()`).
- [ ] `FormateurProfileSerializer.Meta.extra_kwargs` — ajoute un message
      personnalisé **exactement** `"Le téléphone est obligatoire."` sur la
      clé `"required"` du champ `"telephone"`.

Valide ton travail :

```bash
python manage.py test formation.tests.test_tp4
```

### ✅ Critères de réussite

- `CreneauSerializer(creneau).data["formateur_email"]` renvoie bien l'email
  du formateur lié, pas une valeur brute.
- `heures_restantes` renvoie un nombre cohérent avec l'écart réel.
- Un `FormateurProfileSerializer` sans `telephone` renvoie l'erreur exacte
  `"Le téléphone est obligatoire."` sur la clé `telephone`.
