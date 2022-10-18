# Get DWD Ten Minute Weather Data

Small collection of Python functions to download some parameters from the ten minute observations of the Deutscher Wetterdienst (DWD) [Open Data server](https://opendata.dwd.de/). All data falls under the DWD's [copyright](https://www.dwd.de/EN/service/copyright/copyright_node.html).

Every time get-dwd-weather.py is run it will save all the observations not already saved from today into a SQLite3 database.

## Configuration

There are only two options, configured in `weather_config.ini`, which are the DWD weather station ID and the (relative) path to the SQLite DB to use. If no DB exists under that name a new one will be created, with the relevant tables.

The DWD's [Station List](https://www.dwd.de/DE/leistungen/klimadatendeutschland/stationsliste.html) contains a [table](https://www.dwd.de/DE/leistungen/klimadatendeutschland/statliste/statlex_html.html;jsessionid=71B944BA8926E79F6275E99477C73159.live21072?view=nasPublication&nn=16102) of IDs in the column 'Stations_ID'. They are numeric, and in the 10 minute data directories padded to 5 places with zeros.

E.G. '7341' for Offenbach is '07341' in the URLs.

## Changing Observation Data Saved

weather_data_schemas.py contains the details of which columns are saved from the observation data, into which table and under what column names. If you need add/remove/rename any of this, change it there.

## Requirements

- Python (3.9 and 3.10 tested)
- Python [Reqests](https://requests.readthedocs.io/en/latest/) module
- SQLite3


## Testing

Check the latest data in the DB with:

```SQL
SELECT datetime(timestamp_utc, 'unixepoch'), * FROM <tablename>;
```
