from datetime import datetime
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import EntityCategory
from .sensor_base import TuyaBLEBaseEntity

async def async_setup_entry(hass, entry, async_add_entities) -> bool:
    async_add_entities([
        TuyaBatterySensor(entry), TuyaIlluminanceSensor(entry),
        TuyaRSSISensor(entry), TuyaLastSeenSensor(entry),
    ])
    return True

class TuyaRSSISensor(TuyaBLEBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = "dBm"
    _attr_name = "Signalstärke"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    @property
    def native_value(self):
        return self.coordinator.rssi

class TuyaBatterySensor(TuyaBLEBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_name = "Batterie" # (DP4)

    @property
    def native_value(self):
        return self.coordinator.battery_level

class TuyaIlluminanceSensor(TuyaBLEBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ILLUMINANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "lx"
    _attr_name = "Helligkeit" # (DP2)

    @property
    def native_value(self):
        return self.coordinator.illuminance

class TuyaLastSeenSensor(TuyaBLEBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_name = "Zuletzt gesehen"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_seen
