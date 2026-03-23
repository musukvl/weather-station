#!/usr/bin/env python3
"""
PostgreSQL Logger

This module handles logging of weather station messages to PostgreSQL database.
"""

import psycopg2
from psycopg2.extras import Json
from typing import Dict, Any
from loguru import logger
import time


class PostgresLogger:
    """Handles PostgreSQL database operations for weather station messages."""

    def __init__(
        self,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
    ):
        """
        Initialize PostgreSQL logger.

        Args:
            db_host: Database host
            db_port: Database port
            db_name: Database name
            db_user: Database user
            db_password: Database password
        """
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.connection = None
        self._connect()

    def _connect(self):
        """Establish database connection with retry logic."""
        max_retries = 5
        retry_delay = 2

        for attempt in range(1, max_retries + 1):
            try:
                self.connection = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    database=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    connect_timeout=10,
                )
                logger.info(f"Connected to PostgreSQL database: {self.db_name}")

                # Validate connection
                cursor = self.connection.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                logger.info(f"PostgreSQL version: {version[0]}")
                cursor.close()

                return
            except psycopg2.OperationalError as error:
                if attempt < max_retries:
                    logger.warning(
                        f"Failed to connect to database (attempt {attempt}/{max_retries}): {error}. "
                        f"Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(
                        f"Failed to connect to database after {max_retries} attempts: {error}"
                    )
                    raise
            except Exception as error:
                logger.error(f"Unexpected error connecting to database: {error}")
                raise

    def _ensure_connection(self):
        """Ensure database connection is active."""
        try:
            if self.connection is None or self.connection.closed:
                self._connect()
            else:
                # Test connection
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
        except Exception as error:
            logger.warning(f"Connection lost, reconnecting: {error}")
            self._connect()

    def log_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Log a weather station message to the database.

        Args:
            message_data: Parsed message data containing datetime, temperature_outside,
                         wind_speed, and data fields

        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_connection()

            cursor = self.connection.cursor()

            query = """
                INSERT INTO weather_messages
                (datetime, temperature_outside, wind_speed, data)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    message_data.get("datetime"),
                    message_data.get("temperature_outside"),
                    message_data.get("wind_speed"),
                    Json(message_data.get("data", {})),
                ),
            )

            self.connection.commit()
            cursor.close()

            logger.debug("Logged weather message to database")
            return True

        except Exception as error:
            logger.error(f"Failed to log message: {error}")
            if self.connection:
                self.connection.rollback()
            return False

    def close(self):
        """Close database connection."""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("Database connection closed")
