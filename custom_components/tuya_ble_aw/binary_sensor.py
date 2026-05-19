from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from .sensor_base import TuyaBLEBaseEntity

async def async_setup_entry(hass, entry, async_add_entities) -> bool:
    async_add_entities([TuyaPIRSensor(entry)])
    return True

class TuyaPIRSensor(TuyaBLEBaseEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.MOTION
    _attr_name = "Bewegung"

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.motion_detected
