"""Async MQTT subscriber using paho-mqtt."""
import asyncio
import logging
import ssl
from typing import Awaitable, Callable

import paho.mqtt.client as mqtt
from structlog import get_logger

from .config import settings

log = get_logger()


class MQTTSubscriber:
    """Wraps paho-mqtt client into async API."""

    def __init__(
        self,
        settings,
        on_message: Callable[[str, bytes], Awaitable[None]],
    ):
        self.settings = settings
        self.on_message = on_message
        self.client = mqtt.Client(client_id=f"{settings.KAFKA_CLIENT_ID}-mqtt", clean_session=True)
        self._connected = False
        self._loop = asyncio.get_event_loop()

        if settings.MQTT_USERNAME:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        if settings.MQTT_BROKER_TLS:
            self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    async def start(self):
        """Connect and subscribe."""
        log.info("mqtt.connecting", host=self.settings.MQTT_BROKER_HOST, port=self.settings.MQTT_BROKER_PORT)
        self.client.connect(self.settings.MQTT_BROKER_HOST, self.settings.MQTT_BROKER_PORT, self.settings.MQTT_KEEPALIVE)
        self.client.loop_start()

        # Subscribe to topic prefix with wildcard
        topic = f"{self.settings.MQTT_TOPIC_PREFIX}/#"
        self.client.subscribe(topic, qos=self.settings.MQTT_QOS)
        log.info("mqtt.subscribed", topic=topic, qos=self.settings.MQTT_QOS)

    async def stop(self):
        """Cleanly disconnect."""
        self.client.loop_stop()
        self.client.disconnect()
        log.info("mqtt.disconnected")

    def is_connected(self) -> bool:
        return self._connected

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        self._connected = (rc == 0)
        log.info("mqtt.connected", rc=rc)

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self._connected = False
        log.warning("mqtt.disconnected.unexpected", rc=rc)

    def _on_message(self, client, userdata, msg):
        """Forward to async handler."""
        log.debug("mqtt.message", topic=msg.topic, payload_len=len(msg.payload))
        try:
            asyncio.run_coroutine_threadsafe(
                self.on_message(msg.topic, msg.payload), self._loop
            )
        except Exception as e:
            log.error("mqtt.dispatch_failed", error=str(e))
