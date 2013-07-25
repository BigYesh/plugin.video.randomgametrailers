# Random trailer player
#
# Author - kzeleny
# Version - 1.0.6
# Compatibility - Frodo
#

import xbmc
import xbmcgui
from urllib import quote_plus, unquote_plus
import re
import sys
import os
import random
import simplejson as json
import time
import datetime
import xbmcaddon
import MyFont
addon = xbmcaddon.Addon()
number_trailers =  addon.getSetting('number_trailers')
do_password = addon.getSetting('do_password')
password = addon.getSetting('password')
do_curtains = addon.getSetting('do_animation')
do_genre = addon.getSetting('do_genre')
do_mute = addon.getSetting('do_mute')
hide_info = addon.getSetting('hide_info')
addon_path = addon.getAddonInfo('path')
hide_watched = addon.getSetting('hide_watched')
watched_days = addon.getSetting('watched_days')
resources_path = xbmc.translatePath( os.path.join( addon_path, 'resources' ) ).decode('utf-8')
media_path = xbmc.translatePath( os.path.join( resources_path, 'media' ) ).decode('utf-8')
open_curtain_path = xbmc.translatePath( os.path.join( media_path, 'OpenSequence.mp4' ) ).decode('utf-8')
close_curtain_path = xbmc.translatePath( os.path.join( media_path, 'ClosingSequence.mp4' ) ).decode('utf-8')
selectedGenre =''
exit_requested = False
movie_file = ''
if len(sys.argv) == 2:
	do_genre ='false'

# Emulate Confluence fonts
MyFont.addFont( "addon_font12" , "arial.ttf" , "15")
MyFont.addFont( "addon_font13" , "arial.ttf" , "18")
MyFont.addFont( "addon_font14" , "arial.ttf" , "20")
MyFont.addFont( "addon_font15" , "arial.ttf" , "22")
MyFont.addFont( "addon_font35_title" , "arial.ttf" , "33" , style = "bold")
trailer=''
do_timeout = False
def askGenres():
  # default is to select from all movies
  selectGenre = False
  # ask user whether they want to select a genre
  a = xbmcgui.Dialog().yesno("Select genre", "Do you want to select a genre to watch?")
  # deal with the output
  if a == 1: 
    # set filter
    selectGenre = True
  return selectGenre  
  
def selectGenre():
  success = False
  selectedGenre = ""
  myGenres = []
  trailerstring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties": ["genre", "playcount", "file", "trailer"]}, "id": 1}')
  trailerstring = unicode(trailerstring, 'utf-8', errors='ignore')
  trailers = json.loads(trailerstring)
  for movie in trailers["result"]["movies"]:
    # Let's get the movie genres
    genres = movie["genre"]
    for genre in genres:
        # check if the genre is a duplicate
        if not genre in myGenres:
          # if not, add it to our list
          myGenres.append(genre)
  # sort the list alphabeticallt        
  mySortedGenres = sorted(myGenres)
  # prompt user to select genre
  selectGenre = xbmcgui.Dialog().select("Select genre:", mySortedGenres)
  # check whether user cancelled selection
  if not selectGenre == -1:
    # get the user's chosen genre
    selectedGenre = mySortedGenres[selectGenre]
    success = True
  else:
    success = False
  # return the genre and whether the choice was successfult
  return success, selectedGenre
  
def getTrailers(genre):
	# get the raw JSON output
	trailerstring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["title", "lastplayed", "studio", "writer", "plot", "votes", "top250", "originaltitle", "director", "tagline", "fanart", "runtime", "mpaa", "rating", "thumbnail", "file", "year", "genre", "trailer"], "filter": {"field": "genre", "operator": "contains", "value": "%s"}}, "id": 1}' % genre)
	trailerstring = unicode(trailerstring, 'utf-8', errors='ignore')
	trailers = json.loads(trailerstring)	
	return trailers

class movieWindow(xbmcgui.WindowXMLDialog):

	def onInit(self):
		global SelectedGenre
		global trailer
		global do_timeout
		trailer=random.choice(trailers["result"]["movies"])
		lastPlay = True
		if not trailer["lastplayed"] =='' and hide_watched == 'true':
			pd=time.strptime(trailer["lastplayed"],'%Y-%m-%d %H:%M:%S')
			pd = time.mktime(pd)
			pd = datetime.datetime.fromtimestamp(pd)
			lastPlay = datetime.datetime.now() - pd
			lastPlay = lastPlay.days
			if lastPlay > int(watched_days) or watched_days == '0':
				lastPlay = True
			else:
				lastPlay = False
		if  trailer["trailer"] != '' and lastPlay:
			if hide_info == 'false':
				w=infoWindow('script-DialogVideoInfo.xml',addon_path,'default')
				do_timeout=True
				w.doModal()
				do_timeout=False
				del w
				if exit_requested:
					xbmc.Player().stop()
			else:
				xbmc.Player().play(trailer["trailer"])
			self.getControl(30011).setLabel(trailer["title"] + ' - ' + str(trailer["year"]))
			self.getControl(30011).setVisible(True)
			while xbmc.Player().isPlaying():				
				xbmc.sleep(250)
		self.close()
		
	def onAction(self, action):
		ACTION_PREVIOUS_MENU = 10
		ACTION_BACK = 92
		ACTION_ENTER = 7
		ACTION_I = 11
		ACTION_LEFT = 1
		ACTION_RIGHT = 2
		ACTION_UP = 3
		ACTION_DOWN = 4
		ACTION_TAB = 18
		
		xbmc.log('action  =' + str(action.getId()))
		
		global exit_requested
		global movie_file
		if action == ACTION_PREVIOUS_MENU or action == ACTION_LEFT or action == ACTION_BACK:
			xbmc.Player().stop()
			exit_requested = True
			self.close()

		if action == ACTION_RIGHT or action == ACTION_TAB:
			xbmc.Player().stop()
			
		if action == ACTION_ENTER:
			exit_requested = True
			xbmc.Player().stop()
			movie_file = trailer["file"]
			self.getControl(30011).setVisible(False)
			self.close()
		
		if action == ACTION_I or action == ACTION_UP:
			self.getControl(30011).setVisible(False)
			w=infoWindow('script-DialogVideoInfo.xml',addon_path,'default')
			w.doModal()
			self.getControl(30011).setVisible(True)
			
class infoWindow(xbmcgui.WindowXMLDialog):

	def onInit(self):
		self.getControl(30001).setImage(trailer["thumbnail"])
		self.getControl(30003).setImage(trailer["fanart"])
		self.getControl(30002).setLabel(trailer["title"])
		self.getControl(30012).setLabel(trailer["tagline"])
		self.getControl(30004).setLabel(trailer["originaltitle"])
		directors = trailer["director"]
		movieDirector=''
		for director in directors:
			movieDirector = movieDirector + director + ', '
			if not movieDirector =='':
				movieDirector = movieDirector[:-2]
		self.getControl(30005).setLabel(movieDirector)
		writers = trailer["writer"]
		movieWriter=''
		for writer in writers:
			movieWriter = movieWriter + writer + ', '
			if not movieWriter =='':
				movieWriter = movieWriter[:-2]
		self.getControl(30006).setLabel(movieWriter)
		strImdb=''
		if not trailer["top250"] == 0:
			strImdb = ' - IMDB Top 250:' + str(trailer["top250"]) 
		self.getControl(30007).setLabel(str(round(trailer["rating"],2)) + ' (' + str(trailer["votes"]) + ' votes)' + strImdb)
		self.getControl(30009).setText(trailer["plot"])
		movieStudio=''
		studios=trailer["studio"]
		for studio in studios:
			movieStudio = movieStudio + studio + ', '
			if not movieStudio =='':
				movieStudio = movieStudio[:-2]
		self.getControl(30010).setLabel(movieStudio + ' - ' + str(trailer["year"]))
		movieGenre=''
		genres = trailer["genre"]
		for genre in genres:
			movieGenre = movieGenre + genre + ' / '
		if not movieGenre =='':
			movieGenre = movieGenre[:-3]
		self.getControl(30011).setLabel(str(trailer["runtime"] / 60) + ' Minutes - ' + movieGenre)
		imgRating='ratings/notrated.png'
		if trailer["mpaa"].startswith('G'): imgRating='ratings/g.png'
		if trailer["mpaa"] == ('G'): imgRating='ratings/g.png'
		if trailer["mpaa"].startswith('Rated G'): imgRating='ratings/g.png'
		if trailer["mpaa"].startswith('PG '): imgRating='ratings/pg.png'
		if trailer["mpaa"] == ('PG'): imgRating='ratings/pg.png'
		if trailer["mpaa"].startswith('Rated PG'): imgRating='ratings/pg.png'
		if trailer["mpaa"].startswith('PG-13 '): imgRating='ratings/pg13.png'
		if trailer["mpaa"] == ('PG-13'): imgRating='ratings/pg13.png'
		if trailer["mpaa"].startswith('Rated PG-13'): imgRating='ratings/pg13.png'
		if trailer["mpaa"].startswith('R '): imgRating='ratings/r.png'
		if trailer["mpaa"] == ('R'): imgRating='ratings/r.png'
		if trailer["mpaa"].startswith('Rated R'): imgRating='ratings/r.png'
		if trailer["mpaa"].startswith('NC17'): imgRating='ratings/nc17.png'
		if trailer["mpaa"].startswith('Rated NC17'): imgRating='ratings/nc1.png'
		self.getControl(30013).setImage(imgRating)
		if do_timeout:
			xbmc.sleep(2500)
			xbmc.Player().play(trailer["trailer"])
			self.close()
		
	def onAction(self, action):
		ACTION_PREVIOUS_MENU = 10
		ACTION_BACK = 92
		ACTION_ENTER = 7
		ACTION_I = 11
		ACTION_LEFT = 1
		ACTION_RIGHT = 2
		ACTION_UP = 3
		ACTION_DOWN = 4
		ACTION_TAB = 18
		
		xbmc.log('action  =' + str(action.getId()))
		global do_timeout
		global exit_requested
		global movie_file
		if action == ACTION_PREVIOUS_MENU or action == ACTION_LEFT or action == ACTION_BACK:
			do_timeout=False
			xbmc.Player().stop()
			exit_requested=True
			self.close()
			
		if action == ACTION_I or action == ACTION_DOWN:
			self.close()
			
		if action == ACTION_RIGHT or action == ACTION_TAB:
			xbmc.Player().stop()
			self.close()

		if action == ACTION_ENTER:
			movie_file = trailer["file"]
			xbmc.Player().stop()
			exit_requested=True
			self.close()
		
class blankscreen(xbmcgui.Window):
	def __init__(self,):
		pass

class passwordscreen(xbmcgui.WindowXMLDialog):
	def onInit(self):
		pass

	def onAction(self, action):
	# Read Password via a keyboard
		pwd_success = False
		while not pwd_success:
			keyboard = xbmc.Keyboard("", heading = "Please type your password", hidden = True)
			keyboard.setHeading('Password') # optional
			keyboard.setHiddenInput(True) # optional
			keyboard.doModal()
			if (keyboard.isConfirmed()):
				inputText = keyboard.getText()
				if inputText == password:
					pwd_success=True
				else:
					dialog = xbmcgui.Dialog()
					dialog.ok("Error", "Invalid Password, try again")
			keyboard.setHiddenInput(False) # optional
			del keyboard
		self.close()
	
class XBMCPlayer(xbmc.Player):
	def __init__( self, *args, **kwargs ):
		pass
	def onPlayBackStarted(self):
		pass
	
	def onPlayBackStopped(self):
		global exit_requested
		pass
		
def playTrailers():
	bs=blankscreen()
	bs.show()
	global exit_requested
	global movie_file
	movie_file = ''
	exit_requested = False
	player = XBMCPlayer()
	#xbmc.log('Getting Trailers')
	DO_CURTIANS = addon.getSetting('do_animation')
	DO_EXIT = addon.getSetting('do_exit')
	NUMBER_TRAILERS =  int(addon.getSetting('number_trailers'))
	if do_mute == 'true':
		muted = xbmc.getCondVisibility("Player.Muted")
		if not muted:
			xbmc.executebuiltin('xbmc.Mute()')
	if DO_CURTIANS == 'true':
		player.play(open_curtain_path)
		while player.isPlaying():
			xbmc.sleep(250)
	trailercount = 0
	while not exit_requested:
		if NUMBER_TRAILERS == 0:
			while not exit_requested and not xbmc.abortRequested:
				myMovieWindow = movieWindow('script-trailerwindow.xml', addon_path,'default',)
				myMovieWindow.doModal()
				del myMovieWindow
		else:
			for x in xrange(0, NUMBER_TRAILERS):
				myMovieWindow = movieWindow('script-trailerwindow.xml', addon_path,'default',)
				myMovieWindow.doModal()
				del myMovieWindow
				if exit_requested:
					break
		if not exit_requested:
			if DO_CURTIANS == 'true':
				player.play(close_curtain_path)
				while player.isPlaying():
					xbmc.sleep(250)
		exit_requested=True
	if do_mute == 'true':
		muted = xbmc.getCondVisibility("Player.Muted")
		if muted:
			xbmc.executebuiltin('xbmc.Mute()')
	if not movie_file == '':
		xbmc.Player(0).play(movie_file)
	del bs

	
filtergenre = False
if do_genre == 'true':
	filtergenre = askGenres()
	
success = False
if filtergenre:
	success, selectedGenre = selectGenre()

if success:
	trailers = getTrailers(selectedGenre)
else:
	trailers = getTrailers("")

playTrailers()

if do_password == 'true':
	pwscreen = passwordscreen('script-trailerwindow.xml', addon_path,'default',)
	pwscreen.doModal()
	del pwscreen
