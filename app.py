import sqlalchemy
import pandas as pd
import pickle
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify, render_template

import datetime as dt


#################################################
# Database Setup
#################################################
# conn = pymysql.connect(
#     host='mypostgresdb.cmpzubidxryk.us-west-2.rds.amazonaws.com',
#     port=5432,
#     user='root',
#     password='Project4!',
#     db='my_data_class_db'

# )
engine = create_engine(
    f'postgresql://root:Project4!@mypostgresdb.cmpzubidxryk.us-west-2.rds.amazonaws.com:5432/my_data_class_db')

# engine = create_engine(
#     f'postgresql://postgres:PostGresPasscode@localhost:5432/Smokingdb')
# # reflect an existing database into a new model
Base = automap_base()
# # reflect the tables
Base.prepare(engine, reflect=True)

# # Save reference to the table
smoking_data = Base.classes.smoking_data
session = Session(engine)

# lat_lng = Base.classes.lat_lng

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# list of precipitations

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/api/v1.0/machinelearning")
def machine_learning():
    model = pickle.load(open("model.pkl", "rb"))
    test_df = pd.read_csv("complete_xtest.csv")
    prediction = model.predict(test_df)
    return jsonify(f"{prediction}")


@app.route("/api/v1.0/country")
def country():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and precipitation from all rows
    results = session.query(smoking_data.index, smoking_data.year, smoking_data.location, smoking_data.cigarettesmokingprevalence,
                            smoking_data.tobaccosmokingprevalence, smoking_data.tobaccouseprevalence, smoking_data.mostsoldbrandcigarettecurrency,
                            smoking_data.mostsoldbrandcigaretteprice, smoking_data.rates, smoking_data.mostsoldusd, smoking_data.lat, smoking_data.lng).all()

    session.close()

    # Convert list of tuples into normal list
    all_measure = []
    years = []
    countries = []

    for index, year, Location, CigaretteSmokingPrevalence, TobaccoSmokingPrevalence, TobaccoUsePrevalence, MostSoldBrandCigaretteCurrency, MostSoldBrandCigarettePrice, rates, MostSoldUSD, Lat, Lng in results:
        if year not in years:
            years.append(year)
        if Location not in countries:
            countries.append(Location)

    for country in countries:
        measure_dict = {"Country": country, "Years": []}
        for index, year, Location, CigaretteSmokingPrevalence, TobaccoSmokingPrevalence, TobaccoUsePrevalence, MostSoldBrandCigaretteCurrency, MostSoldBrandCigarettePrice, rates, MostSoldUSD, Lat, Lng in results:
            if country == Location:
                measure_dict["Years"].append({
                    "Year": year,
                    'CigaretteSmokingPrevalence': CigaretteSmokingPrevalence,
                    'TobaccoSmokingPrevalence': CigaretteSmokingPrevalence,
                    'TobaccoUsePrevalence': TobaccoUsePrevalence,
                    'Currency': MostSoldBrandCigaretteCurrency,
                    'Price': MostSoldBrandCigarettePrice,
                    'PriceUSD': MostSoldUSD,
                    'Latitude': Lat,
                    'Longitude': Lng
                })
        all_measure.append(measure_dict)
    return jsonify(all_measure)


if __name__ == '__main__':
    app.run(debug=True)
