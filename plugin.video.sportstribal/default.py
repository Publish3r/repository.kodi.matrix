import sys
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json
import re
from datetime import datetime

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()

mode = args.get('mode', None)

sportstribal = xbmcaddon.Addon('plugin.video.sportstribal')
epg = addon.getSetting("epg")
geoblock = addon.getSetting("geo")
hide = addon.getSetting("hide")

addon_icon = 'special://home/addons/plugin.video.sportstribal/icon.png'
addon_fanart = 'special://home/addons/plugin.video.sportstribal/fanart.jpg'

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0'
REF = 'https://watch.sportstribal.tv/'

s_headers = {
    'User-Agent': UA,
    'Referer': REF,
    'authorization': 'Bearer Sydn2gA9pRhjSThFPdPSZgm7E|Sydn2gA9pRhjSThFPdPSZgm7E|Sydn2gA9pRhjSThFPdPSZgm7E|null|1718626574955|1721218574955|true|e78e0cdc-aac5-407a-bc71-c27ca5179fa8|WEB||||KjHCowRdT8akM7wV7AFKuV39ET3t7j/KxaBs5KF1Z+4=',
}

s_params = {
    'mute': 'false',
    'consent': '',
    'gdprOptin': 'true',
}

c_headers = {
    'Referer': REF,
    'User-Agent': UA,
}

c_params = {
    'X-Response-Version': '3.0',
}

e_params = {
    'includeDetails': 'false',
    'X-Response-Version': '3.0',
}

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

def get_stream(channelid):
    try:
        r = requests.get(
            f'https://exposureapi.emp.ebsd.ericsson.net/v2/customer/SportsTribal/businessunit/Prod/entitlement/{channelid}/play',
            params=s_params,
            headers=s_headers,
            timeout=5,
        )
        json_data = json.loads(r.content.decode())
        stream = json_data['formats'][0]['mediaLocator']
        return stream
    except:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Stream is not available.', 5000, addon_icon))
        stream = "error"
        return stream

def get_channels():
    r1 = requests.get('https://api.watch.sportstribal.tv/channels/list', params=c_params, headers=c_headers, timeout=5)
    json_data1 = json.loads(r1.content.decode())
    if epg == "true":
        r2 = requests.get('https://api.watch.sportstribal.tv/guide/channels/nownext', params=e_params, headers=c_headers, timeout=5)
        json_data2 = json.loads(r2.content.decode())
    for i in json_data1:
        channelid = i['ID']
        name = i['name']
        desc = i['summary']
        if geoblock == "true":
            geo = ""
            try:
                if "*Available" in i['summary']:
                    match = re.findall('Available(.*?)nly',str(desc),re.DOTALL|re.MULTILINE)[0]
                    geo = f"*Available{match}nly."
                    name = f"{name}[COLOR red]*[/COLOR]"
            except:
                pass
        if epg == "true":
            try:
                epg_now = json_data2[channelid][0]['title']
                epg_now_start = json_data2[channelid][0]['start']
                epg_now_stop = json_data2[channelid][0]['end']
                epg_now_start = int(epg_now_start)
                epg_now_stop = int(epg_now_stop)
                epg_now_start = datetime.fromtimestamp(epg_now_start).strftime('%H:%M')
                epg_now_stop = datetime.fromtimestamp(epg_now_stop).strftime('%H:%M')
                time_now = f"{epg_now_start} - {epg_now_stop}"
                epg_next = json_data2[channelid][1]['title']
                epg_next_start = json_data2[channelid][1]['start']
                epg_next_stop = json_data2[channelid][1]['end']
                epg_next_start = int(epg_next_start)
                epg_next_stop = int(epg_next_stop)
                epg_next_start = datetime.fromtimestamp(epg_next_start).strftime('%H:%M')
                epg_next_stop = datetime.fromtimestamp(epg_next_stop).strftime('%H:%M')
                time_next = f"{epg_next_start} - {epg_next_stop}"
                desc = f"[COLOR green][B]{time_now}[/B][/COLOR][CR][COLOR yellow]{epg_now}[/COLOR][CR][COLOR green][B]{time_next}[/B][/COLOR][CR][COLOR yellow]{epg_next}[/COLOR]" 
                if geoblock == "true":
                    try:
                        if geo != "":
                            geo = geo.replace("Only", "only") 
                            geo = geo.replace(geo, f"[COLOR red]{geo}[/COLOR]")
                            desc = f"{desc}[CR][CR]{geo}" 
                    except:
                        pass                    
            except:
                desc = i['summary']
                if geoblock == "true":
                    try:
                        desc = desc.replace(geo, f"[COLOR red]{geo}[/COLOR]")
                        desc = desc.replace("Only", "only")
                    except:
                        pass
        else:
            desc = i['summary']
            if geoblock == "true":
                try:
                    desc = desc.replace(geo, f"[COLOR red]{geo}[/COLOR]")
                    desc = desc.replace("Only", "only")
                except:
                    pass
        logo = i['images']['logo']
        url = build_url({'mode': 'play', 'channelid': channelid, 'name': name, 'desc': desc, 'logo': logo})
        if hide == "true":
            if not "*Available" in desc:
                li = xbmcgui.ListItem(name)
                li.setInfo('Video', {"title": name, "plot": desc})
                li.setArt({'fanart': addon_fanart, 'icon': logo, 'thumb' : logo}) 
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        else:
            li = xbmcgui.ListItem(name)
            li.setInfo('Video', {"title": name, "plot": desc})
            li.setArt({'fanart': addon_fanart, 'icon': logo, 'thumb' : logo}) 
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
    
def play(stream, name, desc, logo):
    play_item = xbmcgui.ListItem(path=stream)
    play_item.setContentLookup(False)
    play_item.setProperty('IsPlayable', 'true')
    play_item.setInfo("Video", {"title": name, 'plot': desc})
    play_item.setArt({'fanart': addon_fanart, 'thumb': logo, 'icon': logo})
    xbmcplugin.setResolvedUrl(addon_handle, True, play_item)
    xbmc.Player().play(item=stream, listitem=play_item)

if mode is None:
    get_channels()
        
elif mode[0] == "play":
    channelid = args['channelid'][0]
    name = args['name'][0]
    if geoblock == "true":
        try:
            if "*" in name:
                name = name.replace("[COLOR red]*[/COLOR]", "")
        except:
            pass
    desc = args['desc'][0]
    logo = args['logo'][0]
    stream = get_stream(channelid)
    if stream == "error":
        xbmc.executebuiltin("Container.Refresh")
    else:
        play(stream, name, desc, logo)