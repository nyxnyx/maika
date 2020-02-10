import logging

_LOGGER = logging.getLogger(__name__)
from homeassistant.util import slugify
from homeassistant.helpers.event import track_utc_time_change

from . import DOMAIN


def setup_scanner(hass, config, see, discovery_info=None):

    data = hass.data[DOMAIN]
    tracker = AIKADeviceTracker(see, data)
    _LOGGER.info("AIKA device_tracker set-up")
    tracker.setup(hass)
    _LOGGER.info("AIKA device_tracker setup done.")
    return True

class AIKADeviceTracker():
    """AIKA Connected Drive device tracker."""

    def __init__(self, see, data):
        """Initialize the Tracker."""
        self._see = see
        self._data = data

    def setup(self, hass):
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
        dev_id = slugify(self._data.status['maika.model'])

        _LOGGER.info("Updating device_tracker: %s", dev_id)
        attrs = {"id": self._data.status['maika.id']}
        self._see(
            dev_id=dev_id,
            host_name=self._data.status['maika.model'],
            gps=self._data.gps_position,
            attributes=attrs,
            icon="mdi:car",
        )
