# app.py
import json

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))



#________________________________________MOVIES___________________________________________
class MovieSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    description = fields.String()
    trailer = fields.String()
    year = fields.Integer()
    rating = fields.Float()
    genre_id = fields.Integer()
    director_id = fields.Integer()

movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()
movies_ns = api.namespace("movies")

@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        movies_all = Movie.query.all()
        return movies_schema.dump(movies_all), 200

@movies_ns.route('/<uid>')
class MovieView(Resource):
    def get(self, uid):
        movie = Movie.query.get(uid)
        return movie_schema.dump(movie), 200

@movies_ns.route('/director_id/<int:did>')
class Movie_by_dirView(Resource):
    def get(self, did):
        director = Director.query.get(did)
        director_name = director.name
        movies_raw = Movie.query.all()
        movies = movies_schema.dump(movies_raw)
        dir_movies = []

        for movie in movies:
            if movie['director_id'] == did:
                dir_movies.append(movie)
        result = {director_name: dir_movies}

        return jsonify(result), 200

@movies_ns.route('/genre_id/<int:gid>')
class Movie_by_genreView(Resource):
    def get(self, gid):
        genre = Genre.query.get(gid)
        genre_name = genre.name
        movies_raw = Movie.query.all()
        movies = movies_schema.dump(movies_raw)
        genre_movies = []

        for movie in movies:
            if movie['genre_id'] == gid:
                genre_movies.append(movie)
        result = {genre_name: genre_movies}

        return jsonify(result), 200

@movies_ns.route('/director_id=<int:did>&genre_id=<int:gid>')
class Movie_by_dir_and_genreView(Resource):
    def get(self, did, gid):
        director = Director.query.get(did)
        director_name = director.name
        genre = Genre.query.get(gid)
        genre_name = genre.name
        movies_raw = Movie.query.all()
        movies = movies_schema.dump(movies_raw)
        found_movies = []
        for movie in movies:
            if movie['director_id'] == did and movie['genre_id'] == gid:
                found_movies.append(movie)

        result = {f"{director_name}, {genre_name}": found_movies}
        return result, 200

#________________________________________DIRECTORS___________________________________________

class DirectorShema(Schema):
    id = fields.Integer()
    name = fields.String()


director_ns = api.namespace("directors")
directors_schema = DirectorShema(many=True)
director_schema = DirectorShema()

@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = Director.query.all()
        return directors_schema.dump(directors), 200

    def post(self):
        req_json = json.loads(request.data)
        new_director = Director(**req_json)
        db.session.add(new_director)
        db.session.commit()

        return f"Режиссер {new_director.name} зарегистрирован в базе данных", 201

@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did):
        director = Director.query.get(did)
        return director_schema.dump(director), 200


    def put(self, did):
        director = Director.query.get(did)
        req_json = json.loads(request.data)
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, did):
        director = Director.query.get(did)
        director_name = director.name
        db.session.delete(director)
        db.session.commit()
        return f"Режиссер {director_name} удален из базы данных", 204

#________________________________________GENRES___________________________________________

class GenreSchema(Schema):
    id = fields.Integer()
    name = fields.String()

genre_ns = api.namespace("genres")
genres_schema = GenreSchema(many=True)
genre_schema = GenreSchema()

@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = Genre.query.all()
        return genres_schema.dump(genres), 200

    def post(self):
        req_json = json.loads(request.data)
        new_genre = Genre(**req_json)
        genre_name = new_genre.name
        db.session.add(new_genre)
        db.session.commit()
        return f'Жанр {genre_name} добавлен в базу данных', 201

@genre_ns.route("/<int:gid>")
class GenreView(Resource):
    def get(self, gid):
        genre = Genre.query.get(gid)
        return genre_schema.dump(genre), 200

    def put(self, gid):
        genre = Genre.query.get(gid)
        req_json = json.loads(request.data)
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return '', 204

    def delete(self, gid):
        genre = Genre.query.get(gid)
        genre_name = genre.name
        db.session.delete(genre)
        db.session.commit()
        return f'Жанр {genre_name} удален из базы данных', 204

if __name__ == '__main__':
    app.run(debug=True)
