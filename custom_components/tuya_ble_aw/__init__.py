from __future__ import annotations
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from .const import DOMAIN
from .coordinator import TuyaBLEDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    coordinator = TuyaBLEDataCoordinator(hass, entry)
    await coordinator.setupBluetooth()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS)

    if unload_ok:
        coordinator: TuyaBLEDataCoordinator = entry.runtime_data
        await coordinator.stopBluetooth()

    return unload_ok