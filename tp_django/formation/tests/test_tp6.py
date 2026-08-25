"""
TP6 — Relations (serializer imbriqué, many=True/ListSerializer, Hyperlinked).
Lance : python manage.py test formation.tests.test_tp6
"""
from django.test import RequestFactory, TestCase

from formation.models import Formateur, Session
from formation.serializers import (
    SessionHyperlinkedSerializer,
    SessionSerializer,
)


class NestedWriteTests(TestCase):
    def setUp(self):
        self.formateur = Formateur.objects.create(
            email="nested@ipssi-corp.fr", telephone="0600000000"
        )

    def test_creer_une_session_avec_ses_inscriptions(self):
        serializer = SessionSerializer(
            data={
                "title": "DRF Avancé",
                "formateur": self.formateur.id,
                "date": "2026-09-15",
                "inscriptions": [
                    {"participant_name": "Alice", "email": "alice@ipssi.fr"},
                    {"participant_name": "Bob", "email": "bob@ipssi.fr"},
                ],
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        session = serializer.save()

        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(session.inscriptions.count(), 2)


class ListSerializerTests(TestCase):
    def setUp(self):
        self.formateur = Formateur.objects.create(
            email="liste@ipssi-corp.fr", telephone="0600000000"
        )
        for i in range(2):
            s = SessionSerializer(
                data={
                    "title": f"Session {i}",
                    "formateur": self.formateur.id,
                    "date": "2026-09-15",
                    "inscriptions": [{"participant_name": "X", "email": "x@ipssi.fr"}],
                }
            )
            s.is_valid()
            s.save()

    def test_total_inscriptions_sur_toute_la_liste(self):
        data = SessionSerializer(Session.objects.all(), many=True).data
        self.assertIn("total_inscriptions", data)
        self.assertEqual(data["total_inscriptions"], 2)
        self.assertEqual(len(data["sessions"]), 2)


class HyperlinkedTests(TestCase):
    def test_url_remplace_id(self):
        formateur = Formateur.objects.create(
            email="lien@ipssi-corp.fr", telephone="0600000000"
        )
        session = Session.objects.create(
            title="Hyperlink Demo", formateur=formateur, date="2026-09-15"
        )
        request = RequestFactory().get("/")
        data = SessionHyperlinkedSerializer(session, context={"request": request}).data

        self.assertIn("url", data)
        self.assertNotIn("id", data)
        self.assertTrue(data["url"].endswith(f"/sessions/{session.id}/"))
