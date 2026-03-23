#!/usr/bin/env python3
"""
Ecowitt WS3802 Weather Station Parser

Parses MQTT messages from the Ecowitt weather station.
The WS3802 publishes raw HTTP POST requests over MQTT with URL-encoded form data.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, unquote_plus
from loguru import logger


class WeatherStationParser:
    """Parses Ecowitt WS3802 MQTT weather messages."""

    def parse_message(self, topic: str, payload: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse a weather station MQTT message.

        The Ecowitt station publishes raw HTTP POST requests over MQTT:
        HTTP headers followed by a blank line and URL-encoded form body.

        Args:
            topic: MQTT topic the message was received on
            payload: Raw MQTT message payload

        Returns:
            Parsed message dict or None if parsing fails
        """
        try:
            payload_str = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            logger.warning(f"Failed to decode payload from topic {topic}: {error}")
            return None

        data = self._parse_ecowitt_payload(payload_str)
        if data is None:
            logger.warning(f"Failed to parse Ecowitt payload from topic {topic}")
            return None

        # Extract timestamp or use current time
        message_datetime = self._extract_datetime(data)

        # Extract temperature outside
        temperature_outside = self._extract_temperature_outside(data)

        # Extract wind speed
        wind_speed = self._extract_wind_speed(data)

        return {
            "datetime": message_datetime,
            "temperature_outside": temperature_outside,
            "wind_speed": wind_speed,
            "data": data,
        }

    def _parse_ecowitt_payload(self, payload_str: str) -> Optional[Dict[str, str]]:
        """
        Parse raw Ecowitt HTTP POST payload into a dict.

        The payload contains HTTP headers followed by a blank line and
        URL-encoded form body (key=value&key=value).

        Args:
            payload_str: Raw payload string

        Returns:
            Dict of field name to value, or None if parsing fails
        """
        # Split headers from body on blank line
        parts = payload_str.split("\n\n", 1)
        if len(parts) == 2:
            body = parts[1].strip()
        else:
            # No headers found, try treating entire payload as form body
            body = payload_str.strip()

        if not body:
            return None

        try:
            parsed = parse_qs(body, keep_blank_values=True)
            # parse_qs returns lists; flatten to single values
            return {key: values[0] for key, values in parsed.items()}
        except Exception as error:
            logger.warning(f"Failed to parse URL-encoded body: {error}")
            return None

    def _extract_datetime(self, data: Dict[str, Any]) -> datetime:
        """Extract datetime from message data, fallback to current UTC time."""
        # Try common Ecowitt timestamp fields
        for field in ("dateutc", "date", "timestamp"):
            value = data.get(field)
            if value is None:
                continue

            # Integer epoch timestamp
            if isinstance(value, (int, float)):
                try:
                    return datetime.fromtimestamp(value, tz=timezone.utc)
                except (ValueError, OSError):
                    continue

            # String timestamp
            if isinstance(value, str):
                for fmt in (
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%SZ",
                ):
                    try:
                        parsed = datetime.strptime(value, fmt)
                        return parsed.replace(tzinfo=timezone.utc)
                    except ValueError:
                        continue

        logger.debug("No timestamp found in message, using current UTC time")
        return datetime.now(tz=timezone.utc)

    def _extract_temperature_outside(self, data: Dict[str, Any]) -> Optional[float]:
        """Extract outside temperature from message data."""
        # Try common Ecowitt temperature field names
        for field in ("tempf", "temp_outside", "outdoor_temperature", "tempoutf"):
            value = data.get(field)
            if value is not None:
                try:
                    temp_f = float(value)
                    # Convert Fahrenheit to Celsius
                    return round((temp_f - 32) * 5 / 9, 2)
                except (ValueError, TypeError):
                    continue

        # Try Celsius fields directly
        for field in ("tempc", "temp_outside_c", "outdoor_temperature_c"):
            value = data.get(field)
            if value is not None:
                try:
                    return round(float(value), 2)
                except (ValueError, TypeError):
                    continue

        logger.debug("No outside temperature found in message")
        return None

    def _extract_wind_speed(self, data: Dict[str, Any]) -> Optional[float]:
        """Extract wind speed from message data."""
        # Try common Ecowitt wind speed field names (mph)
        for field in ("windspeedmph", "wind_speed", "windSpeed"):
            value = data.get(field)
            if value is not None:
                try:
                    speed_mph = float(value)
                    # Convert mph to m/s
                    return round(speed_mph * 0.44704, 2)
                except (ValueError, TypeError):
                    continue

        # Try m/s fields directly
        for field in ("windspeed_ms", "wind_speed_ms"):
            value = data.get(field)
            if value is not None:
                try:
                    return round(float(value), 2)
                except (ValueError, TypeError):
                    continue

        logger.debug("No wind speed found in message")
        return None
