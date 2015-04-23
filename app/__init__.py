#!/usr/bin/env python

from flask import Flask
from flask.ext.cors import CORS

app = Flask(__name__)

from app import apiPokemon