# dp_description.py

from dataclasses import dataclass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.entity import EntityCategory


@dataclass(frozen=True)
class DPDescription:
    dp_id: int
    entity_type: str
    name: str
    stable_name: str
    device_class: SensorDeviceClass | BinarySensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    unit: str | None = None
    entity_category: EntityCategory | None = None
    invert: bool | None = None

#Das ist nur für SBLM04. Unklar ist, ob andere Geräte die gleichen DP-IDs haben.
KNOWN_SENSOR_DPS: dict[int, DPDescription] = {
    2: DPDescription(
        dp_id=2,
        entity_type="sensor",
        name="Helligkeit",
        stable_name="illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        state_class=SensorStateClass.MEASUREMENT,
        unit="lx",
    ),
    4: DPDescription(
        dp_id=4,
        entity_type="sensor",
        name="Batterie",
        stable_name="battery",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        unit="%",
    ),
    101: DPDescription(
        dp_id=101,
        entity_type="binary_sensor",
        name="Bewegung",
        stable_name="motion",
        device_class=BinarySensorDeviceClass.MOTION,
        invert=True,
    ),
}