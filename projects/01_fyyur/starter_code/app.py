#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import app, db, Venue, Artist, Show






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
    locals = []
    venues = Venue.query.all()
    for place in Venue.query.distinct(Venue.city, Venue.state).order_by(Venue.city.desc(), Venue.state.desc()).all():
        locals.append({
            'city': place.city,
            'state': place.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
            } for venue in venues if
                venue.city == place.city and venue.state == place.state]
        })
    return render_template('pages/venues.html', areas=locals)





@app.route('/venues/search', methods=['POST','GET'])
def search_venues():

  
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []

  for venue in venues:
    num_upcoming_shows = 0
    shows = db.session.query(Show).filter(Show.venue_id == venue.id)
    for show in shows:
      if (show.start_time > datetime.now()):
        num_upcoming_shows += 1
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  results={
    "count": len(venues),
    "data": data
  }

  return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the individual venue page with the given venue_id
  

  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time < datetime.now()
    ).\
    all()

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time > datetime.now()
    ).\
    all()

  data = {
    'id': venue.id,
    'name': venue.name,
    'city': venue.city,
    'state': venue.state,
    'address': venue.address,
    'phone': venue.phone,
    'image_link': venue.image_link,
    'facebook_link': venue.facebook_link,
    'website': venue.website,
    'genres': venue.genres,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    
    'past_shows': list([{
      'artist_id': artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M')
    } for artist, show in past_shows]),
    'upcoming_shows': list([{
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M')
    } for artist, show in upcoming_shows]),
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
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

  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
        venue = Venue()
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash('The Venue was successfully listed!')
    except ValueError as e:
        print(e)
        flash('An error occurred. The Venue could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
  return render_template('pages/home.html')


  

@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The Venue has been successfully deleted!')
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('Delete was unsuccesful. Try again!')
  finally:
    db.session.close()
  return None
 
  


  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({'id': artist.id, 'name': artist.name})
  return render_template('pages/artists.html', artists=artists)







@app.route('/artists/search', methods=['POST', 'GET'])
def search_artists():

  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  data = []

  for artist in artists:
    num_upcoming_shows = 0
    shows = db.session.query(Show).filter(Show.artist_id == artist.id)
    for show in shows:
      if (show.start_time > datetime.now()):
        num_upcoming_shows += 1
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
 

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
      Show.artist_id == artist_id,
      Show.venue_id == Venue.id,
      Show.start_time < datetime.now()
    ).\
    all()

  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
      Show.artist_id == artist_id,
      Show.venue_id == Venue.id,
      Show.start_time > datetime.now()
    ).\
    all()

  data = {
    'id': artist.id,
    'name': artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'website': artist.website,
    'genres': artist.genres,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    
    'past_shows': list([{
      'venue_id': venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M')
    } for venue, show in past_shows]),
    'upcoming_shows': list([{
      'venue': venue.id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M')
    } for venue, show in upcoming_shows]),
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }
    
  return render_template('pages/show_artist.html', artist=data)


 



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form['genres']
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website = request.form['website']
    artist.seeking_venue = True if request.form['seeking_venue']== 'y' else False
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
    db.session.close()
  
  if not error:
    flash('The Artist has been updated!')
  if error:
    flash('The Artist could not be updated!')
        
  return redirect(url_for('show_artist', artist_id=artist_id))






@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(request.form, meta={"csrf": False})
  if form.validate():
    try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data,
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website = form.website.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
        flash('The Venue has been successfully updated!')
    except Exception as e:
          print(e)
          print(sys.exc_info())
          db.session.rollback()
          flash('The Venue could not be updated!')
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
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        flash('The Artist was successfully listed!')
    except ValueError as e:
        print(e)
        flash('The Artist could not be listed!')
        db.session.rollback()
    finally:
        db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
  return render_template('pages/home.html')

  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.order_by(Show.start_time.desc()).all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
    artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
    data.extend([{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M')

    }])
  
  return render_template('pages/shows.html', shows=data)
  

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm(request.form)
  show = Show(
    artist_id = form.artist_id.data,
    venue_id = form.venue_id.data,
    start_time = form.start_time.data
  )
  try:
    db.session.add(show)
    db.session.commit()
  
  except Exception as e:
    error = True
    print(f'Error ==> {e}')
    db.session.rollback()

  finally:
    db.session.close()
    if error: flash('An error occurred. Show could not be listed.')
    else: flash('Show was successfully listed!')
  
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
