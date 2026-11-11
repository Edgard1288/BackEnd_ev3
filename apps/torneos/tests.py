from django.test import TestCase
from django.contrib.auth.models import User

from apps.pedidos.models import ComprobanteInscripcion
from .models import CategoriaJuego, Inscripcion, TorneoEvento


class TorneoPageTests(TestCase):
    def setUp(self):
        self.categoria = CategoriaJuego.objects.create(
            nombre='Fighting Games',
            descripcion='Torneos de juegos de pelea.',
        )
        self.torneo = TorneoEvento.objects.create(
            nombre='Copa de prueba',
            categoria=self.categoria,
            organizador='Organizador',
            reglas='Formato eliminatorio.',
            costo_inscripcion=0,
            cupos_maximos=16,
        )
        self.usuario = User.objects.create_user(
            username='jugador',
            password='Fuerte-2026-clave!',
        )

    def test_lista_muestra_opcion_de_inscripcion_para_torneo_abierto(self):
        response = self.client.get('/torneos/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.torneo.nombre)
        self.assertContains(response, 'Agregar al carrito')

    def test_detalle_muestra_formulario_de_inscripcion_para_torneo_abierto(self):
        response = self.client.get(f'/torneos/{self.torneo.slug}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.torneo.nombre)
        self.assertContains(response, 'Agregar al carrito')

    def test_agregar_al_carrito_no_inscribe_automaticamente(self):
        response = self.client.post(
            f'/pedidos/carrito/agregar-torneo/{self.torneo.slug}/',
        )

        self.assertRedirects(response, '/pedidos/carrito/')
        self.assertEqual(self.client.session['carrito_torneos'], [self.torneo.pk])
        self.assertFalse(Inscripcion.objects.filter(torneo=self.torneo).exists())
        self.assertContains(self.client.get('/pedidos/carrito/'), self.torneo.nombre)

    def test_confirmar_carrito_requiere_autenticacion(self):
        self.client.post(f'/pedidos/carrito/agregar-torneo/{self.torneo.slug}/')

        response = self.client.post('/pedidos/carrito/confirmar/')

        self.assertRedirects(
            response,
            '/usuarios/login/?next=/pedidos/carrito/confirmar/',
        )
        self.assertFalse(Inscripcion.objects.filter(torneo=self.torneo).exists())

    def test_confirmar_carrito_crea_inscripcion_y_limpia_carrito(self):
        self.client.force_login(self.usuario)
        self.client.post(f'/pedidos/carrito/agregar-torneo/{self.torneo.slug}/')

        response = self.client.post('/pedidos/carrito/confirmar/')

        self.assertTrue(
            Inscripcion.objects.filter(torneo=self.torneo, usuario=self.usuario).exists(),
        )
        self.assertEqual(self.torneo.cupos_disponibles, 15)
        self.assertNotIn('carrito_torneos', self.client.session)
        comprobante = ComprobanteInscripcion.objects.get(usuario=self.usuario)
        self.assertRedirects(response, f'/pedidos/comprobante/{comprobante.codigo}/')

    def test_comprobante_guarda_y_muestra_desglose_de_cobros(self):
        self.client.force_login(self.usuario)
        self.torneo.costo_inscripcion = 15000
        self.torneo.save()
        self.client.post(f'/pedidos/carrito/agregar-torneo/{self.torneo.slug}/')

        carrito_response = self.client.get('/pedidos/carrito/')
        self.assertContains(carrito_response, '$15.000 CLP')
        self.assertContains(carrito_response, '$1.500 CLP')
        self.assertContains(carrito_response, '$2.395 CLP')
        self.assertContains(carrito_response, '$16.500 CLP')

        self.client.post('/pedidos/carrito/confirmar/')
        comprobante = ComprobanteInscripcion.objects.get(usuario=self.usuario)

        self.assertEqual(comprobante.subtotal, 15000)
        self.assertEqual(comprobante.subtotal_neto, 12605)
        self.assertEqual(comprobante.recargo_servicio, 1500)
        self.assertEqual(comprobante.iva, 2395)
        self.assertEqual(comprobante.total, 16500)
        self.assertTrue(comprobante.iva_incluido)
        response = self.client.get(f'/pedidos/comprobante/{comprobante.codigo}/')
        self.assertContains(response, 'Copa de prueba')
        self.assertContains(response, '$15.000 CLP')
        self.assertContains(response, '$12.605 CLP')
        self.assertContains(response, '$1.500 CLP')
        self.assertContains(response, '$2.395 CLP')
        self.assertContains(response, '$16.500 CLP')
        self.assertContains(response, 'No acredita un pago ni reemplaza una boleta o factura tributaria.')
        self.assertContains(self.client.get('/usuarios/perfil/'), 'Ver comprobante')

    def test_comprobante_solo_es_visible_para_su_usuario(self):
        comprobante = ComprobanteInscripcion.objects.create(
            usuario=self.usuario,
            subtotal=0,
            recargo_servicio=0,
            iva=0,
            total=0,
        )
        otro_usuario = User.objects.create_user(
            username='otro_jugador',
            password='Fuerte-2026-clave!',
        )
        self.client.force_login(otro_usuario)

        response = self.client.get(f'/pedidos/comprobante/{comprobante.codigo}/')

        self.assertEqual(response.status_code, 404)

    def test_torneo_no_se_agrega_dos_veces_al_carrito(self):
        self.client.post(f'/pedidos/carrito/agregar-torneo/{self.torneo.slug}/')
        self.client.post(f'/pedidos/carrito/agregar-torneo/{self.torneo.slug}/')

        self.assertEqual(self.client.session['carrito_torneos'], [self.torneo.pk])

    def test_no_confirma_carrito_si_torneo_se_cierra_o_agota(self):
        self.client.force_login(self.usuario)
        otro_torneo = TorneoEvento.objects.create(
            nombre='Otra copa',
            categoria=self.categoria,
            organizador='Organizador',
            reglas='Formato eliminatorio.',
            costo_inscripcion=1000,
            cupos_maximos=4,
        )
        self.client.post(f'/pedidos/carrito/agregar-torneo/{self.torneo.slug}/')
        self.client.post(f'/pedidos/carrito/agregar-torneo/{otro_torneo.slug}/')
        self.torneo.estado = 'en_curso'
        self.torneo.save()

        self.client.post('/pedidos/carrito/confirmar/')

        self.assertFalse(Inscripcion.objects.exists())
        self.assertEqual(len(self.client.session['carrito_torneos']), 2)

    def test_quitar_torneo_del_carrito(self):
        self.client.post(f'/pedidos/carrito/agregar-torneo/{self.torneo.slug}/')

        response = self.client.post(
            f'/pedidos/carrito/quitar-torneo/{self.torneo.slug}/',
        )

        self.assertRedirects(response, '/pedidos/carrito/')
        self.assertEqual(self.client.session['carrito_torneos'], [])

    def test_usuario_puede_cancelar_inscripcion_mientras_torneo_esta_abierto(self):
        self.client.force_login(self.usuario)
        Inscripcion.objects.create(torneo=self.torneo, usuario=self.usuario)

        response = self.client.post(
            f'/torneos/{self.torneo.slug}/cancelar-inscripcion/',
        )

        self.assertRedirects(response, '/usuarios/perfil/')
        self.assertFalse(
            Inscripcion.objects.filter(torneo=self.torneo, usuario=self.usuario).exists(),
        )
        self.assertEqual(self.torneo.cupos_disponibles, 16)

    def test_no_se_puede_cancelar_inscripcion_cuando_torneo_ya_inicio(self):
        self.client.force_login(self.usuario)
        self.torneo.estado = 'en_curso'
        self.torneo.save()
        inscripcion = Inscripcion.objects.create(torneo=self.torneo, usuario=self.usuario)

        response = self.client.post(
            f'/torneos/{self.torneo.slug}/cancelar-inscripcion/',
        )

        self.assertRedirects(response, '/usuarios/perfil/')
        self.assertTrue(Inscripcion.objects.filter(pk=inscripcion.pk).exists())

    def test_perfil_muestra_inscripciones_confirmadas(self):
        self.client.force_login(self.usuario)
        Inscripcion.objects.create(torneo=self.torneo, usuario=self.usuario)

        response = self.client.get('/usuarios/perfil/')

        self.assertContains(response, self.torneo.nombre)
        self.assertContains(response, 'Cancelar inscripción')
