# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
#conn = engine.connect()

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Create an app, being sure to pass __name__

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Define what to do when a user hits the index route

#   1. /
# Start at the homepage.
# List all the available routes.
@app.route('/')
def homepage():
    return(
        f'Welcome to the Hawaii Climate Analysis API!<br/>'
        f'Avilable Routes:</br>'
        f'/api/v1.0/precipitation</br>'
        f'</api/v1.0/stations/br>'
        f'</api/v1.0/tobs/br>'
        f'</api/v1.0/<start>/br>'
        f'/api/v1.0/<start>/<end>'
    )

# 2./api/v1.0/precipitation

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value.

# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    one_year = dt.date(2017,8,23)-dt.timedelta(days=365)
    last__date_year_data = dt.date(one_year.year, one_year.month, one_year.day)
    data_score = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last__date_year_data)\
                .order_by(Measurement.date.desc()).all()

    j_dict = dict(data_score) 
    return jsonify(j_dict) 

# 3./api/v1.0/stations

# Return a JSON list of stations from the dataset.

@app.route('/api/v1.0/stations')
def station():

    session = Session(engine)

    list = [Station.station, Station.name,	Station.latitude,	Station.longitude,	Station.elevation]
    result = session.query(*list).all()
    session.close()

    stations = []
    for station,name,lat,log,ele in result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = lat
        station_dict["Longitude"] = log
        station_dict["Elevation"] = ele
        station.append(station_dict)
    return jsonify(stations)

# 4./api/v1.0/tobs

# Query the dates and temperature observations of the most-active station for the previous year of data.

# Return a JSON list of temperature observations for the previous year.
app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    results = session.query(Measurement.date,Measurement.tobs)\
                .filter(Measurement.station == 'USC00519281') .filter(Measurement.date>='2016-08-23').all()

    tobs_obser = []
    for date,tobs in results:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['Tobs'] = tobs
        tobs_obser.append(tobs_dict)

    return jsonify(tobs_obser)

# 5./api/v1.0/<start> and /api/v1.0/<start>/<end>

# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates 
# greater than or equal to the start date.

# For a specified start date and end date, calculate TMIN, TAVG, and 
# TMAX for the dates from the start date to the end date, inclusive.

app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)

    list_result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
                                func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    temp = []
    for min_temp, max_temp, avg_temp in list_result:
        temp_dict = {}
        temp_dict['Minimum Temperature'] = min_temp
        temp_dict['Maximum Temperature'] = max_temp
        temp_dict['Average Temperature'] = avg_temp
        temp.append(temp_dict)

        return jsonify(temp)
    
    
app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    session = Session(engine)

    list_results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
                                func.avg(Measurement.tobs)).filter(Measurement.date >= start)\
                                    .filter(Measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, max_temp, avg_temp in list_results:
        temp_dict = {}
        temp_dict['Minimum Temperature'] = min_temp
        temp_dict['Maximum Temperature'] = max_temp
        temp_dict['Average Temperature'] = avg_temp
        temps.append(temp_dict)

        return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)

    