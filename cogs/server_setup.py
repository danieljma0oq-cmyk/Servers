# -*- coding: utf-8 -*-
"""
Comando !server: instalador automático del servidor del club TAQ.

Idempotente: se puede correr varias veces sin duplicar nada. Nunca
borra ni renombra elementos existentes.
"""

import asyncio
import discord
from discord.ext import commands

import config

# Guilds con una instalación en curso, para que dos ejecuciones
# simultáneas no se pisen entre sí.
_INSTALACIONES_EN_CURSO = set()


def _resolver_overwrites(guild: discord.Guild, permisos: list) -> dict:
    """Convierte [(rol_o_grupo, nivel), ...] en un dict listo para
    pasarle a create_category / create_text_channel / etc."""
    overwrites = {}
    for nombre, nivel in permisos:
        if nombre == "@everyone":
            roles = [guild.default_role]
        elif nombre in config.GRUPOS:
            roles = [discord.utils.get(guild.roles, name=n) for n in config.GRUPOS[nombre]]
            roles = [r for r in roles if r is not None]
        else:
            rol = discord.utils.get(guild.roles, name=nombre)
            roles = [rol] if rol else []
        for rol in roles:
            overwrites[rol] = config.NIVELES[nivel]
    return overwrites


class ErrorInstalacion(Exception):
    def __init__(self, elemento: str, tipo: str, motivo: str):
        self.elemento = elemento
        self.tipo = tipo
        self.motivo = motivo
        super().__init__(f"{tipo}: {elemento} -> {motivo}")


class ConfirmarServerView(discord.ui.View):
    def __init__(self, autor_id: int):
        super().__init__(timeout=120)
        self.autor_id = autor_id
        self.decision = None  # True / False / None (timeout)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message(
                "❌ No puedes utilizar estos botones.\n\n"
                "Solo la persona que ejecutó el comando puede confirmar esta acción.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="SÍ, CREAR SERVIDOR", emoji="✅", style=discord.ButtonStyle.success)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.decision = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="NO, CANCELAR", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.decision = False
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class ServerSetup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------------------------------------------
    # Helpers de búsqueda (evitan duplicados)
    # -------------------------------------------------------------
    @staticmethod
    def _buscar_rol(guild: discord.Guild, nombre: str):
        return discord.utils.get(guild.roles, name=nombre)

    @staticmethod
    def _buscar_categoria(guild: discord.Guild, nombre: str):
        return discord.utils.get(guild.categories, name=nombre)

    @staticmethod
    def _buscar_canal_en_categoria(categoria: discord.CategoryChannel, nombre: str, tipo: str):
        canales = categoria.text_channels if tipo == "texto" else categoria.voice_channels
        return discord.utils.get(canales, name=nombre)

    # -------------------------------------------------------------
    # Pasos de la instalación
    # -------------------------------------------------------------
    async def _comprobar_permisos_bot(self, guild: discord.Guild):
        perms = guild.me.guild_permissions
        faltantes = []
        if not perms.manage_roles:
            faltantes.append("Gestionar roles")
        if not perms.manage_channels:
            faltantes.append("Gestionar canales")
        if faltantes:
            raise ErrorInstalacion(
                elemento=", ".join(faltantes), tipo="permisos del bot",
                motivo="Al bot le faltan estos permisos en el servidor.",
            )

    async def _crear_roles(self, guild: discord.Guild) -> int:
        creados = 0
        for nombre in config.ROLES:
            if self._buscar_rol(guild, nombre):
                continue
            try:
                await guild.create_role(name=nombre, reason="Instalación automática TAQ")
                creados += 1
            except discord.HTTPException as e:
                raise ErrorInstalacion(elemento=nombre, tipo="rol", motivo=str(e))
        return creados

    async def _crear_categorias_y_canales(self, guild: discord.Guild, on_progreso=None):
        stats = {"categorias": 0, "texto": 0, "voz": 0}
        total_categorias = len(config.CATEGORIAS_TEXTO) + 1  # +1 por la de voz
        hechas = 0

        # --- categorías de texto ---
        for cat_cfg in config.CATEGORIAS_TEXTO:
            categoria = self._buscar_categoria(guild, cat_cfg["nombre"])
            if categoria is None:
                overwrites = _resolver_overwrites(guild, cat_cfg["permisos"])
                try:
                    categoria = await guild.create_category(cat_cfg["nombre"], overwrites=overwrites)
                    stats["categorias"] += 1
                except discord.HTTPException as e:
                    raise ErrorInstalacion(elemento=cat_cfg["nombre"], tipo="categoría", motivo=str(e))

            for nombre_canal in cat_cfg["canales"]:
                if self._buscar_canal_en_categoria(categoria, nombre_canal, "texto"):
                    continue
                permisos_canal = cat_cfg["overrides"].get(nombre_canal)
                overwrites_canal = _resolver_overwrites(guild, permisos_canal) if permisos_canal else {}
                try:
                    await guild.create_text_channel(
                        nombre_canal, category=categoria, overwrites=overwrites_canal or None
                    )
                    stats["texto"] += 1
                except discord.HTTPException as e:
                    raise ErrorInstalacion(elemento=nombre_canal, tipo="canal de texto", motivo=str(e))

            hechas += 1
            if on_progreso:
                await on_progreso(hechas, total_categorias)
            await asyncio.sleep(0.5)  # margen para no saturar el rate limit de Discord

        # --- categoría de voz ---
        voz_cfg = config.CATEGORIA_VOZ
        categoria_voz = self._buscar_categoria(guild, voz_cfg["nombre"])
        if categoria_voz is None:
            overwrites = _resolver_overwrites(guild, voz_cfg["permisos"])
            try:
                categoria_voz = await guild.create_category(voz_cfg["nombre"], overwrites=overwrites)
                stats["categorias"] += 1
            except discord.HTTPException as e:
                raise ErrorInstalacion(elemento=voz_cfg["nombre"], tipo="categoría", motivo=str(e))

        for nombre_canal in voz_cfg["canales"]:
            if self._buscar_canal_en_categoria(categoria_voz, nombre_canal, "voz"):
                continue
            permisos_canal = voz_cfg["overrides"].get(nombre_canal)
            overwrites_canal = _resolver_overwrites(guild, permisos_canal) if permisos_canal else {}
            try:
                await guild.create_voice_channel(
                    nombre_canal, category=categoria_voz, overwrites=overwrites_canal or None
                )
                stats["voz"] += 1
            except discord.HTTPException as e:
                raise ErrorInstalacion(elemento=nombre_canal, tipo="canal de voz", motivo=str(e))

        hechas += 1
        if on_progreso:
            await on_progreso(hechas, total_categorias)

        return stats

    # -------------------------------------------------------------
    # Comando principal
    # -------------------------------------------------------------
    @commands.command(name="server")
    async def server(self, ctx: commands.Context):
        guild = ctx.guild

        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(
                "❌ No tienes permisos para utilizar este comando.\n\n"
                "Necesitas permisos administrativos para configurar la estructura del servidor."
            )

        if guild.id in _INSTALACIONES_EN_CURSO:
            return await ctx.send("⏳ Ya hay una instalación en curso en este servidor. Espera a que termine.")

        embed_confirmacion = discord.Embed(
            title="⚠️ CONFIGURACIÓN DEL SERVIDOR",
            description=(
                "Estás a punto de crear automáticamente toda la estructura del servidor del club.\n\n"
                "Se crearán:\n"
                "• Categorías\n• Canales de texto\n• Canales de voz\n• Roles\n• Permisos\n"
                "• Organización completa del servidor\n\n"
                "⚠️ Esta acción puede modificar considerablemente la estructura actual del servidor.\n\n"
                "¿Estás seguro de que deseas continuar?"
            ),
            color=discord.Color.orange(),
        )
        view = ConfirmarServerView(ctx.author.id)
        mensaje = await ctx.send(embed=embed_confirmacion, view=view)

        await view.wait()

        if view.decision is not True:
            embed_cancelado = discord.Embed(
                title="❌ Instalación cancelada",
                description="No se ha creado ni modificado nada.",
                color=discord.Color.red(),
            )
            return await mensaje.edit(embed=embed_cancelado, view=view)

        _INSTALACIONES_EN_CURSO.add(guild.id)
        try:
            await self._ejecutar_instalacion(ctx, mensaje, guild)
        finally:
            _INSTALACIONES_EN_CURSO.discard(guild.id)

    async def _ejecutar_instalacion(self, ctx, mensaje: discord.Message, guild: discord.Guild):
        pasos = [
            "⏳ Comprobando permisos",
            "⬜ Creando roles",
            "⬜ Creando categorías",
            "⬜ Creando canales",
            "⬜ Configurando permisos",
            "⬜ Finalizando",
        ]

        async def actualizar(indice: int, estado: str):
            pasos[indice] = f"{estado} {pasos[indice].split(' ', 1)[1]}"
            embed = discord.Embed(
                title="⚙️ CONFIGURANDO SERVIDOR...",
                description="\n".join(pasos),
                color=discord.Color.blurple(),
            )
            await mensaje.edit(embed=embed, view=None)

        async def reportar_progreso_categorias(hechas: int, total: int):
            pasos[2] = f"⏳ Creando categorías y canales ({hechas}/{total})"
            embed = discord.Embed(
                title="⚙️ CONFIGURANDO SERVIDOR...",
                description="\n".join(pasos),
                color=discord.Color.blurple(),
            )
            await mensaje.edit(embed=embed, view=None)

        try:
            await actualizar(0, "✅")
            await self._comprobar_permisos_bot(guild)

            await actualizar(1, "⏳")
            roles_creados = await self._crear_roles(guild)
            await actualizar(1, "✅")

            await actualizar(2, "⏳")
            await actualizar(3, "⬜")
            stats = await self._crear_categorias_y_canales(guild, on_progreso=reportar_progreso_categorias)
            pasos[2] = "✅ Creando categorías y canales"
            await actualizar(3, "✅")

            await actualizar(4, "✅")  # los permisos se aplicaron al crear cada elemento
            await actualizar(5, "✅")

        except ErrorInstalacion as e:
            embed_error = discord.Embed(
                title="❌ ERROR DURANTE LA CONFIGURACIÓN",
                description=(
                    f"**Elemento:**\n`{e.elemento}`\n\n"
                    f"**Tipo:**\n`{e.tipo}`\n\n"
                    f"**Motivo:**\n`{e.motivo}`\n\n"
                    "El proceso se ha detenido para evitar realizar cambios innecesarios."
                ),
                color=discord.Color.red(),
            )
            return await mensaje.edit(embed=embed_error, view=None)

        except Exception as e:
            # Cualquier error no previsto (rate limit raro, permisos de
            # jerarquía, etc.) también debe avisar en vez de dejar el
            # mensaje congelado.
            print(f"[!server] Error inesperado: {type(e).__name__}: {e}")
            embed_error = discord.Embed(
                title="❌ ERROR INESPERADO DURANTE LA CONFIGURACIÓN",
                description=(
                    f"**Tipo:**\n`{type(e).__name__}`\n\n"
                    f"**Detalle:**\n`{e}`\n\n"
                    "Revisa los logs de Railway para más detalle. El proceso se detuvo aquí."
                ),
                color=discord.Color.red(),
            )
            return await mensaje.edit(embed=embed_error, view=None)

        total_categorias = len(config.CATEGORIAS_TEXTO) + 1
        total_canales_texto = sum(len(c["canales"]) for c in config.CATEGORIAS_TEXTO)
        total_canales_voz = len(config.CATEGORIA_VOZ["canales"])

        embed_final = discord.Embed(
            title="✅ SERVIDOR CONFIGURADO",
            description="La estructura del club ha sido creada correctamente.",
            color=discord.Color.green(),
        )
        embed_final.add_field(name="📁 Categorías", value=str(total_categorias), inline=True)
        embed_final.add_field(name="💬 Canales de texto", value=str(total_canales_texto), inline=True)
        embed_final.add_field(name="🔊 Canales de voz", value=str(total_canales_voz), inline=True)
        embed_final.add_field(name="👑 Roles", value=str(len(config.ROLES)), inline=True)
        embed_final.set_footer(
            text="🔐 Permisos configurados correctamente. 🛡️ Sistema protegido contra duplicados."
        )
        embed_final.add_field(
            name="\u200b",
            value="⚽ ¡El servidor está listo para comenzar la temporada!",
            inline=False,
        )
        await mensaje.edit(embed=embed_final, view=None)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerSetup(bot))
