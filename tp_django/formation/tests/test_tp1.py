"""
TP1 — Validation de champ & d'objet.
Lance : python manage.py test formation.tests.test_tp1
"""
from django.test import TestCase

from formation.serializers import FormateurSignupSerializer


def payload(**overrides):
    data = {
        "email": "prof@ipssi-corp.fr",
        "telephone": "0612345678",
        "password": "motdepasse123",
        "password_confirm": "motdepasse123",
    }
    data.update(overrides)
    return data


class ValidateTelephoneTests(TestCase):
    def test_telephone_valide_commence_par_0(self):
        serializer = FormateurSignupSerializer(data=payload(telephone="0612345678"))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_telephone_valide_commence_par_plus33(self):
        serializer = FormateurSignupSerializer(data=payload(telephone="+33612345678"))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_telephone_invalide_est_rejete(self):
        serializer = FormateurSignupSerializer(data=payload(telephone="612345678"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("telephone", serializer.errors)


class ValidateObjectLevelTests(TestCase):
    def test_mots_de_passe_differents_sont_rejetes(self):
        serializer = FormateurSignupSerializer(
            data=payload(password="abcdefgh", password_confirm="autrechose")
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_mots_de_passe_identiques_sont_acceptes(self):
        serializer = FormateurSignupSerializer(data=payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)
