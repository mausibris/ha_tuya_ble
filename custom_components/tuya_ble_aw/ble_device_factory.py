import asyncio
from bleak_retry_connector import get_device
from homeassistant.components import bluetooth
from homeassistant.exceptions import ConfigEntryNotReady

from .tuya_ble import TuyaBLEDevice, TuyaBLEDeviceCredentials, AbstaractTuyaBLEDeviceManager

class DeviceCredentialsManager(AbstaractTuyaBLEDeviceManager):
    def __init__(self, uuid, local_key):
        self.uuid = uuid
        self.local_key = local_key

    # TODO feste Werte entfernen
    async def get_device_credentials(
            self,
            address: str,
            force_update: bool = False,
            save_data: bool = False) -> TuyaBLEDeviceCredentials:
        result = TuyaBLEDeviceCredentials(
            self.uuid, # uuid. Unbeding nötig!
            self.local_key, # local_key
            "<still unknown>", # device_id, in cloud id, in app: virtual-id.
            "ldcg", # category
            "lel5afa4", # product_id
            "Motion&brightness Sensor", # device_name, in cloud name
            "SBLM04", # product_model, in cloud model
            "<still unknown>") # product_name.
        #_LOGGER.warning(f"get_device_credentials: {result}")
        return result

class TuyaBLEDeviceFactory:
    _instances = {}

    @classmethod
    async def get(cls, hass, mac_adr, uuid, local_key) -> TuyaBLEDevice:
        if mac_adr in cls._instances:
            return cls._instances[mac_adr]

        device = None
        try:
            ble_device = bluetooth.async_ble_device_from_address(
                hass, mac_adr.upper(), True) or await get_device(mac_adr)
            if not ble_device:
                raise ConfigEntryNotReady(
                    f"Could not find Tuya BLE device with address {mac_adr}")

            manager = DeviceCredentialsManager(uuid, local_key)
            device = TuyaBLEDevice(manager, ble_device)
            await device.initialize()

            await asyncio.wait_for(
                device.update(),
                timeout=20,
            )

            cls._instances[mac_adr] = device
            return device
        except Exception:
            if device:
                await device.stop()
            raise

    @classmethod
    def forget_device(cls, mac_adr):
        if mac_adr in cls._instances:
            del cls._instances[mac_adr]