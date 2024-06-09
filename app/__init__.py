from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import jwt
from functools import wraps
import os
from datetime import datetime, timedelta
from pymongo import MongoClient

MONGO_HOST = "10.10.10.20"
MONGO_DBUSER = "mongoadmin"
MONGO_DBPASS = "mongopass"
MONGO_DBNAME = "API_LDAP"
MONGO_COLLECTIONNAME = "logs"


app = Flask(__name__)
# Needed for the Javascript error
CORS(app)

from app import views
