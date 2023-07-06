import xbmcaddon,os,requests,xbmc,xbmcgui,urllib.request,urllib.parse,urllib.error,urllib.request,urllib.error,urllib.parse,re,xbmcplugin,xbmcvfs,time

deye = xbmcaddon.Addon('plugin.program.deye.wechselrichter')

addon = xbmcaddon.Addon()

addonname = addon.getAddonInfo('name')
addonicon = addon.getAddonInfo('icon')

script_file = os.path.realpath(__file__)
addondir = os.path.dirname(script_file)

path = 'special://home/addons/plugin.program.deye.wechselrichter/resources/'
watt_image = f"{path}watt.png"
kwh_image = f"{path}kwh.png"
info_image = f"{path}info.png"

deye_ip = addon.getSetting("ip")
deye_name = addon.getSetting("name")
deye_password = addon.getSetting("password")
deye_view = addon.getSetting("view")
deye_home = addon.getSetting("homescreen")
deye_reload = addon.getSetting("reload")
deye_interval = int(addon.getSetting("interval"))
deye_timeout = int(addon.getSetting("timeout"))

deye_url = f"http://{deye_ip}/status.html"

def MENU():
    if deye_view == "false":
        try:
            r = requests.post(deye_url, auth=(deye_name, deye_password), timeout=deye_timeout)
            now = re.findall('var webdata_now_p = "(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            today = re.findall('var webdata_today_e = "(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            total = re.findall('var webdata_total_e = "(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            now = "[B]Jetzt: [COLOR green]" + now + " W[/COLOR][/B]"
            today = "[B]Heute: [COLOR green]" + today + " kWh[/COLOR][/B]"
            total = "[B]Gesamt: [COLOR green]" + total + " kWh[/COLOR][/B]"
            addLink(now,now,watt_image,'','')
            addLink(today,today,kwh_image,'','')
            addLink(total,total,kwh_image,'','')
        except:
            info = "[COLOR red]Keine Verbindung zum Wechselrichter.[/COLOR]"
            addLink(info,info,info_image,'','')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        if deye_reload == "true":
            time.sleep(deye_interval)
            xbmc.executebuiltin("Container.Refresh")
        else:
            pass
    else:
        try:
            r = requests.post(deye_url, auth=(deye_name, deye_password), timeout=deye_timeout)
            now = re.findall('var webdata_now_p = "(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            today = re.findall('var webdata_today_e = "(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            total = re.findall('var webdata_total_e = "(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            now = "[B]Jetzt: [COLOR green]" + now + " W[/COLOR][/B]"
            today = "[B]Heute: [COLOR green]" + today + " kWh[/COLOR][/B]"
            total = "[B]Gesamt: [COLOR green]" + total + " kWh[/COLOR][/B]"
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Deye Wechselrichter', now+'[CR]'+today+'[CR]'+total)
        except:
            info = "[COLOR red]Keine Verbindung zum Wechselrichter.[/COLOR]"
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Deye Wechselrichter', info)
        if deye_home == "false":
            pass
        else:
            xbmc.executebuiltin('activatewindow(home)')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
def addLink(name,desc,image,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    u=sys.argv[0]+"?url=None&mode=1"
    liz.setProperty('IsPlayable','false')
    liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
    liz.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': deye.getAddonInfo('fanart')})
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

if mode==None or url==None or len(url)<1:
    MENU()

elif mode==1:
    xbmc.executebuiltin("Container.Refresh")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))