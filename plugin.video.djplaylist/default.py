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
icon_video = 'special://home/addons/plugin.video.djplaylist/resources/video.png'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"}

mode = args.get('mode', None)

def ddp(page):
    r = requests.get(page,headers=headers,timeout=5)
    match = re.findall('<div class="score">(.*?)<div class="charts big mobile"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
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
    
def playlist(page):
    playlist=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)  
    playlist.clear() 
    r = requests.get(page,headers=headers,timeout=5)
    match = re.findall('<div class="score">(.*?)<div class="charts big mobile"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
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
            playlist.add(url, li)
    xbmc.executebuiltin("ActivateWindow(10028,playlistvideo://)")
    xbmc.Player().play(playlist)

if mode is None:

    url = build_url({'mode': 'dance', 'foldername': 'DDP - Dance - Top 100'})
    li = xbmcgui.ListItem('DDP - Dance - Top 100')
    li.setInfo(type='video',infoLabels={'title': 'DDP - Dance - Top 100', 'plot': 'DDP - Dance - Top 100'})
    li.setArt({'fanart': djplaylist.getAddonInfo('fanart'), 'icon': icon_dance, 'thumb' : icon_dance}) 
    li.addContextMenuItems([('Playlist Mode', f'RunPlugin(plugin://plugin.video.djplaylist/?mode=playlist&folder=dance)')])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'dance-hot', 'foldername': 'DDP - Dance - Hot 50'})
    li = xbmcgui.ListItem('DDP - Dance - Hot 50')
    li.setInfo(type='video',infoLabels={'title': 'DDP - Dance - Hot 50', 'plot': 'DDP - Dance - Hot 50'})
    li.setArt({'fanart': djplaylist.getAddonInfo('fanart'), 'icon': icon_dance, 'thumb' : icon_dance}) 
    li.addContextMenuItems([('Playlist Mode', f'RunPlugin(plugin://plugin.video.djplaylist/?mode=playlist&folder=dance-hot)')])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'dance-neueinsteiger', 'foldername': 'DDP - Dance - Neueinsteiger'})
    li = xbmcgui.ListItem('DDP - Dance - Neueinsteiger')
    li.setInfo(type='video',infoLabels={'title': 'DDP - Dance - Neueinsteiger', 'plot': 'DDP - Dance - Neueinsteiger'})
    li.setArt({'fanart': djplaylist.getAddonInfo('fanart'), 'icon': icon_dance, 'thumb' : icon_dance}) 
    li.addContextMenuItems([('Playlist Mode', f'RunPlugin(plugin://plugin.video.djplaylist/?mode=playlist&folder=dance-neueinsteiger)')])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'schlager', 'foldername': 'DDP - Schlager - Top 100'})
    li = xbmcgui.ListItem('DDP - Schlager - Top 100')
    li.setInfo(type='video',infoLabels={'title': 'DDP - Schlager - Top 100', 'plot': 'DDP - Schlager - Top 100'})
    li.setArt({'fanart': djplaylist.getAddonInfo('fanart'), 'icon': icon_schlager, 'thumb' : icon_schlager})
    li.addContextMenuItems([('Playlist Mode', f'RunPlugin(plugin://plugin.video.djplaylist/?mode=playlist&folder=schlager)')])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'schlager-hot', 'foldername': 'DDP - Schlager - Hot 50'})
    li = xbmcgui.ListItem('DDP - Schlager - Hot 50')
    li.setInfo(type='video',infoLabels={'title': 'DDP - Schlager - Hot 50', 'plot': 'DDP - Schlager - Hot 50'})
    li.setArt({'fanart': djplaylist.getAddonInfo('fanart'), 'icon': icon_schlager, 'thumb' : icon_schlager})
    li.addContextMenuItems([('Playlist Mode', f'RunPlugin(plugin://plugin.video.djplaylist/?mode=playlist&folder=schlager-hot)')])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'schlager-neueinsteiger', 'foldername': 'DDP - Schlager - Neueinsteiger'})
    li = xbmcgui.ListItem('DDP - Schlager - Neueinsteiger')
    li.setInfo(type='video',infoLabels={'title': 'DDP - Schlager - Neueinsteiger', 'plot': 'DDP - Schlager - Neueinsteiger'})
    li.setArt({'fanart': djplaylist.getAddonInfo('fanart'), 'icon': icon_dance, 'thumb' : icon_schlager}) 
    li.addContextMenuItems([('Playlist Mode', f'RunPlugin(plugin://plugin.video.djplaylist/?mode=playlist&folder=schlager-neueinsteiger)')])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'video-top30', 'foldername': 'DDP - Video - Top 30'})
    li = xbmcgui.ListItem('DDP - Video - Top 30')
    li.setInfo(type='video',infoLabels={'title': 'DDP - Video - Top 30', 'plot': 'DDP - Video - Top 30'})
    li.setArt({'fanart': djplaylist.getAddonInfo('fanart'), 'icon': icon_dance, 'thumb' : icon_video}) 
    li.addContextMenuItems([('Playlist Mode', f'RunPlugin(plugin://plugin.video.djplaylist/?mode=playlist&folder=video-top30)')])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'dance':
    ddp("https://www.dj-playlist.de/top-100/dance")

elif mode[0] == 'schlager':
    ddp("https://www.dj-playlist.de/top-100/schlager")
    
elif mode[0] == 'dance-hot':
    ddp("https://www.dj-playlist.de/hot-50/dance")

elif mode[0] == 'schlager-hot':
    ddp("https://www.dj-playlist.de/hot-50/schlager")
    
elif mode[0] == 'dance-neueinsteiger':
    ddp("https://www.dj-playlist.de/neueinsteiger/dance")

elif mode[0] == 'schlager-neueinsteiger':
    ddp("https://www.dj-playlist.de/neueinsteiger/schlager")
    
elif mode[0] == 'video-top30':
    ddp("https://www.dj-playlist.de/top-30/video")
    
elif mode[0] == 'error':
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Video not available.', 5000, addon_icon))
    
elif mode[0] == 'playlist':
    folder = args['folder'][0]
    if folder == 'dance':
        playlist("https://www.dj-playlist.de/top-100/dance")
    elif folder == 'dance-hot':
        playlist("https://www.dj-playlist.de/hot-50/dance")
    elif folder == 'dance-neueinsteiger':
        playlist("https://www.dj-playlist.de/neueinsteiger/dance")
    elif folder == 'schlager':
        playlist("https://www.dj-playlist.de/top-100/schlager")
    elif folder == 'schlager-hot':
        playlist("https://www.dj-playlist.de/hot-50/schlager")
    elif folder == 'schlager-neueinsteiger':
        playlist("https://www.dj-playlist.de/neueinsteiger/schlager")
    elif folder == 'video-top30':
        playlist("https://www.dj-playlist.de/top-30/video")