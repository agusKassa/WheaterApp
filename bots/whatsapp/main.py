#!/usr/bin/env python3

import os
import asyncio
import aiohttp
import logging
import json
from whatsapp_api_client_python import API

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variables de entorno
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.tudominio.com')  # Tu API
API_ENDPOINT = os.getenv('API_WHATSAPP_ENDPOINT', '/api/weather/whatsapp')
GREEN_API_INSTANCE_ID = os.getenv('GREEN_API_INSTANCE_ID')
GREEN_API_TOKEN = os.getenv('GREEN_API_TOKEN')

class WhatsAppWeatherBot:
    def __init__(self):
        self.api_url = f"{API_BASE_URL}{API_ENDPOINT}"
        self.greenapi = None
        logger.info(f"Bot configurado para usar: {self.api_url}")

    async def initialize_api(self):
        """Inicializar conexión con WhatsApp mediante Green API"""
        try:
            if not GREEN_API_INSTANCE_ID or not GREEN_API_TOKEN:
                logger.error("GREEN_API_INSTANCE_ID y GREEN_API_TOKEN deben estar configurados")
                return False

            logger.info("Inicializando conexión con Green API...")

            # Inicializar Green API
            self.greenapi = API.GreenApi(GREEN_API_INSTANCE_ID, GREEN_API_TOKEN)

            # Verificar estado de la cuenta
            result = self.greenapi.account.getStateInstance()
            logger.info(f"Estado de la instancia: {result.data}")

            if result.data.get('stateInstance') == 'authorized':
                logger.info("✅ Conexión con WhatsApp establecida y autorizada")
                return True
            else:
                logger.warning("⚠️ Instancia no autorizada. Necesitas escanear el código QR")
                return False

        except Exception as e:
            logger.error(f"❌ Error al inicializar Green API: {e}")
            return False

    async def process_weather_request(self, chat_id: str, phone_number: str, city: str):
        """Procesar solicitud de clima enviándola a TU API"""
        try:
            # Preparar datos para TU API
            payload = {
                'city': city.strip(),
                'user_id': phone_number,
                'username': phone_number,
                'platform': 'whatsapp',
                'phone_number': phone_number,
                'chat_id': chat_id
            }

            logger.info(f"Enviando solicitud a tu API: {self.api_url}")
            logger.info(f"Datos: {payload}")

            # Hacer petición a TU API de Symfony (no directamente a OpenWeather)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:

                    logger.info(f"Respuesta de tu API: Status {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        await self.send_weather_response(chat_id, data)

                    elif response.status == 404:
                        await self.send_message(
                            chat_id,
                            f"❌ No pude encontrar información del clima para '{city}'.\n\n"
                            "Por favor, verifica que el nombre de la ciudad sea correcto.\n\n"
                            "Ejemplo: *Buenos Aires* o *Madrid*"
                        )

                    elif response.status == 500:
                        error_data = await response.json()
                        error_msg = error_data.get('message', 'Error interno del servidor')
                        await self.send_message(
                            chat_id,
                            f"⚠️ *Error del servidor:* {error_msg}\n\n"
                            "Por favor, intenta nuevamente en unos momentos."
                        )

                    else:
                        await self.send_message(
                            chat_id,
                            "❌ Ocurrió un error inesperado.\n\n"
                            "Por favor, intenta nuevamente."
                        )

        except asyncio.TimeoutError:
            logger.error("Timeout al conectar con tu API")
            await self.send_message(
                chat_id,
                "⏰ *Timeout* - La consulta tardó demasiado.\n\n"
                "Por favor, intenta nuevamente."
            )

        except aiohttp.ClientError as e:
            logger.error(f"Error de conexión con tu API: {e}")
            await self.send_message(
                chat_id,
                "❌ *Error de conexión* con el servidor de clima.\n\n"
                "Por favor, verifica tu conexión e intenta nuevamente."
            )

        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            await self.send_message(
                chat_id,
                "❌ Ocurrió un error inesperado.\n\n"
                "Por favor, intenta nuevamente."
            )

    async def send_weather_response(self, chat_id: str, data: dict):
        """Enviar respuesta formateada del clima basada en la respuesta de TU API"""
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
                f"{weather_emoji} *Clima en {city}*"
                f"{f', {country}' if country else ''}\n\n"
                f"🌡️ *Temperatura:* {temp}°C\n"
                f"🤗 *Sensación térmica:* {feels_like}°C\n"
                f"📝 *Descripción:* {description.capitalize()}\n"
                f"💧 *Humedad:* {humidity}%\n"
                f"🔽 *Presión:* {pressure} hPa\n"
                f"💨 *Viento:* {wind_speed} m/s\n\n"
                f"📅 _Actualizado ahora_\n\n"
                f"💡 Envía el nombre de otra ciudad para más información"
            )

            await self.send_message(chat_id, message)

        except Exception as e:
            logger.error(f"Error al formatear respuesta: {e}")
            await self.send_message(
                chat_id,
                "✅ Información del clima recibida, pero hubo un error al formatearla."
            )

    async def send_help_message(self, chat_id: str):
        """Enviar mensaje de ayuda"""
        help_text = (
            "🌤️ *Bot del Clima - Ayuda*\n\n"
            "¡Hola! Soy tu asistente del clima 🤖\n\n"
            "📍 *¿Cómo usarme?*\n"
            "Simplemente escribe el nombre de una ciudad:\n\n"
            "✅ *Ejemplos:*\n"
            "• Buenos Aires\n"
            "• Madrid\n"
            "• New York\n"
            "• London\n\n"
            "📊 *Información incluida:*\n"
            "• Temperatura actual\n"
            "• Sensación térmica\n"
            "• Descripción del clima\n"
            "• Humedad\n"
            "• Presión atmosférica\n"
            "• Velocidad del viento\n\n"
            "💬 *Comandos:*\n"
            "• help, ayuda o menu - Mostrar esta ayuda\n\n"
            "🚀 ¡Envía el nombre de una ciudad para comenzar!"
        )
        await self.send_message(chat_id, help_text)

    def get_weather_emoji(self, description: str) -> str:
        """Obtener emoji apropiado según la descripción del clima"""
        description_lower = description.lower()

        if any(word in description_lower for word in ['sunny', 'clear', 'despejado', 'soleado']):
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

    async def send_message(self, chat_id: str, message: str):
        """Enviar mensaje a WhatsApp usando Green API"""
        try:
            if not self.greenapi:
                logger.error("Green API no está inicializada")
                return False

            response = self.greenapi.sending.sendMessage(chat_id, message)
            logger.info(f"Mensaje enviado a {chat_id}: {response.data}")
            return True

        except Exception as e:
            logger.error(f"Error al enviar mensaje: {e}")
            return False

    async def process_notification(self, notification):
        """Procesar notificación recibida de WhatsApp"""
        try:
            if not notification or 'body' not in notification:
                return

            body = notification['body']

            # Solo procesar mensajes de texto entrantes
            if body.get('typeWebhook') != 'incomingMessageReceived':
                return

            message_data = body.get('messageData', {})
            sender_data = body.get('senderData', {})

            # Extraer información del mensaje
            sender = sender_data.get('sender', '')
            chat_id = sender_data.get('chatId', '')
            message_type = message_data.get('typeMessage', '')

            # Solo procesar mensajes de texto
            if message_type != 'textMessage':
                return

            message_text = message_data.get('textMessageData', {}).get('textMessage', '')

            # Limpiar número de teléfono
            phone_number = sender.replace('@c.us', '') if '@c.us' in sender else sender

            logger.info(f"Mensaje recibido de {phone_number}: {message_text}")

            # Procesar mensaje
            if message_text and not message_text.startswith('/'):
                await self.process_weather_request(chat_id, phone_number, message_text)
            elif message_text.lower() in ['/start', '/help', 'help', 'ayuda', 'menu']:
                await self.send_help_message(chat_id)

        except Exception as e:
            logger.error(f"Error al procesar notificación: {e}")

    async def start_polling(self):
        """Iniciar polling para recibir mensajes de WhatsApp"""
        logger.info("🔄 Iniciando polling de WhatsApp...")

        while True:
            try:
                # Recibir notificaciones
                response = self.greenapi.receiving.receiveNotification()

                if response and hasattr(response, 'data') and response.data:
                    await self.process_notification(response.data)

                    # Eliminar notificación procesada
                    receipt_id = response.data.get('receiptId')
                    if receipt_id:
                        self.greenapi.receiving.deleteNotification(receipt_id)

                await asyncio.sleep(2)  # Esperar 2 segundos entre checks

            except Exception as e:
                logger.error(f"Error en polling: {e}")
                await asyncio.sleep(10)  # Esperar más tiempo si hay error

async def main():
    """Función principal"""
    logger.info("🚀 Iniciando Bot de WhatsApp...")

    bot = WhatsAppWeatherBot()

    # Inicializar API
    if await bot.initialize_api():
        logger.info("Bot de WhatsApp iniciado correctamente")

        # Iniciar polling
        await bot.start_polling()
    else:
        logger.error("❌ No se pudo inicializar el bot de WhatsApp")

if __name__ == '__main__':
    asyncio.run(main())