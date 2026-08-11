"""Usuarios del servicio.

Este servicio tiene identidad **propia**: no depende de que el IAM de InnoTech
esté levantado. Pero el token que emite lleva **los mismos claims** que emitiría
el IAM, así que el resto del código no sabe —ni le importa— quién lo firmó.

El día que esto se integre al ecosistema: se apunta `JWT_SIGNING_KEY` a la
clave del IAM, se borra el login local, y ninguna vista cambia.

Los usuarios viven en el schema **público**, no en el de cada institución: una
persona puede pertenecer a más de una, igual que en el IAM.
"""
import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, **extra):
        if not username:
            raise ValueError('El usuario necesita un nombre de acceso.')
        email = self.normalize_email(extra.pop('email', '') or '')
        user = self.model(username=username, email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra)


class User(AbstractBaseUser):
    """Persona que accede al sistema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(blank=True, default='')
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')

    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'acc_user'
        ordering = ['username']

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.strip()

    def __str__(self):
        return self.username


class Membership(models.Model):
    """Pertenencia de un usuario a una institución.

    Sin membresías el usuario existe pero no ve datos de ninguna institución:
    los datos viven en el schema de cada tenant.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='memberships',
    )
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, related_name='memberships',
    )
    # Texto y no catálogo: los roles del proceso todavía no están definidos.
    # Cuando lo estén, esto pasa a ser FK a un catálogo de roles.
    role = models.CharField(max_length=80, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Membresía'
        verbose_name_plural = 'Membresías'
        db_table = 'acc_membership'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'tenant'], name='acc_membership_unique_user_tenant',
            ),
        ]

    def __str__(self):
        return f'{self.user.username} @ {self.tenant.schema_name}'
