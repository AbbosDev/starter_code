#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

# Abbas Al-Akashi

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
import datetime
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

###migration
migrate = Migrate(app, db)

# COMPLETED TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    generes= db.Column(db.String())    
    website= db.Column(db.String)
    seeking_talent= db.Column(db.Boolean, default=False)
    seeking_description= db.Column(db.String())
    

    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<SHOW {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue= db.Column(db.Boolean, default=False)
    seeking_description= db.Column(db.String())

    shows = db.relationship('Show', backref='artist', lazy=True)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
	__tablename__ = 'Show'
	id = db.Column(db.Integer, primary_key=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
	venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
	start_time = db.Column(db.DateTime, nullable=False)
	
	def __repr__(self):
		return f'<SHOW {self.venue_item} {self.artist_item}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
	
	#data=[{ "city": "San Francisco", "state": "CA", "venues": [{ "id": 1, "name": "The Musical Hop", "num_upcoming_shows": 0, }, { "id": 3, "name": "Park Square Live Music & Coffee", "num_upcoming_shows": 1, }]}, { "city": "New York", "state": "NY", "venues": [{ "id": 2, "name": "The Dueling Pianos Bar", "num_upcoming_shows": 0, }] }]
	
	areas2 = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
	data = []
	for area in areas2:
		areas2 = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
		venues = []
		for venue in areas2:
			upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time >= datetime.now()).count()
			venues.append({ 'id':venue.id, 'name': venue.name, 'num_upcoming_shows': upcoming_shows})
			for show in venues:
				print("THIS IS UPCOMING SHOWS: ", upcoming_shows)
		data.append({ 'city':area.city, 'state':area.state, 'venues':venues, 'num_upcoming_shows':upcoming_shows })

	#venue_data.append({ 'id':venue.id, 'name':venue.name, 'num_upcoming_shows': len(db.session.query(Show).filter(Show.show_date>datetime.now()).all())})

	return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for Hop should return "The Musical Hop".
	# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"	
	#response={ "count": 1, "data": [{ "id": 2, "name": "The Dueling Pianos Bar", "num_upcoming_shows": 0, }] }
	
	search_term = request.form.get('search_term', None)
	venues = Venue.query.filter(Venue.name.match("'%{}%'".format(search_term))).all()
	#venues = Venue.query.filter(Venue.name.like("%{}%".format(search_term))).all()
	print("FOUND: ", venues)
	count_venues = len(venues)
	print("COUNTED THIS MANY VENUES: ", count_venues)
	
	upcoming_shows = 0
	
	response = []
	for us in venues:
		upcoming_shows = Show.query.filter_by(venue_id=us.id).filter(Show.start_time >= datetime.now()).count()
		#response.append({"count": count_venues, "data": us, "num_upcoming_shows": upcoming_shows })
		
	response = { "count": count_venues, "data": [v for v in venues], "num_upcoming_shows": upcoming_shows }
	
	print("THIS IS THE RESPONSE: ", response)
	return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = db.session.query(Venue).filter(Venue.id == venue_id).all()
  list_shows = db.session.query(Show).filter(Show.venue_id == venue_id).all()
  past_shows = []
  upcoming_shows = []
  
  for show in list_shows:
    artist = []
    artist = Artist.query.filter_by(id = show.artist_id).all()
    #db.session.query(Artist.name, Artist.image_link).filter(show.artist_id == Artist.id)
    
    for a in artist:
      all_show= {
        "artist_id": show.artist_id,
        "artist_name":a.name,
        "artist_image_link": a.image_link,
        "start_time": show.start_time.strftime('%m/%d/%Y')
      }

    if(show.start_time < datetime.now()):
      past_shows.append(all_show)
    else:
      upcoming_shows.append(all_show)
    
  for v in venue:
      data={
        "id": v.id,
        "name": v.name,
        "generes": v.generes,
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
      }
  
  return render_template('pages/show_venue.html', venue=data)
  
"""
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id

	print("I AM HERE")

	print("THIS IS VENUE_ID: ", venue_id)

	venues_list = Venue.query.filter_by(id = venue_id).all()
	data_list = []
	upcoming_shows_cnt = 0

	

	past_shows_cnt = 0
	past_show_list = []
	upcmg_show_list = []
	for v2 in venues_list:
		print("THIS IS V2", v2)
		upcmg_show_list.append(Show.query.filter_by(artist_id=v2.id).filter(Show.start_time >= datetime.now()).all())
		past_show_list.append(Show.query.filter_by(artist_id=v2.id).filter(Show.start_time <= datetime.now()).all())
		upcoming_shows_cnt = Show.query.filter_by(venue_id=v2.id).filter(Show.start_time >= datetime.now()).count()
		past_shows_cnt = Show.query.filter_by(venue_id=v2.id).filter(Show.start_time <= datetime.now()).count()

		data_list.append({ "id":v2.id, "name": v2.id, "genres":v2.generes, "address": v2.address, "city": v2.city, "state": v2.state, "phone": v2.phone, "website": v2.website, "facebook_link": v2.facebook_link, "seeking_talent": v2.seeking_talent, "seeking_description": v2.seeking_description, "image_link": v2.image_link, "past_shows": [ps for ps in past_show_list], "upcoming_shows": [us2 for us2 in upcmg_show_list], "past_shows_count": past_shows_cnt , "upcoming_shows_count": upcoming_shows_cnt })
	
	print("THIS IS THE DATA: \n", data_list)

	#data = list(filter( dList == venue_id, [dList for dList in data_list]))
	#data = list(filter(lambda d: d['id'] == venue_id, data_list))[0]
	
	data = [data_list]
	
	print(data)	

	return render_template('pages/show_venue.html', venue=data)

  data1={
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
"""


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    ven_name = request.form.get('name')
    city_name = request.form.get('city')
    state_name = request.form.get('state')
    address_venue = request.form.get('address')
    phone_nbr = request.form.get('phone')
    genres_ven = request.form.get('genres')
    facebook = request.form.get('facebook_link')
    
    venue_list = Venue(name = ven_name, city = city_name, state = state_name, address = address_venue, phone = phone_nbr, generes = genres_ven, facebook_link = facebook)

    db.session.add(venue_list)

    db.session.commit()
    
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
    flash('AN ERROR OCCURED. VENUE ' + data.name + ' COULD NOT BE LISTED.')
    print("THERE HAS BEEN AN ERROR")

  finally:
    db.session.close()

  
  # TODO: modify data to be the data object returned from db insertion


  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    Venue.query.filter_by(id = venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	# TODO: replace with real data returned from querying the database
	
	areas3 = db.session.query(Artist.id, Artist.name).distinct(Artist.id, Artist.id)
	data = []
	for area in areas3:
		areas3 = Artist.query.filter_by(name=area.name).filter_by(id=area.id).all()
		venues = []
		data.append({ 'id':area.id, 'name':area.name })

	return render_template('pages/artists.html', artists=data)

"""
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
"""
  
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', None)
  artist = Artist.query.filter(Artist.name.match("'%{}%'".format(search_term))).all()
  print("FOUND: ", artist)
  count_artist = len(artist)
  
  print("COUNTED THIS MANY Artist: ", count_artist)
	
  upcoming_shows = 0
	
  response = []
  for us in artist:
    upcoming_shows = Show.query.filter_by(artist_id=us.id).filter(Show.start_time >= datetime.now()).count()
  
  #response.append({"count": count_venues, "data": us, "num_upcoming_shows": upcoming_shows })
  
  response = { "count": count_artist, "data": [a for a in artist], "num_upcoming_shows": upcoming_shows }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

"""
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
"""
  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  
  art = Artist.query.filter(Artist.id == artist_id).one_or_none()
  #past_shows, upcoming_shows
  shows = Show.query.filter(Show.artist_id==artist_id).all()
  past_shows =[]
  upcoming_shows=[]
  for show in shows:
        date_time_str = show.start_time
        #date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
        date_time_obj = date_time_str
        if date_time_obj < datetime.now():
              past_show = {"artist_image_link": show.artist.image_link, "artist_id": show.artist.id,
              "artist_name":show.artist.name, "start_time": show.start_time} 
              past_shows.append(past_show)                
        else:
              upcoming_show = {"artist_image_link": show.artist.image_link, "artist_id": show.artist.id,
              "artist_name":show.artist.name, "start_time": show.start_time}
              upcoming_shows.append(upcoming_show)

  return render_template('pages/show_artist.html', artist=art, upcoming_shows=upcoming_shows, past_shows = past_shows)
  #return render_template('pages/show_venue.html', venue=venue, upcoming_shows=upcoming_shows, past_shows=past_shows)
"""
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
"""
  
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj = artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

"""
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
"""
  
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)
  
  try:
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.get('genres')
    artist.facebook_link = request.form.get('facebook_link')
    
    #artist_list = Artist(name = ven_name, city = city_name, state = state_name, phone = phone_nbr, generes = genres_ven, facebook_link = facebook)

    db.session.commit()
  
  except:
    db.session.rollback()

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj = venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


"""
venue={
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
  }
"""
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  
  try:
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.address = request.form.get('address')
    venue.generes = request.form.get('genres')
    venue.facebook_link = request.form.get('facebook_link')
    
    #artist_list = Artist(name = ven_name, city = city_name, state = state_name, phone = phone_nbr, generes = genres_ven, facebook_link = facebook)

    db.session.commit()
  
  except:
    db.session.rollback()

  finally:
    db.session.close()

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

  try:
    ven_name = request.form.get('name')
    city_name = request.form.get('city')
    state_name = request.form.get('state')
    phone_nbr = request.form.get('phone')
    genres_ven = request.form.get('genres')
    facebook = request.form.get('facebook_link')
    
    art_list = Artist(name = ven_name, city = city_name, state = state_name, phone = phone_nbr, genres = genres_ven, facebook_link = facebook)

    db.session.add(art_list)

    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    db.session.rollback()
    flash('AN ERROR OCCURED. ART ' + request.form['name'] + ' COULD NOT BE LISTED.')
    print("THERE HAS BEEN AN ERROR")

  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()
  for show in shows:
    artist =[]
    
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show[0])
    venue = db.session.query(Venue.name).filter(Venue.id == show[1])
    
    for a, v in zip(artist, venue):
      data.append({
        "venue_id": show.venue_id,
        "venue_name":v.name,
        "artist_id":show.artist_id,
        "artist_name":a.name,
        "artist_image_link":a.image_link,
        "start_time": str(show.start_time)
      })

  return render_template('pages/shows.html', shows=data)


"""
areas3 = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()

  data = []
  venue = []
  artist = []

  for area in areas3:
    venue = Venue.query.filter_by(id=area.venue_id).all()
    artist = Artist.query.filter_by(id=area.artist_id).all()
    
    data.append({ "venue_id": area.venue_id, "venue_name":[v.name for v in venue], "artist_id":area.artist_id, "artist_name":artist[0], "image_link":[a.image_link for a in artist], "start_time":area.start_time })

  data=[{
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
  }]
"""


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead


  try:
    artistId = request.form.get('artist_id')
    venueId = request.form.get('venue_id')
    startTime = request.form.get('start_time')
    
    show_list = Show(artist_id = artistId, venue_id = venueId, start_time = startTime )

    db.session.add(show_list)

    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    db.session.rollback()

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')

  finally:
    db.session.close()

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
