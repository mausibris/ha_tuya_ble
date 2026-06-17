import logging
from bleak_retry_connector import get_device
from homeassistant.components import bluetooth
from homeassistant.exceptions import ConfigEntryNotReady

from .tuya_ble import TuyaBLEDevice, TuyaBLEDeviceCredentials, AbstaractTuyaBLEDeviceManager

_LOGGER = logging.getLogger(__name__)

class TuyaBLEDeviceFactory(AbstaractTuyaBLEDeviceManager):
    

    def __init__(self):
        super().__init__()
        self._instances = {}
        self._credentials = {}

    
    async def addDevice(self, hass, mac_adr, device_type, uuid, local_key) -> TuyaBLEDevice:
        if mac_adr in self._instances:
            return self._instances[mac_adr]

        device = None
        try:
            if device_type == "ldcg/lel5afa4":
                self._credentials[mac_adr] = TuyaBLEDeviceCredentials(
                    uuid, # uuid. Unbeding nötig!
                    local_key, # local_key
                    "<still unknown>", # device_id, in cloud id, in app: virtual-id.
                    "ldcg", # category
                    "lel5afa4", # product_id
                    "Motion&brightness Sensor", # device_name, in cloud name
                    "SBLM04", # product_model, in cloud model
                    "<still unknown>") # product_name.
            else: #"generic":
                self._credentials[mac_adr] = TuyaBLEDeviceCredentials(
                    uuid, # uuid. Unbeding nötig!
                    local_key, # local_key
                    "<still unknown>", # device_id, in cloud id, in app: virtual-id.
                    "<category unknown>", # category
                    "<pr_id unknown>", # product_id
                    "Generic Sensor", # device_name, in cloud name
                    "<product_model unknown>", # product_model, in cloud model
                    "<product_name unknown>") # product_name.

            ble_device = bluetooth.async_ble_device_from_address(
                hass, mac_adr.upper(), True) or await get_device(mac_adr)
            if not ble_device:
                raise ConfigEntryNotReady(
                    f"Could not find Tuya BLE device with address {mac_adr}")

            device = TuyaBLEDevice(self, ble_device)
            await device.initialize()

            self._instances[mac_adr] = device
            return device
        except Exception:
            if device:
                await device.stop()
            raise

    def forget_device(self, mac_adr):
        if mac_adr in self._instances:
            del self._instances[mac_adr]
            del self._credentials[mac_adr]

    async def get_device_credentials(
            self,
            address: str,
            force_update: bool = False,
            save_data: bool = False) -> TuyaBLEDeviceCredentials:

        if address in self._credentials:
            return self._credentials[address]

        return None


tuyaBLEDeviceFactory = TuyaBLEDeviceFactory()