#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime
from model import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#db = SQLAlchemy(app)
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
'''
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    looking_for_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    show = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
  ################
  ###   DONE  ####
  ################

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    looking_for_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    show = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
'''
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
################
###   DONE  ####
################
##### TODO Flask migrate muss ich nach Tests noch ausführen#######

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  places = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by('state').all()
  data = []
  for place in places:
      venues = Venue.query.filter_by(state=place.state).filter_by(city=place.city).order_by('name').all()
      venue_data = []
      data.append({
          'city': place.city,
          'state': place.state,
          'venues': venue_data
      })
      for venue in venues:
          shows = Show.query.filter_by(venue_id=venue.id).order_by('id').all()
          venue_data.append({
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': len(shows)
          })

  '''data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]'''
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  print(venues)
  data = []
  current_datetime = datetime.now()

  for venue in venues:
    venue_data = {
      "id" : venue.id,
      "name" : venue.name,
      "num_upcoming_shows": Show.query.filter(Show.start_date > current_datetime,Show.venue_id==venue.id).count() 
    }
    data.append(venue_data)
  response = {
    "count": len(venues),
    "data" : data
  }
  '''response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }'''
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  current_datetime = datetime.now()
  past_shows = Show.query.filter(Show.start_date < current_datetime, Show.venue_id==venue_id).all()
  upcoming_shows = Show.query.filter(Show.start_date > current_datetime, Show.venue_id==venue_id).all()

  past_shows_arr = []
  past_shows_dict = {}
  for past_show in past_shows:
    past_shows_dict= {
      "artist_id": past_show.artist.id,
      "artist_name": past_show.artist.name,
      "artist_image_link": past_show.artist.image_link,
      "start_time": past_show.start_date.strftime("%m-%d-%Y %H:%M:%S")
    }
    past_shows_arr.append(past_shows_dict.copy())
  
  upcoming_shows_arr = []
  upcoming_shows_dict = {}
  for upcoming_show in upcoming_shows:
    upcoming_shows_dict= {
      "artist_id": upcoming_show.artist.id,
      "artist_name": upcoming_show.artist.name,
      "artist_image_link": upcoming_show.artist.image_link,
      "start_time": upcoming_show.start_date.strftime("%m-%d-%Y %H:%M:%S")
    }
    upcoming_shows_arr.append(upcoming_shows_dict.copy())


  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.looking_for_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_arr,
    "upcoming_shows": upcoming_shows_arr,
    "past_shows_count": Show.query.filter(Show.start_date < current_datetime, Show.venue_id==venue_id).count(),
    "upcoming_shows_count": Show.query.filter(Show.start_date > current_datetime,Show.venue_id==venue_id).count(),
  }
  
  '''data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]'''
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    error = False
    req = request.form
    try:
        name = req['name']
        city = req['city']
        state = req['state']
        address = req['address']
        phone = req['phone']
        genres = req['genres']
        facebook_link = req['facebook_link']
        website_link = req['website_link']
        image_link = req['image_link']
        looking_for_talent = False
        if 'seeking_talent' in req:
          looking_for_talent = True
        seeking_description = req['seeking_description']
        print(looking_for_talent)
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, 
        genres=genres, facebook_link=facebook_link, website_link=website_link, image_link=image_link, 
        looking_for_talent=looking_for_talent,seeking_description=seeking_description)
        #todo = Todo(description=description, list_id=list_id)
        db.session.add(venue)
        db.session.commit()
        #body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        abort(400)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  ################
  ###   DONE  ####
  ################

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  return None
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None
  ################
  ### DONE??? ####
  ################

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  '''data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]'''
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  data = []
  current_datetime = datetime.now()

  for artist in artists:
    artist_data = {
      "id" : artist.id,
      "name" : artist.name,
      "num_upcoming_shows": Show.query.filter(Show.start_date > current_datetime,Show.artist_id==artist.id).count() 
    }
    data.append(artist_data)
  response = {
    "count": len(artists),
    "data" : data
  }
  '''response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }'''
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  current_datetime = datetime.now()
  past_shows = Show.query.filter(Show.start_date < current_datetime, Show.artist_id==artist_id).all()
  upcoming_shows = Show.query.filter(Show.start_date > current_datetime, Show.artist_id==artist_id).all()

  past_shows_arr = []
  past_shows_dict = {}
  for past_show in past_shows:
    past_shows_dict= {
      "venue_id": past_show.venue.id,
      "venue_name": past_show.venue.name,
      "venue_image_link": past_show.venue.image_link,
      "start_time": past_show.start_date.strftime("%m-%d-%Y %H:%M:%S")
    }
    past_shows_arr.append(past_shows_dict.copy())
  
  upcoming_shows_arr = []
  upcoming_shows_dict = {}
  for upcoming_show in upcoming_shows:
    upcoming_shows_dict= {
      "venue_id": upcoming_show.venue.id,
      "venue_name": upcoming_show.venue.name,
      "venue_image_link": upcoming_show.venue.image_link,
      "start_time": upcoming_show.start_date.strftime("%m-%d-%Y %H:%M:%S")
    }
    upcoming_shows_arr.append(upcoming_shows_dict.copy())


  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_for_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_arr,
    "upcoming_shows": upcoming_shows_arr,
    "past_shows_count": Show.query.filter(Show.start_date < current_datetime, Show.artist_id==artist_id).count(),
    "upcoming_shows_count": Show.query.filter(Show.start_date > current_datetime,Show.artist_id==artist_id).count(),
  }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist1 = Artist.query.get(artist_id)
  '''artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay place!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }'''
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist1)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  artist = Artist.query.get(artist_id)
  req = request.form
  print(req)
  try:
    artist.name = req['name']
    artist.city = req['city']
    artist.state = req['state']
    artist.phone = req['phone']
    artist.genres = req['genres']
    artist.facebook_link = req['facebook_link']
    artist.website_link = req['website_link']
    artist.image_link = req['image_link']
    artist.looking_for_venue = False
    if 'seeking_venue' in req:
      artist.looking_for_venue = True
    artist.seeking_description = req['seeking_description']

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    abort(400)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  #return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  '''venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }'''
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)
  req = request.form
  print(req)
  try:
    venue.name = req['name']
    venue.city = req['city']
    venue.state = req['state']
    venue.address = req['address']
    venue.phone = req['phone']
    venue.genres = req['genres']
    venue.facebook_link = req['facebook_link']
    venue.website_link = req['website_link']
    venue.image_link = req['image_link']
    venue.looking_for_talent = False
    if 'seeking_talent' in req:
      venue.looking_for_talent = True
    venue.seeking_description = req['seeking_description']

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    abort(400)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  #return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  req = request.form
  print(req)
  try:
    
    name = req['name']
    city = req['city']
    state = req['state']
    phone = req['phone']
    genres = req['genres']
    facebook_link = req['facebook_link']
    website_link = req['website_link']
    image_link = req['image_link']
    looking_for_venue = False
    if 'seeking_venue' in req:
      looking_for_venue = True
    seeking_description = req['seeking_description']
    print(looking_for_venue)
    
    artist = Artist(name=name, city=city, state=state, phone=phone, 
    genres=genres, facebook_link=facebook_link, website_link=website_link, image_link=image_link, 
    looking_for_venue=looking_for_venue,seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    abort(400)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data1 = []
  show_data = {}
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    show_data = {
      "venue_id":show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_date.strftime("%m-%d-%Y %H:%M:%S")
      }
    data1.append(show_data.copy())
  print(data1)
  '''data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]'''
  return render_template('pages/shows.html', shows=data1)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  req = request.form
  print(req)
  try:
    artist_id = req['artist_id']
    venue_id = req['venue_id']
    start_date = req['start_time']
    
    show = Show(artist_id=artist_id, venue_id=venue_id, start_date=start_date)

    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
    abort(400)
  else:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
