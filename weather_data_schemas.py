""" Schemas, tables names and CSV to schema mapping for
downloaded DWD weather data.
"""

LAST_UPDATE_SCHEM = ('station_obs_id PRIMARY KEY STRING, '
                     'station_id STRING, '
                     'temp_c FLOAT, '
                     'last_update_utc TIMESTAMP')

METEO_TEMPS_SCHEMA = ('station_id STRING, '
                     'temp_c FLOAT, '
                     'pressure_hpa FLOAT, '
                     'relative_hum_pct FLOAT, '
                     'timestamp_utc FLOAT')

METEO_TEMPS_MAPPING = {'STATIONS_ID': 'station_id',
                       'MESS_DATUM': 'timestamp_utc',
                       'TT_10': 'temp_c', # At 2m high.
                       'PP_10': 'pressure_hpa',
                       'RF_10': 'relative_hum_pct'}

METEO_SOLAR_SCHEMA = ('station_id STRING, '
                      'global_rad_10min_jcm2 FLOAT, '
                      'diffuse_rad_10min_jcm2 FLOAT, '
                      'back_rad_10min_jcm2 FLOAT, '
                      'timestamp_utc FLOAT')

METEO_SOLAR_MAPPING = {'STATIONS_ID': 'station_id',
                       'MESS_DATUM': 'timestamp_utc',
                       'GS_10': 'global_rad_10min_jcm2',
                       'DS_10': 'diffuse_rad_10min_jcm2',
                       'LS_10': 'back_rad_10min_jcm2'}

METEO_WIND_SCHEMA = ('station_id STRING, '
                     'wind_speed_10min_ms FLOAT, '
                     'wind_dir_10min_deg FLOAT, '
                     'timestamp_utc FLOAT')

METEO_WIND_MAPPING = {'STATIONS_ID': 'station_id',
                      'MESS_DATUM': 'timestamp_utc',
                      'FF_10': 'wind_speed_10min_ms',
                      'DD_10': 'wind_dir_10min_deg'}

METEO_PRECIP_SCHEMA = ('station_id STRING, '
                       'precip_dur_10min_min FLOAT, '
                       'precip_height_10min_mm FLOAT, '
                       'timestamp_utc FLOAT')

METEO_PRECIP_MAPPING = {'STATIONS_ID': 'station_id',
                        'MESS_DATUM': 'timestamp_utc',
                        'RWS_DAU_10': 'precip_dur_10min_min',
                        'RWS_IND_10': 'precip_height_10min_mm'}

SCHEMAS = {'temps': {'table_name': 'meteoTemps',
                     'schema': METEO_TEMPS_SCHEMA,
                     'mapping': METEO_TEMPS_MAPPING},
           'solar': {'table_name': 'meteoSolar',
                     'schema': METEO_SOLAR_SCHEMA,
                     'mapping': METEO_SOLAR_MAPPING},
           'wind': {'table_name': 'meteoWind',
                    'schema': METEO_WIND_SCHEMA,
                    'mapping': METEO_WIND_MAPPING},
           'precipitation': {'table_name': 'meteoPrecip',
                             'schema': METEO_PRECIP_SCHEMA,
                             'mapping': METEO_PRECIP_MAPPING}
           }
