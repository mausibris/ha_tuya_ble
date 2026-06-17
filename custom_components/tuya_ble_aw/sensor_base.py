import logging
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import TuyaBLEDataCoordinator

_LOGGER = logging.getLogger(__name__)

class TuyaBLEBaseEntity(CoordinatorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry):
        coordinator = entry.runtime_data
        super().__init__(coordinator)


    # To link this entity to the device, this property must return an
    # identifiers value matching that used in the ??, but no other information such
    # as name. If name is returned, this entity will then also become a device in the
    # HA UI.
    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info()
