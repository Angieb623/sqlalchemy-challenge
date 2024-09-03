# Import the dependencies.


import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask
from flask import jsonify


#################################################
# Database Setup
#################################################
# connect to database
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.SQLite")


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
# Home route
@app.route("/")
def home():
    return(
        f"<center><h2>Welcome to the Hawaii Climate Analysis Local API</h2></center>"
        f"<center><h3>Select from one of the available routes</h3></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
        )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    # return the previous yr's precip as a json
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8,23) - dt.timedelta(days=365)
   
    # Perform a query to retrieve the data and precipitation scores
    scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previousYear).all()

    session.close()
    
    # dictionary with date as the key and precip as the value
    precipitation = {date: prcp for date, prcp in scores}

    # convert to json
    return jsonify(precipitation)


# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # show list of stations
    # Perform a query to retrieve station names
    results = session.query(Station.station).all()

    session.close()

    stationList = list(np.ravel(results))

    # convert to json and display
    return jsonify(stationList)


# Tobs route
@app.route("/api/v1.0/tobs")
def temperatures():
    # return the prev yr's temperatures
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8,23) - dt.timedelta(days=365)
   
    # Perform a query to retrieve the temperatures from most active station from the past year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previousYear).all()

     
    session.close()

    temperatureList = list(np.ravel(results))

    # return the list of temperatures
    return jsonify(temperatureList)


# Start and Start/End routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):

    # select statement
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:

        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).all()

        session.close()

        temperatureList = list(np.ravel(results))

        # return the list of temperatures
        return jsonify(temperatureList)
    
    else:

        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*selection)\
            .filter(Measurement.date >= startDate)\
            .filter(Measurement.date <= endDate).all()

        session.close()

        temperatureList = list(np.ravel(results))

        # return the list of temperatures
        return jsonify(temperatureList)













## app launcher
if __name__ == "__main__":
    app.run(debug=True)
    