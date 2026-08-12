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


class Role(models.Model):
    """Un rol del proceso, con los permisos que trae.

    Vive en el schema **público** y no en el de cada institución, igual que en
    el IAM de InnoTech: los roles son del sistema y las instituciones los
    comparten. Si algún día una necesita los suyos, se mueve — pero empezar
    compartiéndolos es lo consistente con el ecosistema.

    A diferencia de los permisos, que se declaran en el código, los roles **sí**
    se gestionan desde pantalla: son decisiones de la organización y cambian
    sin desplegar.
    """

    class Scope(models.TextChoices):
        INSTITUTIONAL = 'INSTITUTIONAL', 'Cargo en la institución'
        PROJECT = 'PROJECT', 'Papel dentro de un proyecto'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(
        max_length=60, unique=True, db_index=True,
        help_text='Identificador estable. En MAYÚSCULAS, sin espacios.',
    )
    name = models.CharField(max_length=120, help_text='Como se lee en pantalla.')
    description = models.CharField(max_length=255, blank=True, default='')

    # De los roles del proceso, unos son cargos —el Director de Emprendimiento
    # lo es siempre— y otros dependen del proyecto: el Emprendedor lo es del
    # suyo, no de todos. Los permisos de módulo solo tienen sentido en los
    # primeros; los segundos esperan la tabla que los ate a un proyecto.
    scope = models.CharField(
        max_length=20, choices=Scope.choices, default=Scope.INSTITUTIONAL,
        db_index=True,
    )

    # Los de fábrica no se borran: sostienen la siembra y el acceso inicial.
    is_system = models.BooleanField(
        default=False,
        help_text='Viene con el sistema. No se puede eliminar.',
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        db_table = 'acc_role'
        ordering = ['scope', 'name']

    @property
    def permission_codes(self) -> set:
        return set(self.permissions.values_list('code', flat=True))

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Un permiso concedido a un rol.

    Se guarda el código y no una FK a un catálogo en base: los permisos se
    declaran en `permissions.py` y esa es su única fuente. Guardar filas de
    permisos en base solo agregaría un lugar más que puede quedar desfasado.

    Un código que ya no exista en el catálogo queda huérfano y se ignora al
    resolver, que es justo lo que debe pasar si se retiró una funcionalidad.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        'accounts.Role', on_delete=models.CASCADE, related_name='permissions',
    )
    code = models.CharField(max_length=60, db_index=True)

    class Meta:
        verbose_name = 'Permiso del rol'
        verbose_name_plural = 'Permisos del rol'
        db_table = 'acc_role_permission'
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'code'], name='acc_role_permission_unique',
            ),
        ]

    def __str__(self):
        return f'{self.role.code} · {self.code}'


class Membership(models.Model):
    """Pertenencia de un usuario a una institución.

    Sin membresías el usuario existe pero no ve datos de ninguna institución:
    los datos viven en el schema de cada tenant.

    El rol va acá y no en el usuario porque **una persona puede tener un rol
    distinto en cada institución**: coordinadora en una y solo lectora en otra.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='memberships',
    )
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, related_name='memberships',
    )
    role = models.ForeignKey(
        'accounts.Role',
        on_delete=models.PROTECT,
        related_name='memberships',
        null=True, blank=True,
        help_text='Sin rol, la persona entra pero no puede hacer nada.',
    )
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
