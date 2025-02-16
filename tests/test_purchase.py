import pytest
from run import app, db
from app.models import User, Merch, Transaction, seed_merch
from flask_jwt_extended import create_access_token
