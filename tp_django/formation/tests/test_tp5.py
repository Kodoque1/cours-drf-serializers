"""
TP5 — Contexte & représentation (context, to_representation).
Lance : python manage.py test formation.tests.test_tp5
"""
from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase

from formation.models import Formateur
from formation.serializers import FormateurProfileSerializer


def fake_request(user):
    """Un faux `request` minimal : le serializer n'a besoin que de `.user`."""
    return SimpleNamespace(user=user)


class ToRepresentationContextTests(TestCase):
    def setUp(self):
        self.formateur = Formateur.objects.create(
            email="visible@ipssi-corp.fr", telephone="0612345678"
        )

    def test_visiteur_anonyme_ne_voit_pas_le_telephone(self):
        serializer = FormateurProfileSerializer(
            self.formateur, context={"request": fake_request(AnonymousUser())}
        )
        self.assertNotIn("telephone", serializer.data)

    def test_utilisateur_authentifie_voit_le_telephone(self):
        user = User.objects.create_user(username="prof", password="x")
        serializer = FormateurProfileSerializer(
            self.formateur, context={"request": fake_request(user)}
        )
        self.assertIn("telephone", serializer.data)
        self.assertEqual(serializer.data["telephone"], "0612345678")

    def test_email_reste_toujours_visible(self):
        serializer = FormateurProfileSerializer(
            self.formateur, context={"request": fake_request(AnonymousUser())}
        )
        self.assertEqual(serializer.data["email"], "visible@ipssi-corp.fr")
