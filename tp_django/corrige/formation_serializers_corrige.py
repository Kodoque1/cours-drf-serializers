from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from formation.models import Creneau, Formateur, Inscription, Session


class FormateurSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Formateur.objects.all())]
    )

    class Meta:
        model = Formateur
        fields = ["id", "email", "telephone", "password", "password_confirm"]

    def validate_telephone(self, value):
        if not (value.startswith("0") or value.startswith("+33")):
            raise serializers.ValidationError(
                "Numéro français requis (commence par 0 ou +33)."
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        return Formateur.objects.create(
            password_hash=make_password(password), **validated_data
        )


class CreneauSerializer(serializers.ModelSerializer):
    salle_nom = serializers.CharField(source="salle.name", read_only=True)
    formateur_email = serializers.CharField(source="formateur.email", read_only=True)
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
        validators = [
            UniqueTogetherValidator(
                queryset=Creneau.objects.all(), fields=["salle", "horaire"]
            )
        ]

    def get_heures_restantes(self, obj):
        delta = obj.horaire - timezone.now()
        return int(delta.total_seconds() // 3600)


class FormateurProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formateur
        fields = ["id", "email", "telephone"]
        extra_kwargs = {
            "telephone": {
                "error_messages": {"required": "Le téléphone est obligatoire."}
            },
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request is not None and not request.user.is_authenticated:
            data.pop("telephone")
        return data


class InscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscription
        fields = ["id", "participant_name", "email"]


class SessionListSerializer(serializers.ListSerializer):
    # `ListSerializer.data` enveloppe toujours dans un ReturnList, même si
    # to_representation renvoie un dict : il faut surcharger `data` directement.
    @property
    def data(self):
        sessions = super().data
        total = sum(len(session["inscriptions"]) for session in sessions)
        return {"total_inscriptions": total, "sessions": sessions}


class SessionSerializer(serializers.ModelSerializer):
    inscriptions = InscriptionSerializer(many=True)

    class Meta:
        model = Session
        fields = ["id", "title", "formateur", "date", "inscriptions"]
        list_serializer_class = SessionListSerializer

    def create(self, validated_data):
        inscriptions_data = validated_data.pop("inscriptions")
        session = Session.objects.create(**validated_data)
        for data in inscriptions_data:
            Inscription.objects.create(session=session, **data)
        return session


class SessionHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    formateur = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Session
        fields = ["url", "formateur", "title", "date"]
        extra_kwargs = {"url": {"view_name": "session-detail"}}
