"""
Ressource MIROIR — c'est ici que tu travailles (We do / You do).

Chaque TODO renvoie au TP correspondant (voir dossier `tps/`). Tant qu'un
TODO n'est pas résolu, la méthode lève `NotImplementedError` : c'est normal,
les tests de ce TP te le rappelleront jusqu'à ce que tu l'implémentes.
"""
from rest_framework import serializers

from .models import Creneau, Formateur, Inscription, Session


# ---------------------------------------------------------------------------
# TP1 (validate_<champ> / validate) + TP2 (UniqueValidator) + TP3 (create)
# ---------------------------------------------------------------------------
class FormateurSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    # TODO TP2 : ajoute validators=[UniqueValidator(queryset=Formateur.objects.all())]
    # ci-dessus, sur le champ `email`.

    class Meta:
        model = Formateur
        fields = ["id", "email", "telephone", "password", "password_confirm"]

    def validate_telephone(self, value):
        # TODO TP1 : un téléphone valide commence par "0" ou "+33".
        # Sinon, lève une serializers.ValidationError. Retourne `value` sinon.
        raise NotImplementedError("TP1 : à compléter")

    def validate(self, attrs):
        # TODO TP1 : vérifie que attrs["password"] == attrs["password_confirm"].
        # Sinon, lève une ValidationError ciblée sur "password_confirm".
        # Retourne `attrs` dans tous les cas.
        raise NotImplementedError("TP1 : à compléter")

    def create(self, validated_data):
        # TODO TP3 : ne JAMAIS stocker validated_data["password"] tel quel.
        # Utilise django.contrib.auth.hashers.make_password() pour remplir
        # Formateur.password_hash. N'oublie pas de retirer password_confirm
        # et password de validated_data avant Formateur.objects.create(...).
        raise NotImplementedError("TP3 : à compléter")


# ---------------------------------------------------------------------------
# TP2 (Meta.validators + UniqueTogetherValidator) + TP4 (source, SerializerMethodField)
# ---------------------------------------------------------------------------
class CreneauSerializer(serializers.ModelSerializer):
    # Exemple déjà fourni (source="relation.attribut") :
    salle_nom = serializers.CharField(source="salle.name", read_only=True)

    # TODO TP4 : ce champ doit exposer l'email du formateur du créneau.
    # Indice : c'est la même mécanique que `salle_nom` juste au-dessus.
    formateur_email = serializers.CharField(read_only=True)

    heures_restantes = serializers.SerializerMethodField()

    class Meta:
        model = Creneau
        fields = [
            "id",
            "salle",
            "salle_nom",
            "formateur",
            "formateur_email",
            "horaire",
            "heures_restantes",
        ]
        # TODO TP2 : ajoute ici
        # validators = [UniqueTogetherValidator(
        #     queryset=Creneau.objects.all(), fields=["salle", "horaire"],
        # )]

    def get_heures_restantes(self, obj):
        # TODO TP4 : nombre d'heures (entier) entre maintenant et obj.horaire.
        # Indice : django.utils.timezone.now(), puis (obj.horaire - now).
        raise NotImplementedError("TP4 : à compléter")


# ---------------------------------------------------------------------------
# TP4 (error_messages) + TP5 (context, to_representation)
# ---------------------------------------------------------------------------
class FormateurProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formateur
        fields = ["id", "email", "telephone"]
        # TODO TP4 : ajoute un extra_kwargs sur "telephone" avec un
        # error_messages personnalisé pour la clé "required".

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # TODO TP5 : masque data["telephone"] si la requête n'est PAS
        # authentifiée (self.context["request"].user.is_authenticated).
        # Un visiteur anonyme ne doit jamais voir le numéro de téléphone.
        return data


# ---------------------------------------------------------------------------
# TP6 (serializer imbriqué en écriture, many=True/ListSerializer, Hyperlinked)
# ---------------------------------------------------------------------------
class InscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscription
        fields = ["id", "participant_name", "email"]


class SessionListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        result = super().to_representation(data)
        # TODO TP6 : retourne plutôt
        # {"total_inscriptions": <somme des inscriptions de toutes les sessions>,
        #  "sessions": result}
        return result


class SessionSerializer(serializers.ModelSerializer):
    inscriptions = InscriptionSerializer(many=True)

    class Meta:
        model = Session
        fields = ["id", "title", "formateur", "date", "inscriptions"]
        list_serializer_class = SessionListSerializer

    def create(self, validated_data):
        # TODO TP6 : pop("inscriptions"), crée la Session, puis boucle pour
        # créer chaque Inscription liée (comme Order/OrderItem côté boutique).
        raise NotImplementedError("TP6 : à compléter")


class SessionHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    # Donné tel quel : le point du TP est de comprendre ce que ce serializer
    # change, pas de le retaper. Regarde le résultat, compare à SessionSerializer.
    formateur = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Session
        fields = ["url", "formateur", "title", "date"]
        extra_kwargs = {"url": {"view_name": "session-detail"}}
