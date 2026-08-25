"""
Ressource PRINCIPALE (démo prof) — solution complète, TP1 à TP6.

Ce fichier est la référence que le prof montre/tape en live (I do).
Les étudiants reproduisent la même logique dans `formation/serializers.py`
sur leur propre ressource miroir.
"""
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import Booking, Order, OrderItem


# ---------------------------------------------------------------------------
# TP1 (validate_<champ> / validate) + TP2 (UniqueValidator) + TP3 (create/create_user)
# ---------------------------------------------------------------------------
class SignupSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ["id", "email", "password", "password_confirm"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "error_messages": {"min_length": "8 caractères minimum."},
            },
        }

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

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        email = validated_data["email"]
        return User.objects.create_user(username=email, email=email, password=validated_data["password"])


# ---------------------------------------------------------------------------
# TP2 (Meta.validators + UniqueTogetherValidator) + TP4 (source, SerializerMethodField)
# ---------------------------------------------------------------------------
class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    jours_restants = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ["id", "room", "room_name", "user", "date", "jours_restants"]
        validators = [
            UniqueTogetherValidator(
                queryset=Booking.objects.all(), fields=["room", "date"]
            )
        ]

    def get_jours_restants(self, obj):
        return (obj.date - timezone.now().date()).days


# ---------------------------------------------------------------------------
# TP4 (error_messages, partial=True côté vue) + TP5 (context, to_representation)
# ---------------------------------------------------------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]
        extra_kwargs = {
            "email": {"error_messages": {"required": "L'email est obligatoire."}},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request is not None and request.user != instance:
            data.pop("email")
        return data


# ---------------------------------------------------------------------------
# TP6 (serializer imbriqué en écriture, many=True/ListSerializer, Hyperlinked)
# ---------------------------------------------------------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "price"]


class OrderListSerializer(serializers.ListSerializer):
    # Piège DRF : `ListSerializer.data` enveloppe TOUJOURS le retour de
    # `to_representation()` dans un `ReturnList(...)`, même si on renvoie un
    # dict — `ReturnList({"total": ..., "orders": ...})` redevient la liste
    # des CLÉS du dict. Pour changer la forme finale, il faut donc surcharger
    # `data` directement, pas `to_representation`.
    @property
    def data(self):
        orders = super().data
        total = sum(
            float(item["price"]) * item["quantity"]
            for order in orders
            for item in order["items"]
        )
        return {"total": total, "orders": orders}


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "items"]
        list_serializer_class = OrderListSerializer

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order


class OrderHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    # `user` reste en PrimaryKeyRelatedField pour ne pas exiger une vue
    # "user-detail" : le TP porte sur `url`, pas sur toutes les relations.
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ["url", "user", "created_at"]
        extra_kwargs = {"url": {"view_name": "order-detail"}}
