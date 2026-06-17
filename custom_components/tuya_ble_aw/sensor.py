from datetime import datetime
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_NEW_DP
from .sensor_base import TuyaBLEBaseEntity
from .dp_description import DPDescription, KNOWN_SENSOR_DPS
from .generic_sensor import TuyaGenericSensor

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> bool:
    coordinator = entry.runtime_data

    # immer vorhandene Sensor hinzufügen
    async_add_entities([
        TuyaRSSISensor(entry),
        TuyaLastSeenSensor(entry),
    ])

    known_entities: set[int] = set()

    @callback
    def async_discover_entity(dp_id: int):
        if dp_id in known_entities:
            return
        known_entities.add(dp_id)

        description: DPDescription | None = None
        if coordinator.device_type == "ldcg/lel5afa4":
            description = KNOWN_SENSOR_DPS.get(dp_id)
            if description.entity_type != "sensor":
                return
        if not description:
            description = DPDescription(
                dp_id=dp_id,
                entity_type="sensor",
                name=f"Datapoint {dp_id}",
                stable_name=f"dp_{dp_id}",
            )

        async_add_entities([
            TuyaGenericSensor(entry, description)
        ])

    entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            f"{DOMAIN}_{SIGNAL_NEW_DP}_{coordinator.mac_adr}",
            async_discover_entity,
        )
    )
    return True

class TuyaRSSISensor(TuyaBLEBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = "dBm"
    _attr_name = "Signalstärke"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{self.coordinator.mac_adr}_rssi"

    @property
    def native_value(self):
        return self.coordinator.rssi

class TuyaLastSeenSensor(TuyaBLEBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_name = "Zuletzt gesehen"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{self.coordinator.mac_adr}_last_seen"

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_seen
