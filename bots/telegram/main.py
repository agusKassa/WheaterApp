#!/usr/bin/env python3

import os
import asyncio
import aiohttp
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://web:8000')
API_ENDPOINT = os.getenv('API_TELEGRAM_ENDPOINT', '/api/weather/telegram')

class TelegramWeatherBot:
    def __init__(self):
        self.api_url = f"{API_BASE_URL}{API_ENDPOINT}"

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /start"""
        await update.message.reply_text(
            "¡Hola! 🌤️ Soy tu bot del clima.\n\n"
            "Envíame el nombre de una ciudad y te diré el clima actual.\n"
            "Ejemplo: 'Buenos Aires' o 'Madrid'\n\n"
            "Comandos disponibles:\n"
            "/start - Mostrar este mensaje\n"
            "/help - Ayuda"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /help"""
        await update.message.reply_text(
            "🌤️ **Bot del Clima - Ayuda**\n\n"
            "Simplemente escribe el nombre de una ciudad para obtener el clima:\n\n"
            "📍 Ejemplos:\n"
            "• Buenos Aires\n"
            "• Madrid\n"
            "• New York\n"
            "• London\n\n"
            "📊 La respuesta incluirá:\n"
            "• Temperatura actual\n"
            "• Descripción del clima\n"
            "• Humedad\n"
            "• Presión atmosférica\n\n"
            "/start - Volver al inicio"
        )

    async def handle_weather_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Manejar solicitudes de clima"""
        city = update.message.text.strip()
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name

        # Enviar mensaje de "escribiendo..."
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        try:
            # Preparar datos para enviar a TU API
            payload = {
                'city': city,
                'user_id': user_id,
                'username': username,
                'platform': 'telegram',
                'chat_id': update.effective_chat.id
            }

            # Hacer petición a TU API de Symfony (no a OpenWeather)
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers={'Content-Type': 'application/json'}) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.send_weather_response(update, data)
                    elif response.status == 404:
                        await update.message.reply_text(
                            f"❌ No pude encontrar información del clima para '{city}'.\n"
                            "Por favor, verifica que el nombre de la ciudad sea correcto."
                        )
                    elif response.status == 500:
                        error_data = await response.json()
                        error_msg = error_data.get('message', 'Error interno del servidor')
                        await update.message.reply_text(
                            f"⚠️ Error del servidor: {error_msg}\n"
                            "Por favor, intenta nuevamente en unos momentos."
                        )
                    else:
                        await update.message.reply_text(
                            "❌ Ocurrió un error inesperado. Por favor, intenta nuevamente."
                        )

        except aiohttp.ClientError as e:
            logger.error(f"Error de conexión: {e}")
            await update.message.reply_text(
                "❌ Error de conexión con el servidor.\n"
                "Por favor, intenta nuevamente más tarde."
            )
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            await update.message.reply_text(
                "❌ Ocurrió un error inesperado.\n"
                "Por favor, intenta nuevamente."
            )

    async def send_weather_response(self, update: Update, data: dict) -> None:
        """Enviar respuesta formateada del clima"""
        try:
            city = data.get('city', 'Ciudad desconocida')
            country = data.get('country', '')
            temp = data.get('temperature', 'N/A')
            feels_like = data.get('feels_like', 'N/A')
            description = data.get('description', 'Sin descripción')
            humidity = data.get('humidity', 'N/A')
            pressure = data.get('pressure', 'N/A')
            wind_speed = data.get('wind_speed', 'N/A')

            # Determinar emoji según el clima
            weather_emoji = self.get_weather_emoji(description)

            message = (
                f"{weather_emoji} **Clima en {city}**"
                f"{f', {country}' if country else ''}\n\n"
                f"🌡️ **Temperatura:** {temp}°C\n"
                f"🤗 **Sensación térmica:** {feels_like}°C\n"
                f"📝 **Descripción:** {description.capitalize()}\n"
                f"💧 **Humedad:** {humidity}%\n"
                f"🔽 **Presión:** {pressure} hPa\n"
                f"💨 **Viento:** {wind_speed} m/s\n\n"
                f"📅 *Actualizado ahora*"
            )

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error al formatear respuesta: {e}")
            await update.message.reply_text(
                "✅ Información del clima recibida, pero hubo un error al formatearla."
            )

    def get_weather_emoji(self, description: str) -> str:
        """Obtener emoji apropiado según la descripción del clima"""
        description_lower = description.lower()

        if any(word in description_lower for word in ['sunny', 'clear', 'despejado']):
            return '☀️'
        elif any(word in description_lower for word in ['cloud', 'nublado', 'parcialmente']):
            return '⛅'
        elif any(word in description_lower for word in ['rain', 'lluvia', 'llovizna']):
            return '🌧️'
        elif any(word in description_lower for word in ['storm', 'tormenta']):
            return '⛈️'
        elif any(word in description_lower for word in ['snow', 'nieve']):
            return '❄️'
        elif any(word in description_lower for word in ['fog', 'mist', 'niebla']):
            return '🌫️'
        else:
            return '🌤️'

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Manejar errores globales"""
        logger.error('Exception while handling an update:', exc_info=context.error)

async def main():
    """Función principal"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado")
        return

    # Crear instancia del bot
    bot = TelegramWeatherBot()

    # Crear aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Agregar handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_weather_request))

    # Agregar error handler
    application.add_error_handler(bot.error_handler)

    # Iniciar bot
    logger.info("🤖 Bot de Telegram iniciado...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    asyncio.run(main())