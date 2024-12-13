import sys,xbmcaddon,os,requests,xbmc,xbmcgui,base64,urllib.request,urllib.parse,urllib.error,urllib.request,urllib.error,urllib.parse,re,xbmcplugin,json
import YDStreamUtils
import YDStreamExtractor

philizzmedia = xbmcaddon.Addon('plugin.video.philizz.media')

addon = xbmcaddon.Addon()

addonname = addon.getAddonInfo('name')
addonicon = addon.getAddonInfo('icon')

script_file = os.path.realpath(__file__)
addondir = os.path.dirname(script_file)

icon = 'special://home/addons/plugin.video.philizz.media/resources/folder.png'

abcd = "aHR0cHM6Ly9wYXN0ZWp1c3RpdC5jb20vcmF3L3oyYW5xdW54ZnI="
abcd = abcd.encode("ascii")
abcd = base64.b64decode(abcd)
abcd = abcd.decode("ascii")

bcde = "aHR0cHM6Ly9waGlsaXp6LmNvbQ=="
bcde = bcde.encode("ascii")
bcde = base64.b64decode(bcde)
bcde = bcde.decode("ascii")

cdef = "cGhpbGl6ei5jb20="
cdef = cdef.encode("ascii")
cdef = base64.b64decode(cdef)
cdef = cdef.decode("ascii")

defg = "Y2RuLWNmLnZpZHlhcmQuY29t"
defg = defg.encode("ascii")
defg = base64.b64decode(defg)
defg = defg.decode("ascii")

efgh = "UmVmZXJlcj1odHRwczovL3BsYXkudmlkeWFyZC5jb20v"
efgh = efgh.encode("ascii")
efgh = base64.b64decode(efgh)
efgh = efgh.decode("ascii")

fghi = "aHR0cHM6Ly9pLnBoaWxpenouY29t"
fghi = fghi.encode("ascii")
fghi = base64.b64decode(fghi)
fghi = fghi.decode("ascii")

ghij = "cG9zdGltZy5jYw=="
ghij = ghij.encode("ascii")
ghij = base64.b64decode(ghij)
ghij = ghij.decode("ascii")

hijk = "bS8="
hijk = hijk.encode("ascii")
hijk = base64.b64decode(hijk)
hijk = hijk.decode("ascii")

ijkl = "bS9wbGF5ZXIv"
ijkl = ijkl.encode("ascii")
ijkl = base64.b64decode(ijkl)
ijkl = ijkl.decode("ascii")

jklm = "Y2RuLWNm"
jklm = jklm.encode("ascii")
jklm = base64.b64decode(jklm)
jklm = jklm.decode("ascii")

klmn = "cGxheQ=="
klmn = klmn.encode("ascii")
klmn = base64.b64decode(klmn)
klmn = klmn.decode("ascii")

lmno = "bTN1OA=="
lmno = lmno.encode("ascii")
lmno = base64.b64decode(lmno)
lmno = lmno.decode("ascii")

mnop = "anNvbj9kaXNhYmxlX3BvcG91dHM9MSZkaXNhYmxlX2FuYWx5dGljcz0wJnByZWxvYWQ9YXV0byZkaXNhYmxlX2xhcmdlcl9wbGF5ZXI9ZmFsc2UmY29udHJvbGxlcj1odWJzJmFjdGlvbj1zaG93JnR5cGU9aW5saW5lJnY9NC4zLjY="
mnop = mnop.encode("ascii")
mnop = base64.b64decode(mnop)
mnop = mnop.decode("ascii")

def MENU():
    addDir('Yearmixes','-',3,icon,'','Yearmixes')
    addDir('Decademixes','-',4,icon,'','Decademixes')
    addDir('Heroes of the 00s','-',5,icon,'','Heroes of the 00s')
    addDir('Back to the 90s','-',6,icon,'','Back to the 90s')
    addDir('Back to the 80s','-',16,icon,'','Back to the 80s')
    addDir('I covered the 80s','-',7,icon,'','I covered the 80s')
    addDir('Holland in de Mix','-',15,icon,'','Holland in de Mix')
    addDir('Videomixes','-',8,icon,'','Videomixes')
    addDir('Specials','-',13,icon,'','Specials')
    addDir('Mashups','-',14,icon,'','Mashups')

def YEARMIXES():
    r = requests.get(abcd)
    match = re.compile('#YEARMIXES#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
         desc = name
         if image == "none":
             image = addonicon
         if ' ' in image:
             image = image.replace(" ", "%20")
         if fghi in image:
             image = image.replace(cdef, ghij)
         if ' ' in url:
             url = url.replace(" ", "%20")
         addLink(name,url,image,desc,'','')

def DECADEMIXES():
    r = requests.get(abcd)
    match = re.compile('#DECADEMIXES#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def ZEROS():
    r = requests.get(abcd)
    match = re.compile('#ZEROS#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def NINETIES():
    r = requests.get(abcd)
    match = re.compile('#NINETIES#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')
        
def B2EIGHTIES():
    r = requests.get(abcd)
    match = re.compile('#B2EIGHTIES#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def EIGHTIES():
    r = requests.get(abcd)
    match = re.compile('#EIGHTIES#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def VIDEOMIXESDIR():
    addDir('Videomixes 2016','-',9,icon,'','Videomixes 2016')
    addDir('Videomixes 2013','-',10,icon,'','Videomixes 2013')
    addDir('Videomixes 2012','-',11,icon,'','Videomixes 2012')
    addDir('Videomixes 2011','-',12,icon,'','Videomixes 2011')

def VIDEOMIXES2016():
    r = requests.get(abcd)
    match = re.compile('#VIDEOMIXES2016#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def VIDEOMIXES2013():
    r = requests.get(abcd)
    match = re.compile('#VIDEOMIXES2013#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def VIDEOMIXES2012():
    r = requests.get(abcd)
    match = re.compile('#VIDEOMIXES2012#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def VIDEOMIXES2011():
    r = requests.get(abcd)
    match = re.compile('#VIDEOMIXES2011#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def SPECIALS():
    r = requests.get(abcd)
    match = re.compile('#SPECIALS#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def MASHUPS():
    r = requests.get(abcd)
    match = re.compile('#MASHUPS#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')
        
def HOLLAND():
    r = requests.get(abcd)
    match = re.compile('#HOLLAND#NAME=###(.+?)###URL=###(.+?)###IMAGE=###(.+?)###').findall(str(r.content))
    for name,url,image in match:
        desc = name
        if image == "none":
            image = addonicon
        if ' ' in image:
            image = image.replace(" ", "%20")
        if fghi in image:
            image = image.replace(cdef, ghij)
        if ' ' in url:
            url = url.replace(" ", "%20")
        addLink(name,url,image,desc,'','')

def addLink(name,url,image,desc,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    if not "mp4" in url:
        url = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode=99&name="+name+"&description="+desc+"&iconimage="+image
        liz.setProperty('IsPlayable','false')
    elif "mp4.urlset" in url:
        url = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode=99&name="+name+"&description="+desc+"&iconimage="+image
        liz.setProperty('IsPlayable','false')
    else:
        url = url
        liz.setProperty('IsPlayable','true')
    liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': philizzmedia.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	
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

def addDir(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&fanart="+urllib.parse.quote_plus(fanart)+"&description="+urllib.parse.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'fanart': philizzmedia.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

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
    MENU()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==1:
    OPEN_URL(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==3:
    print("")
    YEARMIXES()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==4:
    print("")
    DECADEMIXES()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==5:
    print("")
    ZEROS()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==6:
    print("")
    NINETIES()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==7:
    print("")
    EIGHTIES()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==8:
    print("")
    VIDEOMIXESDIR()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==9:
    print("")
    VIDEOMIXES2016()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==10:
    print("")
    VIDEOMIXES2013()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==11:
    print("")
    VIDEOMIXES2012()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==12:
    print("")
    VIDEOMIXES2011()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==13:
    print("")
    SPECIALS()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==14:
    print("")
    MASHUPS()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==15:
    print("")
    HOLLAND()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==16:
    print("")
    B2EIGHTIES()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==99:
    url = str(url)
    title = str(name)
    plot = str(description)
    pic = str(iconimage)
    try:
        if not (".m3u8" or ".ts" or ".mkv" or ".mp4" or "alltubedownload.net") in url:
            vid = YDStreamExtractor.getVideoInfo(url,quality=1)
            url = vid.streamURL()
    except:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Video not found.', 5000, addonicon))
    if bcde in url:
        url = url.replace(cdef, defg)
        url = url.replace(hijk, ijkl)
        url = url.replace(jklm, klmn)
        url = url.replace(lmno, mnop)
        url = requests.get(url)
        url = url.json()
        url = url['payload']['chapters'][0]['sources']['hls'][0]['url']
        url = url+"|"+efgh
    listitem=xbmcgui.ListItem(title)
    listitem.setInfo( type="Video", infoLabels={ "Title": title, "plot": plot } )
    listitem.setArt({'icon': pic, 'thumb': pic})
    xbmc.Player().play(url, listitem)