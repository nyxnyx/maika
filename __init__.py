import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from datetime import timedelta
from homeassistant.helpers import discovery
from obdtracker import api, location, device_status
from homeassistant.util import Throttle
from homeassistant.util.dt import utcnow
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_send

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

# Those components will be dicovered automatically based on ocnfiguration
MAIKA_COMPONENTS = ["sensor", "device_tracker"]

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

async def async_setup(hass, base_config: dict) -> bool:
    
    config = base_config.get(DOMAIN)
    
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    server = config.get(CONF_ADDRESS)
    interval = MIN_TIME_BETWEEN_UPDATES

    hass.data[DOMAIN] = AikaData(username, password, server, hass)
    async def _update(now):
        try:
            await hass.data[DOMAIN].async_update()
            async_dispatcher_send(hass, SIGNAL_STATE_UPDATED)
        finally:
            async_track_point_in_utc_time(hass, _update, utcnow() + interval)
        return True
    #
    for component in MAIKA_COMPONENTS:
        await discovery.async_load_platform(hass, component, DOMAIN, {}, config)

    async def handle_send_command(call):
        command = call.data.get("command")
        if command:
            api_instance = hass.data[DOMAIN].api
            if api_instance:
                try:
                    await api_instance.send_command(command)
                    _LOGGER.info("Command '%s' sent successfully.", command)
                except Exception as e:
                    _LOGGER.error("Failed to send command '%s': %s", command, e)
            else:
                 _LOGGER.error("API not ready to send command")

    hass.services.async_register(DOMAIN, "send_command", handle_send_command)

    return await _update(utcnow())
    #return Trueasync_update


class AikaData(object):
    """Stores the data retrieved from AIKA.
    For each entity to use, acts as the single point responsible for fetching
    updates from the server.
    """

    async def async_configure(self) -> None:
        self.api = api.API(self._server)
        self.api.registerUpdater(location.Location(self.api))
        self.api.registerUpdater(device_status.DeviceStatus(self.api))

    def __init__(self, username, password, server, hass):
        """Initialize the data object."""
        self._username = username
        self._password = password
        self._server = server
        self._hass = hass
        self.api = None


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
            #'maika.serialnumber' : ['Serial Number', None, 'mdi:message-text'],
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
            'maika.ignition'     : ['Ignition (ACC)', None, 'mdi:key'],
            'maika.warning_type' : ['Warning Type', None, 'mdi:alert'],
        }
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self, **kwargs):
        """Fetch the latest status from AIKA."""
        _LOGGER.info("Update AIKA data.")
        self._status = await self._get_status() 

    # Retrieves info from Aika
    async def _get_status(self) -> {}:

        if not hasattr(self.api, 'key2018'):
            try:
                if self.api == None:
                    await self.async_configure()
                await self.api.doLogin(self._username, self._password)
            except:
                _LOGGER.error("Invalid username or password for MAIKA component")
                raise HomeAssistantError("Login error - check config for MAIKA component")
            _LOGGER.info("AIKA - logged in")
        
        _LOGGER.info("AIKA - doUpdate")
        await self.api.doUpdate()
        
        try:

            v={}
            info = self.api.device_info
            loc = self.api.location
            status = self.api.status
            
            v['maika.battery']       = status.battery if status else None
            v['maika.batterystatus'] = status.battery_status if status else None
            v['maika.course']        = loc.course if loc else None
            v['maika.datacontext']   = None # Not available in current models
            v['maika.deviceid']      = info.device_id if info else None
            v['maika.devicename']    = info.device_name if info else None
            v['maika.iccid']         = info.imei if info else None
            v['maika.icon']          = None
            v['maika.id']            = info.device_id if info else None
            v['maika.isgps']         = loc.is_gps if loc else None
            v['maika.isstop']        = loc.is_stop if loc else None
            v['maika.lat']           = loc.lat if loc else None
            v['maika.lng']           = loc.lng if loc else None
            v['maika.model']         = info.model if info else None
            v['maika.ofl']           = None
            v['maika.olat']          = None
            v['maika.olng']          = None
            v['maika.positiontime']  = loc.position_time if loc else None
            v['maika.sendcommand']   = None
            v['maika.speed']         = loc.speed if loc else None
            v['maika.sn']            = info.sn if info else None
            v['maika.state']         = status.state if status else None
            v['maika.status']        = status.status if status else None
            v['maika.statusx20']     = None
            v['maika.stm']           = None
            v['maika.timezone']      = None
            v['maika.vin']           = None
            v['maika.voice']         = None
            v['maika.warn']          = None
            v['maika.warnstr']       = None
            v['maika.warntime']      = None
            v['maika.warntxt']       = status.warn_txt if status else None
            v['maika.work']          = None
            v['maika.xg']            = status.signal_strength if status else None
            v['maika.yinshen']       = None
            v['maika.ignition']      = status.is_ignition_on if status else False
            v['maika.warning_type']  = status.warning_type.value if status and hasattr(status, 'warning_type') else "None"

            return v
        except (ConnectionResetError) as err:
            _LOGGER.error(
                "Error getting AIKA info: %s", err)
            return None

    @property
    def status(self) -> {}:
        """Get latest update if throttle allows. Return status."""
        return self._status

