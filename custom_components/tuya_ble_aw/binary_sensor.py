from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_NEW_DP
from .dp_description import DPDescription, KNOWN_SENSOR_DPS
from .generic_sensor import TuyaGenericBinarySensor

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> bool:
    coordinator = entry.runtime_data

    known_entities: set[int] = set()

    @callback
    def async_discover_entity(dp_id: int):
        if dp_id in known_entities:
            return
        known_entities.add(dp_id)

        description: DPDescription | None = None
        if coordinator.device_type == "ldcg/lel5afa4":
            description = KNOWN_SENSOR_DPS.get(dp_id)
            if description.entity_type != "binary_sensor":
                return
        if not description:
            return

        async_add_entities([
            TuyaGenericBinarySensor(entry, description)
        ])

    entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            f"{DOMAIN}_{SIGNAL_NEW_DP}_{coordinator.mac_adr}",
            async_discover_entity,
        )
    )
    return True
