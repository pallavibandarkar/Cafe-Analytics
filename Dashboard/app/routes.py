from flask import Blueprint, jsonify, render_template,redirect
import pandas as pd
from config import Config

# Define the main Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
   return redirect('/dash/')