from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.decrypt import *

from pyamf import AMF0, AMF3
from pyamf import remoting
from pyamf.remoting.client import RemotingService

def dmaxShowsListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

def dmaxEpisodesListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]

def dmaxPartsListEntry(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 800, 25, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0])
		]
		
class DMAXShowsScreen(Screen):		

	def __init__(self, session):
		print 'DMAXShowsScreen'
		self.session = session
		
		self.plugin_path = mp_globals.pluginPath
		self.skin_path =  mp_globals.pluginPath + "/skins"
		
		path = "%s/%s/DMAXShowsScreen.xml" % (self.skin_path, config.mediaportal.skin.value)
		if not fileExists(path):
			path = self.skin_path + "/original/DMAXShowsScreen.xml"

		with open(path, "r") as f:
			self.skin = f.read()
			f.close()
			
		Screen.__init__(self, session)
		
		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
		}, -1)
		
		self.lastservice = session.nav.getCurrentlyPlayingServiceReference()
		self.playing = False
		
		self.keyLocked = True
		
		self['title'] = Label("DMAX.de")
		self['name'] = Label("Sendung Auswahl")
		self['handlung'] = Label("")
		self['Pic'] = Pixmap()

		self.movieList = []
		self.keyLocked = True
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList
		self.onLayoutFinish.append(self.loadPage)
	
	def loadPage(self):
		print 'loadPage'
		menuUrl = "http://www.dmax.de/video/shows/"	
		getPage(menuUrl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)
		
	def loadPageData(self, data):
		data = data.replace('\t','')
		data = data.replace('\r','')
		data = data.replace('\n','')
		shows=re.findall('<li class="first-child"><a href="(.*?)">(.*?)</a></li>', data)
		print 'shows'
		print shows
		if shows:
			self.movieList = []
			for (url,title) in shows:
				url = "http://www.dmax.de" + url + "moreepisodes/"
				print 'url - title'
				print url
				print title
				self.movieList.append((decodeHtml(title),url))
		
		self.chooseMenuList.setList(map(dmaxShowsListEntry, self.movieList))
		self.keyLocked = False
	
	def keyOK(self):
		if self.keyLocked:
			return
		
		streamEpisodesLink = self['List'].getCurrent()[0][1]
		self.session.open(DMAXEpisodesListScreen, streamEpisodesLink)
	
	def keyCancel(self):
		self.close()
	
	def dataError(self, error):
		print error
		
class DMAXEpisodesListScreen(Screen):
	
	def __init__(self, session, streamEpisodesLink):
		print 'DMAXEpisodesScreen'	
		self.session = session
		self.streamEpisodesLink = streamEpisodesLink
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/DMAXEpisodesScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/DMAXEpisodesScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()
			
		Screen.__init__(self, session)
		
		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("DMAX.de")
		self['name'] = Label("Folge Auswahl")

		self.keyLocked = True
		self.episodeList = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPage)
		
	def loadPage(self):
		print 'episodeList url'
		print self.streamEpisodesLink
		getPage(self.streamEpisodesLink, agent=std_headers, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)
		
	def dataError(self, error):
		print error
		
	def loadPageData(self, data):
		print 'loadPageData'
		data = data.replace('\t','')
		data = data.replace('\r','')
		data = data.replace('\n','')
		#print data
		episodeDefinitionList=re.findall('<dl class=" item item-(.*?)">(.*?)</dl>', data)
		print 'episodeDefinitionList'
		print episodeDefinitionList
		if episodeDefinitionList:
			for (idx,episodeDefinition) in episodeDefinitionList:
				episodeList=re.findall('<a href="(.*?)">(.*?)<dd class="description">(.*?)</dd><dd class="part">(.*)</dd><dd class="thumbnail">', episodeDefinition)
				url=episodeList[0][0]
				print url
				title=episodeList[0][2]
				title=title.strip()
				
				if title.endswith(" Teil 1"):
					title=title[:-7]
				elif title.endswith(" - 1"):
					title=title[:-4]
				elif title.endswith(" 1"):
					title=title[:-2]
				print title
			
				print episodeList[0][3]
				episodeParts=re.findall('\(Teil (.*?) von (.*?)\)', episodeList[0][3])
				print 'Teil'
				print episodeParts[0][0]
				print 'von'
				parts=episodeParts[0][1]
				print parts
				print '-------------------------'
				self.episodeList.append((decodeHtml(title),url,parts))
						
			self.chooseMenuList.setList(map(dmaxEpisodesListEntry, self.episodeList))
			self.keyLocked = False
					
	def keyOK(self):
		if self.keyLocked:
			return
		
		streamEpisodeLink = self['List'].getCurrent()[0][1]
		parts = self['List'].getCurrent()[0][2]
		self.session.open(DMAXPartsListScreen, streamEpisodeLink, parts)
			
	def keyCancel(self):
		self.close()
		
class DMAXPartsListScreen(Screen):
	
	def __init__(self, session, streamEpisodeLink, parts):
		print 'DMAXEpisodesScreen'	
		self.session = session
		self.streamEpisodeLink = streamEpisodeLink
		self.parts = parts
		path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/%s/DMAXPartsScreen.xml" % config.mediaportal.skin.value
		if not fileExists(path):
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins/original/DMAXPartsScreen.xml"
		print path
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()
			
		Screen.__init__(self, session)
		
		self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("DMAX.de")
		self['name'] = Label("Teil Auswahl")

		self.keyLocked = True
		self.episodeList = []
		self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))
		self.chooseMenuList.l.setItemHeight(25)
		self['List'] = self.chooseMenuList

		self.onLayoutFinish.append(self.loadPageData)
		
	def dataError(self, error):
		print error
		
	def loadPageData(self):
		print 'loadPageData'
		for i in range(1, int(self.parts)+1):
			print i
			#correctedUrl="http://www.dmax.de" + self.streamEpisodeLink[:-2] + str(i) + "/"
			correctedUrl="http://www.dmax.de" + self.streamEpisodeLink
			print correctedUrl
			title="Teil " + str(i) + " von " + self.parts
			print title
			self.episodeList.append((decodeHtml(title),correctedUrl, str(i)))
		self.chooseMenuList.setList(map(dmaxPartsListEntry, self.episodeList))
		self.keyLocked = False
					
	def keyOK(self):
		if self.keyLocked:
			return
		url = self['List'].getCurrent()[0][1]
		print 'url: ' + url
		self.part = self['List'].getCurrent()[0][2]
		print 'part: ' + self.part
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)
		
	def parseData(self, data):
		videoIds = list(re.finditer("videoIds.push\(\"(.*)\"\);", data))
		print videoIds
		print 'self.part: ' + self.part
		streamUrl = ""
		streamName = ""
		x = 1
		for videoId in videoIds:
			if int(self.part) == x:
				print 'in for videoId'
				print videoId.group(1)
				conn = HTTPConnection("c.brightcove.com")
				env = remoting.Envelope(amfVersion=3)
				env.bodies.append(("/1",remoting.Request(target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById",
						body=["ef59d16acbb13614346264dfe58844284718fb7b", 586587148001, videoId.group(1), 1659832546],
						envelope=env)))
				conn.request("POST", "/services/messagebroker/amf?playerKey=AAAAAGLvCOI~,a0C3h1Jh3aQKs2UcRZrrxyrjE0VH93xl", str(remoting.encode(env).read()), {'content-type': 'application/x-amf'})
				response = conn.getresponse().read()
				rtmpdata = remoting.decode(response).bodies[0][1].body
				streamName = ""
				default = 'skip'
				streamUrl = rtmpdata.get('FLVFullLengthURL', default);
				
				for item in sorted(rtmpdata['renditions'], key=lambda item:item['frameHeight'], reverse=False):
					streamHeight = item['frameHeight']
        
					if streamHeight <= 1080:
						streamUrl = item['defaultURL']
    
				streamName = streamName + rtmpdata['displayName']
			x = x + 1
		print 'streamUrl'
		print streamUrl
		print 'streamName'
		print streamName
		sref = eServiceReference(0x1001, 0, streamUrl)
		sref.setName(streamName)
		self.session.open(MoviePlayer, sref)
			
	def keyCancel(self):
		self.close()