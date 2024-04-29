import sys,xbmcaddon,os,requests,xbmc,xbmcgui,urllib.request,urllib.parse,urllib.error,urllib.request,urllib.error,urllib.parse,re,xbmcplugin,html

get = xbmcaddon.Addon('plugin.video.wedotv')

addon = xbmcaddon.Addon()

addonname = addon.getAddonInfo('name')
addonicon = addon.getAddonInfo('icon')
addonfanart = addon.getAddonInfo('fanart')

script_file = os.path.realpath(__file__)
addondir = os.path.dirname(script_file)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
headers = {
    'User-Agent': UA,
}

BASE_URL = "https://wedotv.com"

def MENU():
    addDir('LIVE TV','-',2,addonicon,'','LIVE TV')
    addDir('MOVIES','-',3,addonicon,'','MOVIES')
    addDir('SERIES','-',4,addonicon,'','SERIES')

def PLAY(page, name, iconimage):
    r = requests.get(page, headers=headers, timeout=5)
    match = re.findall('<video id=(.*?)</video>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    url = re.findall('src="(.*?)"',match,re.DOTALL|re.MULTILINE)[0]
    listitem=xbmcgui.ListItem(name)
    listitem.setArt({'icon': iconimage, 'thumb' : iconimage})
    xbmc.Player().play(url, listitem)
    
def LIVETV(BASE_URL):
    page = BASE_URL + "/channels"
    r = requests.get(page, headers=headers, timeout=15)
    match = re.findall('<div class="epg-channels">(.*?)</div>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    channels = re.compile('<a href="(.+?)"><img src="(.+?)"/></a>').findall(match)
    for link,image in channels:
        url = BASE_URL + link
        image = html.unescape(image)
        try:
            image = image.split("?")[0]
        except:
            pass
        name = link.replace("/channels?program=", "")
        name = name.strip()
        name = name.replace("-", " ")
        name = name.replace("_", " ")
        if "nocache" in name:
            name = name.replace("?nocache", "")
        name = name.upper()
        desc = name
        addLink(url,name,image,desc,'','')
        
def MOVIES(BASE_URL):
    page = BASE_URL + "/movies"
    r = requests.get(page, headers=headers, timeout=15)
    match = re.findall('<div class="collections"(.*?)<br clear="both"/>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    cover = re.compile('data-lazy="(.+?)"').findall(match)
    movies = re.compile('<a href="(.+?)"').findall(match)
    i = 0
    for link in movies:
        url = BASE_URL + link
        name = link[1:]
        name = name.strip()
        name = name.replace("-", " ")
        name = name.replace("_", " ")
        name = name.upper()
        end = re.search(r'\d+$', name)
        if end is not None:
            if not "PART" in name:
                try:
                    req = requests.get(url, headers=headers, timeout=15)
                    block = re.findall('<div class="video-info-container">(.*?)<button class="',req.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
                    name = re.findall('<h1>(.*?)</h1>',block,re.DOTALL|re.MULTILINE)[0]
                    name = name.strip()
                    name = name.upper()
                except:
                    pass
        desc = name
        image = str(cover[i])
        image = html.unescape(image)
        try:
            image = image.split("?")[0]
        except:
            pass
        addLink(url,name,image,desc,'','')
        i = i + 1
        
def SERIES(BASE_URL):
    page = BASE_URL + "/series_1"
    r = requests.get(page, headers=headers, timeout=15)
    match = re.findall('<div class="collections"(.*?)<br clear="both"/>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    cover = re.compile('data-lazy="(.+?)"').findall(match)
    series = re.compile('<a href="(.+?)"').findall(match)
    i = 0
    for link in series:
        url = BASE_URL + link
        name = link[1:]
        name = name.strip()
        name = name.replace("-", " ")
        name = name.replace("_", " ")
        name = name.upper()
        end = re.search(r'\d+$', name)
        if end is not None:
            name = name[:-1]
        desc = name
        image = str(cover[i])
        image = html.unescape(image)
        try:
            image = image.split("?")[0]
        except:
            pass
        addDir(name,url,5,image,'',desc)
        i = i + 1
        
def EPISODES(page):
    r = requests.get(page, headers=headers, timeout=15)
    match = re.findall('<h3 class="padding">Episoden in  Season(.*?)<div class="inner"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    title = re.compile('<h3>(.+?)</h3>').findall(match)
    episodes = re.compile('<a data-lazy="(.+?)" class="lazy" href="(.+?)"').findall(match)
    i = 0
    for image,link in episodes:
        url = BASE_URL + link
        image = html.unescape(image)
        try:
            image = image.split("?")[0]
        except:
            pass
        name = str(title[i])
        name = name.strip()
        name = name.replace("–", "-")
        name = name.replace("   ", " ")
        name = name.replace("  ", " ")
        desc = name
        addLink(url,name,image,desc,'','')
        i = i + 1
    
def addLink(link,name,image,desc,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    url = sys.argv[0]+"?url="+urllib.parse.quote_plus(link)+"&mode=1&name="+name+"&description="+desc+"&iconimage="+image
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': addonfanart})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)

def addDir(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&fanart="+urllib.parse.quote_plus(fanart)+"&description="+urllib.parse.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'fanart': addonfanart})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
	
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
    MENU()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==1:
    PLAY(url, name, iconimage)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==2:
    LIVETV(BASE_URL)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==3:
    MOVIES(BASE_URL)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==4:
    SERIES(BASE_URL)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==5:
    EPISODES(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))