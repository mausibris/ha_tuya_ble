import logging
from typing import Any
from datetime import datetime, timedelta
from homeassistant.util import dt as dt_util
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import device_registry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN, CONF_MAC, CONF_DEVICE_TYPE_KEY, CONF_UUID_KEY, CONF_LOCAL_KEY, SIGNAL_NEW_DP
from .tuya_ble import TuyaBLEDevice, TuyaBLEDataPoint
from .ble_device_factory import tuyaBLEDeviceFactory

_LOGGER = logging.getLogger(__name__)


class TuyaBLEDataCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, entry):
        mac_adr = entry.data.get(CONF_MAC)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{mac_adr}",)
        
        self.hass = hass
        self.entry = entry
        self.mac_adr = mac_adr
        self.device_type = entry.data.get(CONF_DEVICE_TYPE_KEY, "generic")
        self.uuid = entry.data.get(CONF_UUID_KEY)
        self.local_key = entry.data.get(CONF_LOCAL_KEY)
        self.dp_values: dict[int, Any] = {}
        self.discovered_dps: set[int] = set()
        self.device: TuyaBLEDevice | None = None

        # Aktuelle Zustände
        self.last_seen: datetime | None = None
        self.motion_detected: bool|None = None
        self.battery_level: int|None = None
        self.illuminance: int|None = None
        #self.value101: int|None = None
        #self.product_info: TuyaBLEProductInfo

        #_LOGGER.info("Coord initialisiert %s: %s", self.mac_adr, self.local_key)

    async def setupBluetooth(self):

        self.device = await tuyaBLEDeviceFactory.addDevice(self.hass, self.mac_adr, self.device_type, self.uuid, self.local_key)
        #self.product_info = get_device_product_info(self.device) #need a catalog

        self.entry.async_on_unload(
            self.device.register_callback(self._handle_device_update))

        # Hier registrieren wir den Callback für Bluetooth-Pakete
        # HA filtert automatisch Pakete für diese MAC-Adresse
        self.entry.async_on_unload(
            bluetooth.async_register_callback(
                self.hass,
                self._handle_bluetooth_event,
                bluetooth.match.BluetoothCallbackMatcher({bluetooth.match.ADDRESS: self.mac_adr}),
                bluetooth.BluetoothScanningMode.ACTIVE, # "active" scan für Tuya nötig
            )
        )

    async def stopBluetooth(self):
        try:
            if self.device:
                await self.device.stop()
        except Exception:
            _LOGGER.exception("Failed stopping BLE device")
        finally:
            tuyaBLEDeviceFactory.forget_device(self.mac_adr)

    @callback
    def _handle_device_update(self, updates: list[TuyaBLEDataPoint]) -> None:
        #_LOGGER.warning("UPDATE DATAPOINTS: %s --- %s", vars(self.device.datapoints), dir(self.device.datapoints))

        #datapoints = self.device.datapoints._datapoints
        #for dp_id, dp in datapoints.items():
        for dp in updates:
            if dp.id not in self.discovered_dps:
                self.discovered_dps.add(dp.id)
                _LOGGER.info(f"Discovered new datapoint {dp.id} ({type(dp.value)}) on {self.mac_adr}")
                async_dispatcher_send(
                    self.hass,
                    f"{DOMAIN}_{SIGNAL_NEW_DP}_{self.mac_adr}",
                    dp.id)
            self.dp_values[dp.id] = dp.value

        self.last_seen = dt_util.utcnow()
        self.async_update_listeners()

    @callback
    def _handle_bluetooth_event(self,
            service_info: bluetooth.BluetoothServiceInfoBleak,
            change: bluetooth.BluetoothChange) -> None:
        # Wird aufgerufen, wenn ein Bluetooth-Proxy Daten empfängt.
        #_LOGGER.error("Neues Paket von %s: %s", self.mac_adr, service_info)
        if not self.device:
            return

        self.last_seen = dt_util.utcnow()
        self.device.set_ble_device_and_advertisement_data(
            service_info.device, service_info.advertisement)
        self.async_update_listeners()

    def device_info(self) -> DeviceInfo:
        """Erstellt die Verknüpfung zum Gerät."""
        if not self.device:
            return None

        info = DeviceInfo(
            # Die Identifiers müssen über die ganze HA-Instanz eindeutig sein.
            # Die MAC-Adresse ist hier perfekt.
            identifiers={(DOMAIN, self.mac_adr)},
            name="Bewegungsmelder (Tuya BLE)",
            manufacturer="Tuya",
            model=self.device.product_model,
            model_id = self.device.product_id,
            hw_version=self.device.hardware_version,
            sw_version=f"{self.device.device_version} (Protocol {self.device.protocol_version})",
            # Verknüpfe das Gerät direkt mit der Bluetooth-Hardware
            connections={(device_registry.CONNECTION_BLUETOOTH, self.mac_adr)},
        )
        #noch möglich: serial_number configuration_url suggested_area via_device entry_type
        return info

    @property
    def rssi(self) -> int | None:
        return self.device.rssi

    @property
    def available(self) -> bool:
        if not self.device or not self.last_seen:
            return False

        client = getattr(self.device, "_client", None)
        return bool(
            client
            and client.is_connected
            and dt_util.utcnow() - self.last_seen < timedelta(hours=2))
