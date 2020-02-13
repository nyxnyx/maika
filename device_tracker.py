import logging

_LOGGER = logging.getLogger(__name__)
from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.util import slugify
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import HomeAssistantType
from . import DOMAIN, SIGNAL_STATE_UPDATED


async def async_setup_scanner(hass, config, async_see, discovery_info=None):

    data = hass.data[DOMAIN]
    tracker = AIKADeviceTracker(hass, data, async_see)
    await tracker.async_update()
    _LOGGER.info("Setup of AIKA device tracker")
    async_dispatcher_connect(hass, SIGNAL_STATE_UPDATED, tracker.async_update)

    return True

class AIKADeviceTracker(TrackerEntity):
    """AIKA Connected Drive device tracker."""

    def __init__(self, hass, data, async_see):
        """Initialize the Tracker."""
        self.hass = hass
        self.data = data
        self.async_see = async_see
        self.status = None
        self._latitude = None
        self._longitude = None
        self._attributes = {
            "trackr_id": None,
            "heading": None,
            "speed": None
        }

    async def async_update(self):
        """Update the device info.
        Only update the state in home assistant if tracking in
        the car is enabled.
        """
        self.status = self.data.status
        self._latitude = float(self.status["maika.lat"])
        self._longitude = float(self.status["maika.lng"])
        self._attributes = {
            "trackr_id": self.status["maika.sn"],
            "heading": self.get_heading(int(self.status["maika.course"])),
            "speed": self.status["maika.speed"]
        }
        await self.async_see(
            dev_id = "maika_{}".format(self.status["maika.iccid"]),
            mac = self.status["maika.iccid"],
            host_name = self.status["maika.devicename"],
            gps = (self._latitude, self._longitude),
            attributes = self._attributes,
            icon="mdi:car"
        )

    def get_heading(self, course: int):
        if course > 349 or course < 10: return "N"
        if course > 9 and course < 80: return "NE"
        if course > 79 and course < 100: return "E"
        if course > 99 and course < 170: return "SE"
        if course > 169 and course < 190: return "S"
        if course > 189 and course < 260: return "SW"
        if course > 259 and course < 280: return "W"
        if course > 279 and course < 350: return "NW"
    
    @property
    def dev_id(self):
        return "maika_{}".format(slugify(self.status["maika.iccid"]))

    @property
    def source_type(self):
        return SOURCE_TYPE_GPS

    @property
    def location_accuracy(self):
        return 4 # default for GPS

    @property
    def latitude(self) -> float:
        """Return latitude value of the device."""
        return self._latitude

    @property
    def longitude(self) -> float:
        """Return longitude value of the device."""
        return self._longitude

    def force_update(self):
        return True