from django.test import TestCase
from django.contrib.auth.models import User


class RegistroUsuarioTests(TestCase):
    def test_registro_crea_cuenta_y_redirige_al_inicio(self):
        response = self.client.post('/usuarios/registro/', {
            'username': 'jugador_nuevo',
            'first_name': 'Jose',
            'last_name': 'Garcia',
            'email': 'jose@example.com',
            'password1': 'Fuerte-2026-clave!',
            'password2': 'Fuerte-2026-clave!',
        })

        self.assertRedirects(response, '/')
        self.assertTrue(
            self.client.session.get('_auth_user_id'),
            'La cuenta creada debe quedar con la sesión iniciada.',
        )

    def test_login_redirige_al_inicio(self):
        User.objects.create_user(username='jugador', password='Fuerte-2026-clave!')

        response = self.client.post('/usuarios/login/', {
            'username': 'jugador',
            'password': 'Fuerte-2026-clave!',
        })

        self.assertRedirects(response, '/')
