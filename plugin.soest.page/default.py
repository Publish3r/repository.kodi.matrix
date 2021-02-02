import sys,xbmcaddon,os,requests,xbmc,xbmcgui,urllib.request,urllib.parse,urllib.error,urllib.request,urllib.error,urllib.parse,re,xbmcplugin,random
from xml.dom import minidom
from dateutil import parser
from datetime import datetime
from bs4 import BeautifulSoup
import json
import html

soestpage = xbmcaddon.Addon('plugin.soest.page')

addon = xbmcaddon.Addon()

addonname = addon.getAddonInfo('name')
addonicon = addon.getAddonInfo('icon')

script_file = os.path.realpath(__file__)
addondir = os.path.dirname(script_file)

path = 'special://home/addons/plugin.soest.page/resources/'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'

def MENU():
    addDir('Lokalnachrichten','-',2,path+'rss_orange.png','','')
    addDir('Weltnachrichten','-',13,path+'rss_blau.png','','')
    addDir2('Wetterbericht','-',4,path+'wetter.png','','')
    addDir2('Verkehrsmeldungen','-',5,path+'verkehr.png','','')
    addDir('Veranstaltungen','-',9,path+'events.png','','')
    addDir('Jahres-Highlights','-',11,path+'highlights.png','','')
    addDir('Webcams','-',6,path+'webcams.png','','')
    
def LOKALNACHRICHTEN():
    # https://www.soester-anzeiger.de/lokales/rssfeed.rdf
    # https://www.hellwegradio.de/thema/lokalnachrichten-392.rss
    try:
        RSS_RESOURCE = requests.get('https://www.soester-anzeiger.de/lokales/rssfeed.rdf', headers={'USER-AGENT': USER_AGENT}).text.encode('utf-8')
        xml = minidom.parseString(RSS_RESOURCE).getElementsByTagName('rss')
        channel = xml[0].getElementsByTagName('channel')
        items = channel[0].getElementsByTagName('item')
        rss_items = list()
        for item in items:
            title = item.getElementsByTagName('title')[0].firstChild.wholeText
            desc = item.getElementsByTagName('description')[0].firstChild.wholeText
            link = item.getElementsByTagName('guid')[0].firstChild.wholeText
            pub = item.getElementsByTagName('pubDate')[0].firstChild.wholeText
            do = parser.parse(pub)
            now = do.strftime("%d.%m.%Y - %H:%M")
            title = title.replace('  ', ' ')
            name = str(title)+' [COLOR blue]'+str(now)+' Uhr[/COLOR]'
            addLinkLokalnachrichten1(link,name,str(desc),'','')
    except:
        RSS_RESOURCE = requests.get('https://www.hellwegradio.de/thema/lokalnachrichten-392.rss', headers={'USER-AGENT': USER_AGENT}).text.encode('utf-8')
        xml = minidom.parseString(RSS_RESOURCE).getElementsByTagName('rss')
        channel = xml[0].getElementsByTagName('channel')
        items = channel[0].getElementsByTagName('item')
        rss_items = list()
        for item in items:
            title = item.getElementsByTagName('title')[0].firstChild.wholeText
            desc = item.getElementsByTagName('description')[0].firstChild.wholeText
            link = item.getElementsByTagName('guid')[0].firstChild.wholeText
            pub = item.getElementsByTagName('pubDate')[0].firstChild.wholeText
            do = parser.parse(pub)
            now = do.strftime("%d.%m.%Y - %H:%M")
            title = title.replace('  ', ' ')
            name = str(title)+' [COLOR blue]'+str(now)+' Uhr[/COLOR]'
            addLinkLokalnachrichten2(link,name,str(desc),'','')

def WELTNACHRICHTEN():
    try:
        RSS_RESOURCE = requests.get('https://www.hellwegradio.de/thema/weltnachrichten-391.rss', headers={'USER-AGENT': USER_AGENT}).text.encode('utf-8')
        xml = minidom.parseString(RSS_RESOURCE).getElementsByTagName('rss')
        channel = xml[0].getElementsByTagName('channel')
        items = channel[0].getElementsByTagName('item')
        rss_items = list()
        for item in items:
            title = item.getElementsByTagName('title')[0].firstChild.wholeText
            desc = item.getElementsByTagName('description')[0].firstChild.wholeText
            link = item.getElementsByTagName('guid')[0].firstChild.wholeText
            pub = item.getElementsByTagName('pubDate')[0].firstChild.wholeText
            do = parser.parse(pub)
            now = do.strftime("%d.%m.%Y - %H:%M")
            title = title.replace('  ', ' ')
            name = str(title)+' [COLOR blue]'+str(now)+' Uhr[/COLOR]'
            addLinkWeltnachrichten(link,name,str(desc),'','')
    except:
        pass

def WEBCAMS():
    webcamname = ["Blick auf den Markt"]
    webcamurls = ["https://www.wms-soest.de/uploads/webcam/1/webcam.jpg"]
    for name,url in zip(webcamname, webcamurls):
       addLinkWebcams(name,url,'','')

def KALENDER():
    r = requests.get("https://www.wms-soest.de/aktivitaeten/veranstaltungskalender/")
    soup = BeautifulSoup(r.content, 'html.parser')
    datum = soup.find_all(class_="eventDate")
    beschreibung = soup.find_all(class_="eventListInfos")
    i = 0
    for date,desc in zip(datum, beschreibung):
        date = date.get_text()
        date = str(date)
        date = date.lstrip()
        date = date.rstrip()
        date = date.replace(' )', ')')
        date = ' [COLOR blue]'+date+'[/COLOR]'
        name = re.compile('<h4><a href="(.+?)</a></h4>').findall(r.content.decode('utf-8'))[i]
        name = str(name)
        name = name.split('>')[-1]
        name = name+date
        desc = desc.get_text()
        desc = str(desc)
        desc = desc.replace(' )', ')')
        desc = desc.replace('Details', '')
        desc = desc.lstrip()
        desc = desc.rstrip()
        desc = desc.replace('\n', ' ').replace('\r', '')
        addLinkKalender(name,desc,'','')
        i = i + 1

def HIGHLIGHTS():
    r = requests.get("https://www.wms-soest.de/stadtfeste/unsere-jahres-highlights/")
    html = re.compile('data-small="(.+?)" alt="(.+?)"').findall(r.content.decode('utf-8'))
    for image,name in html:
        image = str(image)
        image = 'https://www.wms-soest.de/'+image
        name = str(name)
        name = name.replace('  ', ' ')
        addLinkEvents(name,image,'','')

def addLinkEvents(name,image,urlType,fanart):
    ok=True
    desc = name
    u=sys.argv[0]+"?url="+image+"&mode=12"    
    liz=xbmcgui.ListItem(name)
    liz.setInfo( type="video", infoLabels={ "Title": name, "plot": name } )
    liz.setProperty('IsPlayable','false')
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': soestpage.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def addLinkKalender(name,desc,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    image = path+'events.png'
    u=sys.argv[0]+"?url="+image+"&mode=12"
    liz.setProperty('IsPlayable','false')
    liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': soestpage.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def addLinkLokalnachrichten1(link,name,desc,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    image = path+'rss_orange.png'
    u=sys.argv[0]+"?url="+link+"&mode=3&name="+name+"&description="+desc
    liz.setProperty('IsPlayable','false')
    liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': soestpage.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def addLinkLokalnachrichten2(link,name,desc,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    image = path+'rss_orange.png'
    u=sys.argv[0]+"?url="+link+"&mode=33&name="+name+"&description="+desc
    liz.setProperty('IsPlayable','false')
    liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': soestpage.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def addLinkWeltnachrichten(link,name,desc,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    image = path+'rss_blau.png'
    u=sys.argv[0]+"?url="+link+"&mode=14&name="+name+"&description="+desc
    liz.setProperty('IsPlayable','false')
    liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': soestpage.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def addLinkWebcams(name,url,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    num = random.randint(10000, 99999999)
    image = url+'?rnd='+str(num)
    u=sys.argv[0]+"?url="+url+"&mode=7"
    liz.setProperty('IsPlayable','false')
    liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": name } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': soestpage.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def addDir(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&fanart="+urllib.parse.quote_plus(fanart)+"&description="+urllib.parse.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'fanart': soestpage.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addDir2(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&fanart="+urllib.parse.quote_plus(fanart)+"&description="+urllib.parse.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'fanart': soestpage.getAddonInfo('fanart')})
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
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
    OPEN_URL(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==2:
    print("")
    LOKALNACHRICHTEN()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==3:
    print("")
    r = requests.get(url, headers={'USER-AGENT': USER_AGENT})
    html = r.content.decode('utf-8')   
    html = html.replace('</li>','\n')   
    html = html.replace('</ul>','\n')
    soup = BeautifulSoup(html, 'html.parser')
    news = soup.find_all(class_="id-Article-content-item")    
    text = ''
    for i in news:
        i = i.get_text()
        i = i.lstrip()
        i = i.rstrip()
        text += i+'\n'    
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Lokalnachrichten', name+'[CR][CR]'+text)
    sys.exit(0)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==33:
    print("")
    r = requests.get(url, headers={'USER-AGENT': USER_AGENT})
    html = r.content.decode('utf-8')
    html = html.replace('class="small date article__date">','class="small date article__date">\n')
    html = html.replace('<p>','\n')  
    html = html.replace('</li>','\n')   
    html = html.replace('</ul>','\n')
    soup = BeautifulSoup(html, 'html.parser')
    news = soup.find_all('article')
    text = ''
    for i in news:
        i = i.get_text()
        i = i.lstrip()
        i = i.rstrip()
        text += i+'\n'
    text = text.split("\n",2)[2]
    text = text.replace('\n\n','\n') 
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Lokalnachrichten', name+'[CR][CR]'+text)
    sys.exit(0)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==4:
    print("")
    try:
        r = requests.get('https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnings_gemeinde_nrw.html', headers={'USER-AGENT': USER_AGENT})
        wetter = re.compile('<h2 id="Stadt Soest">Stadt Soest</h2>(.+?)</table>').findall(r.content.decode('utf-8'))[0]
        wetter = wetter.replace('Schlagzeile','')
        wetter = wetter.replace('G&uuml;ltig von','')
        wetter = wetter.replace('G&uuml;ltig bis','')
        wetter = wetter.replace('Beschreibung','')
        wetter = wetter.replace('</td><td>',' - ')
        wetter = wetter.replace('</tr><tr>','[CR]')
        txt = html.unescape(wetter)
        tags = re.findall("<[^>]+>",wetter)
        for tag in tags:
            txt=txt.replace(tag,'')
        wetter = txt
        wetter = str(wetter)
        wetter = wetter.lstrip()
        wetter = wetter.rstrip()
        wetter1 = "[COLOR blue][B]Unwetterwarnungen:[/B][/COLOR][CR]"+wetter+"[CR][CR]"
    except:
        wetter1 = ''
    r = requests.get("https://www.wetter.com/deutschland/soest/DE0009935.html")
    soup = BeautifulSoup(r.content, 'html.parser')
    wetter = soup.find(class_="json-ld-answer")
    wetter = str(wetter)
    wetter = wetter.replace('<p class="json-ld-answer">', '')
    wetter = wetter.replace('</p>', '')
    wetter = wetter.lstrip()
    wetter = wetter.rstrip()
    wetter2 = wetter
    wetter2 = "[COLOR blue][B]Heute:[/B][/COLOR][CR]"+wetter2+"[CR][CR]"
    r = requests.get("https://www.wetterdienst.de/Deutschlandwetter/Soest_Westfalen/")
    soup = BeautifulSoup(r.content, 'html.parser')
    wetter = soup.find(class_="forecast_text").get_text()
    wetter = str(wetter)
    wetter = wetter.replace('Wettervorhersage für Soest, Westfalen', '')
    wetter = wetter.lstrip()
    wetter = wetter.rstrip()
    wetter3 = "[COLOR blue][B]Verlauf:[/B][/COLOR][CR]"+wetter
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Wettervorhersage für den Kreis Soest', wetter1+wetter2+wetter3)
    # Optional
    xbmc.executebuiltin('activatewindow(home)')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==5:
    print("")
    r = requests.get('https://api-prod.nrwlokalradios.com/traffic/detail?station=40')
    json_data = json.loads(r.content.decode())
    try:
        stud_list = json_data['local']['accident']
        unfalle = ''
        for i in stud_list:
            do = parser.parse(i['datecreated'])
            zeit = do.strftime("%d.%m.%Y - %H:%M")
            zeit = '[COLOR aqua]'+zeit+' Uhr[/COLOR]'
            wo = '[COLOR red]'+i['autobahn']+'[/COLOR]'
            richtung = '[COLOR yellow]'+i['direction']+'[/COLOR]'
            unfalle += zeit+' '+wo+' '+richtung+' '+i['message']+'\n\n'
        unfalle = str(unfalle)
        unfalle = unfalle[:-2]
        unfalle = unfalle.replace('  ', ' ')
        if not unfalle:
            unfalle = '[COLOR blue][B]Unfälle:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Unfälle vor.'
        else:
            unfalle = '[COLOR blue][B]Unfälle:[/B][/COLOR][CR]'+unfalle
    except:
        unfalle = '[COLOR blue][B]Unfälle:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Unfälle vor.'
    try:
        stud_list = json_data['local']['trafficjam']
        staus = ''
        for i in stud_list:
            do = parser.parse(i['datecreated'])
            zeit = do.strftime("%d.%m.%Y - %H:%M")
            zeit = '[COLOR aqua]'+zeit+' Uhr[/COLOR]'
            wo = '[COLOR red]'+i['autobahn']+'[/COLOR]'
            richtung = '[COLOR yellow]'+i['direction']+'[/COLOR]'
            staus += zeit+' '+wo+' '+richtung+' '+i['message']+'\n\n'
        staus = str(staus)
        staus = staus[:-2]
        staus = staus.replace('  ', ' ')
        if not staus:
            staus = '[COLOR blue][B]Staus:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Staus vor.'
        else:
            staus = '[COLOR blue][B]Staus:[/B][/COLOR][CR]'+staus
    except:
        staus = '[COLOR blue][B]Staus:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Staus vor.'
    try:
        stud_list = json_data['local']['construction']
        baustellen = ''
        for i in stud_list:
            do = parser.parse(i['datecreated'])
            zeit = do.strftime("%d.%m.%Y - %H:%M")
            zeit = '[COLOR aqua]'+zeit+' Uhr[/COLOR]'
            wo = '[COLOR red]'+i['autobahn']+'[/COLOR]'
            richtung = '[COLOR yellow]'+i['direction']+'[/COLOR]'
            baustellen += zeit+' '+wo+' '+richtung+' '+i['message']+'\n\n'
        baustellen = str(baustellen)
        baustellen = baustellen[:-2]
        baustellen = baustellen.replace('  ', ' ')
        if not baustellen:
            baustellen = '[COLOR blue][B]Baustellen:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Baustellen vor.'
        else:
            baustellen = '[COLOR blue][B]Baustellen:[/B][/COLOR][CR]'+baustellen
    except:
        baustellen = '[COLOR blue][B]Baustellen:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Baustellen vor.'
    try:
        stud_list = json_data['local']['warning']
        warnungen = ''
        for i in stud_list:
            do = parser.parse(i['datecreated'])
            zeit = do.strftime("%d.%m.%Y - %H:%M")
            zeit = '[COLOR aqua]'+zeit+' Uhr[/COLOR]'
            wo = '[COLOR red]'+i['autobahn']+'[/COLOR]'
            richtung = '[COLOR yellow]'+i['direction']+'[/COLOR]'
            warnungen += zeit+' '+wo+' '+richtung+' '+i['message']+'\n\n'
        warnungen = str(warnungen)
        warnungen = warnungen[:-2]
        warnungen = warnungen.replace('  ', ' ')
        if not warnungen:
            warnungen = '[COLOR blue][B]Warnungen:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Warnungen vor.'
        else:
            warnungen = '[COLOR blue][B]Warnungen:[/B][/COLOR][CR]'+warnungen
    except:
        warnungen = '[COLOR blue][B]Warnungen:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Warnungen vor.'
    try:
        stud_list = json_data['radars']
        radar = ''
        for i in stud_list:
            radar += i['message']+'\n\n'
        radar = str(radar)
        radar = radar[:-2]
        radar = radar.replace('  ', ' ')
        radar = radar.replace('<br />', '[CR]')
        if not radar:
            radar = '[COLOR blue][B]Blitermeldungen:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Blitzer vor.'
        else:
            radar = '[COLOR blue][B]Blitermeldungen:[/B][/COLOR][CR]'+radar
    except:
        radar = '[COLOR blue][B]Blitermeldungen:[/B][/COLOR][CR]Es liegen keine aktuellen Meldungen über Blitzer vor.'
    r = requests.get('https://soest.polizei.nrw/artikel/radar-messstellen/', headers={'USER-AGENT': USER_AGENT})
    messstellen = re.findall('<div property="schema:text" class="field__item">(.*?)</div>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    messstellen = messstellen.replace('<b>','[CR]')
    messstellen = messstellen.replace('<br />','[CR]')
    messstellen = messstellen.replace('</p>','[CR]')
    messstellen = messstellen.replace('<span style="font-size: 12pt;"><span style="font-family: &quot;Arial&quot;,sans-serif;">','')
    txt = html.unescape(messstellen)
    tags = re.findall("<[^>]+>",messstellen)
    for tag in tags:
        txt=txt.replace(tag,'')
    messstellen = txt
    messstellen = "".join(messstellen.splitlines())
    messstellen = messstellen[17:]
    messstellen = messstellen[:-16] 
    messstellen = messstellen.lstrip()
    messstellen = messstellen.rstrip()
    messstellen = '[COLOR blue][B]Radar-Messstellen:[/B][/COLOR][CR]'+messstellen
    text = unfalle+'[CR][CR]'+staus+'[CR][CR]'+baustellen+'[CR][CR]'+warnungen+'[CR][CR]'+radar+'[CR][CR]'+messstellen
    text = text.replace('<br />', ' ')
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Verkehrsmeldungen für den Kreis Soest', text)
    # Optional
    xbmc.executebuiltin('activatewindow(home)')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==6:
    print("")
    WEBCAMS()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==7:
    print("")
    num = random.randint(10000, 99999999)
    snap = str(url)+'?rnd='+str(num)
    xbmc.executebuiltin('ShowPicture('+snap+')')

elif mode==9:
    print("")
    KALENDER()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==11:
    print("")
    HIGHLIGHTS()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==12:
    print("")
    xbmc.executebuiltin("Container.Refresh")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==13:
    print("")
    WELTNACHRICHTEN()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==14:
    print("")
    r = requests.get(url, headers={'USER-AGENT': USER_AGENT})
    html = r.content.decode('utf-8')
    html = html.replace('class="small date article__date">','class="small date article__date">\n')
    html = html.replace('<p>','\n')   
    html = html.replace('</p>','\n')  
    html = html.replace('</li>','\n')   
    html = html.replace('</ul>','\n')
    soup = BeautifulSoup(html, 'html.parser')
    news = soup.find_all('article')
    text = ''
    for i in news:
        i = i.get_text()
        i = i.lstrip()
        i = i.rstrip()
        text += i+'\n'
    text = text.split("\n",2)[2]   
    dialog = xbmcgui.Dialog()
    dialog.textviewer('NRW, Deutschland und die Welt', name+'[CR][CR]'+text)
    sys.exit(0)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))