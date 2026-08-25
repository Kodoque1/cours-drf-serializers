"""
TP2 — Mécanismes déclaratifs (UniqueValidator, UniqueTogetherValidator, validator custom).
Lance : python manage.py test formation.tests.test_tp2
"""
from datetime import datetime, timezone as dt_timezone

from django.test import TestCase

from formation.models import Creneau, Formateur, Salle
from formation.serializers import CreneauSerializer, FormateurSignupSerializer
from formation.validators import FrenchPhoneValidator


class UniqueEmailValidatorTests(TestCase):
    def setUp(self):
        Formateur.objects.create(
            email="deja-inscrit@ipssi-corp.fr", telephone="0600000000"
        )

    def test_email_deja_utilise_est_rejete(self):
        serializer = FormateurSignupSerializer(
            data={
                "email": "deja-inscrit@ipssi-corp.fr",
                "telephone": "0612345678",
                "password": "motdepasse123",
                "password_confirm": "motdepasse123",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class UniqueTogetherValidatorTests(TestCase):
    def setUp(self):
        self.salle = Salle.objects.create(name="Salle A")
        self.formateur = Formateur.objects.create(
            email="f@ipssi-corp.fr", telephone="0600000000"
        )
        self.horaire = datetime(2026, 9, 1, 9, 0, tzinfo=dt_timezone.utc)
        Creneau.objects.create(
            salle=self.salle, formateur=self.formateur, horaire=self.horaire
        )

    def test_meme_salle_meme_horaire_est_rejete(self):
        serializer = CreneauSerializer(
            data={
                "salle": self.salle.id,
                "formateur": self.formateur.id,
                "horaire": self.horaire.isoformat(),
            }
        )
        self.assertFalse(serializer.is_valid())

    def test_meme_salle_autre_horaire_est_accepte(self):
        serializer = CreneauSerializer(
            data={
                "salle": self.salle.id,
                "formateur": self.formateur.id,
                "horaire": datetime(2026, 9, 1, 14, 0, tzinfo=dt_timezone.utc).isoformat(),
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)


class FrenchPhoneValidatorTests(TestCase):
    def test_prefixe_correct_ne_leve_rien(self):
        validator = FrenchPhoneValidator(prefix="0")
        validator("0612345678")  # ne doit pas lever d'exception

    def test_prefixe_incorrect_leve_une_erreur(self):
        from rest_framework import serializers

        validator = FrenchPhoneValidator(prefix="0")
        with self.assertRaises(serializers.ValidationError):
            validator("+33612345678")
