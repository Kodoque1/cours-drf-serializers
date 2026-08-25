# TP6 — Relations

**Fichiers concernés :** `boutique/serializers.py` (démo), `formation/serializers.py` (à toi de jouer)
**Concepts :** serializer imbriqué en écriture, `many=True`/`ListSerializer`, `HyperlinkedModelSerializer`

## Objectif

Gérer une création imbriquée (une ressource + ses sous-éléments en un seul
POST), une donnée calculée sur **toute** une liste, et la représentation
d'une relation en URL plutôt qu'en identifiant brut.

---

## 🧑‍🏫 Modélisation / Démo prof (I do)

**Problème métier n°1 :** créer une `Order` et ses `OrderItem` en un seul
POST. `ModelSerializer.create()` ne sait pas le faire tout seul — il faut
l'override :

```python
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order
```

**Problème métier n°2 :** calculer un total sur **toute** la liste des
commandes (pas commande par commande) :

```python
class OrderListSerializer(serializers.ListSerializer):
    # ⚠️ ListSerializer.data enveloppe TOUJOURS le retour dans un
    # ReturnList, même si to_representation() renvoie un dict. Il faut
    # donc surcharger `data` directement, pas `to_representation()`.
    @property
    def data(self):
        orders = super().data
        total = sum(float(i["price"]) * i["quantity"] for o in orders for i in o["items"])
        return {"total": total, "orders": orders}

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = OrderListSerializer
```

**Problème métier n°3 :** dans une API publique, exposer une URL cliquable
vers la commande plutôt qu'un simple ID :

```python
class OrderHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ["url", "user", "created_at"]
```

Points à faire ressortir à l'oral :
- Le nested write n'est jamais automatique côté écriture, contrairement à
  la lecture (`items` s'affiche tout seul en sortie).
- `many=True` déclenche un `ListSerializer` ; pour une logique globale
  (total, count...), on le subclasse et on le branche via
  `Meta.list_serializer_class`.
- `HyperlinkedModelSerializer` remplace `id` par `url` — c'est un choix de
  représentation des relations, indépendant du nested write vu juste avant.

---

## 👥 Pratique guidée (We do)

Dans `boutique/serializers.py`, enlève temporairement le corps de
`OrderSerializer.create()` et de `OrderListSerializer.data`, puis
retape-les toi-même.

Vérifie :

```bash
python manage.py test boutique.tests.OrderSerializerTests
```

---

## 🚀 Pratique autonome / Challenge (You do)

**Problème métier miroir :** une `Session` de formation a plusieurs
`Inscription`. On veut : (1) créer une session et ses inscriptions en un
seul POST, (2) afficher le nombre total d'inscriptions sur toutes les
sessions, (3) comparer `SessionSerializer` à `SessionHyperlinkedSerializer`
(déjà fourni) pour comprendre ce qui change.

Complète `formation/serializers.py` :

- [ ] `SessionSerializer.create()` — `pop("inscriptions")`, crée la
      `Session`, puis boucle pour créer chaque `Inscription` liée.
- [ ] `SessionListSerializer.data` — retourne
      `{"total_inscriptions": <somme des inscriptions de toutes les sessions>, "sessions": ...}`.

Valide ton travail :

```bash
python manage.py test formation.tests.test_tp6
```

Regarde ensuite `SessionHyperlinkedSerializer` (déjà écrit) et compare sa
sortie à celle de `SessionSerializer` sur la même instance — sois prêt à
expliquer à l'oral ce que `url` change concrètement.

### ✅ Critères de réussite

- Un POST avec une liste `inscriptions` crée bien la `Session` **et**
  chaque `Inscription` liée.
- `SessionSerializer(Session.objects.all(), many=True).data` renvoie un
  dict avec les clés `total_inscriptions` et `sessions` (pas une simple
  liste).
- `SessionHyperlinkedSerializer(session, context={"request": request}).data`
  contient `url` et ne contient pas `id`.
