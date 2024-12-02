from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import InviteCode

User = get_user_model()


@receiver(post_save, sender=User)
def create_invite_code(sender, instance, created, **kwargs):
    """Создание баланса."""
    if created:
        InviteCode.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_invite_code(sender, instance, **kwargs):
    """Сохранение баланса."""
    instance.invite_code.save()
