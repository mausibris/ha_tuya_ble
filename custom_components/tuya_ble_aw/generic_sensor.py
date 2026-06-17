#generic_sensor.py

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from .sensor_base import TuyaBLEBaseEntity
from .dp_description import DPDescription


class TuyaGenericSensor(TuyaBLEBaseEntity, SensorEntity):

    def __init__(self, entry, description: DPDescription):
        super().__init__(entry)

        self.dp_id = description.dp_id
        self.dp_stable_name = description.stable_name
        self._attr_name = description.name
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_native_unit_of_measurement = description.unit
        self._attr_unique_id = f"{self.coordinator.mac_adr}_{self.dp_stable_name}"

    @property
    def native_value(self):
        return self.coordinator.dp_values.get(self.dp_id)

class TuyaGenericBinarySensor(TuyaBLEBaseEntity, BinarySensorEntity):
    def __init__(self, entry, description: DPDescription):
        super().__init__(entry)

        self.dp_id = description.dp_id
        self.dp_stable_name = description.stable_name
        self._attr_name = description.name
        self._attr_device_class = description.device_class
        self._attr_unique_id = f"{self.coordinator.mac_adr}_{self.dp_stable_name}"
        self._invert = description.invert

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.dp_values.get(self.dp_id)
        if value is None:
            return None

        return not value if self._invert else bool(value)
