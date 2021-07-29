from flask import Flask, render_template,redirect,url_for, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import requests
import pandas as pd
from sqlalchemy import create_engine

main_data_set_to_sql = pd.read_pickle(r"C:\Users\rejks\Desktop\Python\Flask\dummy.pkl")
movie_title = "Iron Man"
smth = main_data_set_to_sql.loc[main_data_set_to_sql["primaryTitle"]
                                              == movie_title].values.tolist()
print(smth)