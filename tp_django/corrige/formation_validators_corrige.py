from rest_framework import serializers


class FrenchPhoneValidator:
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, value):
        if not value.startswith(self.prefix):
            raise serializers.ValidationError(f"Le numéro doit commencer par {self.prefix}.")
