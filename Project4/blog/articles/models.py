from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class CustomDateTimeField(models.DateTimeField):
    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        if val:
            val.replace(microsecond=0)
            return val.strftime("%d-%m-%y, %H:M")
        return ''

class Article(models.Model):
    class Meta:
        verbose_name = "Artykuł"
        verbose_name_plural = "Artykuły"

    title = models.CharField(max_length=100, verbose_name="Tytuł")
    slug = models.SlugField(verbose_name="Tytuł w pasku adresowym")
    content = models.TextField(verbose_name="Treść")
    timestamp = CustomDateTimeField(auto_now_add=True, verbose_name="Czas utworzenia")
    author = models.ForeignKey(User, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def snippet(self):
        return self.content[:100] + "..."

class Comment(models.Model):
    class Meta:
        verbose_name = "Komentarz"
        verbose_name_plural = "Komentarze"

    timestamp = CustomDateTimeField(auto_now_add=True, verbose_name="Czas utworzenia")
    content = models.TextField(verbose_name="Treść")
    author = models.ForeignKey(User, default=None, on_delete=models.CASCADE, verbose_name="Autor")
    article = models.ForeignKey(Article, default=None, on_delete=models.CASCADE, verbose_name="Artykuł")

class Reaction(models.Model):
    class Meta:
        verbose_name = "Reakcja"
        verbose_name_plural = "Reakcje"

    class ReactionType(models.TextChoices):
        HAPPY = 'HP', "Szczęśliwy"
        SAD = 'SD', 'Smutny'
        NEUTRAL = 'NT', 'Neutralny'


    author = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, default=None, on_delete=models.CASCADE)
    reaction_type = models.CharField(
        max_length=2,
        choices = ReactionType.choices,
        default = ReactionType.HAPPY,
    )
