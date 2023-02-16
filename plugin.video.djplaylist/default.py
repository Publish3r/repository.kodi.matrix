import sys
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import os
import re
import requests
from bs4 import BeautifulSoup

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

djplaylist = xbmcaddon.Addon('plugin.video.djplaylist')

addon_icon = 'special://home/addons/plugin.video.djplaylist/icon.png'
icon_dance = 'special://home/addons/plugin.video.djplaylist/resources/dance.png'
icon_schlager = 'special://home/addons/plugin.video.djplaylist/resources/schlager.png'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"}

mode = args.get('mode', None)

def ddp(page):
    r = requests.get(page,headers=headers,timeout=5)
    match = re.findall('<div class="s-wk">Week</div>(.*?)<div class="charts big mobile"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    soup = BeautifulSoup(match, 'html.parser')
    platz = soup.find_all(class_="rank")
    bild = soup.find_all(class_="cover")
    kuenstler = soup.find_all(class_="artist")
    lied = soup.find_all(class_="title")
    adressen = soup.find_all(class_="links")
    for rank,image,artist,title,links in zip(platz, bild, kuenstler, lied, adressen):
        rank = rank.get_text()
        rank = str(rank)
        rank = rank.lstrip()
        rank = rank.rstrip()
        artist = artist.get_text()
        artist = str(artist)
        artist = artist.lstrip()
        artist = artist.rstrip()
        title = title.get_text()
        title = str(title)
        title = title.lstrip()
        title = title.rstrip()
        name = rank + " - " + artist + " - " + title
        desc = name
        image = str(image)
        image = re.compile('src="(.+?)width=').findall(image)[0]
        links = str(links)
        if "youtube_play_video" in links:
            links = re.compile('youtube_play_video(.+?)"').findall(links)[0]
            links = links[2:]
            links = links[:-2]
            url = "plugin://plugin.video.youtube/play/?video_id=" + links
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','true')
            li.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': djplaylist.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        else:
            url = build_url({'mode': 'error', 'foldername': name})
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','false')
            li.setInfo( type="Video", infoLabels={ "Title": name, "plot": desc } )
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': djplaylist.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)

if mode is None:

    url = build_url({'mode': 'dance', 'foldername': 'DDP - Top 100 - Dance'})
    li = xbmcgui.ListItem('DDP - Top 100 - Dance')
    li.setInfo(type='video',infoLabels={'title': 'DDP - Top 100 - Dance', 'plot': 'DDP - Top 100 - Dance'})
    li.setArt({'fanart': djplaylist.getAddonInfo('fanart'), 'icon': icon_dance, 'thumb' : icon_dance}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'schlager', 'foldername': 'DDP - Top 100 - Schlager'})
    li = xbmcgui.ListItem('DDP - Top 100 - Schlager')
    li.setInfo(type='video',infoLabels={'title': 'DDP - Top 100 - Schlager', 'plot': 'DDP - Top 100 - Schlager'})
    li.setArt({'fanart': djplaylist.getAddonInfo('fanart'), 'icon': icon_schlager, 'thumb' : icon_schlager})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'dance':
    ddp("https://www.dj-playlist.de/top-100/dance")

elif mode[0] == 'schlager':
    ddp("https://www.dj-playlist.de/top-100/schlager")
    
elif mode[0] == 'error':
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Video not available.', 5000, addon_icon))