Homelab infra for weather station:
- Weather Sensor WS85
- Wireless Weather Station WS3802 


# API

GET http://192.168.50.211/get_livedata_info? — current live measurements.
GET http://192.168.50.211/get_network_info? — MAC, Wi-Fi/IP info.
GET http://192.168.50.211/get_ws_settings? — upload / cloud / customized server / MQTT settings.
GET http://192.168.50.211/get_sensors_info? — paired sensor inventory and metadata.
GET http://192.168.50.211/get_rain_totals? — rain totals / rain source priority.
GET http://192.168.50.211/get_piezo_rain — piezo rain data/settings.
GET http://192.168.50.211/get_calibration_data — calibration values.
GET http://192.168.50.211/get_units_info? — configured units for temperature, pressure, wind, rain, light.
GET http://192.168.50.211/get_device_info? — device info, timezone/DST-related fields, AP name, upgrade flags.
GET http://192.168.50.211/get_version? — firmware version / platform / new-version flag.
GET http://192.168.50.211/get_cli_lds? — laser distance sensor settings, if relevant in your setup.