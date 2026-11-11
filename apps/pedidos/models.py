import uuid

from django.db import models
from django.conf import settings


def formato_clp(monto):
    return f"${monto:,.0f}".replace(",", ".")


class ComprobanteInscripcion(models.Model):
    codigo = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comprobantes_inscripcion",
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
    subtotal_neto = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
    )
    recargo_servicio = models.DecimalField(max_digits=12, decimal_places=0)
    iva = models.DecimalField(max_digits=12, decimal_places=0)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    iva_incluido = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha_emision"]
        verbose_name = "Comprobante de inscripción"
        verbose_name_plural = "Comprobantes de inscripción"

    def __str__(self):
        return f"Comprobante {self.codigo} - {self.usuario}"

    @property
    def subtotal_formateado(self):
        return formato_clp(self.subtotal)

    @property
    def subtotal_neto_formateado(self):
        return formato_clp(self.subtotal_neto)

    @property
    def recargo_servicio_formateado(self):
        return formato_clp(self.recargo_servicio)

    @property
    def iva_formateado(self):
        return formato_clp(self.iva)

    @property
    def total_formateado(self):
        return formato_clp(self.total)


class DetalleComprobante(models.Model):
    comprobante = models.ForeignKey(
        ComprobanteInscripcion,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    torneo = models.ForeignKey(
        "torneos.TorneoEvento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detalles_comprobantes",
    )
    nombre_torneo = models.CharField(max_length=200)
    categoria_torneo = models.CharField(max_length=100)
    precio_inscripcion = models.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        ordering = ["id"]
        verbose_name = "Detalle de comprobante"
        verbose_name_plural = "Detalles de comprobantes"

    @property
    def precio_formateado(self):
        return formato_clp(self.precio_inscripcion)
