from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from .models import Customer, BulkMail
from django.core.mail import send_mass_mail
from django.conf import settings


@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    print('SHOW', instance, created)
    if created:
        Customer.objects.create(user=instance)
        
@receiver(post_save, sender=BulkMail)
def bulk_mail_send(sender, instance, created, *args, **kwargs):
    emails = list(instance.customers.exclude(user__email='').values_list('user__email', flat=True))
    subject = instance.subject
    content = instance.content
    host_user = settings.EMAIL_HOST_USER
    send_mass_mail(
        ((subject, content, host_user, [email]) for email in emails),
        fail_silently=False
    )