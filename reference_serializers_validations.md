# Serializers & Validations DRF — Document de référence

> Support détaillé du **Bloc 1**. Les slides (`slides.html`) sont un support
> d'oral : elles ne contiennent que l'essentiel. Ce document contient les
> détails, les cas limites et les pièges — c'est ici qu'on revient après le
> cours, et pendant les TP (`tps/`).
>
> Tous les comportements décrits ici ont été **vérifiés** sur Django 6.1 /
> DRF 3.18. Quand une affirmation est contre-intuitive, la sortie réelle est
> donnée.

## Sommaire

1. [Vocabulaire de base](#1-vocabulaire-de-base)
2. [L'ordre d'exécution de `is_valid()`](#2-lordre-dexécution-de-is_valid) ← *la clé de tout le bloc*
3. [Validation de champ & d'objet](#3-validation-de-champ--dobjet)
4. [Mécanismes déclaratifs](#4-mécanismes-déclaratifs)
5. [Cycle de vie de l'objet](#5-cycle-de-vie-de-lobjet)
6. [Champs avancés](#6-champs-avancés)
7. [Contexte & représentation](#7-contexte--représentation)
8. [Relations](#8-relations)
9. [Tableau des pièges](#9-tableau-des-pièges)
10. [Aide-mémoire](#10-aide-mémoire)

---

## 1. Vocabulaire de base

Ces distinctions ne sont pas de la pédanterie : chacune correspond à une
erreur classique en TP.

| Terme | Définition | À ne pas confondre avec |
|---|---|---|
| **Méthode** | Fonction définie dans une classe, prend `self` | **Fonction** : indépendante, pas de `self` |
| **Désérialisation** | JSON entrant → Python (`validated_data`) | **Sérialisation** : instance → JSON sortant |
| `raise` | Lève une exception, **interrompt** le flux | `return` : renvoie une valeur, le flux continue |
| **Attribut d'instance** | Propre à chaque objet, posé dans `__init__` | **Attribut de classe** : partagé par toutes les instances |
| **Override** | Redéfinir une méthode héritée | **Overload** : surcharge par signature — n'existe pas en Python |

**Le sens de la flèche.** C'est la confusion la plus fréquente et la plus
coûteuse :

```
Client → JSON → [DÉSÉRIALISATION] → validated_data → create() → base de données
Base   →  ORM → [SÉRIALISATION]   → .data          → JSON     → client
```

Une règle de validation agit **toujours** en désérialisation (entrée).
`read_only` / `write_only` décident, eux, de quel côté un champ existe.

---

## 2. L'ordre d'exécution de `is_valid()`

Le point qui rend tout le reste lisible. Quand on appelle `serializer.is_valid()`,
DRF exécute **six étapes, dans cet ordre**, pour chaque requête :

```
POUR CHAQUE CHAMP (dans l'ordre de déclaration) :
  1. validate_empty_values()  → required / allow_null / default
  2. to_internal_value()      → conversion de type ("3" → 3)
  3. run_validators()         → la liste validators=[...] du champ   ◄ déclaratif
  4. validate_<champ>()       → ta méthode                            ◄ manuel

UNE FOIS TOUS LES CHAMPS VALIDÉS :
  5. Meta.validators          → UniqueTogetherValidator, etc.         ◄ déclaratif
  6. validate(attrs)          → ta méthode                            ◄ manuel
```

Trois conséquences à retenir :

**(a) Le déclaratif passe avant le manuel**, aux deux niveaux (3 avant 4,
5 avant 6). Donc quand `validate_email()` s'exécute, `UniqueValidator` a
déjà tourné.

**(b) Un échec arrête la suite pour ce champ.** Si un `validators=[...]`
lève, le `validate_<champ>` correspondant **n'est jamais appelé**.

**(c) Si un seul champ échoue, `validate()` n'est jamais appelée.** C'est
logique : `validate()` reçoit `attrs`, or `attrs` serait incomplet. D'où
une règle pratique — dans `validate()`, tu peux accéder à `attrs["password"]`
sans crainte du `KeyError`… **sauf** si le champ est optionnel ou absent
d'un PATCH. Dans le doute : `attrs.get("password")`.

> **Vérification** — trace réelle d'un serializer instrumenté :
> ```
> 1-2. to_internal_value (required + conversion de type)
> 3.   validators=[...] du champ
> 4.   validate_<champ> (méthode)
> 5.   Meta.validators (objet)
> 6.   validate() (objet)
> ```
> et avec un `validators=[...]` qui lève :
> ```
> is_valid: False  {'email': ['nope']}
> trace: ['validators=[...] -> LÈVE']    ← validate_email jamais appelée
> ```

---

## 3. Validation de champ & d'objet

### 3.1 `validate_<champ>(self, value)`

Validation d'**un seul champ**, isolément.

```python
def validate_email(self, value):
    if not value.endswith("@ipssi.fr"):
        raise serializers.ValidationError("Email IPSSI requis.")
    return value
```

- Appelée **automatiquement** par `is_valid()`, par convention de nommage
  (`validate_` + nom exact du champ). Personne ne l'appelle explicitement.
- Reçoit la valeur **déjà convertie** au bon type (étape 2 ci-dessus) :
  pour un `IntegerField`, `value` est un `int`, pas une chaîne.
- Doit **retourner la valeur**. Cette valeur de retour est ce qui atterrit
  dans `validated_data[champ]` — on peut donc l'utiliser pour normaliser :
  ```python
  def validate_email(self, value):
      return value.lower().strip()   # normalisation au passage
  ```

> ⚠️ **Piège silencieux.** Un `validate_<champ>` sans `return` ne lève
> **aucune erreur** : la méthode renvoie `None`, et le champ vaut `None`
> dans `validated_data`.
> ```
> validate_<champ> sans return -> is_valid: True   validated_data = {'x': None}
> ```
> C'est la donnée qui part en base. Contrairement à `validate()` (voir
> 3.2), rien ne t'avertit.

### 3.2 `validate(self, attrs)`

Validation **entre plusieurs champs**, une fois tous les champs validés.

```python
def validate(self, attrs):
    if attrs["password"] != attrs["password_confirm"]:
        raise serializers.ValidationError(
            {"password_confirm": "Les mots de passe ne correspondent pas."}
        )
    return attrs
```

- Reçoit le dictionnaire complet, doit retourner **le dictionnaire complet**.
- Sert dès que la règle compare deux champs (mot de passe, date de début
  vs date de fin, cohérence prix/remise…).

> ⚠️ Un `validate()` sans `return` lève, lui, une erreur explicite :
> ```
> AssertionError: .validate() should return the validated data
> ```
> Asymétrie à connaître : bruyant au niveau objet, **silencieux** au niveau
> champ.

### 3.3 Cibler l'erreur : chaîne vs dictionnaire

Le type passé à `ValidationError` détermine **où** l'erreur s'affiche côté
client — donc sous quel champ du formulaire.

```python
raise serializers.ValidationError("message")            # → non_field_errors
raise serializers.ValidationError({"champ": "message"}) # → sous "champ"
```

> **Vérification** :
> ```
> string au niveau objet -> clés d'erreur : ['non_field_errors']
> dict   au niveau objet -> clés d'erreur : ['x']
> ```

Dans un `validate_<champ>`, pas besoin de dictionnaire : DRF sait déjà de
quel champ il s'agit, une chaîne suffit.

### 3.4 Le code HTTP

`is_valid(raise_exception=True)` lève une `ValidationError` que DRF
transforme automatiquement en réponse **400**. Aucun `try/except` à écrire
dans la vue.

| Code | Sens | Exemple |
|---|---|---|
| **400** | Les données envoyées sont invalides | email mal formé, mots de passe différents |
| **401** | Non authentifié — « je ne sais pas qui tu es » | token absent ou expiré |
| **403** | Authentifié mais pas autorisé — « je sais qui tu es, tu n'as pas le droit » | user non-admin sur une route admin |
| **500** | Bug côté serveur | `KeyError` dans ton `create()` |

Confondre 401 et 403 est l'erreur classique : la distinction porte sur
*identité* (401) vs *permission* (403).

---

## 4. Mécanismes déclaratifs

### 4.1 La grille à retenir

Deux axes indépendants : le **périmètre** (un champ / tout l'objet) et le
**style** (une méthode que j'écris / un objet que je déclare).

|            | Méthode manuelle        | Mécanisme déclaratif        |
|------------|-------------------------|-----------------------------|
| **Champ**  | `validate_<champ>()`     | `validators=[...]`          |
| **Objet**  | `validate()`             | `Meta.validators = [...]`   |

Les deux colonnes s'exécutent **toutes les deux**, orchestrées par
`is_valid()` — la colonne déclarative en premier (cf. §2). Elles ne
s'appellent **jamais** l'une l'autre.

> C'est la source d'un contresens fréquent : *« comme le modèle a
> `unique=True`, `ModelSerializer` ajoute le test d'unicité dans mon
> `validate_email` »*. **Non.** Il ajoute un `UniqueValidator` dans la liste
> `validators` du champ. Deux mécanismes séparés, qui tournent tous les deux.

### 4.2 `validators=[...]` sur un champ

```python
from rest_framework.validators import UniqueValidator

email = serializers.EmailField(
    validators=[UniqueValidator(queryset=User.objects.all())]
)
```

Le `queryset` dit **où chercher** les doublons. À préférer à un
`validate_email` qui ferait un `.filter().exists()` à la main : c'est
réutilisable, et `ModelSerializer` le génère tout seul quand le modèle
porte `unique=True`.

### 4.3 `Meta.validators` — l'équivalent objet

Pour une contrainte portant sur **plusieurs champs combinés** :

```python
from rest_framework.validators import UniqueTogetherValidator

class Meta:
    model = Booking
    validators = [
        UniqueTogetherValidator(
            queryset=Booking.objects.all(),   # UN seul queryset
            fields=["room", "date"],          # les champs de la contrainte
        )
    ]
```

**Un** queryset (la table où chercher) + **une liste** de champs. L'erreur
classique est d'en passer deux (`queryset_room`, `queryset_date`) : la
contrainte porte sur une combinaison au sein d'une seule table.

Côté modèle, l'équivalent Django est `unique_together` (ou
`UniqueConstraint`), et `ModelSerializer` en génère automatiquement le
`UniqueTogetherValidator` :

```python
class Meta:                                  # dans le MODÈLE
    unique_together = [["room", "date"]]     # liste de listes :
                                             #  - liste externe = plusieurs contraintes
                                             #  - liste interne = les champs d'UNE contrainte
```

### 4.4 Écrire un validator réutilisable

**Version fonction** — quand la règle n'a aucun paramètre :

```python
def validate_ipssi_domain(value):
    if not value.endswith("@ipssi.fr"):
        raise serializers.ValidationError("Domaine @ipssi.fr requis.")
```

**Version classe** — dès que la règle est **configurable** :

```python
class CompanyEmailValidator:
    def __init__(self, domain):
        self.domain = domain              # état d'INSTANCE, fixé à la construction

    def __call__(self, value):
        if not value.endswith(self.domain):
            raise serializers.ValidationError(f"Domaine {self.domain} requis.")
```

Usage : `EmailField(validators=[CompanyEmailValidator(domain="@ipssi.fr")])`

Pourquoi une classe ? Parce que **DRF appelle un validator avec un seul
argument** : `validator(value)`. Il n'y a aucun moyen de lui passer le
domaine au moment de l'appel — il faut donc le stocker à la construction.
C'est exactement le rôle d'un attribut d'instance.

> ⚠️ **Ne nomme jamais ta classe `EmailValidator`** : collision avec
> `django.core.validators.EmailValidator`. Préfixe par le métier
> (`CompanyEmailValidator`).
>
> ⚠️ « Une classe peut stocker un état **statique** » est un contresens :
> un attribut posé dans `__init__` est *par définition* propre à l'instance,
> donc l'inverse de statique. Un attribut *de classe* (déclaré hors
> `__init__`) serait, lui, partagé par tous les validators.

---

## 5. Cycle de vie de l'objet

### 5.1 `ModelSerializer` : ce qu'il génère tout seul

À partir du modèle, il **introspecte** et déduit :

| Sur le modèle | Génère sur le serializer |
|---|---|
| `CharField(max_length=100)` | `CharField(max_length=100)` |
| `EmailField()` | `EmailField()` (+ validation de format) |
| `null=False, blank=False` | `required=True` |
| `unique=True` | un `UniqueValidator` dans `validators=[...]` |
| `unique_together` | un `UniqueTogetherValidator` dans `Meta.validators` |

### 5.2 `extra_kwargs` : ajuster sans redéclarer

Pour changer **une option** d'un champ auto-généré, sans le réécrire en
entier :

```python
class Meta:
    model = User
    fields = ["id", "email", "password"]
    extra_kwargs = {
        "password": {"write_only": True, "min_length": 8},
        "email": {"error_messages": {"required": "L'email est obligatoire."}},
    }
```

C'est un **dictionnaire de dictionnaires** : nom du champ → options. Sans
lui, il faudrait redéclarer `password = serializers.CharField(...)` et
perdre tout ce que l'introspection avait déduit.

### 5.3 `save()` vs `create()` / `update()`

```
serializer.save()
    ├── self.instance is None ?  → create(validated_data)
    └── sinon                    → update(instance, validated_data)
```

`save()` est un **dispatcher générique** fourni par DRF. Son seul travail
est de choisir entre création et mise à jour. **On ne l'override jamais** —
on override `create()` et/ou `update()`.

```python
def create(self, validated_data):
    validated_data.pop("password_confirm")     # champ de contrôle, pas une colonne
    return User.objects.create_user(**validated_data)
```

> `password_confirm` doit être retiré : ce n'est pas un champ du modèle.
> Sinon `Model.objects.create(**validated_data)` lève
> `TypeError: 'password_confirm' is an invalid keyword argument`.

### 5.4 Le mot de passe : `create_user()` vs `create()`

```python
User.objects.create(password="secret")        # ❌ stocké EN CLAIR
User.objects.create_user(password="secret")   # ✅ haché (set_password en interne)
```

Pour un modèle qui n'est pas un `User` Django, hacher explicitement :

```python
from django.contrib.auth.hashers import make_password

def create(self, validated_data):
    validated_data.pop("password_confirm")
    password = validated_data.pop("password")
    return Formateur.objects.create(
        password_hash=make_password(password), **validated_data
    )
```

> ⚠️ **Deux préoccupations totalement séparées**, souvent confondues :
> - `create_user()` / `make_password()` → **stockage** (le mot de passe est
>   haché en base)
> - `write_only=True` → **exposition API** (le mot de passe ne ressort pas
>   dans le JSON)
>
> L'un ne remplace pas l'autre. Il faut **les deux** : sans hachage, la base
> est compromise ; sans `write_only`, l'API renvoie le hash au client.

---

## 6. Champs avancés

### 6.1 `source` — découpler nom exposé et attribut réel

```python
room_name = serializers.CharField(source="room.name", read_only=True)
```

Le chemin à points traverse les relations. Le JSON expose `room_name`,
la donnée vient de `instance.room.name`.

Sert aussi à renommer simplement : `nom = CharField(source="last_name")`.

### 6.2 `SerializerMethodField` — un champ calculé

```python
jours_restants = serializers.SerializerMethodField()

def get_jours_restants(self, obj):
    return (obj.date - timezone.now().date()).days
```

- Toujours en **lecture seule** (jamais en entrée).
- Méthode compagnon obligatoirement nommée `get_<nom_du_champ>`.
- `obj` est **l'instance complète** du modèle : on accède librement à ses
  attributs. Inutile de déclarer quoi que ce soit sur les champs à lire.

### 6.3 `read_only` / `write_only`

| Option | En entrée (désérialisation) | En sortie (sérialisation) |
|---|---|---|
| *(défaut)* | ✅ accepté | ✅ renvoyé |
| `read_only=True` | ❌ **ignoré** | ✅ renvoyé |
| `write_only=True` | ✅ accepté | ❌ absent |

> **Vérification** :
> ```
> write_only -> validated_data: ['email','password']  |  sortie .data: ['email']
> read_only  -> validated_data: {'name': 'n'}         (slug ignoré en entrée)
> ```
> Noter le `read_only` : une valeur envoyée par le client est **silencieusement
> ignorée**, pas rejetée. C'est la protection contre l'injection de champs
> calculés ou d'identifiants.

Il n'existe **ni** `PasswordField`, **ni** option `hidden=True` dans DRF.
Le masquage en sortie, c'est `write_only=True`, rien d'autre.

### 6.4 `error_messages`

```python
email = serializers.EmailField(
    error_messages={
        "required": "L'email est obligatoire.",
        "blank": "L'email ne peut pas être vide.",
        "invalid": "Format d'email invalide.",
    }
)
```

Les clés correspondent aux types d'erreur standard du champ. Via
`extra_kwargs` sur un `ModelSerializer` (cf. §5.2) pour ne pas redéclarer
le champ. Il n'existe pas de message global pour tous les champs : c'est
par champ, ce qui est heureux — un bon message est spécifique.

### 6.5 `partial=True`

```python
serializer = UserSerializer(instance, data=request.data, partial=True)
```

Utilisé automatiquement par `partial_update()` (PATCH), jamais par
`update()` (PUT).

**Ce qu'il fait exactement** : il neutralise le contrôle `required` pour
les champs **absents** de la requête. C'est tout.

**Ce qu'il ne fait pas** : il ne désactive aucune validation sur les champs
**présents**. Un champ présent mais invalide est rejeté normalement.

> **Vérification** :
> ```
> partial + champ ABSENT   -> is_valid: True   {}
> partial + champ INVALIDE -> is_valid: False  {'email': ['Enter a valid email address.']}
> ```

---

## 7. Contexte & représentation

### 7.1 `context` — faire entrer l'ambiant

Un serializer ne connaît, par défaut, que les données qu'on lui passe. Pour
savoir *qui* fait la requête, il faut le lui dire :

```python
MySerializer(data=request.data, context={"request": request})
```

`context` attend un **dictionnaire** (l'erreur classique :
`context=request.user`). La convention est de passer l'objet `request`
complet sous la clé `"request"`, pas juste le user — on ne sait pas d'avance
ce dont on aura besoin.

Puis, dans le serializer :

```python
self.context["request"].user
```

**Dans les vues génériques, c'est automatique.** `self.get_serializer(...)`
appelle `get_serializer_context()`, qui fournit :

```python
{"request": self.request, "view": self, "format": self.format_kwarg}
```

On ne passe donc `context=` à la main que si l'on instancie le serializer
soi-même (dans un `APIView` brut, une commande, un test).

> C'est la **vue** qui construit le contexte, pas le serializer. Le
> serializer ne fait que le consulter.

Défensif — le contexte peut être absent (test, appel direct) :

```python
request = self.context.get("request")
if request is not None and request.user != instance:
    ...
```

### 7.2 `to_representation()` — modifier le JSON de sortie

```python
def to_representation(self, instance):
    data = super().to_representation(instance)     # ← TOUJOURS super()
    request = self.context.get("request")
    if request is not None and request.user != instance:
        data.pop("email")
    return data
```

Deux règles absolues :

1. **Commencer par `super().to_representation(instance)`.** Appeler
   `self.to_representation(instance)` se rappelle elle-même → `RecursionError`.
2. **Vérifier le sens de la condition.** Ici `!=` : on masque l'email quand
   le lecteur **n'est pas** le propriétaire. Avec `==`, on masque son propre
   email et on expose celui des autres — une fuite de données, pas une
   coquille.

Pour un seul champ calculé, préférer `SerializerMethodField` (§6.2) :
`to_representation` est un outil lourd, réservé aux modifications
conditionnelles de la structure de sortie.

---

## 8. Relations

### 8.1 Serializer imbriqué en écriture

En **lecture**, l'imbrication marche toute seule :

```python
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
```

En **écriture**, non : `ModelSerializer.create()` ne sait pas transformer
une liste de dictionnaires en objets liés par clé étrangère. Il faut
l'écrire :

```python
def create(self, validated_data):
    items_data = validated_data.pop("items")        # 1. sortir l'imbriqué
    order = Order.objects.create(**validated_data)  # 2. créer le parent
    for item_data in items_data:                    # 3. créer les enfants
        OrderItem.objects.create(order=order, **item_data)
    return order
```

L'ordre est contraint : l'enfant a besoin de la clé étrangère du parent,
donc le parent doit exister d'abord.

> Le blocage n'a **rien à voir avec `many=True`**. `many=True` gère très bien
> la lecture d'une liste ; c'est `create()` qui ne sait pas écrire une
> relation inverse.

### 8.2 `many=True` et `ListSerializer`

`MySerializer(many=True)` ne renvoie pas un `MySerializer` : DRF construit
un **`ListSerializer`** dont l'attribut `child` est ton serializer.

Pour une logique portant sur **toute la liste** (un total, un regroupement),
on sous-classe `ListSerializer` et on le branche via
`Meta.list_serializer_class` :

```python
class OrderListSerializer(serializers.ListSerializer):
    @property
    def data(self):
        orders = super().data
        total = sum(float(i["price"]) * i["quantity"]
                    for o in orders for i in o["items"])
        return {"total": total, "orders": orders}


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "user", "items"]
        list_serializer_class = OrderListSerializer
```

> ⚠️ **Piège non documenté.** L'instinct est d'override `to_representation()`,
> comme au §7.2. **Ça ne marche pas ici** : `ListSerializer.data` enveloppe
> systématiquement le retour de `to_representation()` dans un `ReturnList(...)`.
> Un dictionnaire y est reconstruit en liste de ses **clés** — on récupère
> `['total', 'orders']` au lieu du dictionnaire.
>
> Pour changer la **forme** du résultat, il faut donc surcharger `data`
> lui-même, comme ci-dessus. Pour modifier chaque élément *sans* changer la
> forme, `to_representation()` reste correct.

### 8.3 `HyperlinkedModelSerializer`

Change la manière dont les **relations** sont représentées : une URL vers la
ressource, au lieu d'une clé primaire.

```python
class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ["url", "user", "created_at"]
```

| | `ModelSerializer` | `HyperlinkedModelSerializer` |
|---|---|---|
| Identifiant | `"id": 12` | `"url": "http://api/orders/12/"` |
| Relation | `"user": 3` | `"user": "http://api/users/3/"` |
| Prérequis | — | une vue nommée `<model>-detail` + `request` dans le contexte |

Trois représentations possibles d'une relation, à ne pas confondre :

```json
"user": 3                              // PK          (ModelSerializer)
"user": "http://api/users/3/"          // hyperlien   (HyperlinkedModelSerializer)
"user": {"id": 3, "email": "a@b.fr"}   // imbriqué    (UserSerializer())
```

L'hyperlien est un **lien vers** la ressource, pas la ressource elle-même :
le client doit faire une seconde requête pour obtenir le détail.

---

## 9. Tableau des pièges

| Symptôme | Cause | Correction |
|---|---|---|
| La validation ne rejette rien | `return False` au lieu de `raise` | `raise serializers.ValidationError(...)` |
| Un champ vaut `None` en base | `validate_<champ>` sans `return` | Retourner `value` |
| `AssertionError: .validate() should return...` | `validate()` sans `return` | Retourner `attrs` |
| `TypeError: invalid keyword argument` dans `create()` | `password_confirm` non retiré | `validated_data.pop("password_confirm")` |
| Mot de passe lisible en base | `objects.create()` | `create_user()` / `make_password()` |
| Mot de passe renvoyé par l'API | Pas de `write_only` | `write_only=True` (en plus du hachage) |
| `RecursionError` | `self.to_representation()` | `super().to_representation()` |
| L'email des autres est visible | Condition inversée (`==` / `!=`) | Vérifier le sens |
| `total` absent, on reçoit `['total','orders']` | `to_representation` sur un `ListSerializer` | Surcharger `data` |
| Erreur sur `non_field_errors` au lieu du champ | `ValidationError("texte")` | `ValidationError({"champ": "texte"})` |
| `KeyError` dans `validate()` sur un PATCH | Champ absent en partiel | `attrs.get("champ")` |
| Collision de noms de validators | Classe nommée `EmailValidator` | Préfixer : `CompanyEmailValidator` |

**Et le piège de méthode** : inventer un nom d'API plausible quand on ne
sait pas. `ErrorHandler`, `PasswordField`, `hidden=True`, `construct_<champ>`
— aucun n'existe. Le bon réflexe est de dire « je ne sais pas » et d'ouvrir
la documentation : un nom inventé qui sonne juste coûte plus cher qu'une
question.

---

## 10. Aide-mémoire

```python
class MonSerializer(serializers.ModelSerializer):

    # --- champs déclarés explicitement -----------------------------------
    email       = serializers.EmailField(
                      validators=[UniqueValidator(queryset=User.objects.all())])
    password    = serializers.CharField(write_only=True, min_length=8)
    nom_salle   = serializers.CharField(source="salle.name", read_only=True)
    calcule     = serializers.SerializerMethodField()

    class Meta:
        model  = MonModele
        fields = ["id", "email", "password", "nom_salle", "calcule"]

        extra_kwargs = {                      # ajuster sans redéclarer
            "email": {"error_messages": {"required": "Email obligatoire."}},
        }

        validators = [                        # contrainte multi-champs
            UniqueTogetherValidator(queryset=MonModele.objects.all(),
                                    fields=["a", "b"]),
        ]

        list_serializer_class = MonListSerializer   # logique sur many=True

    # --- validation -------------------------------------------------------
    def validate_email(self, value):          # 1 champ  → retourne la VALEUR
        if not value.endswith("@ipssi.fr"):
            raise serializers.ValidationError("Email IPSSI requis.")
        return value

    def validate(self, attrs):                # N champs → retourne le DICT
        if attrs["a"] > attrs["b"]:
            raise serializers.ValidationError({"b": "b doit dépasser a."})
        return attrs

    # --- écriture ---------------------------------------------------------
    def create(self, validated_data):         # jamais save()
        enfants = validated_data.pop("enfants", [])
        obj = MonModele.objects.create(**validated_data)
        for e in enfants:
            Enfant.objects.create(parent=obj, **e)
        return obj

    # --- lecture ----------------------------------------------------------
    def get_calcule(self, obj):               # get_ + nom du champ
        return obj.quantite * obj.prix

    def to_representation(self, instance):    # toujours super() d'abord
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request is not None and not request.user.is_authenticated:
            data.pop("email")
        return data
```

### Les trois idées à emporter

1. **La grille 2×2** (champ/objet × manuel/déclaratif) range tout le bloc.
   Les deux colonnes s'exécutent, le déclaratif d'abord, sans jamais
   s'appeler l'une l'autre.

2. **`save()` ne construit rien** — il choisit entre `create()` et
   `update()` et délègue. Le même réflexe de séparation explique pourquoi
   le hachage (`create_user`) et la visibilité API (`write_only`) sont deux
   problèmes distincts.

3. **La réutilisabilité est le fil rouge.** Valider dans le serializer
   plutôt que dans la vue évite la duplication entre vues ; écrire un
   validator custom évite la duplication entre serializers. C'est le
   « pourquoi » de tout le Bloc 1, décliné à chaque niveau.

---

## Pour aller plus loin

- Serializers : <https://www.django-rest-framework.org/api-guide/serializers/>
- Champs : <https://www.django-rest-framework.org/api-guide/fields/>
- Validators : <https://www.django-rest-framework.org/api-guide/validators/>
- Relations : <https://www.django-rest-framework.org/api-guide/relations/>

**Dans ce dépôt** — `slides.html` (support d'oral), `tps/` (les 6 TP),
`tp_django/boutique/` (implémentation de référence, testée),
`bilan_bloc1_serializers_validations.md` (synthèse courte).
