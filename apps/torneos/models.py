from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class CategoriaJuego(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Categoría de Juego")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descripcion = models.TextField(verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="¿Activo?")

    class Meta:
        verbose_name_plural = "Categorías de Juegos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class TorneoEvento(models.Model):
    ESTADOS = (
        ('abierto', 'Abierto para Inscripción'),
        ('en_curso', 'En Curso'),
        ('finalizado', 'Finalizado'),
    )

    nombre = models.CharField(max_length=200, verbose_name="Nombre del Torneo")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categoria = models.ForeignKey(CategoriaJuego, on_delete=models.PROTECT, related_name="torneos", verbose_name="Categoría")
    organizador = models.CharField(max_length=150, verbose_name="Organizador / Juego")
    reglas = models.TextField(verbose_name="Reglas y Formato")
    costo_inscripcion = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="Costo de Inscripción (CLP)")
    cupos_maximos = models.PositiveIntegerField(verbose_name="Cupos Máximos")
    banner = models.ImageField(upload_to="torneos/", blank=True, null=True, verbose_name="Banner Promocional")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierto', verbose_name="Estado Operativo")
    activo = models.BooleanField(default=True, verbose_name="Baja Lógica (Activo)")

    class Meta:
        verbose_name_plural = "Torneos y Eventos"
        ordering = ['-id']

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"

    @property
    def cupos_disponibles(self):
        return max(0, self.cupos_maximos - self.inscripciones.count())

    @property
    def precio_formateado(self):
        return f"${self.costo_inscripcion:,.0f}".replace(",", ".")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            contador = 1
            while TorneoEvento.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Inscripcion(models.Model):
    torneo = models.ForeignKey(
        TorneoEvento,
        on_delete=models.CASCADE,
        related_name="inscripciones",
        verbose_name="Torneo",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inscripciones_torneos",
        verbose_name="Usuario",
    )
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha_inscripcion"]
        constraints = [
            models.UniqueConstraint(
                fields=["torneo", "usuario"],
                name="inscripcion_unica_por_usuario_y_torneo",
            ),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.torneo}"