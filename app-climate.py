
from flask import Flask, jsonify
from sqlalchemy import func
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# lets reflect tables into a SQLAlchemy ORM
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Design a query to retrieve the last 12 months of precipitation data and plot the results
# dates in sqlachemy do not requiere transformation
# better PANDAS
year = pd.read_sql("SELECT*FROM Measurement WHERE date >= '2016-08-23'",engine)
year
#lests search for missing values
year.isnull().sum()/len(year) # 209 missing values in prcp (9.3%)
year = year.dropna()
# lets search for duplicates observation
year[year.duplicated(["id","station","date","prcp"])]
#There is not duplicated information
# Calculate the date 1 year ago from the last data point in the database
year["date"].max() #2017-08-23 is the most recent date
last_day = dt.date(2017,8,23)
time_delta = dt.timedelta(days=365)
one_year = last_day - time_delta
one_year

#################################################
# Flask Setup
#################################################
# @TODO: Initialize your Flask app here
# YOUR CODE GOES HERE
app = Flask(__name__)
#################################################
# Flask Routes
#################################################


# @TODO: Complete the routes for your app here
# YOUR CODE GOES HERE

# home endpoint
@app.route("/")
def home():
    print ("Server received a GET request...")
    return (f""" 
            <h1>Climate App</h1>
            <p>By Rodrigo Guarneros</p>
            <h3>Welcome to this aplication!</h3>
            <br>
            <p>In this API you are going to find the following routes:</p> 
            <ol>
            <li>Precipitation observations in Honolulu, Hawaii: <a href="http://localhost:5000/api/v1.0/precipitation">/api/v1.0/precipitation</a></li> 
            <li>List of every station in the Honolulu, Hawaii: <a href="http://localhost:5000/api/v1.0/stations">/api/v1.0/stations</a></li>
            <li>Temperature observations on the last year in the main station in Honolulu, Hawaii: <a href="http://localhost:5000/api/v1.0/tobs">/api/v1.0/tobs</a></li>
            <li>Minimal, Maximal and Average temperature for a given start, or start and end range (please introduce the format "YYYY-MM-DD" for start, end date or both of them):
            <br>
            <a href="http://localhost:5000/api/v1.0/start">/api/v1.0/start</a> and
            <a href="http://localhost:5000/api/v1.0/start/end">/api/v1.0/start/end</a>
            </li>
            <br>
            <p>Note: The format for start and end dates should be "YYYY-MM-DD".
            </ol>
    """)

# second endpoint
@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    A = (
        session
        .query(Measurement.date, Measurement.prcp)
        .all()
        )
 
# making the key in the dictionary previous of jsonify
    date_prcp = []
    
    for date, prcp in A:
        A_dict = {}
        A_dict["Date"] = date
        A_dict["Precipitation (In)"] = prcp
        date_prcp.append(A_dict)
    
    session.close()

    print ("Server received a GET request for prcp...")
    return jsonify(date_prcp)


# third endpoint
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    B = (
        session
        .query(Measurement.station)
        .distinct()
        .all()
        )

# making the key in the dictionary previous of jsonify
    stations_list = []
    
    for station in B:
        B_dict = {}
        B_dict["Station ID"] = station
        stations_list.append(B_dict)
    
    session.close()
    print ("Server received a GET request for stations...")
    return jsonify(stations_list)

# fourth endpoint
@app.route("/api/v1.0/tobs")
def temp_main():
    session = Session(engine)
    C = (
        session
        .query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station=='USC00519281')
        .filter(Measurement.date >= one_year)
        .all()
        )
# making the key in the dictionary previous of jsonify
    temperature_list = []
    
    for date, tobs in C:
        C_dict = {}
        C_dict["Date"] = date
        C_dict["Temperature"] = tobs
        temperature_list.append(C_dict)
      
    session.close()
    print ("Server received a GET request for temp in the main station...")
    return jsonify(temperature_list)

# fifth endpoint
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
# giving format to input    
    start_dt = str(start)
    D = (
        session
        .query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))
        .filter(Measurement.date>=start_dt)
        .all()
        )
   # making the key in the dictionary previous of jsonify
    start_list = []
    
    for minimal, maximal, average in D:
        D_dict = {}
        D_dict["Minimal Temperature"] = minimal
        D_dict["Maximal Temperature"] = maximal
        D_dict["Average Temperature"] = round(average,1)
        start_list.append(D_dict)
      
    session.close()
    print ("Server received a GET request from a start date ...")
    return jsonify(start_list)

# sixth endpoint
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
# giving format to input    
    start_dt = str(start)
    end_dt = str(end)
    E = (
        session
        .query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))
        .filter(Measurement.date>=start_dt)
        .filter(Measurement.date<=end_dt)
        .all()
        )
   # making the key in the dictionary previous of jsonify
    start_end_list = []
    
    for minimal, maximal, average in E:
        E_dict = {}
        E_dict[f'Minimal temperature from {start} to {end}'] = minimal
        E_dict[f'Maximal temperature from {start} to {end}'] = maximal
        E_dict[f'Average temperature from {start} to {end}'] = round(average,1)
        start_end_list.append(E_dict)
      
    session.close()
    print ("Server received a GET request from a start to end date ...")
    return jsonify(start_end_list)



if __name__ == "__main__":
    # @TODO: Create your app.run statement here
    # YOUR CODE GOES HERE
    app.run(debug=True)