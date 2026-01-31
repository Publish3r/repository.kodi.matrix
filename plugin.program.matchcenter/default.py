import os
import re
import sys
import requests
import urllib.parse
import urllib3
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from dateutil import parser
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen
from urllib.error import URLError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    BASE_DOMAIN = "https://matchcenter.laola1.at"
    CREST_BASE_URL = urljoin(BASE_DOMAIN, "crests/")
    headers = {'User-Agent': UA, 'Referer': 'https://www.laola1.at', 'Accept': 'application/json'}
    if "1. BL" in name:
        DATA_PATH = "data/Fussball/Deutschland/Bundesliga/standings.json"
        X = "1"
    elif "2. BL" in name:
        DATA_PATH = "data/Fussball/Deutschland/2Bundesliga/standings.json"
        X = "2"
    else: return
    URL = urljoin(BASE_DOMAIN, DATA_PATH)
    try:
        r = requests.get(URL, headers=headers, timeout=10, verify=False)
        data = r.json()
        standings = data['standings']['team_results'][0]['team_standings']
    except: return
    for entry in standings:
        rank_val = str(entry.get('rank', '0'))
        platz = rank_val.zfill(2)
        team_obj = entry.get('team', {})
        mannschaft = team_obj.get('name', 'Unbekannt')
        punkte = str(entry.get('points', '0')).zfill(2)
        spiele = str(entry.get('played', '0')).zfill(2)
        t_plus = str(entry.get('goals_for', '0')).zfill(2)
        t_minus = str(entry.get('goals_against', '0')).zfill(2)
        tore = f"{t_plus}:{t_minus}"
        team_id = str(team_obj.get('id', '')).split(':')[-1]
        image = urljoin(CREST_BASE_URL, f"{team_id}.png")
        if X == "1":
            if platz in ["01", "02", "03", "04"]: platz = "[COLOR green]"+platz+"[/COLOR]"
            elif platz == "05": platz = "[COLOR deepskyblue]"+platz+"[/COLOR]"
            elif platz == "06": platz = "[COLOR skyblue]"+platz+"[/COLOR]"
            elif platz == "16": platz = "[COLOR orange]"+platz+"[/COLOR]"
            elif platz in ["17", "18"]: platz = "[COLOR red]"+platz+"[/COLOR]"
            else: platz = "[COLOR silver]"+platz+"[/COLOR]"
        if X == "2":
            if platz in ["01", "02"]: platz = "[COLOR green]"+platz+"[/COLOR]"
            elif platz == "03": platz = "[COLOR yellow]"+platz+"[/COLOR]"
            elif platz == "16": platz = "[COLOR orange]"+platz+"[/COLOR]"
            elif platz in ["17", "18"]: platz = "[COLOR red]"+platz+"[/COLOR]"
            else: platz = "[COLOR silver]"+platz+"[/COLOR]"
        name_str = f"[B]{platz}[/B] [COLOR silver]- {punkte} - {tore} - {spiele} -[/COLOR] [B]{mannschaft}[/B]"
        addLinkFussball(name_str, name_str, image, '', '')
       
def ERGEBNISSE(name):
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    BASE_DOMAIN = "https://matchcenter.laola1.at"
    headers = {'User-Agent': UA, 'Referer': 'https://www.laola1.at', 'Accept': 'application/json'}
    if "1. BL" in name:
        DATA_PATH = "data/Fussball/Deutschland/Bundesliga/schedule_by_round.json"
        img = path+'bl1.png'
    elif "2. BL" in name:
        DATA_PATH = "data/Fussball/Deutschland/2Bundesliga/schedule_by_round.json"
        img = path+'bl2.png'
    else: return
    URL = urljoin(BASE_DOMAIN, DATA_PATH)
    try:
        r = requests.get(URL, headers=headers, timeout=10, verify=False)
        data = r.json()
        current_round_name = data.get('tournament', {}).get('current_round', '')
        all_rounds = data.get('rounds', [])
    except: return
    for round_entry in all_rounds:
        if round_entry.get('round') == current_round_name:
            matches = round_entry.get('matches', [])
            try: matches.sort(key=lambda x: x.get('scheduled', ''))
            except: pass
            for match in matches:
                sched = match.get('scheduled', '')
                try:
                    dt = parser.parse(sched)
                    days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
                    datum = f"{days[dt.weekday()]}, {dt.strftime('%d.%m. %H:%M')}"
                except: datum = sched
                heim, gast = "Unbekannt", "Unbekannt"
                for comp in match.get('competitors', []):
                    if comp.get('qualifier') == 'home': heim = comp.get('name')
                    elif comp.get('qualifier') == 'away': gast = comp.get('name')
                res = match.get('result', {})
                s_info = match.get('status_info', {})
                match_status = match.get('status', '')
                h_score = res.get('home_score') if res.get('home_score') is not None else s_info.get('home_score')
                a_score = res.get('away_score') if res.get('away_score') is not None else s_info.get('away_score')
                score = f"{h_score}:{a_score}" if h_score is not None else "0:0"
                if match_status == 'closed':
                    status_anzeige = f"- {score} - Endstand"
                elif match_status == 'not_started':
                    status_anzeige = f"({datum})"
                else:
                    status_anzeige = f"- {score} - Live"
                final_name = f"{heim} : {gast} {status_anzeige}"
                addLinkFussball(final_name, final_name, img, '', '')
            break
        
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