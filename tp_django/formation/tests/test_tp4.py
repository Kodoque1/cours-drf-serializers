"""
TP4 — Champs avancés (source, error_messages, SerializerMethodField).
Lance : python manage.py test formation.tests.test_tp4
"""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from formation.models import Creneau, Formateur, Salle
from formation.serializers import CreneauSerializer, FormateurProfileSerializer


class SourceFieldTests(TestCase):
    def setUp(self):
        self.salle = Salle.objects.create(name="Salle B")
        self.formateur = Formateur.objects.create(
            email="source@ipssi-corp.fr", telephone="0600000000"
        )
        self.creneau = Creneau.objects.create(
            salle=self.salle,
            formateur=self.formateur,
            horaire=timezone.now() + timedelta(hours=3),
        )

    def test_formateur_email_utilise_bien_source(self):
        data = CreneauSerializer(self.creneau).data
        self.assertEqual(data["formateur_email"], "source@ipssi-corp.fr")


class SerializerMethodFieldTests(TestCase):
    def test_heures_restantes_est_calcule(self):
        salle = Salle.objects.create(name="Salle C")
        formateur = Formateur.objects.create(
            email="methode@ipssi-corp.fr", telephone="0600000000"
        )
        creneau = Creneau.objects.create(
            salle=salle, formateur=formateur, horaire=timezone.now() + timedelta(hours=5)
        )
        data = CreneauSerializer(creneau).data
        # Tolérance de 1h pour le temps d'exécution du test.
        self.assertIn(data["heures_restantes"], (3, 4))


class ErrorMessagesTests(TestCase):
    def test_message_personnalise_sur_telephone_manquant(self):
        serializer = FormateurProfileSerializer(data={"email": "sanstel@ipssi-corp.fr"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("telephone", serializer.errors)
        self.assertEqual(
            str(serializer.errors["telephone"][0]), "Le téléphone est obligatoire."
        )
