import sys,xbmcaddon,os,requests,xbmc,xbmcgui,urllib.request,urllib.parse,urllib.error,urllib.request,urllib.error,urllib.parse,re,xbmcplugin,html,json,xbmcvfs

get = xbmcaddon.Addon('plugin.audio.radio_de_light')

addon = xbmcaddon.Addon()

addonname = addon.getAddonInfo('name')
addonicon = addon.getAddonInfo('icon')
addonfanart = addon.getAddonInfo('fanart')

script_file = os.path.realpath(__file__)
addondir = os.path.dirname(script_file)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
REF = "https://www.radio.de/"
headers = {
    'Referer': REF,
    'User-Agent': UA,
}

save_folder = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.audio.radio_de_light')
favourites_list = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.audio.radio_de_light/sender.txt')
temp_list = xbmcvfs.translatePath('special://home/userdata/addon_data/plugin.audio.radio_de_light/temp.txt')
no_image = "special://home/addons/plugin.audio.radio_de_light/no_image.jpg"

def MENU():
    addDir('Sender aus deiner Region','-',2,addonicon,'','Sender aus deiner Region')
    addDir('Sender suchen','-',3,addonicon,'','Sender suchen')
    addDir('Meine Sender','-',5,addonicon,'','Meine Sender')

def LOCAL(page):
    try:
        addDir('[COLOR yellow][B]Zurück zum Menü[/B][/COLOR]','','',addonicon,'','')
        r = requests.get(page, headers=headers, timeout=5)
        json_data = json.loads(r.content.decode())
        stud_list = json_data['playables']
        count = int(json_data['totalCount'])
        for i in stud_list:
            name = i['name']
            image = i['logo300x300']
            if image == "":
                image = i['logo630x630']
            if image == "":
                image = i['logo100x100']
            if image == "":
                image = no_image                    
            url = i['streams'][0]['url']
            try:
                city = i['city']
            except:
                city = ""
            try:
                country = i['country']
            except:
                country = ""
            if city != "" and country != "":
                city = city + ", "
                country = country + "[CR]"
            if city == "" and country != "":
                country = country + "[CR]"
            if city != "" and country == "":
                city = city + "[CR]"
            try:
                genres = str(i['genres'])
                genres = genres.replace("[", "")
                genres = genres.replace("]", "")
                genres = genres.replace("'", "")
                genres = genres.replace('"', '')
            except:
                genres = ""
            city = "[COLOR skyblue]" + city + "[/COLOR]"
            country = "[COLOR skyblue]" + country + "[/COLOR]"
            genres = "[COLOR yellow]" + genres + "[/COLOR]"
            desc = city + country + genres
            addLink(url,name,image,desc,'','')
        offset = page.replace('https://prod.radio-api.net/stations/local?count=25&offset=', '')
        offset = int(offset) + 25
        if offset < count:
            offset = str(offset)
            nextpage = 'https://prod.radio-api.net/stations/local?count=25&offset='+offset+''
            addDir('[COLOR yellow][B]Nächste Seite[/B][/COLOR] [COLOR green][B]>>>[/B][/COLOR]',nextpage,2,addonicon,'','')
    except:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Keine Streams gefunden.', 5000, addonicon))

def SEARCH(page):
    try:
        addDir('[COLOR yellow][B]Zurück zum Menü[/B][/COLOR]','','',addonicon,'','')
        r = requests.get(page, headers=headers, timeout=5)
        json_data = json.loads(r.content.decode())
        stud_list = json_data['playables']
        count = int(json_data['totalCount'])
        for i in stud_list:
            name = i['name']
            image = i['logo300x300']
            if image == "":
                image = i['logo630x630']
            if image == "":
                image = i['logo100x100']
            if image == "":
                image = no_image                    
            url = i['streams'][0]['url']
            try:
                city = i['city']
                city = city + "[CR]"
            except:
                city = ""
            try:
                city = i['city']
            except:
                city = ""
            try:
                country = i['country']
            except:
                country = ""
            if city != "" and country != "":
                city = city + ", "
                country = country + "[CR]"
            if city == "" and country != "":
                country = country + "[CR]"
            if city != "" and country == "":
                city = city + "[CR]"
            try:
                genres = str(i['genres'])
                genres = genres.replace("[", "")
                genres = genres.replace("]", "")
                genres = genres.replace("'", "")
                genres = genres.replace('"', '')
            except:
                genres = ""
            city = "[COLOR skyblue]" + city + "[/COLOR]"
            country = "[COLOR skyblue]" + country + "[/COLOR]"
            genres = "[COLOR yellow]" + genres + "[/COLOR]"
            desc = city + country + genres
            addLink(url,name,image,desc,'','')
        surl = re.findall('https(.*?)offset=',page,re.DOTALL|re.MULTILINE)[0]
        surl = "https" + surl
        offset = page.replace(surl+'offset=', '')
        offset = int(offset) + 25
        if offset < count:
            offset = str(offset)
            nextpage = surl+'offset='+offset+''
            addDir('[COLOR yellow][B]Nächste Seite[/B][/COLOR] [COLOR green][B]>>>[/B][/COLOR]',nextpage,2,addonicon,'','')
    except:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Keine Streams gefunden.', 5000, addonicon))
        
def MYSTATIONS():
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)
    if os.path.exists(f"{favourites_list}"):
        r = open(f"{favourites_list}").read()
        match = re.compile('###NAME###(.+?)###URL###(.+?)###LOGO###(.+?)###').findall(r)
        for name,url,image in match:
            desc = ""
            addMy(url,name,image,desc,'','')    
    else:
        with open(f"{favourites_list}", "a") as f:
            f.close()
        MYSTATIONS()
        
def ADDSTATION(url, name, image):
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)
    if os.path.exists(f"{favourites_list}"):
        pass
    else:
        with open(f"{favourites_list}", "a") as f:
            f.close()
    with open(f"{favourites_list}", "a") as f:
        f.write (f"###NAME###{name}###URL###{url}###LOGO###{image}###")
        f.write("\n")
        f.close()
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]'+name+'[/B]', 'Sender zur Liste hinzugefügt.', 5000, addonicon))
    
def DELSTATION(url):
    try:
        os.remove(f"{temp_list}")
    except:
        pass   
    with open(f"{favourites_list}", "r") as file:
        with open(f"{temp_list}", "w") as output:
            for line in file:
                if url not in line.strip("\n"):
                    output.write(line)
    os.replace(temp_list, favourites_list)
    xbmc.executebuiltin("Container.Refresh")

def addLink(link,name,image,desc,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    url = sys.argv[0]+"?url="+urllib.parse.quote_plus(link)+"&mode=1&name="+name+"&description="+desc+"&iconimage="+image
    add = sys.argv[0]+"?url="+urllib.parse.quote_plus(link)+"&mode=6&name="+name+"&image="+image
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': addonfanart})
    contextMenuItems = []
    contextMenuItems.append(('Zu "Meine Sender" hinzufügen', f'RunPlugin(plugin://plugin.audio.radio_de_light/{add})'))
    liz.addContextMenuItems(contextMenuItems, replaceItems=True)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    
def addMy(link,name,image,desc,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    url = sys.argv[0]+"?url="+urllib.parse.quote_plus(link)+"&mode=1&name="+name+"&description="+desc+"&iconimage="+image
    rem = sys.argv[0]+"?url="+urllib.parse.quote_plus(link)+"&mode=7"
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': addonfanart})
    contextMenuItems = []
    contextMenuItems.append(('Von "Meine Sender" entfernen', f'RunPlugin(plugin://plugin.audio.radio_de_light/{rem})'))
    liz.addContextMenuItems(contextMenuItems, replaceItems=True)
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
    listitem=xbmcgui.ListItem(name)
    listitem.setArt({'icon': iconimage, 'thumb' : iconimage})
    xbmc.Player().play(url, listitem)
elif mode==2:
    if not "offset" in url:
        url = "https://prod.radio-api.net/stations/local?count=25&offset=0"
    else:
        url = url
    LOCAL(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==3:
    kb = xbmc.Keyboard ('default', 'heading', False)
    kb.setDefault('')
    kb.setHeading('Search')
    kb.setHiddenInput(False)
    kb.doModal()
    if (kb.isConfirmed()):
        try:
            search = kb.getText(kb)
            search = search.replace(" ", "+")
            search = 'https://prod.radio-api.net/stations/search?query='+search+'&count=25&offset=0'
            SEARCH(search)
        except:
            pass
    else:
        MENU()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==4:
    SEARCH(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==5:
    MYSTATIONS()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==6:
    image = params.get('image')
    if "special://" in image:
        image = "https://i.postimg.cc/N0MfwFNf/no-image.jpg"
    ADDSTATION(url, name, image)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==7:
    DELSTATION(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))