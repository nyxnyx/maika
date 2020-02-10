import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import asyncio
from datetime import datetime
from datetime import timedelta
from homeassistant.helpers import discovery
from obdtracker import api, location, device_status
from homeassistant.util import Throttle


from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, CONF_ADDRESS,
    )

_LOGGER = logging.getLogger(__name__)

DOMAIN="maika"
SIGNAL_STATE_UPDATED = f"{DOMAIN}.updated"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
            vol.Required(CONF_USERNAME): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
            vol.Required(CONF_ADDRESS): cv.url,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_UPDATE_STATE = "update_state"

# Those components will be dicovered automatically based on ocnfiguration
MAIKA_COMPONENTS = ["sensor", "device_tracker"]

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

async def async_setup(hass, base_config: dict):
    
    config = base_config.get(DOMAIN)
    
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    server = config.get(CONF_ADDRESS)
    hass.data[DOMAIN] = AikaData(username, password, server)
    await hass.data[DOMAIN].async_update()
    _LOGGER.info("AIKA initialization...")
    
    for component in MAIKA_COMPONENTS:
        discovery.load_platform(hass, component, DOMAIN, {}, config)

    _LOGGER.info("Done initialization")
    return True


class AikaData(object):
    """Stores the data retrieved from AIKA.
    For each entity to use, acts as the single point responsible for fetching
    updates from the server.
    """

    def __init__(self, username, password, server):
        """Initialize the data object."""
        self._username = username
        self._password = password
        self._server = server
        self.api = api.API(self._server)
        self.api.registerUpdater(location.Location(self.api))
        self.api.registerUpdater(device_status.DeviceStatus(self.api))
        self.gps_position = None
        self._status = None
        self.SENSOR_TYPES = {
            'maika.battery'      : ['Battery', None, 'mdi:battery'],
            'maika.batterystatus': ['Battery Status', None, 'mdi:battery'],
            'maika.course'       : ['Course', None, 'mdi:compass'],
            'maika.datacontext'  : ['Data Context', None, 'mdi:message-text'],
            'maika.deviceid'     : ['Device ID', None, None],
            'maika.devicename'   : ['Device Name', None, 'mdi:rename-box'],
            'maika.iccid'        : ['ICCID', None, None],
            'maika.icon'         : ['Icon', None, None],
            'maika.id'           : ['ID', None, None],
            'maika.isgps'        : ['Is GPS', None, 'mdi:crosshairs-gps'],
            'maika.isstop'       : ['Is Stop', None, 'mdi:car'],
            #'maika.key2018'     : ['', None, None],
            'maika.lat'          : ['Latitude', None, 'mdi:latitude'],
            'maika.lng'          : ['Longitude', None, 'mdi:longitude'],
            'maika.model'        : ['Model', None, 'mdi:car'],
            #'maika.new201710'   : ['', None, None],
            'maika.ofl'          : ['Ofl', None, None],
            'maika.olat'         : ['Old latitude', None, 'mdi:latitude'],
            'maika.olng'         : ['Old longitude', None, 'mdi:longitude'],
            'maika.positiontime' : ['Position time', None, 'mdi:clock-outline'],
            'maika.serialnumber' : ['Serial Number', None, None],
            'maika.sendcommand'  : ['Send Command', None, 'mdi:message-text'],
            'maika.speed'        : ['Speed', None, 'mdi:speedometer'],
            'maika.sn'           : ['SN', None, 'mdi:message-text'],
            'maika.serialnumber' : ['Serial Number', None, 'mdi:message-text'],
            'maika.sendcommand'  : ['Send Command', None, 'mdi:message-text'],
            'maika.state'        : ['State', None, 'mdi:message-text'],
            'maika.status'       : ['Status', None, 'mdi:message-text'],
            'maika.statusx20'    : ['Status X20', None, 'mdi:message-text'],
            'maika.stm'          : ['STM', None, 'mdi:message-text'],
            'maika.timezone'     : ['Time Zone', None, 'mdi:map-clock'],
            'maika.vin'          : ['VIN', None, 'mdi:message-text'],
            'maika.voice'        : ['Has Voice', None, 'mdi:account-voice'],
            'maika.warn'         : ['Warning', None, 'mdi:message-text'],
            'maika.warnstr'      : ['Warning string', None, 'mdi:message-text'],
            'maika.warntime'     : ['Warning time', None, 'mdi:clock-outline'],
            'maika.warntxt'      : ['Warning text', None, 'mdi:message-text'],
            'maika.work'         : ['Work', None, 'mdi:message-text'],
            'maika.xg'           : ['Xg', None, 'mdi:message-text'],
            'maika.yinshen'      : ['yinshen', None, 'mdi:message-text'],
        }

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self, **kwargs):

        """Fetch the latest status from AIKA."""
        _LOGGER.info("Update AIKA data.")
        self._status = await self._get_status()
        self.gps_position = [self.api.lat, self.api.lng]

    
    # Retrieves info from Aika
    async def _get_status(self):

        if not hasattr(self.api, 'key2018'):
            _LOGGER.info("AIKA - logging in")
            await self.api.doLogin(self._username, self._password)
            _LOGGER.info("AIKA - logged in %s" % self.api.key)
        
        _LOGGER.info("AIKA - doUpdate")
        await self.api.doUpdate()
        
        try:

            v={}
            v['maika.battery']       = self.api.__getattribute__('battery')
            v['maika.batterystatus'] = self.api.__getattribute__('batteryStatus')
            v['maika.course']        = self.api.__getattribute__('course')
            v['maika.datacontext']   = self.api.__getattribute__('dataContext')
            v['maika.deviceid']      = self.api.__getattribute__('deviceID')
            v['maika.devicename']    = self.api.__getattribute__('deviceName')
            v['maika.iccid']         = self.api.__getattribute__('ICCID')
            v['maika.icon']          = self.api.__getattribute__('icon')
            v['maika.id']            = self.api.__getattribute__('id')
            v['maika.isgps']         = self.api.__getattribute__('isGPS')
            v['maika.isstop']        = self.api.__getattribute__('isStop')
            #v['maika.key2018']       = self.api.__getattribute__('key2018')
            v['maika.lat']           = self.api.__getattribute__('lat')
            v['maika.lng']           = self.api.__getattribute__('lng')
            v['maika.model']         = self.api.__getattribute__('model')
            #v['maika.new201710']      = self.api.__getattribute__('new201710')
            v['maika.ofl']           = self.api.__getattribute__('ofl')
            v['maika.olat']          = self.api.__getattribute__('olat')
            v['maika.olng']          = self.api.__getattribute__('olng')
            v['maika.positiontime']  = self.api.__getattribute__('positionTime')
            v['maika.serialnumber']  = self.api.__getattribute__('serialNumber')
            v['maika.sendcommand']   = self.api.__getattribute__('sendCommand')
            v['maika.speed']         = self.api.__getattribute__('speed')
            v['maika.sn']            = self.api.__getattribute__('sn')
            v['maika.state']         = self.api.__getattribute__('state')
            v['maika.status']        = self.api.__getattribute__('status')
            v['maika.statusx20']     = self.api.__getattribute__('statusX20')
            v['maika.stm']           = self.api.__getattribute__('stm')
            v['maika.timezone']      = self.api.__getattribute__('timeZone')
            v['maika.vin']           = self.api.__getattribute__('VIN')
            v['maika.voice']         = self.api.__getattribute__('voice')
            v['maika.warn']          = self.api.__getattribute__('warn')
            v['maika.warnstr']       = self.api.__getattribute__('warnStr')
            v['maika.warntime']      = self.api.__getattribute__('warnTime')
            v['maika.warntxt']       = self.api.__getattribute__('warnTxt')
            v['maika.work']          = self.api.__getattribute__('work')
            v['maika.xg']            = self.api.__getattribute__('xg')
            v['maika.yinshen']       = self.api.__getattribute__('yinshen')

            return v
        except (ConnectionResetError) as err:
            _LOGGER.debug(
                "Error getting AIKA info: %s", err)
            return None

    @property
    def status(self):
        """Get latest update if throttle allows. Return status."""
        return self._status

