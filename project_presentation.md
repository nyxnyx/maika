---
marp: true
theme: default
paginate: true
header: 'Maika Home Assistant Integration'
footer: 'https://github.com/nyxnyx/maika'
---

# Maika Integration for Home Assistant

Integrate your AIKA compatible GPS OBD2 trackers directly into your smart home.

---

## What is it?

Maika is a Home Assistant custom component designed to bridge the gap between GPS OBD2 trackers (purchased from Aliexpress, Wish, Gearbest, etc.) and your Home Assistant instance.

If your tracker uses the **AIKA mobile app**, this integration is for you!

---

## Key Features

1. **Device Tracking**: Seamlessly maps your car's location in Home Assistant using the `device_tracker` component. Shows GPS coordinates, heading, and speed.
2. **Rich Sensor Data**: Provides extensive telemetry through dedicated sensors.
3. **Remote Commands**: Allows sending commands to your vehicle directly from Home Assistant automations.

---

## Available Sensors

The integration pulls out a vast amount of data from the tracker, including:

- **Battery Status & Level** (`sensor.maika_battery`, `sensor.maika_batterystatus`)
- **Location Data** (`sensor.maika_lat`, `sensor.maika_lng`, `sensor.maika_course`)
- **Vehicle Telemetry** (`sensor.maika_speed`, `sensor.maika_ignition`)
- **Device Info** (`sensor.maika_sn`, `sensor.maika_model`, `sensor.maika_iccid`)
- **Network Status** (`sensor.maika_xg` - signal strength, `sensor.maika_isgps`)
- **Warnings & Alerts** (`sensor.maika_warning_type`, `sensor.maika_warntxt`)

---

## Services & Automations

Take control with the `maika.send_command` service.

Directly trigger commands to your GPS Tracker from Home Assistant automations:

```yaml
service: maika.send_command
data:
  command: "DY" # Example: Cut oil/electricity command
```

*Imagine automating anti-theft measures directly from your dashboard.*

---

## Installation

Install as a `custom_component` in your Home Assistant directory:

```bash
cd custom_components
git clone git@github.com:nyxnyx/maika.git
```

---

## Configuration

Configure the integration using your `configuration.yaml` file:

```yaml
maika:
  username: !secret aika_username
  password: !secret aika_password
  address:  !secret aika_server
```

- **username**: Your device serial number
- **password**: Your AIKA/cloud password (default `123456`)
- **address**: Cloud service address (e.g., `http://www.aika168.com`)

---

## Under the Hood

- **Language**: Python 3
- **Dependencies**: Uses the `obdtracker` library to communicate with the AIKA API.
- **Robustness**: Extensively covered with `pytest` unit tests for stability. Type annotations are applied, and the component follows modern Home Assistant development paradigms (using `extra_state_attributes` over outdated implementations).

---

# Thank You!

Enjoy seamless tracking and control of your vehicles from Home Assistant.
