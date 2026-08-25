# Bilan — Bloc 1 : Serializers DRF & Validations
Session de drill socratique — 2026-08-25

## 1. Lexique Technique Correct

**Vocabulaire général**
- **Méthode** (définie dans une classe, prend `self`) ≠ **fonction** (indépendante).
- **Désérialisation** = JSON entrant → Python (`validated_data`). **Sérialisation** = instance modèle → JSON sortant. Ne jamais les inverser.
- `raise` (lever une exception, interrompt le flux) ≠ `return` (renvoyer une valeur normalement).
- **Attribut d'instance** (propre à chaque objet, configurable via `__init__`) ≠ **attribut de classe** (partagé/statique).

**Cycle de validation**
- `validate_<champ>(self, value)` — field-level, appelée automatiquement par `is_valid()` via convention de nommage. Doit **retourner** la valeur (jamais un booléen).
- `validate(self, attrs)` — object-level, pour les checks croisés entre champs. Reçoit et retourne le dict complet.
- `serializers.ValidationError("...")` → `non_field_errors`. `serializers.ValidationError({"champ": "..."})` → erreur ciblée sur ce champ.
- HTTP **400** (données invalides) ≠ 401 (authentification) ≠ 403 (autorisation) ≠ 500 (bug serveur).

**Mécanisme `validators` (indépendant des méthodes ci-dessus)**
- `validators=[...]` sur un field (ex: `UniqueValidator`) — orchestré par `is_valid()`, mais **jamais imbriqué dans** `validate_<champ>`.
- `Meta.validators = [UniqueTogetherValidator(queryset=..., fields=[...])]` — équivalent objet-level, indépendant de `validate()`.

**`ModelSerializer` et ses mécanismes**
- Introspection automatique du modèle (type, `max_length`, `unique=True`...) pour générer les fields.
- `extra_kwargs = {"champ": {...}}` — ajuster des options sans redéclarer le field.
- `save()` = dispatcher générique DRF (ne jamais l'override) → délègue à `create()`/`update()` (à override, toi).
- `UserManager.create_user()` (hash automatique du mdp) ≠ `Model.objects.create()` (stockage brut).
- Serializers imbriqués en écriture : **jamais automatique** → override `create()`, `pop()` la clé imbriquée, boucle manuelle avec la FK.
- `many=True` → wrapping dans un `ListSerializer` (`child=`ton serializer) ; `Meta.list_serializer_class` pour du comportement dépendant de toute la liste.
- `HyperlinkedModelSerializer` → relations en **URL** (hyperlien), pas en PK ni en objet imbriqué.

**Champs spéciaux**
- `SerializerMethodField` + `get_<champ>(self, obj)` — `obj` = instance complète, accès libre à ses attributs.
- `read_only=True` / `write_only=True` — asymétrie lecture/écriture, **indépendant** du hashing du mdp.
- `source='attribut'` ou `source='relation.attribut'` — remapper le nom JSON vers l'attribut réel.
- `error_messages={'required': '...'}` — messages custom par clé standard.
- `partial=True` — désactive **uniquement** le check d'absence (`required`), jamais la validation du contenu si le champ est présent.
- `to_representation(self, instance)` — toujours `data = super().to_representation(instance)` d'abord, puis modifier `data`.
- `context={'request': request}` / `self.context['request'].user` — infos ambiantes, séparées des données métier.

## 2. Top 3 Formulations Clés validées pendant la session

1. **La grille 2×2 field/objet × méthode manuelle/mécanisme déclaratif** :

   |        | Méthode manuelle      | Mécanisme déclaratif indépendant   |
   |--------|------------------------|-------------------------------------|
   | Field  | `validate_<champ>()`   | `validators=[...]`                  |
   | Objet  | `validate()`           | `Meta.validators = [...]`           |

   Les deux colonnes s'exécutent **toutes les deux**, orchestrées par `is_valid()`, sans jamais s'appeler l'une l'autre.

2. **`save()` ne construit rien lui-même** — il décide juste "création ou update ?" et délègue à `create()`/`update()`. C'est pour ça qu'on override toujours `create()`, jamais `save()` — le même principe explique pourquoi `create_user()` (hash mdp) est une préoccupation totalement séparée de `write_only` (visibilité API).

3. **Réutilisabilité comme fil rouge** : valider dans le serializer plutôt que dans la vue évite la duplication entre vues ; écrire un validator custom réutilisable (fonction ou classe) évite la duplication entre serializers. Le "pourquoi" du Bloc 1 tient en cette seule idée, déclinée à chaque niveau.

## 3. Feu Vert Méta-Prompt

✅ **Les briques fondamentales sont acquises.** Le cycle complet (field-level → object-level → validators déclaratifs → cycle de vie save/create → sécurité → réutilisabilité → context → nested → list → hyperlinked) a été couvert et corrigé en profondeur.

⚠️ **Point de vigilance pour le drill CTO** : le seul pattern d'erreur vraiment récurrent sur toute la session n'est pas un trou de connaissance, c'est un **réflexe** — inventer un nom plausible quand on ne sait pas (`ErrorHandler`, `PasswordField`, `hidden=true`, "unicité des objets sérialisés en entrée"). Le bon réflexe validé plusieurs fois dans cette session : dire "je ne sais pas" plutôt que fabriquer un terme qui sonne juste.

**→ Lancer le drill multi-agents.**
