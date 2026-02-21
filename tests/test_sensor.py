import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from maika.sensor import async_setup_platform, AikaSensor, DOMAIN
from homeassistant.exceptions import PlatformNotReady

@pytest.mark.asyncio
async def test_async_setup_platform_no_data():
    mock_hass = MagicMock()
    mock_data = MagicMock()
    mock_data._status = None
    mock_hass.data = {DOMAIN: mock_data}
    
    with pytest.raises(PlatformNotReady):
        await async_setup_platform(mock_hass, {}, MagicMock())

@pytest.mark.asyncio
async def test_async_setup_platform_success():
    mock_hass = MagicMock()
    mock_data = MagicMock()
    mock_data._status = {"maika.battery": 100}
    mock_data.SENSOR_TYPES = {"maika.battery": ["Battery", "%", "mdi:battery"], "maika.other": ["Other", None, None]}
    mock_hass.data = {DOMAIN: mock_data}
    
    add_entities = MagicMock()
    
    await async_setup_platform(mock_hass, {}, add_entities)
    
    add_entities.assert_called_once()
    entities = add_entities.call_args[0][0]
    assert len(entities) == 1
    assert entities[0].name == "Battery"

@pytest.mark.asyncio
async def test_aika_sensor():
    mock_data = MagicMock()
    mock_data.status = {"maika.battery": 80}
    mock_data.SENSOR_TYPES = {"maika.battery": ["Battery", "%", "mdi:battery"]}
    
    sensor = AikaSensor(mock_data, "maika.battery", MagicMock())
    
    assert sensor.name == "Battery"
    assert sensor.icon == "mdi:battery"
    assert sensor.unit_of_measurement == "%"
    
    await sensor.async_update()
    
    assert sensor.state == 80
