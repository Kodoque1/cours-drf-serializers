"""TP2 — validator custom réutilisable (ressource MIROIR, à toi de jouer)."""
from rest_framework import serializers


class FrenchPhoneValidator:
    """Vérifie qu'un numéro commence par un préfixe donné (ex: "0" ou "+33").

    Même logique que `boutique.validators.CompanyEmailValidator` : état
    configurable à la construction, DRF appelle `validator(value)`.
    """

    def __init__(self, prefix):
        # TODO TP2 : stocke `prefix` comme attribut d'instance
        raise NotImplementedError("TP2 : à compléter")

    def __call__(self, value):
        # TODO TP2 : lève une serializers.ValidationError si value ne
        # commence pas par self.prefix
        raise NotImplementedError("TP2 : à compléter")
