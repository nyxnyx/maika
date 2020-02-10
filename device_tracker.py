import logging

_LOGGER = logging.getLogger(__name__)
from homeassistant.util import slugify
from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.helpers.event import track_utc_time_change

from . import DOMAIN


async def async_setup_scanner(hass, config, async_see, discovery_info=None):

    data = hass.data[DOMAIN]
    tracker = AIKADeviceTracker(async_see, data)
    _LOGGER.info("AIKA device_tracker set-up")
    await tracker.async_setup(hass)
    _LOGGER.info("AIKA device_tracker setup done.")
    return True

class AIKADeviceTracker():
    """AIKA Connected Drive device tracker."""

    def __init__(self, async_see, data):
        """Initialize the Tracker."""
        self._see = async_see
        self._data = data

    async def async_setup(self, hass):
        """Set up a timer and start gathering devices."""
        
        track_utc_time_change(
            hass, lambda now: self.async_update(), second=range(0, 60, 30)
        )

    async def async_update(self) -> None:
        """Update the device info.
        Only update the state in home assistant if tracking in
        the car is enabled.
        """
        await self._data.async_update()
        dev_id = slugify(self._data.status['maika.id'])

        _LOGGER.info("Updating device_tracker: %s", dev_id)
        attrs = {"id": self._data.status['maika.id']}
        await self._see(
            dev_id=dev_id,
            host_name=self._data.status['maika.model'],
            source_type=SOURCE_TYPE_GPS,
            gps=self._data.gps_position,
            attributes=attrs,
            icon="mdi:car",
        )
