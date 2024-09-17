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

def datum():
    r = requests.get(baseurl+"gewc-top-15/",headers=headers,timeout=5)
    kw = re.findall('<title>GEWC TOP 15 KW (.*?) ',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    date = re.findall('<title>(.*?)</title>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    date = re.findall('&#8211; (.*?) | GEWC',date,re.DOTALL|re.MULTILINE)[0]
    info = "[COLOR blue]KW " + kw + "[/COLOR]" + " - " + "[COLOR yellow]" + date + "[/COLOR]"
    return info

def songs(match):
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
            name = "[COLOR blue]" + title + "[/COLOR]"
        else:
            name = "[COLOR yellow]" + rank + "[/COLOR]" + " - " + "[COLOR blue]" + title + "[/COLOR]"
        image = str(image)
        image = re.compile('src="(.+?)"').findall(image)[0]
        links = str(links)
        if "options-list-youtube" in links:
            name = name + " [COLOR green](YouTube)[/COLOR]"
            try:
                links = re.compile('<li class="options-list-youtube"><a href="https://www.youtube.com/watch(.+?)"').findall(links)[0]
                links = links[3:]
            except:
                links = re.compile('<li class="options-list-youtube"><a href="https://youtu.be/(.+?)"').findall(links)[0]
            url = "plugin://plugin.video.youtube/play/?video_id=" + links
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','true')
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        elif "bandcamp.com/album" in links:
            name = name + " [COLOR green](Bandcamp)[/COLOR]"
            links = re.compile('<li class="options-list-amazon"><a href="(.+?)"').findall(links)[0]
            r = requests.get(links,headers=headers,timeout=5)
            url = re.findall('mp3-128&quot;:&quot;(.*?)&quot;',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','true')
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        elif "bandcamp.com/track" in links:
            name = name + " [COLOR green](Bandcamp)[/COLOR]"
            links = re.compile('<li class="options-list-amazon"><a href="(.+?)"').findall(links)[0]
            r = requests.get(links,headers=headers,timeout=5)
            url = re.findall('mp3-128&quot;:&quot;(.*?)&quot;',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','true')
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        else:
            name = name + " [COLOR red](not available)[/COLOR]"
            url = build_url({'mode': 'error-song', 'foldername': name})
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','false')
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)
    
def albums(match):
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
            name = "[COLOR blue]" + title + "[/COLOR]"
        else:
            name = "[COLOR yellow]" + rank + "[/COLOR]" + " - " + "[COLOR blue]" + title + "[/COLOR]"
        image = str(image)
        image = re.compile('src="(.+?)"').findall(image)[0]
        links = str(links)
        if "bandcamp.com/album" in links:
            name = name + " [COLOR green](Bandcamp)[/COLOR]"
            links = re.compile('<li class="options-list-amazon"><a href="(.+?)"').findall(links)[0]
            url = build_url({'mode': 'bandcamp-album'+links, 'foldername': name })
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','false')
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
        else:
            name = name + " [COLOR red](not available)[/COLOR]"
            url = build_url({'mode': 'error-album', 'foldername': name})
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable','false')
            li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)
    
def bandcampalbumresolver(bandcampurl):
    i = 0
    t = 1
    r = requests.get(bandcampurl,headers=headers,timeout=5)
    image = re.findall('<link rel="image_src" href="(.*?)"',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    artist = re.findall('<meta name="title" content="(.*?)>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    artist = re.findall(', by (.*?)"',artist,re.DOTALL|re.MULTILINE)[0]
    match = re.compile('&quot;artist&quot;:null,&quot;title&quot;:&quot;(.+?)&quot;,&quot;').findall(r.content.decode('utf-8'))
    for name in match:
        try:
            import html
            name = html.unescape(name)
        except:
            pass
        try:
            import html.parser
            name = html.parser.HTMLParser().unescape(name)
        except:
            pass
        track = str(t)
        try:
            url = re.findall('mp3-128&quot;:&quot;(.*?)&quot;',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[i]
            name = "[COLOR yellow]" + track + "[/COLOR]" + " - " + "[COLOR blue]" + artist + " - " + name + "[/COLOR]" + " [COLOR green](Bandcamp)[/COLOR]"
        except:
            url = build_url({'mode': 'error-song', 'foldername': name})
            name = "[COLOR yellow]" + track + "[/COLOR]" + " - " + "[COLOR blue]" + artist + " - " + name + "[/COLOR]" + " [COLOR red](not available)[/COLOR]"
        li = xbmcgui.ListItem(name)
        li.setProperty('IsPlayable','true')
        li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        i = i + 1
        t = t + 1
    xbmcplugin.endOfDirectory(addon_handle)

if mode is None:

    url = build_url({'mode': 'reload', 'foldername': datum()})
    li = xbmcgui.ListItem(datum())
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'top15', 'foldername': 'GEWC - Top 15 - Tracks'})
    li = xbmcgui.ListItem('GEWC - Top 15 - Tracks')
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    url = build_url({'mode': 'neuvorstellungen', 'foldername': 'GEWC - Neuvorstellungen - Tracks'})
    li = xbmcgui.ListItem('GEWC - Neuvorstellungen - Tracks')
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'top15alben', 'foldername': 'GEWC - Top 15 - Alben'})
    li = xbmcgui.ListItem('GEWC - Top 15 - Alben')
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'neuvorstellungenalben', 'foldername': 'GEWC - Neuvorstellungen - Alben'})
    li = xbmcgui.ListItem('GEWC - Neuvorstellungen - Alben')
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'warteliste', 'foldername': 'GEWC - Warteliste - Tracks'})
    li = xbmcgui.ListItem('GEWC - Warteliste - Tracks')
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    url = build_url({'mode': 'wartelistealben', 'foldername': 'GEWC - Warteliste - Alben'})
    li = xbmcgui.ListItem('GEWC - Warteliste - Alben')
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'top15':
    r = requests.get(baseurl+"gewc-top-15/",headers=headers,timeout=5)
    match = re.findall('<h2 class="wp-block-heading">Top 15 Tracks</h2>(.*?)<h2 class="wp-block-heading">Top 15 Alben</h2>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    songs(match)

elif mode[0] == 'neuvorstellungen':
    r = requests.get(baseurl+"gewc-top-15/",headers=headers,timeout=5)
    match = re.findall('<h2 class="wp-block-heading">Neuvorstellungen</h2>(.*?)<h2 class="wp-block-heading">Neuvorstellungen</h2>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    songs(match)
    
elif mode[0] == 'top15alben':
    r = requests.get(baseurl+"gewc-top-15/",headers=headers,timeout=5)
    match = re.findall('<h2 class="wp-block-heading">Top 15 Alben</h2>(.*?)<h2 class="wp-block-heading">Neuvorstellungen</h2>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    albums(match)
    
elif mode[0] == 'neuvorstellungenalben':
    r = requests.get(baseurl+"gewc-top-15/",headers=headers,timeout=5)
    match = re.findall('<h2 class="wp-block-heading">Neuvorstellungen</h2>(.*?)</div></div><div class="wpb_wrapper',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    match = re.findall('<h2 class="wp-block-heading">Neuvorstellungen</h2>(.*?)<div id="jquery_jplayer"></div>',match,re.DOTALL|re.MULTILINE)[0]
    albums(match)
    
elif mode[0] == 'warteliste':
    r = requests.get(baseurl+'maybe-soon/',headers=headers,timeout=5)
    match = re.findall('<div id="chart_container">(.*?)<div id="chart_container">',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    songs(match)
    
elif mode[0] == 'wartelistealben':
    r = requests.get(baseurl+'maybe-soon/',headers=headers,timeout=5)
    match = re.findall('<h2 class="wp-block-heading">Top 15 Alben</h2>(.*?)<div id="jquery_jplayer"></div>',r.content.decode('utf-8'),re.DOTALL|re.MULTILINE)[0]
    albums(match)
    
elif 'bandcamp-album' in mode[0]:
    bandcampurl = mode[0].replace("bandcamp-album", "")
    bandcampalbumresolver(bandcampurl)
    
elif mode[0] == 'error-song':
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Song not available.', 5000, addon_icon))
    
elif mode[0] == 'error-album':
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Album not available.', 5000, addon_icon))
    
elif mode[0] == 'reload':
    xbmc.executebuiltin('Container.Refresh')