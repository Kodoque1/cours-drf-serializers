"""TP2 — validator custom réutilisable (démo prof)."""
from rest_framework import serializers


class CompanyEmailValidator:
    """Vérifie qu'un email se termine par un domaine donné.

    État configurable à la construction (attribut d'instance) : DRF appelle
    le validator avec un seul argument (`validator(value)`), donc tout
    paramètre de configuration doit être fixé avant, dans __init__.
    """

    def __init__(self, domain):
        self.domain = domain

    def __call__(self, value):
        if not value.endswith(self.domain):
            raise serializers.ValidationError(f"Domaine {self.domain} requis.")
