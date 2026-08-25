"""
Ressource MIROIR (à toi de jouer). Modèles déjà écrits pour que tu te
concentres sur les serializers — c'est le but des TP.

Note volontaire : `Formateur.email` n'est PAS unique au niveau base de
données. C'est exprès (cf. TP2).
"""
from django.db import models


class Formateur(models.Model):
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    password_hash = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.email


class Salle(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Creneau(models.Model):
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, related_name="creneaux")
    formateur = models.ForeignKey(
        Formateur, on_delete=models.CASCADE, related_name="creneaux"
    )
    horaire = models.DateTimeField()


class Session(models.Model):
    title = models.CharField(max_length=150)
    formateur = models.ForeignKey(
        Formateur, on_delete=models.CASCADE, related_name="sessions"
    )
    date = models.DateField()


class Inscription(models.Model):
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="inscriptions"
    )
    participant_name = models.CharField(max_length=150)
    email = models.EmailField()
