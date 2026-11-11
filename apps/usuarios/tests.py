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

    def test_registro_informa_en_recuadro_rojo_si_contrasena_no_cumple(self):
        response = self.client.post('/usuarios/registro/', {
            'username': 'jugador_nuevo',
            'first_name': 'Jose',
            'last_name': 'Garcia',
            'email': 'jose@example.com',
            'password1': '123',
            'password2': '123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-error-message="La contraseña es demasiado corta.')
        self.assertContains(response, 'Requisitos de la contraseña:')
        self.assertContains(response, 'Debe contener por lo menos 8 caracteres')
        self.assertContains(response, 'completamente')
        self.assertNotContains(response, 'alert alert-danger')
        self.assertFalse(User.objects.filter(username='jugador_nuevo').exists())

    def test_registro_muestra_requisitos_de_contrasena_antes_de_enviar(self):
        response = self.client.get('/usuarios/registro/')

        self.assertContains(response, 'border border-secondary rounded p-3 mt-2')
        self.assertContains(response, 'Requisitos de la contraseña:')
        self.assertContains(response, 'Su contraseña debe contener al menos 8 caracteres')

    def test_registro_avisa_y_enfoca_campos_obligatorios_vacios(self):
        response = self.client.post('/usuarios/registro/', {
            'username': 'jugador_nuevo',
            'first_name': '',
            'last_name': 'Garcia',
            'email': 'jose@example.com',
            'password1': 'Fuerte-2026-clave!',
            'password2': 'Fuerte-2026-clave!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-error-message="Este campo está vacío."')
        self.assertContains(response, 'id_first_name')
        self.assertContains(response, 'is-invalid')
        self.assertContains(response, 'scrollIntoView')
        self.assertContains(response, 'reportValidity')

    def test_confirmacion_vacia_se_indica_sin_error_bajo_su_campo(self):
        response = self.client.post('/usuarios/registro/', {
            'username': 'jugador_nuevo',
            'first_name': 'Jose',
            'last_name': 'Garcia',
            'email': 'jose@example.com',
            'password1': 'Fuerte-2026-clave!',
            'password2': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-error-message="Este campo está vacío."')
        self.assertContains(response, 'id_password2')
        self.assertContains(response, 'is-invalid')
        self.assertContains(response, 'Requisitos de la contraseña:')
