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

gewc = xbmcaddon.Addon('plugin.video.gewc')

addon_icon = 'special://home/addons/plugin.video.gewc/icon.png'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"}

mode = args.get('mode', None)

baseurl = "https://www.gewc.de/"

def playlist(match):
    soup = BeautifulSoup(match, 'html.parser')
    platz = soup.find_all(class_="current-rank")
    bild = soup.find_all(class_="cover-art")
    lied = soup.find_all(class_="song-title")
    adressen = soup.find_all(class_="song-links")
    for rank,image,title,links in zip(platz, bild, lied, adressen):
        rank = rank.get_text()
        rank = str(rank)
        rank = rank.lstrip()
        rank = rank.rstrip()
        title = title.get_text()
        title = str(title)
        title = title.lstrip()
        title = title.rstrip()
        if rank == "0":
            name = title
        else:
            name = rank + " - " + title
        image = str(image)
        image = re.compile('src="(.+?)"').findall(image)[0]
        links = str(links)
        if "options-list-youtube" in links:
            links = re.compile('<li class="options-list-youtube"><a href="https://www.youtube.com/watch(.+?)"').findall(links)[0]
            links = links[3:]
            url = "plugin://plugin.video.youtube/play/?video_id=" + links
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','true')
            li.setInfo( type="video", infoLabels={ "title": name } )
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        elif "bandcamp.com/album" in links:
            links = re.compile('<li class="options-list-amazon"><a href="(.+?)"').findall(links)[0]
            r = requests.get(links,headers=headers,timeout=5)
            url = re.findall('mp3-128&quot;:&quot;(.*?)&quot;',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','true')
            li.setInfo( type="music", infoLabels={ "title": name, 'mediatype': 'song' } )
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        elif "bandcamp.com/track" in links:
            links = re.compile('<li class="options-list-amazon"><a href="(.+?)"').findall(links)[0]
            r = requests.get(links,headers=headers,timeout=5)
            url = re.findall('mp3-128&quot;:&quot;(.*?)&quot;',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','true')
            li.setInfo( type="music", infoLabels={ "title": name, 'mediatype': 'song' } )
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        else:
            url = build_url({'mode': 'error', 'foldername': name})
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','false')
            li.setInfo( type="video", infoLabels={ "title": name } )
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)

if mode is None:

    url = build_url({'mode': 'top15', 'foldername': 'GEWC - Top 15 Tracks'})
    li = xbmcgui.ListItem('GEWC - Top 15 Tracks')
    li.setInfo(type='video',infoLabels={'title': 'GEWC - Top 15 Tracks'})
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'neuvorstellungen', 'foldername': 'GEWC - Neuvorstellungen'})
    li = xbmcgui.ListItem('GEWC - Neuvorstellungen')
    li.setInfo(type='video',infoLabels={'title': 'GEWC - Neuvorstellungen'})
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'top15':
    r = requests.get(baseurl,headers=headers,timeout=5)
    match = re.findall('<span>Top 15 Tracks</span>(.*?)<span>Top 15 Alben</span>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    playlist(match)

elif mode[0] == 'neuvorstellungen':
    r = requests.get(baseurl,headers=headers,timeout=5)
    match = re.findall('<span>Neuvorstellungen Tracks</span>(.*?)<span>Neuvorstellungen Alben</span>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    playlist(match)
    
elif mode[0] == 'error':
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Song not available.', 5000, addon_icon))