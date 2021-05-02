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
from sqlalchemy import text
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database --> see config.py
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models --> see model.py.
#----------------------------------------------------------------------------#


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
  #places = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by('state').all()
  sql = text('select distinct city, state from venue order by state')
  places = db.engine.execute(sql)
  data = []
  for place in places:
      sql = text('select * from venue where state= :s and city= :c order by name')
      venues = db.engine.execute(sql,{"s":place.state, "c": place.city})
      venue_data = []
      
      data.append({
          'city': place.city,
          'state': place.state,
          'venues': venue_data
      })
      for venue in venues:
        sql = text('select count(*) from show where venue_id= :v')
        shows = db.engine.execute(sql, {"v": venue.id})
        venue_data.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': shows
        })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = search_term=request.form.get('search_term', '')
  sql = text("select * from venue where name ilike :s")
  venues = db.engine.execute(sql, {"s": "%"+search_term+"%"})
  sql2 = text("select count(*) from venue where name ilike :s")
  venues_length = db.engine.execute(sql2, {"s": "%"+search_term+"%"}).scalar()
  data = []
  current_datetime = datetime.now()

  for venue in venues:
    sql = text('select count(*) from show where venue_id= :v and start_date > :ct')
    shows = db.engine.execute(sql, {"v": venue.id, "ct":current_datetime}).scalar()
    venue_data = {
      "id" : venue.id,
      "name" : venue.name,
      "num_upcoming_shows": shows  
    }
    data.append(venue_data)
  response = {
    "count": venues_length,
    "data" : data
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  current_datetime = datetime.now()

  venue_sql = text("select * from venue where id= :id")
  venue = db.engine.execute(venue_sql, {"id":venue_id}).fetchone()
  if (venue == None):
    abort(404)

  past_shows_sql_count = text("select count(*) from show where venue_id=:id and start_date<:ct")
  past_shows_count = db.engine.execute(past_shows_sql_count, {"id":venue_id,"ct":current_datetime}).scalar()
  upcoming_shows_sql_count = text("select count(*) from show where venue_id=:id and start_date>:ct")
  upcoming_shows_count = db.engine.execute(upcoming_shows_sql_count, {"id":venue_id,"ct":current_datetime}).scalar()
  
  past_shows_sql = text("select * from artist inner join show on artist.id = show.artist_id where start_date<:ct and venue_id=:id")
  past_shows = db.engine.execute(past_shows_sql, {"id":venue_id,"ct": current_datetime})

  past_shows_arr = []
  past_shows_dict = {}
  for past_show in past_shows:
    past_shows_dict= {
      "artist_id": past_show.artist_id,
      "artist_name": past_show.name,
      "artist_image_link": past_show.image_link,
      "start_time": past_show.start_date.strftime("%m-%d-%Y %H:%M:%S")
    }
    past_shows_arr.append(past_shows_dict.copy())
  
  upcoming_shows_sql = text("select * from artist inner join show on artist.id = show.artist_id where start_date>:ct and venue_id=:id")
  upcoming_shows = db.engine.execute(upcoming_shows_sql, {"ct": current_datetime, "id":venue_id})
  upcoming_shows_arr = []
  upcoming_shows_dict = {}
  for upcoming_show in upcoming_shows:
    upcoming_shows_dict= {
      "artist_id": upcoming_show.artist_id,
      "artist_name": upcoming_show.name,
      "artist_image_link": upcoming_show.image_link,
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
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
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
    conn = db.engine.connect()
    trans = conn.begin()
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
        venue_sql = text("insert into venue (name,city,state,address,phone,genres,facebook_link,website_link,image_link,looking_for_talent,seeking_description) values (:n,:c,:s,:a,:p,:g,:f,:w,:i,:l,:sd)")
        conn.execute(venue_sql, {"n":name,"c":city, "s": state, "a":address, "p": phone, "g": genres, "f": facebook_link, "w": website_link, "i": image_link, "l": looking_for_talent, "sd": seeking_description})
        trans.commit()
    except:
        error = True
        trans.rollback()
        print(sys.exc_info())
    finally:
        conn.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        abort(404)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
  # on successful db insert, flash success
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  conn = db.engine.connect()
  trans = conn.begin()
  try:
      venue_sql = text("delete from venue where id=:id")
      conn.execute(venue_sql, {"id":venue_id})
  except:
      trans.rollback()
  finally:
      conn.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_sql = text("select * from artist")
  artists = db.engine.execute(artist_sql).fetchall()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = search_term=request.form.get('search_term', '')
  artists_sql = text("select * from artist where name ilike :s")
  artists = db.engine.execute(artists_sql, {"s": "%"+search_term+"%"})
  artist_length_sql = text("select count(*) from artist where name ilike :s")
  artist_length = db.engine.execute(artist_length_sql, {"s": "%"+search_term+"%"}).scalar()
  data = []
  current_datetime = datetime.now()
  
  
  for artist in artists:
    upcoming_shows_sql = text("select count(*) from show where artist_id=:a and start_date>:ct")
    upcoming_shows = db.engine.execute(upcoming_shows_sql, {"a":artist.id,"ct":current_datetime}).scalar()
    print(upcoming_shows)
    artist_data = {
      "id" : artist.id,
      "name" : artist.name,
      "num_upcoming_shows": upcoming_shows 
    }
    data.append(artist_data)
  response = {
    "count": artist_length,
    "data" : data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  current_datetime = datetime.now()

  artist_sql = text("select * from artist where id=:id")
  artist = db.engine.execute(artist_sql, {"id":artist_id}).fetchone()
  if (artist == None):
    abort(404)

  past_shows_sql_count = text("select count(*) from show where artist_id=:id and start_date<:ct")
  past_shows_count = db.engine.execute(past_shows_sql_count, {"id":artist_id,"ct":current_datetime}).scalar()
  upcoming_shows_sql_count = text("select count(*) from show where artist_id=:id and start_date>:ct")
  upcoming_shows_count = db.engine.execute(upcoming_shows_sql_count, {"id":artist_id,"ct":current_datetime}).scalar()
  past_shows_sql = text("select * from venue inner join show on venue.id = show.venue_id where start_date<:ct and artist_id=:id")
  past_shows = db.engine.execute(past_shows_sql, {"ct": current_datetime, "id":artist_id})

  past_shows_arr = []
  past_shows_dict = {}
  for past_show in past_shows:
    past_shows_dict= {
      "venue_id": past_show.venue_id,
      "venue_name": past_show.name,
      "venue_image_link": past_show.image_link,
      "start_time": past_show.start_date.strftime("%m-%d-%Y %H:%M:%S")
    }
    past_shows_arr.append(past_shows_dict.copy())
  
  upcoming_shows_sql = text("select * from venue inner join show on venue.id = show.venue_id where start_date>:ct and artist_id=:id")
  upcoming_shows = db.engine.execute(upcoming_shows_sql, {"ct": current_datetime, "id":artist_id})
  upcoming_shows_arr = []
  upcoming_shows_dict = {}
  for upcoming_show in upcoming_shows:
    upcoming_shows_dict= {
      "venue_id": upcoming_show.venue_id,
      "venue_name": upcoming_show.name,
      "venue_image_link": upcoming_show.image_link,
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
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_sql = text("select * from artist where id=:id")
  artist = db.engine.execute(artist_sql, {"id":artist_id}).fetchone()
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  req = request.form
  print(req)
  conn = db.engine.connect()
  trans = conn.begin()
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

    add_artist_sql = text("update artist set name=:n, city=:c, state=:s, phone=:p, genres=:g, facebook_link=:f, website_link=:w, image_link=:i, looking_for_venue=:l, seeking_description=:sd where id=:id")
    conn.execute(add_artist_sql, {"n":name, "c": city, "s": state, "p": phone, "g": genres, "f": facebook_link, "w": website_link, "i": image_link, "l": looking_for_venue, "sd": seeking_description, "id": artist_id})
    trans.commit()
  except:
    error = True
    trans.rollback()
    print(sys.exc_info())
  finally:
    conn.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    abort(404)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  #return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_sql = text("select * from venue where id=:id")
  venue = db.engine.execute(venue_sql, {"id":venue_id}).fetchone()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  req = request.form
  conn = db.engine.connect()
  trans = conn.begin()
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

    add_venue_sql = text("update venue set name=:n, city=:c, state=:s, address=:a, phone=:p, genres=:g, facebook_link=:f, website_link=:w, image_link=:i, looking_for_talent=:l, seeking_description=:sd where id=:id")
    conn.execute(add_venue_sql, {"n":name, "c": city, "s": state, "a": address, "p": phone, "g": genres, "f": facebook_link, "w": website_link, "i": image_link, "l": looking_for_talent, "sd": seeking_description, "id": venue_id})
    trans.commit()
  except:
    error = True
    trans.rollback()
    print(sys.exc_info())
  finally:
    conn.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    abort(404)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))


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
  conn = db.engine.connect()
  trans = conn.begin()
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
    artist_sql = text("insert into artist (name,city,state,phone,genres,facebook_link,website_link,image_link,looking_for_venue,seeking_description) values (:n,:c,:s,:p,:g,:f,:w,:i,:l,:sd)")
    conn.execute(artist_sql, {"n":name,"c":city, "s": state, "p": phone, "g": genres, "f": facebook_link, "w": website_link, "i": image_link, "l": looking_for_venue, "sd": seeking_description})
    trans.commit()
    
  except:
    error = True
    trans.rollback()
    print(sys.exc_info())
  finally:
    conn.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    abort(404)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows_sql = text("select * from show")
  shows = db.engine.execute(shows_sql).fetchall()
  data1 = []
  show_data = {}
  for show in shows:
    venue_sql = text("select * from venue where id = :id")
    venue = db.engine.execute(venue_sql, {"id":show.venue_id}).fetchone()
    artist_sql = text("select * from artist where id = :id")
    artist = db.engine.execute(artist_sql, {"id":show.artist_id}).fetchone()
    show_data = {
      "venue_id":show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_date.strftime("%m-%d-%Y %H:%M:%S")
      }
    data1.append(show_data.copy())
  
  return render_template('pages/shows.html', shows=data1)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  req = request.form
  conn = db.engine.connect()
  trans = conn.begin()
  try:
    artist_id = req['artist_id']
    venue_id = req['venue_id']
    start_date = req['start_time']
    
    show_sql = text("insert into show (artist_id, venue_id, start_date) values (:a,:v,:s)")
    
    conn.execute(show_sql, {"a":artist_id,"v":venue_id, "s": start_date})
    trans.commit()
  except:
    error = True
    trans.rollback()
    print(sys.exc_info())
  finally:
    conn.close()
  if error:
    flash('An error occurred. Show could not be listed.')
    abort(404)
  else:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')

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
