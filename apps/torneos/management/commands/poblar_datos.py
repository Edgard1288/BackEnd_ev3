from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.torneos.models import CategoriaJuego, TorneoEvento


class Command(BaseCommand):
    help = "Carga automáticamente superusuario, categorías y torneos iniciales de GG-Arena."

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@ggarena.cl", "admin")
            self.stdout.write(self.style.SUCCESS("✓ Superusuario 'admin' (clave: admin) creado."))

        categorias_data = [
            ("FPS Tactical", "Juegos de disparos tácticos por equipos (ej: Valorant, CS2)."),
            ("Fighting Games", "Juegos de pelea uno contra uno (ej: SF6, Tekken 8, Smash)."),
            ("MOBA", "Estrategia de arena de batalla multijugador (ej: League of Legends, Dota 2)."),
            ("Battle Royale", "Supervivencia campal masiva por escuadras (ej: Fortnite, Apex)."),
        ]

        cat_map = {}
        for nombre, desc in categorias_data:
            cat, created = CategoriaJuego.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc, 'activo': True}
            )
            cat_map[nombre] = cat

        torneos_data = [
            ("Copa Smash Ultimate Chillán", cat_map["Fighting Games"], "GG-Arena South", "Formato Doble Eliminación. Reglas EVO.", 12000, 32, "abierto"),
            ("Valorant 5v5 Open Series", cat_map["FPS Tactical"], "Riot Community", "Mejor de 3 mapa seleccionado. Anticheat obligatorio.", 25000, 16, "abierto"),
            ("League of Legends 5v5 Cup", cat_map["MOBA"], "GG-Arena Central", "Mapa Grieta del Invocador. Fases de grupos y Playoffs.", 30000, 8, "abierto"),
            ("Street Fighter 6 Regional Chile", cat_map["Fighting Games"], "Capcom Pro Tour Chile", "FT2 en pool, FT3 en Top 8.", 15000, 64, "en_curso"),
        ]

        for nombre, cat, org, reglas, costo, cupos, estado in torneos_data:
            TorneoEvento.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'categoria': cat,
                    'organizador': org,
                    'reglas': reglas,
                    'costo_inscripcion': costo,
                    'cupos_maximos': cupos,
                    'estado': estado,
                    'activo': True
                }
            )

        self.stdout.write(self.style.SUCCESS("✓ Categorías y Torneos de prueba poblados exitosamente en GG-Arena."))