import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys

mock_ha_dt = MagicMock()
mock_ha_dt.SOURCE_TYPE_GPS = "gps"
mock_ha_dt.config_entry = MagicMock()
mock_ha_dt.config_entry.TrackerEntity = object

sys.modules['homeassistant.components.device_tracker'] = mock_ha_dt
sys.modules['homeassistant.components.device_tracker.config_entry'] = mock_ha_dt.config_entry

from maika.device_tracker import AIKADeviceTracker, async_setup_scanner, DOMAIN

@pytest.mark.asyncio
async def test_async_setup_scanner():
    mock_hass = MagicMock()
    
    mock_data = MagicMock()
    mock_data.status = {
        "maika.lat": "50.0",
        "maika.lng": "20.0",
        "maika.sn": "123",
        "maika.course": "90",
        "maika.speed": "100",
        "maika.iccid": "iccid_123",
        "maika.devicename": "Car"
    }
    mock_hass.data = {DOMAIN: mock_data}
    
    mock_see = AsyncMock()
    
    with patch("maika.device_tracker.async_dispatcher_connect") as mock_connect:
        result = await async_setup_scanner(mock_hass, {}, mock_see)
        
        assert result is True
        mock_connect.assert_called_once()
        mock_see.assert_called_once()

@pytest.mark.asyncio
async def test_aika_device_tracker_update():
    mock_data = MagicMock()
    mock_data.status = {
        "maika.lat": "51.0",
        "maika.lng": "21.0",
        "maika.sn": "123",
        "maika.course": "180",
        "maika.speed": "120",
        "maika.iccid": "iccid_123",
        "maika.devicename": "Car"
    }
    
    mock_see = AsyncMock()
    tracker = AIKADeviceTracker(MagicMock(), mock_data, mock_see)
    
    await tracker.async_update()
    
    assert tracker.latitude == 51.0
    assert tracker.longitude == 21.0
    mock_see.assert_called_once()
    kwargs = mock_see.call_args.kwargs
    assert kwargs['mac'] == "iccid_123"
    assert kwargs['gps'] == (51.0, 21.0)
    assert kwargs['attributes']['heading'] == "S"

@pytest.mark.asyncio
async def test_aika_device_tracker_get_heading():
    mock_data = MagicMock()
    mock_see = AsyncMock()
    tracker = AIKADeviceTracker(MagicMock(), mock_data, mock_see)

    assert tracker.get_heading(0) == "N"
    assert tracker.get_heading(45) == "NE"
    assert tracker.get_heading(90) == "E"
    assert tracker.get_heading(135) == "SE"
    assert tracker.get_heading(180) == "S"
    assert tracker.get_heading(225) == "SW"
    assert tracker.get_heading(270) == "W"
    assert tracker.get_heading(315) == "NW"
    assert tracker.force_update() is True
