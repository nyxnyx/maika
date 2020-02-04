import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import asyncio
from datetime import datetime
from datetime import timedelta
from homeassistant.helpers import discovery
from openapiv3 import api, location, device_status
from homeassistant.util import Throttle


from homeassistant.const import (
    CONF_NAME, CONF_USERNAME, CONF_PASSWORD, CONF_ADDRESS,
    CONF_SCAN_INTERVAL, CONF_RESOURCES, CONF_ALIAS, ATTR_STATE, STATE_UNKNOWN)

_LOGGER = logging.getLogger(__name__)

DOMAIN="aika"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
            vol.Required(CONF_USERNAME): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
            vol.Required(CONF_ADDRESS): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_UPDATE_STATE = "update_state"

# Those components will be dicovered automatically based on ocnfiguration
AIKA_COMPONENTS = ["sensor", "device_tracker"]

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

async def async_setup(hass, base_config: dict):
    
    config = base_config.get(DOMAIN)
    
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    server = config.get(CONF_ADDRESS)
    hass.data[DOMAIN] = AikaData(username, password, server)
    
    def _update(call) -> None:
        _LOGGER.info("Update service called")
        asyncio.run_coroutine_threadsafe(hass.data[DOMAIN].update(), hass.loop)
    
    hass.services.register(DOMAIN, SERVICE_UPDATE_STATE, _update)

    for component in AIKA_COMPONENTS:
        discovery.load_platform(hass, component, DOMAIN, {}, config)

    _LOGGER.info("Done initialization")
    return True


class AikaData(object):
    """Stores the data retrieved from AIKA.
    For each entity to use, acts as the single point responsible for fetching
    updates from the server.
    """

    async def __init__(self, username, password, server):
        """Initialize the data object."""
        self._username = username
        self._password = password
        self._server = server
        self.api = api.API(server)
        self.a.registerUpdater(location.Location, device_status.DeviceStatus)
        self.gps_position = None
        self._status = None
        self.a = api.API(server)
        self.SENSOR_TYPES = {
            'aika.battery'      : ['Battery', '%', 'mdi:battery'],
            'aika.batteryStatus': ['Battery Status', '', None],
            'aika.course'       : ['Course', '', None],
            'aika.dataContext'  : ['Data Context', None, None],
            'aika.deviceID'     : ['Device ID', None, None],
            'aika.deviceName'   : ['Device Name', None, None],
            'aika.ICCID'        : ['ICCID', None, None],
            'aika.icon'         : ['Icon', None, None],
            'aika.id'           : ['ID', None, None],
            'aika.isGPS'        : ['Is GPS?', None, None],
            'aika.isStop'       : ['Is Stop?', None, None],
            #'aika.key2018'     : ['', None, None],
            'aika.lat'          : ['Latitude', None, None],
            'aika.lng'          : ['Longtitude', None, None],
            'aika.model'        : ['Model', None, None],
            #'aika.new201710'   : ['', None, None],
            'aika.ofl'          : ['Ofl', None, None],
            'aika.olat'         : ['Old latitude', None, None],
            'aika.olng'         : ['Old longtitude', None, None],
            'aika.positionTime' : ['Position time', None, None],
            'aika.serialNumber' : ['Serial Number', None, None],
            'aika.sendCommand'  : ['Send Command', None, None],
            'aika.speed'        : ['Speed', None, None],
            'aika.sn'           : ['SN', None, None],
            'aika.state'        : ['State', None, None],
            'aika.status'       : ['Status', None, None],
            'aika.statusX20'    : ['Status X20', None, None],
            'aika.stm'          : ['STM', None, None],
            'aika.timeZone'     : ['Time Zone', None, None],
            'aika.VIN'          : ['VIN', None, None],
            'aika.voice'        : ['Has Voice?', None, None],
            'aika.warn'         : ['Warning', None, None],
            'aika.warnStr'      : ['Warning string', None, None],
            'aika.warnTime'     : ['Warning time', None, None],
            'aika.warnTxt'      : ['Warning text', None, None],
            'aika.work'         : ['Work', None, None],
            'aika.xg'           : ['Xg', None, None],
            'aika.yinshen'      : ['yinshen', None, None],
        }

    # Retrieves info from Aika
    async def _get_status(self):
        if not hasattr(self.a, 'key2018'):
            await self.a.doLogin(self._username, self._password)

        try:
            await self.a.doUpdate()

            v={}
            v['aika.battery']       = a.__getattribute__('battery')
            v['aika.batteryStatus'] = a.__getattribute__('batteryStatus')
            v['aika.course']        = a.__getattribute__('course')
            v['aika.dataContext'    = a.__getattribute__('dataContext')
            v['aika.deviceID'       = a.__getattribute__('deviceID')
            v['aika.deviceName'     = a.__getattribute__('deviceName')
            v['aika.ICCID'          = a.__getattribute__('ICCID')
            v['aika.icon'           = a.__getattribute__('icon')
            v['aika.id'             = a.__getattribute__('id')
            v['aika.isGPS'          = a.__getattribute__('isGPS')
            v['aika.isStop'         = a.__getattribute__('isStop')
            v[#'aika.key2018        = a.__getattribute__('key2018')
            v['aika.lat'            = a.__getattribute__('lat')
            v['aika.lng'            = a.__getattribute__('lng')
            v['aika.model'          = a.__getattribute__('model')
            v[#'aika.new201710      = a.__getattribute__('new201710')
            v['aika.ofl'            = a.__getattribute__('ofl')
            v['aika.olat'           = a.__getattribute__('olat')
            v['aika.olng'           = a.__getattribute__('olng')
            v['aika.positionTime'   = a.__getattribute__('positionTime')
            v['aika.serialNumber'   = a.__getattribute__('serialNumber')
            v['aika.sendCommand'    = a.__getattribute__('sendCommand')
            v['aika.speed'          = a.__getattribute__('speed')
            v['aika.sn'             = a.__getattribute__('sn')
            v['aika.state'          = a.__getattribute__('state')
            v['aika.status'         = a.__getattribute__('status')
            v['aika.statusX20'      = a.__getattribute__('statusX20')
            v['aika.stm'            = a.__getattribute__('stm')
            v['aika.timeZone'       = a.__getattribute__('timeZone')
            v['aika.VIN'            = a.__getattribute__('VIN')
            v['aika.voice'          = a.__getattribute__('voice')
            v['aika.warn'           = a.__getattribute__('warn')
            v['aika.warnStr'        = a.__getattribute__('warnStr')
            v['aika.warnTime'       = a.__getattribute__('warnTime')
            v['aika.warnTxt'        = a.__getattribute__('warnTxt')
            v['aika.work'           = a.__getattribute__('work')
            v['aika.xg'             = a.__getattribute__('xg')
            v['aika.yinshen'        = a.__getattribute__('yinshen')

           return v
        except (ConnectionResetError) as err:
            _LOGGER.debug(
                "Error getting AIKA info: %s", err)
            return None

    @property
    def status(self):
        """Get latest update if throttle allows. Return status."""
        await self.update()
        return self._status

    # Formats date from 2019-10-16T10:54:52.535+02:00 to human readable
    def _get_date(self, str_date):
        date = datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        return date.strftime('%Y-%m-%d %H:%M:%S')

    # Gets latest location from table
    def get_location(self):

        return {'longtitude': v['aika.lng', 'latitude': v['aika.lat']]}

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update(self, **kwargs):
        """Fetch the latest status from OnStar."""
        _LOGGER.info("Update onstar data.")
        self._status = await self._get_status()
