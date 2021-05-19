from flask import Flask, render_template, json, jsonify, request, current_app as app
from datetime import date
import os
import requests

app = Flask(__name__, static_folder="static")
json_info = ''
movies_path = os.path.join(app.static_folder, 'data', 'movies.json')
with open(movies_path, 'r') as raw_json:
    json_info = json.load(raw_json)
@app.route('/')
def index():
 return render_template('index.html')
#edit
@app.route('/about')
def about():
 return '<h1>About</h1><p>some other content</p>'

@app.route('/jo')
def jo():
 name = "Nicholas"
 ppl = ['A','B','C','D','E']
 return render_template('jo.html', name=name, ppl=ppl)

@app.route('/nasa')
def nasa():
 today = str(date.today())
 response = requests.get('https://api.nasa.gov/planetary/apod?api_key=wjlnR0Xw9B5Sh3WEIJa9kmVd368hNMiUVIGahGPi&date='+today)

 data = response.json()
 
 return render_template('nasa.html',data=data)

@app.route('/api/v1/movies', methods=['GET'])
def all_movies():
    movies_info = os.path.join(app.static_folder, 'data', 'movies.json')
    with open(movies_info, 'r') as json_data:
        json_info = json.load(json_data)
        return jsonify(json_info)

@app.route('/api/v2/movies', methods=['GET'])
def all_movies2():
    movies_info = os.path.join(app.static_folder, 'data', 'movies.json')
    with open(movies_info, 'r') as json_data:
        json_info = json.load(json_data)
        return render_template('movies_template.html', results=json_info)

@app.route('/api/v2/movies/search', methods=['GET'])
def search_title():
    results = []
    if 'title' in request.args:
        title = request.args['title']
        
        for movie in json_info:
            if title in movie['title']:
                results.append(movie)

    if len(results) < 1:
        return "No results found"
    return render_template("search_template.html", results=results)

@app.route('/api/v1/albums', methods=['GET'])
def albums_json():
    albums_info = os.path.join(app.static_folder, 'data', 'albums.json')
    with open(albums_info, 'r') as json_data:
        json_info = json.load(json_data)
        return jsonify(json_info)

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0') 