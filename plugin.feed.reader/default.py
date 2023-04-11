import sys,xbmcaddon,os,requests,xbmc,xbmcgui,urllib.request,urllib.parse,urllib.error,urllib.request,urllib.error,urllib.parse,re,xbmcplugin,random
from xml.dom import minidom
from dateutil import parser
from datetime import datetime
from bs4 import BeautifulSoup
import json
import html

feedreader = xbmcaddon.Addon('plugin.feed.reader')

addon = xbmcaddon.Addon()

addonname = addon.getAddonInfo('name')
addonicon = addon.getAddonInfo('icon')

script_file = os.path.realpath(__file__)
addondir = os.path.dirname(script_file)

path = 'special://home/addons/plugin.feed.reader/resources/'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'

feedurl = addon.getSetting("feedurl")

def FEED():
    try:
        RSS_RESOURCE = requests.get(feedurl, headers={'USER-AGENT': USER_AGENT}).text.encode('utf-8')
        xml = minidom.parseString(RSS_RESOURCE).getElementsByTagName('rss')
        channel = xml[0].getElementsByTagName('channel')
        items = channel[0].getElementsByTagName('item')
        rss_items = list()
        for item in items:
            title = item.getElementsByTagName('title')[0].firstChild.wholeText
            try:
                desc = item.getElementsByTagName('description')[0].firstChild.wholeText
            except:
                desc = ""
            link = item.getElementsByTagName('guid')[0].firstChild.wholeText
            pub = item.getElementsByTagName('pubDate')[0].firstChild.wholeText
            do = parser.parse(pub)
            now = do.strftime("%d.%m.%Y - %H:%M")
            title = title.replace('  ', ' ')
            name = '[COLOR blue]'+str(now)+' Uhr[/COLOR] ' + str(title)
            addLink(link,name,str(desc),'','')
    except:
        pass

def addLink(link,name,desc,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    image = addonicon
    u=sys.argv[0]+"?url="+link+"&mode=1&name="+name+"&description="+desc
    liz.setProperty('IsPlayable','false')
    liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': feedreader.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
	
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param               

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if ADDON.getSetting('auto-view')=='true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % viewType )
            
params=get_params()
url=None
name=None
mode=None
iconimage=None
fanart=None
description=None

try:
    url=urllib.parse.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.parse.unquote_plus(params["name"])
except:
    pass
try:
    iconimage=urllib.parse.unquote_plus(params["iconimage"])
except:
    pass
try:        
    mode=int(params["mode"])
except:
    pass
try:        
    fanart=urllib.parse.unquote_plus(params["fanart"])
except:
    pass
try:        
    description=urllib.parse.unquote_plus(params["description"])
except:
    pass
   
print("Mode: "+str(mode))
print("URL: "+str(url))
print("Name: "+str(name))

if mode==None or url==None or len(url)<1:
    print("")
    FEED()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==1:
    print("")
  
    dialog = xbmcgui.Dialog()
    dialog.textviewer('RSS FEED READER', name+'[CR][CR]'+description)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))