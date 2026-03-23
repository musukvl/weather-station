#!/usr/bin/env python3
"""
MQTT WS3802 Weather Station Consumer

This script subscribes to Ecowitt MQTT topics and logs weather messages to PostgreSQL.
"""

import os
import signal
import sys
import paho.mqtt.client as mqtt
from loguru import logger
from ws_parser import WeatherStationParser
from postgres_logger import PostgresLogger

# Configuration
# MQTT settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "mqtt_ws3802_logger")
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "ecowitt/#")

# PostgreSQL settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "weather")
DB_USER = os.getenv("DB_USER", "weather_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "weather_password")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configure loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level=LOG_LEVEL,
)


class MQTTWeatherConsumer:
    """Consumes MQTT weather station messages and logs them to PostgreSQL."""

    def __init__(self):
        """Initialize MQTT client, parser, and database logger."""
        # Initialize parser
        self.parser = WeatherStationParser()

        # Initialize database logger
        self.db_logger = PostgresLogger(
            db_host=DB_HOST,
            db_port=DB_PORT,
            db_name=DB_NAME,
            db_user=DB_USER,
            db_password=DB_PASSWORD,
        )

        # Initialize MQTT client
        self.mqtt_client = mqtt.Client(
            client_id=MQTT_CLIENT_ID,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc, properties):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            # Subscribe to Ecowitt topics
            client.subscribe(MQTT_TOPIC_PREFIX)
            logger.info(f"Subscribed to topic: {MQTT_TOPIC_PREFIX}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")

    def on_disconnect(self, client, userdata, flags, rc, properties):
        """Callback when disconnected from MQTT broker."""
        logger.warning(f"Disconnected from MQTT broker, return code: {rc}")
        if rc != 0:
            logger.info("Unexpected disconnection, will attempt to reconnect")

    def on_message(self, client, userdata, msg):
        """Callback when a message is received."""
        try:
            topic = msg.topic
            payload = msg.payload

            logger.debug(f"Received message on topic: {topic}")

            # Parse the message
            parsed_message = self.parser.parse_message(topic, payload)

            if parsed_message is None:
                logger.warning(f"Failed to parse message from topic: {topic}")
                return

            # Log the message to database
            success = self.db_logger.log_message(parsed_message)

            if success:
                logger.info(
                    f"Logged weather message: "
                    f"temp={parsed_message.get('temperature_outside')}, "
                    f"wind={parsed_message.get('wind_speed')}"
                )

        except Exception as error:
            logger.error(f"Error handling message: {error}", exc_info=True)

    def run(self):
        """Start the MQTT consumer."""
        logger.info("Starting MQTT WS3802 Weather Station Consumer")

        # Connect to MQTT broker
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        except Exception as error:
            logger.error(f"Failed to connect to MQTT broker: {error}")
            sys.exit(1)

        # Start the MQTT loop
        self.mqtt_client.loop_forever()

    def stop(self):
        """Stop the MQTT consumer."""
        logger.info("Stopping MQTT WS3802 Weather Station Consumer")
        self.mqtt_client.disconnect()
        self.db_logger.close()


# Signal handlers
consumer = None


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    if consumer:
        consumer.stop()
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and run consumer
    consumer = MQTTWeatherConsumer()
    consumer.run()
