# -*- coding: utf-8 -*-
"""
Configuración completa del servidor del club TAQ.
Edita SOLO este archivo si necesitas cambiar nombres, roles o permisos.
"""

import discord

PREFIJO_ROL = "TAQ | "

# ---------------------------------------------------------------------
# 1) ROLES, de mayor a menor jerarquía (arriba = más poder).
#    El nombre completo (con el prefijo) es el nombre real del rol.
# ---------------------------------------------------------------------
ROLES = [
    "TAQ | 👑 PRESIDENTE",
    "TAQ | 💼 VICEPRESIDENTE",
    "TAQ | 🛡️ DIRECTOR DEPORTIVO",
    "TAQ | ⚽ ENTRENADOR",
    "TAQ | 📋 CUERPO TÉCNICO",
    "TAQ | 🎯 SCOUT",
    "TAQ | 🩺 FISIOTERAPEUTA",

    "TAQ | ⭐ CAPITÁN",
    "TAQ | 🥇 PRIMER EQUIPO",
    "TAQ | 🥈 SUPLENTE",
    "TAQ | 🌱 CANTERA",
    "TAQ | 🧪 A PRUEBA",

    "TAQ | 🎨 CREADOR DE CONTENIDO",
    "TAQ | 📸 FOTÓGRAFO",
    "TAQ | 🎥 EDITOR",

    "TAQ | 🛡️ ADMINISTRADOR",
    "TAQ | 🔨 MODERADOR",
    "TAQ | 🎫 SOPORTE",

    "TAQ | 👤 AFICIONADO",
    "TAQ | 🤝 INVITADO",
    "TAQ | 🤖 BOT",
]

# ---------------------------------------------------------------------
# 2) GRUPOS de roles, para no repetir nombres en cada permiso.
# ---------------------------------------------------------------------
GRUPOS = {
    "STAFF_ALTA": ["TAQ | 👑 PRESIDENTE", "TAQ | 💼 VICEPRESIDENTE", "TAQ | 🛡️ ADMINISTRADOR"],
    "STAFF_MOD": ["TAQ | 🔨 MODERADOR"],
    "STAFF_SOPORTE": ["TAQ | 🎫 SOPORTE"],
    "DEPORTIVO": ["TAQ | 🛡️ DIRECTOR DEPORTIVO"],
    "CUERPO_TECNICO": ["TAQ | ⚽ ENTRENADOR", "TAQ | 📋 CUERPO TÉCNICO", "TAQ | 🩺 FISIOTERAPEUTA"],
    "SCOUTING": ["TAQ | 🎯 SCOUT"],
    "JUGADORES": ["TAQ | ⭐ CAPITÁN", "TAQ | 🥇 PRIMER EQUIPO", "TAQ | 🥈 SUPLENTE"],
    "CANTERA": ["TAQ | 🌱 CANTERA", "TAQ | 🧪 A PRUEBA"],
    "CONTENIDO": ["TAQ | 🎨 CREADOR DE CONTENIDO", "TAQ | 📸 FOTÓGRAFO", "TAQ | 🎥 EDITOR"],
    "PUBLICO": ["TAQ | 👤 AFICIONADO"],
    "INVITADO": ["TAQ | 🤝 INVITADO"],
}


def _ow(**kwargs):
    return discord.PermissionOverwrite(**kwargs)


# ---------------------------------------------------------------------
# 3) NIVELES de permiso reutilizables.
# ---------------------------------------------------------------------
NIVELES = {
    "sin_acceso": _ow(view_channel=False, connect=False),
    "ver": _ow(view_channel=True, send_messages=False),
    "ver_escribir": _ow(view_channel=True, send_messages=True, read_message_history=True),
    "ver_publicar": _ow(view_channel=True, send_messages=True, embed_links=True, attach_files=True),
    "gestion_total": _ow(view_channel=True, send_messages=True, manage_messages=True, manage_channels=True),
    "voz_conectar": _ow(view_channel=True, connect=True, speak=True),
}

# ---------------------------------------------------------------------
# 4) CATEGORÍAS Y CANALES DE TEXTO.
#    Cada entrada: nombre categoría, lista de canales, permisos por
#    defecto de la categoría, y "overrides" para canales específicos
#    que necesiten permisos distintos a los del resto de la categoría.
# ---------------------------------------------------------------------
CATEGORIAS_TEXTO = [
    {
        "nombre": "📌・INFORMACIÓN",
        "canales": ["📢・anuncios", "📜・reglamento", "🏆・historia-del-club", "👥・staff", "🎖️・rangos", "🔗・enlaces"],
        "permisos": [("@everyone", "ver"), ("STAFF_ALTA", "gestion_total"), ("STAFF_MOD", "gestion_total")],
        "overrides": {},
    },
    {
        "nombre": "📰・ACTUALIDAD",
        "canales": ["🗞️・noticias", "📸・fotos-del-club", "🎥・videos", "🏅・logros", "📊・estadísticas"],
        "permisos": [("@everyone", "ver"), ("CONTENIDO", "ver_publicar"), ("STAFF_ALTA", "gestion_total")],
        "overrides": {},
    },
    {
        "nombre": "⚽・PRIMER EQUIPO",
        "canales": ["👥・plantilla", "📋・convocatorias", "📑・alineaciones", "🩺・disponibilidad", "📝・entrenamientos", "💬・vestuario"],
        "permisos": [
            ("@everyone", "sin_acceso"),
            ("JUGADORES", "ver_escribir"),
            ("CUERPO_TECNICO", "ver_escribir"),
            ("DEPORTIVO", "gestion_total"),
            ("STAFF_ALTA", "gestion_total"),
        ],
        "overrides": {},
    },
    {
        "nombre": "🏟️・PARTIDOS",
        "canales": ["📅・calendario", "🆚・próximos-partidos", "📢・día-de-partido", "📊・resultados", "🏆・competiciones", "📈・clasificación"],
        "permisos": [
            ("@everyone", "ver"),
            ("JUGADORES", "ver"),
            ("DEPORTIVO", "gestion_total"),
            ("CUERPO_TECNICO", "gestion_total"),
            ("STAFF_ALTA", "gestion_total"),
        ],
        "overrides": {},
    },
    {
        "nombre": "🎮・ROBLOX",
        "canales": ["🎮・servidor-roblox", "🏟️・cueva-zuazua", "🏟️・estadios", "🔗・links-de-partidos", "🕹️・prácticas"],
        "permisos": [("@everyone", "ver_escribir"), ("STAFF_ALTA", "gestion_total")],
        "overrides": {},
    },
    {
        "nombre": "📋・FICHAJES",
        "canales": ["📢・mercado-de-fichajes", "🔄・fichajes", "📝・pruebas", "👀・scouting", "📑・plantilla-oficial"],
        "permisos": [
            ("@everyone", "ver"),
            ("SCOUTING", "gestion_total"),
            ("DEPORTIVO", "gestion_total"),
            ("STAFF_ALTA", "gestion_total"),
        ],
        "overrides": {
            "🔄・fichajes": [
                ("@everyone", "sin_acceso"),
                ("SCOUTING", "ver_escribir"),
                ("DEPORTIVO", "ver_escribir"),
                ("STAFF_ALTA", "gestion_total"),
            ],
            "📝・pruebas": [
                ("@everyone", "sin_acceso"),
                ("SCOUTING", "ver_escribir"),
                ("DEPORTIVO", "ver_escribir"),
                ("STAFF_ALTA", "gestion_total"),
            ],
            "👀・scouting": [
                ("@everyone", "sin_acceso"),
                ("SCOUTING", "ver_escribir"),
                ("DEPORTIVO", "ver_escribir"),
                ("STAFF_ALTA", "gestion_total"),
            ],
        },
    },
    {
        "nombre": "🎓・CANTERA",
        "canales": ["🌱・cantera", "📝・pruebas-cantera", "📋・convocatorias-sub", "⭐・jóvenes-promesas"],
        "permisos": [
            ("@everyone", "ver"),
            ("CANTERA", "ver_escribir"),
            ("CUERPO_TECNICO", "gestion_total"),
            ("DEPORTIVO", "gestion_total"),
            ("STAFF_ALTA", "gestion_total"),
        ],
        "overrides": {},
    },
    {
        "nombre": "💬・COMUNIDAD",
        "canales": ["💬・chat", "😂・memes", "📸・media", "🎮・otros-juegos", "🤖・comandos"],
        "permisos": [("@everyone", "ver_escribir"), ("STAFF_MOD", "gestion_total"), ("STAFF_ALTA", "gestion_total")],
        "overrides": {},
    },
    {
        "nombre": "🎫・SOPORTE",
        "canales": ["🎫・abrir-ticket", "❓・preguntas", "🚨・reportes", "📩・contactar-staff"],
        "permisos": [
            ("@everyone", "ver_escribir"),
            ("STAFF_SOPORTE", "gestion_total"),
            ("STAFF_MOD", "gestion_total"),
            ("STAFF_ALTA", "gestion_total"),
        ],
        "overrides": {},
    },
    {
        "nombre": "🔐・STAFF",
        "canales": ["💼・staff-chat", "📋・pendientes", "📝・registro-staff", "⚠️・sanciones", "🎫・tickets-staff", "📊・logs"],
        "permisos": [
            ("@everyone", "sin_acceso"),
            ("STAFF_ALTA", "gestion_total"),
            ("STAFF_MOD", "ver_escribir"),
            ("STAFF_SOPORTE", "ver_escribir"),
            ("DEPORTIVO", "ver_escribir"),
        ],
        "overrides": {
            # Sanciones y logs: solo cúpula alta + moderación, ni
            # siquiera soporte ni director deportivo.
            "⚠️・sanciones": [
                ("@everyone", "sin_acceso"),
                ("STAFF_ALTA", "gestion_total"),
                ("STAFF_MOD", "ver_escribir"),
            ],
            "📊・logs": [
                ("@everyone", "sin_acceso"),
                ("STAFF_ALTA", "gestion_total"),
                ("STAFF_MOD", "ver_escribir"),
            ],
        },
    },
]

# ---------------------------------------------------------------------
# 5) CATEGORÍA DE VOZ.
# ---------------------------------------------------------------------
CATEGORIA_VOZ = {
    "nombre": "🔊・CANALES DE VOZ",
    "canales": ["🏟️・Vestuario", "⚽・Entrenamiento", "🎙️・Partido", "🗣️・Sala Staff", "🎮・Roblox", "🔊・General"],
    "permisos": [("@everyone", "voz_conectar"), ("STAFF_ALTA", "gestion_total")],
    "overrides": {
        "🗣️・Sala Staff": [
            ("@everyone", "sin_acceso"),
            ("STAFF_ALTA", "gestion_total"),
            ("STAFF_MOD", "voz_conectar"),
            ("STAFF_SOPORTE", "voz_conectar"),
            ("DEPORTIVO", "voz_conectar"),
        ],
    },
}
