# What it is for?
This is custom_component for AIKA / other GPS OBD2 Tracker for cars. 
Just search Alliexpres / Whish / Gearbest / ... for GPS OBD2 Tracker. This is for all GPS OBD2 trackers
that are using AIKA mobile app. If you have trouble - let me know.

# How to install it?
Place in our custom_components folder:
```
git clone git@github.com:nyxnyx/maika.git
```

# Configuration
```configuration.yaml```

```
maika:
  username:   !secret aika_username
  password:   !secret aika_password
  address:     !secret aika_server
```
where:
1. username: your device serial number
1. password: your aika / clound password (default 123456)
1. address: clound service addres (http://www.aika168.com)

# Sensors
Following sensors are available:
```
cards:
  - type: entities
    entities:
    - sensor.maika_battery
    - sensor.maika_batterystatus
    - sensor.maika_course
    - sensor.maika_icon
    - sensor.maika_id
    - sensor.maika_lat
    - sensor.maika_lng
    - sensor.maika_model
    - sensor.maika_ofl
    - sensor.maika_olat
    - sensor.maika_olng
    - sensor.maika_positiontime
    - sensor.maika_sn
    - sensor.maika_speed
    - sensor.maika_state
    - sensor.maika_status
    - sensor.maika_stm
    - sensor.maika_voice
    - sensor.maika_warn
    - sensor.maika_warntxt
    - sensor.maika_warnstr
    - sensor.maika_work
    - sensor.maika_xg
    - sensor.maika_yinshen
```