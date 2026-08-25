"""
Tests de la ressource PRINCIPALE (solution prof). Sert de filet de sécurité :
si ces tests cassent, la démo en cours risque de casser aussi.
Lance : python manage.py test boutique
"""
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from types import SimpleNamespace

from .models import Booking, Order, Room
from .serializers import (
    BookingSerializer,
    OrderHyperlinkedSerializer,
    OrderSerializer,
    SignupSerializer,
    UserProfileSerializer,
)
from .validators import CompanyEmailValidator


class SignupSerializerTests(TestCase):
    def test_domaine_email_invalide_est_rejete(self):
        serializer = SignupSerializer(
            data={
                "email": "test@gmail.com",
                "password": "motdepasse123",
                "password_confirm": "motdepasse123",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_mots_de_passe_differents_sont_rejetes(self):
        serializer = SignupSerializer(
            data={
                "email": "test@ipssi.fr",
                "password": "motdepasse123",
                "password_confirm": "autrechose",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_email_deja_utilise_est_rejete(self):
        User.objects.create_user(username="a@ipssi.fr", email="a@ipssi.fr", password="x")
        serializer = SignupSerializer(
            data={
                "email": "a@ipssi.fr",
                "password": "motdepasse123",
                "password_confirm": "motdepasse123",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_inscription_valide_hache_le_mot_de_passe(self):
        serializer = SignupSerializer(
            data={
                "email": "ok@ipssi.fr",
                "password": "motdepasse123",
                "password_confirm": "motdepasse123",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertTrue(check_password("motdepasse123", user.password))


class BookingSerializerTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="Salle 1")
        self.user = User.objects.create_user(username="u@ipssi.fr", password="x")
        Booking.objects.create(room=self.room, user=self.user, date="2026-09-01")

    def test_meme_salle_meme_date_est_rejete(self):
        serializer = BookingSerializer(
            data={"room": self.room.id, "user": self.user.id, "date": "2026-09-01"}
        )
        self.assertFalse(serializer.is_valid())

    def test_room_name_et_jours_restants_sont_exposes(self):
        booking = Booking.objects.first()
        data = BookingSerializer(booking).data
        self.assertEqual(data["room_name"], "Salle 1")
        self.assertIn("jours_restants", data)


class UserProfileSerializerTests(TestCase):
    def test_email_masque_pour_un_autre_utilisateur(self):
        owner = User.objects.create_user(username="owner@ipssi.fr", password="x")
        other = User.objects.create_user(username="other@ipssi.fr", password="x")
        request = SimpleNamespace(user=other)
        data = UserProfileSerializer(owner, context={"request": request}).data
        self.assertNotIn("email", data)

    def test_email_visible_pour_le_proprietaire(self):
        owner = User.objects.create_user(username="owner2@ipssi.fr", password="x")
        request = SimpleNamespace(user=owner)
        data = UserProfileSerializer(owner, context={"request": request}).data
        self.assertIn("email", data)


class OrderSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="client@ipssi.fr", password="x")

    def test_creation_imbriquee_des_items(self):
        serializer = OrderSerializer(
            data={
                "user": self.user.id,
                "items": [
                    {"product_name": "Clavier", "quantity": 1, "price": "49.99"},
                    {"product_name": "Souris", "quantity": 2, "price": "19.99"},
                ],
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        self.assertEqual(order.items.count(), 2)

    def test_total_sur_toute_la_liste(self):
        order = Order.objects.create(user=self.user)
        order.items.create(product_name="Clavier", quantity=1, price="10.00")
        data = OrderSerializer(Order.objects.all(), many=True).data
        self.assertEqual(data["total"], 10.0)

    def test_hyperlinked_expose_une_url(self):
        order = Order.objects.create(user=self.user)
        request = RequestFactory().get("/")
        data = OrderHyperlinkedSerializer(order, context={"request": request}).data
        self.assertIn("url", data)
        self.assertNotIn("id", data)


class CompanyEmailValidatorTests(TestCase):
    def test_domaine_correct_ne_leve_rien(self):
        CompanyEmailValidator(domain="@ipssi.fr")("a@ipssi.fr")

    def test_domaine_incorrect_leve_une_erreur(self):
        from rest_framework import serializers

        with self.assertRaises(serializers.ValidationError):
            CompanyEmailValidator(domain="@ipssi.fr")("a@gmail.com")
