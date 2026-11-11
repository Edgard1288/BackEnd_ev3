from django.test import TestCase

from .models import CategoriaJuego, TorneoEvento


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

    def test_lista_abre_con_torneo_abierto(self):
        response = self.client.get('/torneos/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.torneo.nombre)
        self.assertContains(response, 'Inscripción no disponible')

    def test_detalle_abre_con_torneo_abierto(self):
        response = self.client.get(f'/torneos/{self.torneo.slug}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.torneo.nombre)
        self.assertContains(response, 'Inscripción no disponible')
