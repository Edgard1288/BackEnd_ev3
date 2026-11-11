
## Ficha de Registro de la Propuesta

* **Nombre de la Organización:** GG-Arena Esports & Tournaments
* **Modelo de Negocio / Giro:** Plataforma de organización de torneos de deportes electrónicos, arriendo/reserva de pases y gestión de aforos.
* **Integrantes del Equipo:**
  * Edgard García — Ingeniería en Informática (INACAP Sede Chillán)
  * Jose García — Ingeniería en Informática (INACAP Sede Chillán)
* **Entidad de Contexto / Agrupación (ORM):** CategoriaJuego (ej: Fighting Games, FPS Tactical, MOBA, Battle Royale / Speedrun)
* **Entidad Principal Gestionable (ORM):** TorneoEvento (con tarifa de inscripción, aforo/cupos máximos, fecha del evento, banner promocional y estado operativo)
* **Propósito de la Sesión (request.session):** Planificador de pases y cotización de inscripciones a torneos con asignación de cupos por equipo, recargo por servicio (10%), IVA (19%) y comprobante de reserva.

---

## Arquitectura Modular del Proyecto

El proyecto sigue el patrón MTV (Model - Template - View) de Django organizado de forma limpia en el directorio contenedor apps/:

```text
tienda_esports/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── manage.py
├── config/                  # Configuración central del proyecto (settings.py, urls.py)
├── apps/
│   ├── core/                # Portada principal y vista institucional (Quiénes Somos)
│   ├── usuarios/            # Autenticación, registro, perfiles y control de acceso
│   ├── torneos/             # Capa de datos ORM (CategoriaJuego, TorneoEvento), CRUD y Admin
│   └── pases/               # Sesión HTTP (request.session), cotizador y Context Processor
└── templates/               # Plantillas HTML5 procesadas por DTL y Bootstrap 5
    ├── base.html
    ├── core/
    ├── usuarios/
    ├── torneos/
    └── pases/
