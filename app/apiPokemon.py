# Author: Chris McDonald
# Pokemon Web API

#!/usr/bin/env python

import datrie
import hashlib
import json
import string
from flask import Flask, jsonify, make_response, render_template, request, url_for
from flask.ext.httpauth import HTTPBasicAuth

from app import app
auth = HTTPBasicAuth()

trie = datrie.Trie(string.ascii_letters)
with open('data/pokemon.json') as file:
    data = json.load(file)
    file.close()

pokemon_json = data['pokemon']

for pokemon in pokemon_json:
    trie[pokemon['name']] = pokemon

@auth.get_password
def get_password(username):
    if username == 'admin':
        return 'admin'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route("/")
def hello():
    return render_template('index.html',items=pokemon_json,title='Home')

@app.route("/pokemon", methods=['GET'])
# @auth.login_required
def get_pokemon_name():
    return jsonify({'pokemon': [make_public_pokemon(pokemon) for pokemon in pokemon_json]})

@app.route("/search/<string:query>", methods=['GET'])
def trie_complete(query):
    if trie.has_keys_with_prefix(query):
        p = []
        for key, pokemon in trie.items(query):
            p.append(pokemon)
        return jsonify({'matches': [make_public_pokemon(pokemon) for pokemon in p]})
    else:
        return jsonify(trie.keys(query))

@app.route("/pokemon/<string:id>", methods=['GET'])
def get_pokemon_id(id):
    pokemon = [pokemon for pokemon in pokemon_json if pokemon['id'] == id]
    if len(pokemon) == 0:
        not_found(404)
    return jsonify({'pokemon': pokemon[0]})

@app.route('/pokemon', methods=['POST'])
def create_pokemon():
    if not request.json or not 'name' in request.json:
        abort(400)
    pokemon = {
        'id': pokemon_json[-1]['id'] + 1,
        'name': request.json['name'],
        'type': request.json.get('type', ""),
    }
    pokemon_json.append(pokemon)
    return jsonify({'pokemon': pokemon}), 201

@app.route('/pokemon/<int:id>', methods=['PUT'])
def update_pokemon(id):
    pokemon = [pokemon for pokemon in pokemon_json if pokemon['id'] == id]
    if len(pokemon) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != unicode:
        abort(400)
    if 'founded' in request.json and type(request.json['type']) is not unicode:
        abort(400)
    pokemon[0]['name'] = request.json.get('name', pokemon[0]['name'])
    pokemon[0]['type'] = request.json.get('type', pokemon[0]['type'])
    return jsonify({'pokemon': pokemon[0]})

@app.route('/pokemon/<int:id>', methods=['DELETE'])
def delete_pokemon(id):
    pokemon = [pokemon for pokemon in pokemon_json if pokemon['id'] == id]
    if len(pokemon) == 0:
        abort(404)
    pokemon_json.remove(pokemon[0])
    return jsonify({'result': True})

def make_public_pokemon(pokemon):
    new_pokemon = {}
    for field in pokemon:
        if field == 'id':
            new_pokemon['uri'] = url_for('get_pokemon_id', id=pokemon['id'], _external=True)
        else:
            new_pokemon[field] = pokemon[field]
    return new_pokemon

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)