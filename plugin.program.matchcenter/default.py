import xbmcaddon,os,requests,xbmc,xbmcgui,urllib.request,urllib.parse,urllib.error,urllib.request,urllib.error,urllib.parse,re,xbmcplugin,xbmcvfs

matchcenter = xbmcaddon.Addon('plugin.program.matchcenter')

addon = xbmcaddon.Addon()

addonname = addon.getAddonInfo('name')
addonicon = addon.getAddonInfo('icon')

script_file = os.path.realpath(__file__)
addondir = os.path.dirname(script_file)

path = 'special://home/addons/plugin.program.matchcenter/resources/'

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
REF = "https://www.google.de/"

headers={
    'Referer': REF,
    'User-Agent': UA,
}

custom_team = addon.getSetting("url")
custom_logo = addon.getSetting("wappen")

def MENU():
    addDir('1. BL Tabelle','-',2,path+'bl1.png','','')
    addDir('1. BL Liveticker','-',3,path+'bl1.png','','')
    addDir('1. BL Spielplan','-',4,path+'bl1.png','','')
    addDir('2. BL Tabelle','-',2,path+'bl2.png','','')
    addDir('2. BL Liveticker','-',3,path+'bl2.png','','')
    addDir('2. BL Spielplan','-',4,path+'bl2.png','','')
    addDir('Spielplan','-',6,custom_logo,'','')
    
def TABELLE(name):
    if "1. BL" in name:
        URL = "https://web.de/magazine/sport/fussball/bundesliga/liveticker/bl/tabelle/"
        X = "1"
    if "2. BL" in name:
        URL = "https://web.de/magazine/sport/fussball/2-liga/liveticker/2bl/konferenz/tabelle"
        X = "2"
    r = requests.get(URL, headers=headers, timeout=5)
    table = re.findall('<th class="points">Punkte</th>(.*?)</table>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    rank = re.compile('<td class="rank">(.+?)</td>').findall(table)
    image = re.compile('<img src="(.+?)"').findall(table)
    team = re.compile('<span>(.+?)</span>').findall(table)
    points = re.compile('<td class="points">(.+?)</td>').findall(table)
    goals = re.compile('<td class="goals">(.+?)</td>').findall(table)
    games = re.compile('<td class="games">(.+?)</td>').findall(table)
    for platz, wappen, mannschaft, punkte, tore, spiele in zip(rank, image, team, points, goals, games):
        try:
            tore = tore.replace("&#58;", ":")
        except:
            tore = tore
        try:
            tore_a = tore.split(':')[0].zfill(2)
            tore_b = tore.split(":",1)[1].zfill(2)
            tore = tore_a + ":" + tore_b
        except:
            pass
        platz = platz.zfill(2)
        if X == "1":
            if platz == "01":
                platz = "[COLOR green]"+platz+"[/COLOR]"
            elif platz == "02":
                platz = "[COLOR green]"+platz+"[/COLOR]"
            elif platz == "03":
                platz = "[COLOR green]"+platz+"[/COLOR]" 
            elif platz == "04":
                platz = "[COLOR green]"+platz+"[/COLOR]"  
            elif platz == "05":
                platz = "[COLOR deepskyblue]"+platz+"[/COLOR]" 
            elif platz == "06":
                platz = "[COLOR skyblue]"+platz+"[/COLOR]"
            elif platz == "16":
                platz = "[COLOR orange]"+platz+"[/COLOR]" 
            elif platz == "17":
                platz = "[COLOR red]"+platz+"[/COLOR]" 
            elif platz == "18":
                platz = "[COLOR red]"+platz+"[/COLOR]"  
            else:
                platz = "[COLOR silver]"+platz+"[/COLOR]"
        if X == "2":
            if platz == "01":
                platz = "[COLOR green]"+platz+"[/COLOR]"
            elif platz == "02":
                platz = "[COLOR green]"+platz+"[/COLOR]"
            elif platz == "03":
                platz = "[COLOR yellow]"+platz+"[/COLOR]" 
            elif platz == "16":
                platz = "[COLOR orange]"+platz+"[/COLOR]" 
            elif platz == "17":
                platz = "[COLOR red]"+platz+"[/COLOR]" 
            elif platz == "18":
                platz = "[COLOR red]"+platz+"[/COLOR]"  
            else:
                platz = "[COLOR silver]"+platz+"[/COLOR]"                
        name = (f"[B]{platz}[/B] [COLOR silver]- {punkte.zfill(2)} - {tore} - {spiele.zfill(2)} -[/COLOR] [B]{mannschaft}[/B]")
        desc = name
        image = wappen.replace("30x30", "500x500")
        addLinkFussball(name,desc,image,'','')
        
def ERGEBNISSE(name):
    if "1. BL" in name:
        URL = "https://web.de/magazine/sport/fussball/bundesliga/liveticker/bl/"
        image = path+'bl1.png'
    if "2. BL" in name:
        URL = "https://web.de/magazine/sport/fussball/2-liga/liveticker/2bl/konferenz/spieltag"
        image = path+'bl2.png'
    r = requests.get(URL, headers=headers, timeout=5)
    results = re.findall('<section class="results">(.*?)</section>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    date = re.compile('(<div class="date">|<div class="live">)(.+?)</div>').findall(results)
    score = re.compile('score">(.+?)</div>').findall(results)
    home = re.compile('<div class="team1">(.+?)title="', re.DOTALL|re.MULTILINE).findall(results)
    guest = re.compile('<div class="team2">(.+?)title="', re.DOTALL|re.MULTILINE).findall(results)
    for datum, ergebnis, heim, gast in zip(date, score, home, guest):
        datum = datum[1]
        heim = re.compile('alt="(.+?)"', re.DOTALL|re.MULTILINE).findall(heim)[0]
        gast = re.compile('alt="(.+?)"', re.DOTALL|re.MULTILINE).findall(gast)[0]
        name = (f"{heim} : {gast} {ergebnis} ({datum})")
        desc = name
        addLinkFussball(name,desc,image,'','')
        
def SPIELPLAN_ALLE_AKTUELL(name):
    if "1. BL" in name:
        URL = "http://www.bulibox.de/statistik/bundesliga-ergebnisse.php?liga=1"
        image = path+'bl1.png'
    if "2. BL" in name:
        URL = "http://www.bulibox.de/statistik/bundesliga-ergebnisse.php?liga=2"
        image = path+'bl2.png'
    r = requests.get(URL, headers=headers, timeout=5)
    table = re.findall('<table(.*?)</table>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    spieltag = re.findall('<b>Ergebnisse vom (.*?)</b><br>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    id = spieltag.replace(". Spieltag", "")
    id = int(id)
    matches = re.compile('<tr><td>(.+?)</td><td>(.+?)</td><td>(.+?)</td><td>(.+?)</td></tr>').findall(table)
    if not id == 1: 
        prev = id - 1
        url = URL + "&spieltag=" + str(prev)
        name = "<<<"        
        addDir(name,url,5,image,'','')
    addLinkFussball(spieltag,spieltag,image,'','')
    for datum, heim, gast, ergebnis in matches:
        datum = datum.replace("&nbsp;&nbsp;", " ")
        datum = datum.replace("&nbsp;", "")
        if ergebnis == ":":
            ergebnis = ergebnis.replace(":", "-:-")
        name = (f"{datum} - {heim} : {gast} ({ergebnis})")
        desc = name
        addLinkFussball(name,desc,image,'','')
    if not id == 34:
        next = id + 1
        url = URL + "&spieltag=" + str(next)
        name = ">>>"        
        addDir(name,url,5,image,'','')
        
def SPIELPLAN_ALLE_NAVIGATION(url):
    if "liga=1" in url:
        image = path+'bl1.png'
        liga = "liga=1"
    if "liga=2" in url:
        image = path+'bl2.png'
        liga = "liga=2"
    r = requests.get(url, headers=headers, timeout=5)
    table = re.findall('<table(.*?)</table>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    spieltag = re.findall('<b>Ergebnisse vom (.*?)</b><br>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    id = spieltag.replace(". Spieltag", "")
    id = int(id)
    matches = re.compile('<tr><td>(.+?)</td><td>(.+?)</td><td>(.+?)</td><td>(.+?)</td></tr>').findall(table)
    if not id == 1: 
        prev = id - 1
        url = "http://www.bulibox.de/statistik/bundesliga-ergebnisse.php?" + liga + "&spieltag=" + str(prev)
        name = "<<<"        
        addDir(name,url,5,image,'','')
    addLinkFussball(spieltag,spieltag,image,'','')
    for datum, heim, gast, ergebnis in matches:
        datum = datum.replace("&nbsp;&nbsp;", " ")
        datum = datum.replace("&nbsp;", "")
        if ergebnis == ":":
            ergebnis = ergebnis.replace(":", "-:-")
        name = (f"{datum} - {heim} : {gast} ({ergebnis})")
        desc = name
        addLinkFussball(name,desc,image,'','')
    if not id == 34:
        next = id + 1
        url = "http://www.bulibox.de/statistik/bundesliga-ergebnisse.php?" + liga + "&spieltag=" + str(next)
        name = ">>>"        
        addDir(name,url,5,image,'','')
        
def SPIELPLAN_CUSTOM():
    URL = custom_team
    image = path+'ball.png'
    r = requests.get(URL, headers=headers, timeout=5)
    table = re.findall('<table  class="tab"(.*?)</table>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    matches = re.compile('<tr><td>(.+?)</td><td>(.+?)</td><td>(.+?)</td><td>(.+?)</td><td>(.+?)</td></tr>').findall(table)
    for spieltag, datum, heim, gast, ergebnis in matches:
        spieltag = spieltag.replace(".", "")
        datum = datum.replace("&nbsp;&nbsp;&nbsp;", " ")
        ergebnis = ergebnis.replace(" ", "")
        if ergebnis == ":":
            ergebnis = ergebnis.replace(":", "-:-")
        name = (f"{spieltag.zfill(2)} - {datum} - {heim} : {gast} ({ergebnis})")
        desc = name
        addLinkFussball(name,desc,image,'','')
    
def addLinkFussball(name,desc,image,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    u=sys.argv[0]+"?url="+image+"&mode=1"
    liz.setProperty('IsPlayable','false')
    liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': matchcenter.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def addDir(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&fanart="+urllib.parse.quote_plus(fanart)+"&description="+urllib.parse.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'fanart': matchcenter.getAddonInfo('fanart')})
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
    print("")
    MENU()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==1:
    print("")
    xbmc.executebuiltin("Container.Refresh")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
elif mode==2:
    print("")
    TABELLE(name)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
elif mode==3:
    print("")
    ERGEBNISSE(name)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
elif mode==4:
    print("")
    SPIELPLAN_ALLE_AKTUELL(name)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
elif mode==5:
    print("")
    SPIELPLAN_ALLE_NAVIGATION(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
elif mode==6:
    print("")
    SPIELPLAN_CUSTOM()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))