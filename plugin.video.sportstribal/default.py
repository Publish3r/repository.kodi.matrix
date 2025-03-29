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

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()

mode = args.get('mode', None)

sportstribal = xbmcaddon.Addon('plugin.video.sportstribal')

addon_icon = 'special://home/addons/plugin.video.sportstribal/icon.png'
addon_fanart = 'special://home/addons/plugin.video.sportstribal/fanart.jpg'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
    'Origin': 'https://www.freelivesports.tv',
    'DNT': '1',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://www.freelivesports.tv/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
}

params = {
    '__site': 'freelivesports',
    '__source': 'web',
}

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

def get_channels():
    r = requests.get('https://epg.unreel.me/v2/sites/freelivesports/live-channels/public/90e79153782dc65c49b824d17b2dcb56?__site=freelivesports&__source=web', params=params, headers=headers, timeout=5)
    json_data = json.loads(r.content.decode())
    for i in json_data:
        name = i['name']
        desc = i['description']
        logo = i['thumbnail']
        stream = i['url']
        stream = stream.split("?")[0]        
        url = build_url({'mode': 'play', 'stream': stream, 'name': name, 'desc': desc, 'logo': logo})
        li = xbmcgui.ListItem(name)
        li.setInfo('Video', {"title": name, "plot": desc})
        li.setArt({'fanart': addon_fanart, 'icon': logo, 'thumb' : logo}) 
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
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
    stream = args['stream'][0]
    name = args['name'][0]
    desc = args['desc'][0]
    logo = args['logo'][0]
    play(stream, name, desc, logo)