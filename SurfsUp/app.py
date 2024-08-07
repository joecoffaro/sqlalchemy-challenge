# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

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

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis</br>"
        f"Available api end points are:</br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/start-date</br>"
        f"/api/v1.0/start-date/end-date</br>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)


    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >=prev_year).all()
    session.close()

    prcip = {date:prcp for date, prcp in results}

    return jsonify(prcip)

@app.route("/api/v1.0/stations")
def stations():

    results = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    most_active = "USC00519281"
    results = session.query(Measurement.tobs)\
    .filter(Measurement.station == most_active)\
    .filter(Measurement.date >= prev_year).all()

    session.close()

    temperatures = list(np.ravel(results))

    return jsonify(temperatures)

@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def stats(start_date = None, end_date = None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end_date:

        start_date = dt.datetime.strptime(start_date, "%m%d%Y")

        results = session.query(*sel).\
            filter(Measurement.date >= start_date).all()
        
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    
    start_date = dt.datetime.strptime(start_date, "%m%d%Y")
    end_date = dt.datetime.strptime(end_date, "%m%d%Y")

    results = session.query(*sel).\
            filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).\
                    all()
    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps)

        




if __name__ == "__main__":
    app.run(debug=True)
