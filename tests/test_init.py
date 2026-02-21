import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from maika import async_setup, AikaData, DOMAIN, SIGNAL_STATE_UPDATED
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_ADDRESS

@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.data = {}
    return hass

from datetime import datetime, timezone
@pytest.mark.asyncio
async def test_async_setup_success(mock_hass):
    with patch("maika.discovery.async_load_platform", new_callable=AsyncMock) as mock_discovery, \
         patch("maika.AikaData.async_update", new_callable=AsyncMock) as mock_update, \
         patch("maika.async_track_point_in_utc_time") as mock_track, \
         patch("maika.async_dispatcher_send"), \
         patch("maika.utcnow", return_value=datetime(2025, 1, 1, tzinfo=timezone.utc)):
         
        config = {
            DOMAIN: {
                CONF_USERNAME: "test_user",
                CONF_PASSWORD: "test_password",
                CONF_ADDRESS: "http://testserver.com"
            }
        }
        
        result = await async_setup(mock_hass, config)
        
        assert result is True
        assert DOMAIN in mock_hass.data
        mock_discovery.assert_any_call(mock_hass, "sensor", DOMAIN, {}, config[DOMAIN])
        mock_discovery.assert_any_call(mock_hass, "device_tracker", DOMAIN, {}, config[DOMAIN])
        mock_update.assert_called_once()
        mock_track.assert_called_once()

@pytest.mark.asyncio
async def test_aika_data_get_status_success():
    mock_api = MagicMock()
    mock_api.doLogin = AsyncMock()
    mock_api.doUpdate = AsyncMock()
    
    # Mocking new SDK dataclasses
    mock_api.device_info = MagicMock()
    mock_api.device_info.device_id = "123"
    
    mock_api.location = MagicMock()
    mock_api.location.lat = "50.0"
    mock_api.location.lng = "20.0"
    
    mock_api.status = MagicMock()
    mock_api.status.battery = 100
    
    del mock_api.key2018
    
    data = AikaData("user", "pass", "http://server", MagicMock())
    data.api = mock_api
    
    status = await data._get_status()
    
    mock_api.doLogin.assert_called_once_with("user", "pass")
    mock_api.doUpdate.assert_called_once()
    
    assert status is not None
    assert status['maika.battery'] == 100
    assert status['maika.lat'] == "50.0"

@pytest.mark.asyncio
async def test_handle_send_command_success(mock_hass):
    with patch("maika.discovery.async_load_platform", new_callable=AsyncMock), \
         patch("maika.AikaData.async_update", new_callable=AsyncMock), \
         patch("maika.async_track_point_in_utc_time"), \
         patch("maika.async_dispatcher_send"), \
         patch("maika.utcnow"):
         
        config = {DOMAIN: {CONF_USERNAME: "u", CONF_PASSWORD: "p", CONF_ADDRESS: "a"}}
        await async_setup(mock_hass, config)
        
        mock_api = MagicMock()
        mock_api.send_command = AsyncMock()
        mock_hass.data[DOMAIN].api = mock_api
        
        # Call the registered service
        handle_send_command = mock_hass.services.async_register.call_args[0][2]
        call = MagicMock()
        call.data = {"command": "DY"}
        
        await handle_send_command(call)
        
        mock_api.send_command.assert_called_once_with("DY")
