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
    country_str = "Location_Albania,Location_Algeria,Location_Andorra,Location_Argentina,Location_Armenia,Location_Australia,Location_Austria,Location_Azerbaijan,Location_Bangladesh,Location_Barbados,Location_Belarus,Location_Belgium,Location_Benin,Location_Bosnia and Herzegovina,Location_Brazil,Location_Burkina Faso,Location_Cambodia,Location_Canada,Location_Chad,Location_Chile,Location_China,Location_Colombia,Location_Comoros,Location_Congo,Location_Cook Islands,Location_Costa Rica,Location_Croatia,Location_Cuba,Location_Cyprus,Location_Czechia,Location_Côte d’Ivoire,Location_Democratic People's Republic of Korea,Location_Denmark,Location_Dominican Republic,Location_Egypt,Location_El Salvador,Location_Estonia,Location_Fiji,Location_Finland,Location_France,Location_Gambia,Location_Georgia,Location_Germany,Location_Ghana,Location_Greece,Location_Guyana,Location_Iceland,Location_India,Location_Indonesia,Location_Iran (Islamic Republic of),Location_Iraq,Location_Ireland,Location_Israel,Location_Italy,Location_Jamaica,Location_Japan,Location_Kazakhstan,Location_Kiribati,Location_Kuwait,Location_Kyrgyzstan,Location_Lao People's Democratic Republic,Location_Latvia,Location_Lebanon,Location_Lithuania,Location_Luxembourg,Location_Madagascar,Location_Mali,Location_Malta,Location_Mauritius,Location_Mexico,Location_Mongolia,Location_Morocco,Location_Mozambique,Location_Namibia,Location_Nauru,Location_Netherlands,Location_New Zealand,Location_Niger,Location_Norway,Location_Oman,Location_Pakistan,Location_Palau,Location_Panama,Location_Paraguay,Location_Peru,Location_Philippines,Location_Poland,Location_Portugal,Location_Qatar,Location_Republic of Korea,Location_Republic of Moldova,Location_Romania,Location_Russian Federation,Location_Rwanda,Location_Samoa,Location_Sao Tome and Principe,Location_Saudi Arabia,Location_Senegal,Location_Serbia,Location_Seychelles,Location_Sierra Leone,Location_Singapore,Location_Slovakia,Location_Slovenia,Location_Spain,Location_Togo,Location_Tuvalu,Location_Zimbabwe,Location_Botswana,Location_Burundi,Location_Cameroon,Location_Eritrea,Location_Eswatini,Location_Ethiopia,Location_Kenya,Location_Lesotho,Location_Liberia,Location_Myanmar,Location_Nepal,Location_Nigeria,Location_Timor-Leste,Location_United States of America"
    country_list = country_str.split(",")
    model = pickle.load(open("model.pkl", "rb"))
    test_df = pd.read_csv("complete_xtest.csv")
    actual = pd.read_csv("TestFile.csv")
    actual_list = actual["CigaretteSmokingPrevalence"].tolist()
    prediction = model.predict(test_df)
    prediction = [int(p) for p in prediction]
    actual_vs_pred = list(zip(actual_list, prediction))
    actual_vs_pred = [list(a) for a in actual_vs_pred]
    predictionary = dict(zip(country_list, actual_vs_pred))
    for k,v in predictionary.items():
        print(k,v, type(v))
    return jsonify(predictionary)



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
