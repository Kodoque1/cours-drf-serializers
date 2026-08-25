"""
TP3 — Cycle de vie de l'objet (create() vs save(), hachage du mot de passe).
Lance : python manage.py test formation.tests.test_tp3
"""
from django.contrib.auth.hashers import check_password
from django.test import TestCase

from formation.models import Formateur
from formation.serializers import FormateurSignupSerializer


class CreatePasswordHashingTests(TestCase):
    def test_le_mot_de_passe_est_hache(self):
        serializer = FormateurSignupSerializer(
            data={
                "email": "hash@ipssi-corp.fr",
                "telephone": "0612345678",
                "password": "motdepasse123",
                "password_confirm": "motdepasse123",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        formateur = serializer.save()

        self.assertNotEqual(formateur.password_hash, "motdepasse123")
        self.assertTrue(check_password("motdepasse123", formateur.password_hash))

    def test_save_ne_plante_pas_et_persiste_un_seul_formateur(self):
        # Si password_confirm n'est pas retiré de validated_data avant
        # Formateur.objects.create(**validated_data), cet appel lève un
        # TypeError ("unexpected keyword argument") : ce test échoue alors
        # avec une erreur, pas juste une assertion.
        serializer = FormateurSignupSerializer(
            data={
                "email": "clean@ipssi-corp.fr",
                "telephone": "0612345678",
                "password": "motdepasse123",
                "password_confirm": "motdepasse123",
            }
        )
        serializer.is_valid()
        serializer.save()
        self.assertEqual(Formateur.objects.count(), 1)
