import logging
import voluptuous as vol
from typing import Any
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.components import bluetooth

from .const import DOMAIN, CONF_MAC, CONF_UUID_KEY, CONF_LOCAL_KEY
from .ble_device_factory import TuyaBLEDeviceFactory

_LOGGER = logging.getLogger(__name__)

async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:

    mac_adr = data[CONF_MAC]
    if len(mac_adr) != 17 or mac_adr.count(":") != 5:
        raise InvalidMacAdr

    #uuid?

    local_key = data[CONF_LOCAL_KEY]
    if len(local_key) < 5:
        raise InvalidLocalKey


class TuyaPIRFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Entry point for handling config flow"""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        self._discovery_info = {}
        self._user_input = None
        self._connect_task = None

    # Wird aufgerufen, wenn ein Gerät via Bluetooth entdeckt wird.
    async def async_step_bluetooth(self, discovery_info: bluetooth.BluetoothServiceInfoBleak):

        # Eindeutige ID setzen, um doppelte Entdeckungen zu vermeiden
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        # MAC-Adresse für den nächsten Schritt speichern
        self._discovery_info = {CONF_MAC: discovery_info.address}

        # Den Benutzer direkt zum Formular leiten (async_step_user)
        return await self.async_step_user()

    # Handle the initial step.
    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)

                mac_adr = user_input[CONF_MAC]
                await self.async_set_unique_id(mac_adr)
                self._abort_if_unique_id_configured()

                self._user_input = user_input
                return await self.async_step_finish()
            except InvalidMacAdr:
                errors[CONF_MAC] = "invalid data"
            except InvalidLocalKey:
                errors[CONF_LOCAL_KEY] = "invalid data"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Falls Daten aus der Bluetooth-Entdeckung vorliegen, diese als Standardwert setzen
        suggested_mac_adr = self._discovery_info.get(CONF_MAC, "")
        # This is the schema that used to display the UI to the user.
        # Note the input displayed to the user will be translated. See the
        # translations/<lang>.json file and strings.json. See here for further information:
        # https://developers.home-assistant.io/docs/config_entries_config_flow_handler/#translations
        data_schema = vol.Schema({
            vol.Required(CONF_MAC, default=suggested_mac_adr): str,
            vol.Required(CONF_UUID_KEY): str,
            vol.Required(CONF_LOCAL_KEY): str
        })

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_finish(self, user_input=None):
        mac_adr = self._user_input[CONF_MAC]

        return self.async_create_entry(
            # "Title" is what is displayed to the user for this device
            # It is stored internally in HA as part of the device config.
            title=f"Tuya Sensor ({mac_adr})",
            data=self._user_input)


class InvalidMacAdr(exceptions.HomeAssistantError):
    """Macadresse sollte aus 17 Zeichen bestehen"""
class InvalidLocalKey(exceptions.HomeAssistantError):
    """Local key zu kurz"""