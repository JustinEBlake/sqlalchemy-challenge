# Import the dependencies.
import datetime as dt
import numpy as np
from pathlib import Path


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
file = Path("Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{file}")

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

# ----------------------------------------------Homepage---------------------------------------------------
@app.route("/")
def welcome():
    """Lists all available routes."""
    return (
        f"<b>Available Routes:</b><br/>"
        f"🛜/api/v1.0/precipitation<br/>"
        f"🛜/api/v1.0/stations<br/>"
        f"🛜/api/v1.0/tobs<br/>"
        f"🛜/api/v1.0/start<br/>"
        f"🛜/api/v1.0/start/end<br/>"
        f"⚠️ start/end format = (yyyy-mm-dd)"
    )


# -----------------------------------------Precipatation------------------------------------------
@app.route("/api/v1.0/precipitation")
def precipatation():
    """Retrieves only the last 12 months of data) to a dictionary using date as the key and prcp as the value."""
    # Query Precipatation for the last year
    precip_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > '2016-08-23').\
            order_by(Measurement.date).all()
    
    # Create empty list to store dictionaries
    precip_list = []

    # Loop through query and store dictionary data to list
    for date, precip in precip_results:
        precip_dict = {}
        precip_dict[date] = precip
        precip_list.append(precip_dict)

    return jsonify(precip_list)


# --------------------------------------------Stations---------------------------------------------
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    station_names = session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(station_names))

    return(jsonify(all_names))


# ------------------------------------------------Temperature--------------------------------------
@app.route("/api/v1.0/tobs")
def temp():
    """Return a JSON list of temperature observations for the previous year from the most active station."""

    # Get most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    
    most_active_station = active_stations[0][0]

    # Get last year's date
    station_last_date = (session.query(func.max(Measurement.date))
    .filter(Measurement.station == most_active_station)
    .scalar())

    station_last_date = dt.datetime.strptime(station_last_date, '%Y-%m-%d').date()

    year_prior = str(station_last_date - dt.timedelta(days=365))

    # Make Query
    query_2 = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station).filter(Measurement.date >= year_prior).\
        all()

    temp = list(np.ravel(query_2))

    return(jsonify(temp))


# --------------------------------------Start Date-----------------------------------------------------
@app.route("/api/v1.0/<start>")
def get_start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature 
    for a specified start or start-end range."""
    date_1 = str(start)
    # Query for date, min temp, avg temp, & max temp for each day given the date in the URL
    query = session.query(Measurement.date,
                          func.min(Measurement.tobs),
                          func.avg(Measurement.tobs),
                          func.max(Measurement.tobs)).filter(Measurement.date > date_1).group_by(Measurement.date).all()
    
    # Create empty list to store dictionaries
    temp_results = []
    
    # Loop through query and create following dict to store in list -> {date: {'Avg': avg, 'Max': max, 'Min': min}}
    for date, min, avg, max in query:
        dates = {}
        results = {}
        results["Min"] = min
        results["Avg"] = avg
        results["Max"] = max
        dates[date] = results
        temp_results.append(dates)


    return(jsonify(temp_results))


#------------------------------Start Date--------------------------------------------------------
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    date_1 = str(start)
    date_2 = str(end)
    # Query for date, min temp, avg temp, & max temp for each day given the date in the URL
    query = session.query(Measurement.date,
                          func.min(Measurement.tobs),
                          func.avg(Measurement.tobs),
                          func.max(Measurement.tobs)).filter(Measurement.date.between(date_1,date_2)).\
                          group_by(Measurement.date).all()

    # Create empty list to store dictionaries
    temp_results = []
    
    # Loop through query and create following dict to store in list -> {date: {'Avg': avg, 'Max': max, 'Min': min}}
    for date, min, avg, max in query:
        dates = {}
        results = {}
        results["Min"] = min
        results["Avg"] = avg
        results["Max"] = max
        dates[date] = results
        temp_results.append(dates)


    return(jsonify(temp_results))


#-------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
