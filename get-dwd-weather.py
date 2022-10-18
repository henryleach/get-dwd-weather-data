import requests
import zipfile
import csv
import datetime
import os
import sqlite3
import configparser
import weather_data_schemas as S
from pathlib import Path

def delete_files(files: list[str]) -> int:
    """ Tries to delete all passed files """

    for unwanted_file in files:
        os.remove(unwanted_file)

    return 0

def dwdtime_to_timestamp(dwdtime: str) -> float:
    """ Turn a timestamp given in the DWD data in the format
    %Y%m%d%H%M as a unix timestamp, both in UTC time.
    """

    time = datetime.datetime.strptime(dwdtime,
            "%Y%m%d%H%M").replace(tzinfo=datetime.timezone.utc)

    return time.timestamp()

def timestamp_to_dwdtime(timestamp: float) -> str:
    """ Turn a timestamp into a string with format %Y%m%d%H%M
    """

    time = datetime.datetime.fromtimestamp(timestamp,
                                           tz=datetime.timezone.utc)

    dwdtime = time.strftime("%Y%m%d%H%M")

    return dwdtime


def download_current_obs(dwd_station_id: str, obs_type: str) -> dict:
    """ Given a DWD Station ID, download the
    current ten minute observations and return them as
    a dict. 
    """
    
    dwd_base_temps_url = ("https://opendata.dwd.de/climate_environment/CDC/"
                          "observations_germany/climate/10_minutes/")

    # Should these be part of the relevant schema dicts?
    obs_urls = {'temps':  "air_temperature/now/10minutenwerte_TU_{}_now.zip",
                'solar': "solar/now/10minutenwerte_SOLAR_{}_now.zip",
                'wind': "wind/now/10minutenwerte_wind_{}_now.zip",
                'precipitation': "precipitation/now/10minutenwerte_nieder_{}_now.zip"}

    
    download_url = (dwd_base_temps_url + obs_urls[obs_type].format(dwd_station_id))

    ten_min_temps = requests.get(download_url).content

    # save the downloaded zipfile
    with open ("temps.zip", "wb") as f:
        f.write(ten_min_temps)

    temp_files = ["temps.zip"]

    with zipfile.ZipFile("temps.zip", 'r') as zip_ref:
        latest_file = zip_ref.namelist()[0]
        # There's normally only one file,
        # but in case of more; plus we need the name
        zip_ref.extract(latest_file)
        
        temp_files.append(latest_file)

    with open(latest_file, newline='') as csvfile:
        latest_data=[x for x in csv.DictReader(csvfile, delimiter=";")]

    # Delete the files we don't need anymore
    delete_files(temp_files)
        
    return latest_data
    

def get_obs_params(obs_dict: dict, obs_type: str) -> dict:
    """ Extract only the main meteo
    parameters we're interested in, and rename them.
    """

    mapping = S.SCHEMAS[obs_type]['mapping']

    out_dict = {}

    for key, value in mapping.items():
        if value == "timestamp_utc":
            out_dict[value] = dwdtime_to_timestamp(obs_dict[key])
        else:
            out_dict[value] = obs_dict[key].strip()

    return out_dict


def insert_meteo_measurements(obs_array: list[dict], db_path: str, obs_type: str) -> int:
    """ Insert the latest observations into the
        sqlite3 DB, using the relevant table and schema
        defined by the obs_type.
    """

    table_name = S.SCHEMAS[obs_type]['table_name']
    table_schema = S.SCHEMAS[obs_type]['schema']

    # The order is import, as sqlite won't correct the value placeholder
    # with the desired column.
    cols = [] # blank array of items
    for _ in S.SCHEMAS[obs_type]['schema'].split(', '):
        cols.append(":" + _.split(' ')[0].strip())

    insert_values = ', '.join(cols)

    insert_statement = (f"INSERT INTO {table_name} VALUES({insert_values})")
        
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        # can you not use the safe substitution
        # at this point?
        cur.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, table_schema))

        cur.executemany(insert_statement, obs_array)

    print("Added {} rows into {}".format(len(obs_array), table_name))

    return 0 # assuming it went well.
 

def get_latest_obs_time(station_id: str, db_path: str, obs_type: str) -> float:
    """ Get the most recent value and timestamp of observation
    for any particular observation type.
    If no value exists, return 1 """

    # TODO: Move to a dedicated 'last observation' table or something, 
    # As the entries grow this is going to get slower and slower.

    select_last = "SELECT timestamp_utc FROM {} WHERE station_id = {} ORDER BY timestamp_utc DESC LIMIT 1;"
    table_name = S.SCHEMAS[obs_type]['table_name']
    
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        try:
            cur.execute(select_last.format(table_name, station_id))      
        except sqlite3.OperationalError as err:
            print("Warning: {}".format(err))
            last_time = None
        else:
            last_time = cur.fetchone()

    # Can be that the table exists, but has no entries, then last_time is also None
    if last_time is None:
        last_time = 1.0
    else:
        last_time = last_time[0]
            
    return last_time


def get_save_latest_obs(dwd_station_id: str, obs_type: str, db_path: str) -> int:
    """ Download and save the unsaved 10 minute weather
    observations from the https://opendata.dwd.de/ into the sqlite3 DB at db_path.
    obs_types supported are: 'temps', 'solar', 'wind', 'precipitation'.
    """

    # check that obs_type is a valid option
    if obs_type not in ['temps', 'solar', 'wind', 'precipitation']:
        raise AttributeError("{} is not a valid observation type".format(obs_type))

    latest_data = download_current_obs(dwd_station_id, obs_type)

    previous_update_time = get_latest_obs_time(dwd_station_id, db_path, obs_type)

    # Put the timestamp into the correct string format so we can filter before conversion
    previous_update_time = timestamp_to_dwdtime(previous_update_time)

    unsaved_data = [get_obs_params(x, obs_type) for x in latest_data if x['MESS_DATUM'] > previous_update_time]

    insert_meteo_measurements(unsaved_data, db_path, obs_type)

    return 0 # assuming all went well

def main():
    """ Download all recent 10 minute weather observations
    and save them into an SQLite DB located as defined in the
    weather_config.ini file.
    """
    
    config = configparser.ConfigParser()

    # Create an absolute path for reading the config file,
    # otherwise you can get errors with things like cron
    # running it from other directories.

    config_file_name = "weather_config.ini"
    abs_path = Path(__file__).parent / config_file_name
    config.read(str(abs_path))

    # For the URL, need the ensure the station ID is padded to
    # 5 digits.
    station_id = str(config['config']['dwd_station_id']).zfill(5)
    db_path = config['config']['db_path']

    all_observations = ['temps', 'solar', 'wind', 'precipitation']

    for obs_type in all_observations:
        get_save_latest_obs(station_id, obs_type, db_path)

    return 0


if __name__ == "__main__":
    main()
