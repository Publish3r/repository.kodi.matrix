import xbmcaddon,os,requests,xbmc,xbmcgui,urllib.request,urllib.parse,urllib.error,urllib.request,urllib.error,urllib.parse,re,xbmcplugin,xbmcvfs

deye = xbmcaddon.Addon('plugin.program.deye.wechselrichter')

addon = xbmcaddon.Addon()

addonname = addon.getAddonInfo('name')
addonicon = addon.getAddonInfo('icon')

script_file = os.path.realpath(__file__)
addondir = os.path.dirname(script_file)

path = 'special://home/addons/plugin.program.deye.wechselrichter/resources/'
info_image = f"{path}info.png"

deye_ip = addon.getSetting("ip")
deye_name = addon.getSetting("name")
deye_password = addon.getSetting("password")

deye_url = f"http://{deye_ip}/status.html"

def MENU():
    try:
        r = requests.post(deye_url, auth=(deye_name, deye_password), timeout=5)
        now = re.findall('var webdata_now_p = "(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
        today = re.findall('var webdata_today_e = "(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
        total = re.findall('var webdata_total_e = "(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
        now = "[B][COLOR green]" + now + " W[/COLOR][/B] (current)"
        today = "[B][COLOR green]" + today + " kWh[/COLOR][/B] (today)"
        total = "[B][COLOR green]" + total + " kWh[/COLOR][/B] (total)"
        addLink(now,now,info_image,'','')
        addLink(today,today,info_image,'','')
        addLink(total,total,info_image,'','')
    except:
        pass
    
def addLink(name,desc,image,urlType,fanart):
    ok=True
    liz=xbmcgui.ListItem(name)
    u=sys.argv[0]+"?url="+image+"&mode=1"
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