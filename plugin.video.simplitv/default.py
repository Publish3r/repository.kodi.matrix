import sys
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import datetime
import requests
import json
import re
import random
import string
import time
import tzlocal

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

simplitv = xbmcaddon.Addon('plugin.video.simplitv')

addon_icon = 'special://home/addons/plugin.video.simplitv/icon.png'

username = addon.getSetting("username")
password = addon.getSetting("password")

api_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0', 'Content-type': 'application/json;charset=utf-8', 'X-Api-Date-Format': 'iso', 'X-Api-Camel-Case': 'true', 'referer': 'https://streaming.simplitv.at/'}
data_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0', 'Accept': 'application/json'}

mode = args.get('mode', None)
start = args.get('start', None)

local_timezone = tzlocal.get_localzone()

def epg_tiles():
    time_start = str(datetime.datetime.now().replace(tzinfo=local_timezone).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"))
    time_end = str(((datetime.datetime.now().replace(tzinfo=local_timezone).astimezone(datetime.timezone.utc)) + datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z"))
    epg_url = "https://api.app.simplitv.at/v1/EpgTile/FilterProgramTiles?$headers=%7B%22Content-Type%22:%22application%2Fjson%3Bcharset%3Dutf-8%22,%22X-Api-Date-Format%22:%22iso%22,%22X-Api-Camel-Case%22:true%7D"
    epg_post = json.dumps({"platformCodename": "www", "from": time_start, "to": time_end})
    try:
        epg_page = requests.post(epg_url, timeout=5, headers=api_headers, data=epg_post, allow_redirects=False)
        epg_resp = epg_page.json()
        return epg_resp["programs"]
    except:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'EPG tiles error.', 5000, addon_icon))
        return {}
    
def epg_details(epg_resp):
    prg_url = "https://api.app.simplitv.at/v2/Tile/GetTiles?$headers=%7B%22Content-Type%22:%22application%2Fjson%3Bcharset%3Dutf-8%22,%22X-Api-Date-Format%22:%22iso%22,%22X-Api-Camel-Case%22:true%7D"
    prg_post = json.dumps({"platformCodename": "www", "requestedTiles": [{"id": epg_resp[i][0]["id"]} for i in epg_resp.keys()]})
    try:
        prg_page = requests.post(prg_url, timeout=5, headers=api_headers, data=prg_post, allow_redirects=False)
        prg_resp = prg_page.json()["tiles"]
        for i in epg_resp.keys():
            epg_resp[i] = None
        for i in prg_resp:
            epg_resp[i["tileChannel"]["codename"]] = i
        return epg_resp
    except:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'EPG details error.', 5000, addon_icon))
        return {}

def stations(channel, epg_tile):
    name = channelname(channel)
    url = build_url({'mode': 'play', 'channel': channel, 'recording': 'false'})
    if epg_tile is not None:
        broadcast_string = datetime.datetime(*(time.strptime(epg_tile["start"].split('+')[0], '%Y-%m-%dT%H:%M:%S')[0:6])).replace(tzinfo=datetime.timezone.utc).astimezone(local_timezone).strftime('%H:%M') + ' - ' + datetime.datetime(*(time.strptime(epg_tile["stop"].split('+')[0], '%Y-%m-%dT%H:%M:%S')[0:6])).replace(tzinfo=datetime.timezone.utc).astimezone(local_timezone).strftime('%H:%M') + ' Uhr'
        li = xbmcgui.ListItem(f'[B]{epg_tile["tileChannel"]["title"]}[/B] | {broadcast_string} | {epg_tile["title"]}' if epg_tile.get("title") is not None else name)
        li.setInfo('video', {"title": epg_tile.get("title", name), "plot": epg_tile.get("description", "")})
        li.setArt({'fanart': epg_tile["images"][0]["url"] if len(epg_tile["images"]) > 0 else simplitv.getAddonInfo('fanart'), 'icon': epg_tile["tileChannel"]["logoUrlOnDark"], 'thumb' : epg_tile["tileChannel"]["logoUrlOnDark"]})
        restart_url = build_url({'mode': 'play', 'channel': channel, 'start': str(int(datetime.datetime(*(time.strptime(epg_tile["start"], '%Y-%m-%dT%H:%M:%S%z')[0:6])).timestamp()))})
        li.addContextMenuItems([("Von Beginn ansehen", f"RunPlugin({restart_url})")])
    else:
        li = xbmcgui.ListItem(name)
        li.setArt({'fanart': simplitv.getAddonInfo('fanart'), 'icon': logomapper(name), 'thumb' : logomapper(name)})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    
def play(stream_url, stream_drm_license_server, stream_drm_challenge_data, codename, start=None):
    if start is not None:
        timeshift = 10800 - (int(datetime.datetime.utcnow().timestamp() - int(start[0]))) - 35
    else:
        timeshift = 0
    url = stream_url
    play_item = xbmcgui.ListItem(path=url)
    play_item.setContentLookup(False)
    try:
        play_item.setInfo("video", {"title": xbmc.getInfoLabel("ListItem.Title"), 'plot': xbmc.getInfoLabel("ListItem.Plot")})
        play_item.setArt({'fanart': xbmc.getInfoLabel("ListItem.Fanart"), 'thumb': xbmc.getInfoLabel("ListItem.Thumb"), 'icon': xbmc.getInfoLabel("ListItem.Icon")})
    except:
        play_item.setInfo('Video', infoLabels={'title': channelname(codename)})
        play_item.setArt({'fanart': simplitv.getAddonInfo('fanart'), 'icon': logomapper(channelname(codename)), 'thumb' : logomapper(channelname(codename))})
    play_item.setProperty('inputstream', 'inputstream.adaptive')
    play_item.setMimeType('application/xml+dash')
    play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    play_item.setProperty('inputstream.adaptive.license_key', f"{stream_drm_license_server}|drmchallengecustomdata={urllib.parse.quote(stream_drm_challenge_data)}|" + "R{SSM}|")
    play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    play_item.setProperty('IsPlayable', 'true')
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    xbmc.Player().play(item=url, listitem=play_item)
    p = xbmc.Player()
    p.play(item=url, listitem=play_item)
    if timeshift > 0:
        xbmc.executebuiltin( "ActivateWindow(busydialognocancel)" )
        while not p.isPlaying():
            time.sleep(1)
        while p.getTime() == 0:
            time.sleep(1)
        p.seekTime(timeshift)
        xbmc.executebuiltin( "Dialog.Close(busydialognocancel)" )
    
def token():
    try:
        login_url = 'https://api.app.simplitv.at/v1/OrsUser/Authenticate'
        login_post = json.dumps({'Login': username, 'LongExpiration': 'true', 'Password': password, 'platformCodename': 'www'})
        login_page = requests.post(login_url, timeout=5, headers=api_headers, data=login_post, allow_redirects=False)
        login_resp = login_page.json()
        token = login_resp['token']
        return token
    except:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Login error.', 5000, addon_icon))
    
def devicekey():
    try:
        key_url = f"https://api.app.simplitv.at/v1/Devices/GetDevices?platformCodename=www&token={token()}"
        key_page = requests.get(key_url, timeout=5, headers=api_headers, allow_redirects=False)
        key_resp = key_page.json()
        key = key_resp['devices'][0]['key']
        return key
    except:
        try:       
            keyreg_url = 'https://api.app.simplitv.at/v1/Devices/RegisterDevice'
            keyreg_post = json.dumps({'deviceKey': generate_key(), 'deviceName': 'Firefox', 'generalDeviceType': '2', 'operatingSystem': 'Windows', 'platformCodename': 'www', 'pushToken': '', 'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0', 'userToken': token(), 'versionOs': '10'})
            keyreg_page = requests.post(keyreg_url, timeout=5, headers=api_headers, data=keyreg_post, allow_redirects=False)        
            key_url = f"https://api.app.simplitv.at/v1/Devices/GetDevices?platformCodename=www&token={token()}"
            key_page = requests.get(key_url, timeout=5, headers=api_headers, allow_redirects=False)
            key_resp = key_page.json()
            key = key_resp['devices'][0]['key']
            return key
        except:
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'DeviceKey error.', 5000, addon_icon))
            
def generate_key():
    generate = string.ascii_letters.lower() + string.digits
    devicekey = ''.join((random.choice(generate) for i in range(32)))
    return devicekey
    
def get_recordings(page):
    i = 0
    recordings_url = f"https://api.app.simplitv.at/v2/Pvr/GetRecordings?platformCodename=www&tokenValue={token()}&page={page}&limit=99999&recordingType=NPvr&recordingFlags=Programs,ProgramImages,ProgramCategories"
    recordings_page = requests.get(recordings_url, timeout=5, headers=api_headers, allow_redirects=False)
    recordings_resp = recordings_page.json()
    page = recordings_resp["pagination"]["page"]
    pages = recordings_resp["pagination"]["totalPages"]
    for x in recordings_page.json()["recordings"]:       
        title = recordings_resp["recordings"][i]["program"]["title"] 
        status = recordings_resp["recordings"][i]["status"]        
        start = recordings_resp["recordings"][i]["program"]["start"] 
        start = datetime.datetime(*(time.strptime(start.split('+')[0], '%Y-%m-%dT%H:%M:%S')[0:6])).replace(tzinfo=datetime.timezone.utc).astimezone(local_timezone).strftime('%d.%m.%Y %H:%M')
        if status == "Recorded":
            start = "[COLOR green]"+start+"[/COLOR]"
        elif status == "Scheduled":
            start = "[COLOR red]"+start+"[/COLOR]"
        title = start + " | " + title        
        try:
            subtitle = recordings_resp["recordings"][i]["program"]["subTitle"]
            title = title + " | " + subtitle
        except:
            pass
        try:
            description = recordings_resp["recordings"][i]["program"]["description"]
        except:
            description = ""
        try:
            image = recordings_resp["recordings"][i]["program"]["images"][0]["url"] 
        except:
            image = addon_icon
        codename = recordings_resp["recordings"][i]["program"]["codename"]
        recordingid = recordings_resp["recordings"][i]["recordingId"]
        i = i + 1
        recordings(title, description, image, codename, recordingid, status)
    if page < pages:
        url = build_url({'mode': 'aufnahmen', 'seite': page})
        li = xbmcgui.ListItem('Nächste Seite >>>')
        li.setArt({'fanart': simplitv.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)    
    xbmcplugin.endOfDirectory(addon_handle)
    
def recordings(title, description, image, codename, recordingid, status):
    if status == "Recorded":
        url = build_url({'mode': 'play', 'recording': codename, 'channel': 'false'})
    elif status == "Scheduled":
        url = build_url({'mode': 'notready'})
    contextMenuItems = []
    contextMenuItems.append(('Aufnahme löschen', f'RunPlugin(plugin://plugin.video.simplitv/?mode=delete&id={recordingid})'))    
    li = xbmcgui.ListItem(title)
    li.setInfo('video', {"title": title, "plot": description})
    li.setArt({'fanart': image, 'icon': image, 'thumb' : image})
    li.addContextMenuItems(contextMenuItems, replaceItems=True)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

def channelname(channel):
    name = channel.replace("-", " ")
    name = name.upper()
    if name.endswith(' HD'):
        name = name[:-3]
    if name.endswith('HD'):
        name = name[:-2]
    return name
    
def logomapper(name):
    if name == "ORF1":
        logo = "https://files.app.simplitv.at/files/orf1-hd-bunt.png"
    elif name == "ORF2NO":
        logo = "https://files.app.simplitv.at/files/orf-no-e-hd-bunt.png"
    elif name == "ATV":
        logo = "https://files.app.simplitv.at/files/atv-hd-bunt.png"
    elif name == "PULS4AUSTRIA":
        logo = "https://files.app.simplitv.at/files/puls4-hd-bunt.png"
    elif name == "PU4":
        logo = "https://files.app.simplitv.at/files/puls4-hd-bunt.png"
    elif name == "SERVUSTV AUSTRIA":
        logo = "https://files.app.simplitv.at/files/servustv-hd-bunt.png"
    elif name == "ORF III":
        logo = "https://files.app.simplitv.at/files/orf3-hd-bunt.png"
    elif name == "ATV 2":
        logo = "https://files.app.simplitv.at/files/atv2-bunt.png"
    elif name == "OE24TV":
        logo = "https://files.app.simplitv.at/files/oe24-tv-bunt.png"
    elif name == "PULS24":
        logo = "https://files.app.simplitv.at/files/puls24-bunt.png"
    elif name == "PROSIEBENAUSTRIA":
        logo = "https://files.app.simplitv.at/files/pro7-hd-bunt.png"
    elif name == "SAT1AUSTRIA":
        logo = "https://files.app.simplitv.at/files/sat1-hd-bunt.png"
    elif name == "RTLAUSTRIA":
        logo = "https://files.app.simplitv.at/files/rtl-austria-hd-bunt.png"
    elif name == "VOXAUSTRIA":
        logo = "https://files.app.simplitv.at/files/vox-hd-bunt.png"
    elif name == "ZDF":
        logo = "https://files.app.simplitv.at/files/zdf-hd-bunt.png"
    elif name == "ARD":
        logo = "https://files.app.simplitv.at/files/ard-hd-bunt.png"
    elif name == "KABELEINSAUSTRIA":
        logo = "https://files.app.simplitv.at/files/kabel1-hd-austria-bunt.png"
    elif name == "SAT1GOLDAUSTRIA":
        logo = "https://files.app.simplitv.at/files/sat1-gold-hd-bunt.png"
    elif name == "3SAT":
        logo = "https://files.app.simplitv.at/files/3sat-hd-bunt.png"
    elif name == "SIXXAUSTRIA":
        logo = "https://files.app.simplitv.at/files/sixx-austria-hd-bunt.png"
    elif name == "PROSIEBENMAXXAUSTRIA":
        logo = "https://files.app.simplitv.at/files/pro7-maxx-austria-bunt.png"
    elif name == "N TV":
        logo = "https://files.app.simplitv.at/files/ntv-hd-bunt.png"
    elif name == "RTLZWEIAUSTRIA":
        logo = "https://files.app.simplitv.at/files/rtl-zwei-hd-bunt.png"
    elif name == "ZDFNEO":
        logo = "https://files.app.simplitv.at/files/zdf-neo-hd-bunt.png"
    elif name == "ZDFINFO":
        logo = "https://files.app.simplitv.at/files/zdf-info-hd-bunt.png"
    elif name == "RTLUP AUSTRIA":
        logo = "https://files.app.simplitv.at/files/rtluphd-kopie.png"
    elif name == "BFS":
        logo = "https://files.app.simplitv.at/files/br-hd-bunt.png"
    elif name == "NITRO AUSTRIA":
        logo = "https://files.app.simplitv.at/files/nitro-logo-hd.png"
    elif name == "TELE 5":
        logo = "https://files.app.simplitv.at/files/tele-5-bunt.png"
    elif name == "COMEDY CENTRAL":
        logo = "https://files.app.simplitv.at/files/comedy-central-austria-bunt.png"
    elif name == "ORF SPORT PLUS":
        logo = "https://files.app.simplitv.at/files/orf-sport-plus-hd-bunt.png"
    elif name == "EUROSPORT1AUSTRIA":
        logo = "https://files.app.simplitv.at/files/eurosport-1-hd-bunt.png"
    elif name == "SPORT1":
        logo = "https://files.app.simplitv.at/files/sport1-hd-bunt.png"
    elif name == "LAOLA1TV":
        logo = "https://files.app.simplitv.at/files/laola1-logo-rgb.jpg"
    elif name == "K19":
        logo = "https://files.app.simplitv.at/files/element-1k19-logo.png"
    elif name == "ARTE":
        logo = "https://files.app.simplitv.at/files/arte-hd-bunt.png"
    elif name == "TLCAUSTRIA":
        logo = "https://files.app.simplitv.at/files/tlc-hd-bunt.png"
    elif name == "KABELEINSDOKU":
        logo = "https://files.app.simplitv.at/files/kabel1-doku-austria-bunt.png"
    elif name == "DMAXAUSTRIA":
        logo = "https://files.app.simplitv.at/files/dmax-hd-bunt.png"
    elif name == "PHOENIX":
        logo = "https://files.app.simplitv.at/files/phoenix-bunt.png"
    elif name == "N24 DOKU":
        logo = "https://files.app.simplitv.at/files/078-n24doku-1024x218.png"
    elif name == "SCHAU TV":
        logo = "https://files.app.simplitv.at/files/kurier-tv-logo-cmyk-b.png"
    elif name == "KRONETV":
        logo = "https://files.app.simplitv.at/files/kronetv-bunt.png"
    elif name == "R9 OESTERREICH":
        logo = "https://files.app.simplitv.at/files/logor9.png"
    elif name == "WELT":
        logo = "https://files.app.simplitv.at/files/welt-bunt.png"
    elif name == "TAGESSCHAU 24":
        logo = "https://files.app.simplitv.at/files/069-tagesschau24hd-1024x208.png"
    elif name == "BILD TV":
        logo = "https://files.app.simplitv.at/files/bild-tv-logo-august-2021.png"
    elif name == "CNN":
        logo = "https://files.app.simplitv.at/files/cnn-bunt.png"
    elif name == "EURONEWS ENGLISH":
        logo = "https://files.app.simplitv.at/files/logo-euronews-white-on-neon-rgb-kopie.png"
    elif name == "AL JAZEERA ENGLISH":
        logo = "https://files.app.simplitv.at/files/aje-logo-rgb.png"
    elif name == "BLOOMBERG EUROPE":
        logo = "https://files.app.simplitv.at/files/075-bloomberg-921x248.png"
    elif name == "TVP WORLD":
        logo = "https://files.app.simplitv.at/files/tvp-world-logo-2022.jpg"
    elif name == "SUPERRTL AUSTRIA":
        logo = "https://files.app.simplitv.at/files/super-rtl-hd-logo-orange.png"
    elif name == "KIKA":
        logo = "https://files.app.simplitv.at/files/kika-hd-bunt.png"
    elif name == "NICKELODEON":
        logo = "https://files.app.simplitv.at/files/nick-austria-bunt.png"
    elif name == "RIC":
        logo = "https://files.app.simplitv.at/files/ric-bunt.png"
    elif name == "FIX UND FOXI":
        logo = "https://files.app.simplitv.at/files/fix-foxi-bunt.png"
    elif name == "ORF2":
        logo = "https://files.app.simplitv.at/files/orf2-hd-bunt.png"
    elif name == "ORF2OO":
        logo = "https://files.app.simplitv.at/files/orf-oo-e-hd-bunt.png"
    elif name == "ORF2ST":
        logo = "https://files.app.simplitv.at/files/orf-steiermark-hd-bunt.png"
    elif name == "ORF2T":
        logo = "https://files.app.simplitv.at/files/orf-tirol-hd-bunt.png"
    elif name == "ORF2B":
        logo = "https://files.app.simplitv.at/files/orf-hd-burgenland-bunt.png"
    elif name == "ORF2K":
        logo = "https://files.app.simplitv.at/files/orf-hd-ka-ernten-bunt.png"
    elif name == "ORF2S":
        logo = "https://files.app.simplitv.at/files/orf-salzburg-hd-bunt.png"
    elif name == "ORF2V":
        logo = "https://files.app.simplitv.at/files/orf-vorarlberg-hd-bunt.png"
    elif name == "KT1":
        logo = "https://files.app.simplitv.at/files/kt1.png"
    elif name == "WNTV":
        logo = "https://files.app.simplitv.at/files/wntv-ihr-privatfernsehen-logo-1801150443.jpg"
    elif name == "W24":
        logo = "https://files.app.simplitv.at/files/100-w24.png"
    elif name == "N1 NOE TV":
        logo = "https://files.app.simplitv.at/files/senderlogo-oesterreichprogramm-n1.png"
    elif name == "LT1":
        logo = "https://files.app.simplitv.at/files/lt1-logo-neu.png"
    elif name == "TV1 OOE":
        logo = "https://files.app.simplitv.at/files/rz-logo-tv1-pos-rgb.jpg"
    elif name == "TIROLTV":
        logo = "https://files.app.simplitv.at/files/tiroltv.png"
    elif name == "LAENDLETV":
        logo = "https://files.app.simplitv.at/files/landletv-s-auf-w.png"
    elif name == "DORFTV":
        logo = "https://files.app.simplitv.at/files/dorftv-kopie-2.png"
    elif name == "ONE":
        logo = "https://files.app.simplitv.at/files/one-hd-bunt.png"
    elif name == "SWR BW":
        logo = "https://files.app.simplitv.at/files/062-swtbwhd-366x71.png"
    elif name == "SR FERNSEHEN":
        logo = "https://files.app.simplitv.at/files/067-srfernsehenhd-1024x627.png"
    elif name == "NDR":
        logo = "https://files.app.simplitv.at/files/ndr-hd-bunt.png"
    elif name == "WDR KÖLN":
        logo = "https://files.app.simplitv.at/files/063-wdrhd-1024x341.png"
    elif name == "MDR SACHSEN":
        logo = "https://files.app.simplitv.at/files/mdr-rgb.png"
    elif name == "HR FERNSEHEN":
        logo = "https://files.app.simplitv.at/files/065-hr-fernsehenhd-170x75.png"
    elif name == "RBB BERLIN":
        logo = "https://files.app.simplitv.at/files/rbb-rgb.png"
    elif name == "ARD ALPHA":
        logo = "https://files.app.simplitv.at/files/ardaplha-rgb.png"
    elif name == "RADIO BREMEN":
        logo = "https://files.app.simplitv.at/files/radio-bremen-rgb.jpg"
    elif name == "OE3 VISUAL RADIO":
        logo = "https://files.app.simplitv.at/files/oe3-logo.png"
    elif name == "MTVAUSTRIA":
        logo = "https://files.app.simplitv.at/files/mtv-hd-bunt.png"
    elif name == "DELUXEMUSICAUSTRIA":
        logo = "https://files.app.simplitv.at/files/deluxe-music-hd-bunt.png"
    elif name == "MELODIETV":
        logo = "https://files.app.simplitv.at/files/093-melodietv-573x538.png"
    elif name == "SCHLAGER DELUXE":
        logo = "https://files.app.simplitv.at/files/schlager-deluxe-logo.png"
    elif name == "DEUTSCHES MUSIKFERNSEHEN":
        logo = "https://files.app.simplitv.at/files/deutsches-musik-fernsehen-infarbe.jpg"
    elif name == "VOLKSMUSIK TV":
        logo = "https://files.app.simplitv.at/files/911px-volksmusik-tv-logosvg.png"
    elif name == "MEI MUSI TV":
        logo = "https://files.app.simplitv.at/files/mei-musi-tv.png"
    elif name == "STARPARADISES TV":
        logo = "https://files.app.simplitv.at/files/starparadies.png"
    elif name == "LILO TV":
        logo = "https://files.app.simplitv.at/files/lilo-color.png"
    elif name == "HGTV":
        logo = "https://files.app.simplitv.at/files/hgtv-bunt.png"
    elif name == "ARCADIA TV":
        logo = "https://files.app.simplitv.at/files/arcadiaworld.png"
    elif name == "SONNENKLARTV":
        logo = "https://files.app.simplitv.at/files/sk-tv-clm-rgb.png"
    elif name == "BIBELTV":
        logo = "https://files.app.simplitv.at/files/084-bibeltvhd-1024x198.png"
    elif name == "FASHION TV":
        logo = "https://files.app.simplitv.at/files/fashiontv-logo-blue-vertical-1.png"
    elif name == "PLAYBOY TV":
        logo = "https://files.app.simplitv.at/files/dorcel-2022-playboytveurope-logo-noir-transparent.png"
    elif name == "HUSTLER TV":
        logo = "https://files.app.simplitv.at/files/hustlertv-light.jpg"
    elif name == "DORCEL TV":
        logo = "https://files.app.simplitv.at/files/2022-dorceltv-black-rvb.jpg"
    else:
        logo = 'special://home/addons/plugin.video.simplitv/icon.png'
    return logo
   
if mode is None:     
    url = build_url({'mode': 'livetv'})
    li = xbmcgui.ListItem('Live TV')
    li.setArt({'fanart': simplitv.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'aufnahmen'})
    li = xbmcgui.ListItem('Aufnahmen')
    li.setArt({'fanart': simplitv.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    xbmcplugin.endOfDirectory(addon_handle)
    
elif mode[0] == "livetv":
    channels_url = 'https://api.app.simplitv.at/v1/EpgTile/FilterChannelTiles' 
    channels_post = json.dumps({'isParentalControlEnabled': 'false', 'platformCodename': 'www', 'token': token()})
    channels_page = requests.post(channels_url, timeout=5, headers=api_headers, data=channels_post, allow_redirects=False)
    channels_resp = channels_page.json()
    channels_resp = str(channels_resp)
    channels_find = re.compile("'codename': '(.+?)'").findall(channels_resp)
    epg_data = epg_details(epg_tiles())
    for channel in channels_find:     
        stations(channel, epg_data.get(channel))        
    xbmcplugin.endOfDirectory(addon_handle)
    
elif mode[0] == "play":
    if args['channel'][0] != "false":
        codename = args['channel'][0]
    elif args['recording'][0] != "false":
        codename = args['recording'][0]
    stream_data = f"https://api.app.simplitv.at/v1/Player/AcquireContent?platformCodename=www&deviceKey={devicekey()}&token={token()}&codename={codename}"
    stream_data = requests.get(stream_data, timeout=5, headers=data_headers, allow_redirects=False)
    stream_resp = stream_data.json()
    stream_url = stream_resp['MediaFiles'][0]['Formats'][0]['Url']
    stream_drm_license_server = stream_resp['DrmInfo'][1]['LicenseServerUrl']
    stream_drm_challenge_data = stream_resp['DrmInfo'][1]['DrmChallengeCustomData']
    stream_url = stream_url.replace(".m3u8", ".mpd")
    play(stream_url, stream_drm_license_server, stream_drm_challenge_data, codename, start)
    
elif mode[0] == "aufnahmen":
    try:
        page = args['page'][0]
    except:
        page = 0
    get_recordings(page)
    
elif mode[0] == "delete":
    id = args['id'][0]
    delete_url = 'https://api.app.simplitv.at/v1/Pvr/DeleteRecording' 
    delete_post = json.dumps({'platformCodename': 'www', 'token': token(), "recordingId": id})
    delete_page = requests.post(delete_url, timeout=5, headers=api_headers, data=delete_post, allow_redirects=False)
    delete_resp = delete_page.json()
    result = str(delete_resp["result"]["success"])
    if result == "True":
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Info[/B]', 'Recording successfully deleted.', 5000, addon_icon))
    elif result == "False":
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Recording not deleted.', 5000, addon_icon))
    xbmc.executebuiltin('Container.Refresh')
    
elif mode[0] == "notready":
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Recording not finished.', 5000, addon_icon))