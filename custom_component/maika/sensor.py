"""
Provides a sensor to track AIKA API information
"""
import logging

from . import (DOMAIN, SIGNAL_STATE_UPDATED)

from homeassistant.const import ATTR_STATE
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_utc_time_change
from homeassistant.helpers.dispatcher import async_dispatcher_connect

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, add_entities, discovery_info=None):

    data = hass.data[DOMAIN]

    if data._status is None:
        _LOGGER.error("No data received from AIKA, unable to setup")
        raise PlatformNotReady

    _LOGGER.debug('AIKA sensors available: %s', data._status)

    entities = []

    for resource in data.SENSOR_TYPES:
        sensor_type = resource.lower()
        if sensor_type in data._status:
            entities.append(AikaSensor(data, sensor_type, hass))
            _LOGGER.debug("Added sensor_type %s" % sensor_type)
        else:
            _LOGGER.warning(
                "Sensor type: %s does not appear in AIKA status "
                "output, cannot add", sensor_type)
    add_entities(entities, True)


class AikaSensor(Entity):
    """Representation of a sensor entity for AIKA status values."""

    def __init__(self, data, sensor_type, hass):
        """Initialize the sensor."""
        self._data = data
        self.type = sensor_type
        self._name = self._data.SENSOR_TYPES[sensor_type][0]
        self.entity_id= "sensor.{}".format(sensor_type.replace('.','_'))
        self._unit = self._data.SENSOR_TYPES[sensor_type][1]
        self._state = None
        self.hass = hass

    async def async_added_to_hass(self):
        """Register update dispatcher."""
        async_dispatcher_connect(
            self.hass, SIGNAL_STATE_UPDATED, self.async_schedule_update_ha_state
        )

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the sensor attributes."""
        attr = dict()
        attr[ATTR_STATE] = self.display_state()
        return attr
    
    @property
    def name(self):
        return self._name
    
    @property
    def icon(self):
        return self._data.SENSOR_TYPES[self.type][2]

    @property
    def state(self):
        return self._state

    def display_state(self):
        """Return display state."""
        if self._data._status is None:
            return 'OFF'
        else:
            return 'ON'

    async def async_update(self):
        """Get the latest status and use it to update our sensor state."""
        _LOGGER.debug("Update state %s" % self._name)
        
        if self.type not in self._data.status:
            self._state = None
        else:
            self._state = self._data.status[self.type]

    def force_update(self):
        return True
