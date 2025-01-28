# Import the dependencies.
from flask import Flask, jsonify, request

# Python SQL toolkit and Object Relational Mapper from climate_analysis
from sqlalchemy import create_engine, func  # Added func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# 1. Welcome Route
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"Hawaii Precipitation and Temperature: 08/2016 - 08/2017<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"  
        f"/api/v1.0/tobs/<station_id><br/>"  
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )


# 2. Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():

   # Create session from Python to the DB
    session = Session(engine)
    
    """Retrieve the last 12 months of precipitation data."""
    #  Define the most recent date in the dataset
    most_recent_date = dt.datetime.strptime('2017-08-23', '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    session.close()

    # Create a dictionary using date as the key and precipitation as the value
    date_prcp = {date: prcp for date, prcp in precipitation_data}

    # Return jsonify version of data
    return jsonify(date_prcp)


# 3. Stations Route
@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to the DB
    session = Session(engine)

    """Return a list of all stations."""
    
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station, name, lat, lon, el in queryresult:
        station_dict = {
            "Station": station,
            "Name": name,
            "Lat": lat,
            "Lon": lon,
            "Elevation": el
        }
        stations.append(station_dict)

    # Return jsonify version of data
    return jsonify(stations)

# 4. Temperature Statistics Route
@app.route("/api/v1.0/tobs/<station_id>")
def temperature_for_station(station_id):

    # Create session from Python to the DB
    session = Session(engine)

    """Return temperature statistics for a given station and date range."""
    
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.datetime.strptime('2017-08-23', '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for this station
    twelve_mo_temp_query = session.query(Measurement.tobs).\
        filter(Measurement.station == station_id).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # unravel temp query list
    list_temps = list(np.ravel(twelve_mo_temp_query))

    # Return jsonify version of data
    return jsonify(Temperatures=list_temps)


# 5. Start date or Start and End date temperature for station
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end=None):

    # Create session from Python to the DB
    session = Session(engine)
 
  """Calculate min, avg, and max temperatures for a given date range"""
    
     # Retrieve start and end dates from query parameters
    start_date = request.args.get('start')
    end_date = request.args.get('end')

   try:
        # Query the database for temperature data for the specified date range
        if end:
            temp_calc = session.query(
                func.min(Measurement.tobs).label('min_temp'), 
                func.avg(Measurement.tobs).label('avg_temp'), 
                func.max(Measurement.tobs).label('max_temp')
            ).filter(
                Measurement.date >= start,
                Measurement.date <= end
            ).all()
        else:
            temp_calc = session.query(
                func.min(Measurement.tobs).label('min_temp'), 
                func.avg(Measurement.tobs).label('avg_temp'), 
                func.max(Measurement.tobs).label('max_temp')
            ).filter(
                Measurement.date >= start
            ).all()

        # Unravel the temp_calc list
        list_temp_stats = list(np.ravel(temp_calc))

        # Return jsonify version of data
        return jsonify(min_avg_max_Temps=list_temp_stats)

    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)