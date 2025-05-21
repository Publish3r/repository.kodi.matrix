import sys
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import html
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

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"}

mode = args.get('mode', None)

baseurl = "https://www.gewc.de/"

def datum():
    response = requests.get(baseurl + "top-15-charts/", headers=headers, timeout=10)    
    match = re.search(r'<h4 class="td-block-title"><span class="td-pulldown-size">KW (.*?) - (.*?)</span>', response.text, re.DOTALL | re.MULTILINE)
    kw, date = match.groups()
    info = f"[COLOR blue]KW {kw}[/COLOR] - [COLOR yellow]{date}[/COLOR]"
    return info

def liste_songs(match):
    soup = BeautifulSoup(match, 'html.parser')
    items = soup.find_all('div', class_="td-module-meta-info")
    for item in items:
        title_tag = item.find('h3', class_='entry-title')
        name = title_tag.text.strip()
        htmllink = title_tag.find('a')['href']
        category_tag = item.find('a', class_='td-post-category')        
        if category_tag:
            category_text = category_tag.text.strip()
            rank = category_text[:2]
            name = f"[COLOR blue]{name}[/COLOR]" if rank == "00" else f"[COLOR yellow]{rank}[/COLOR] - [COLOR blue]{name}[/COLOR]"
        else:
            name = f"[COLOR blue]{name}[/COLOR]"
        image_container = item.find_previous_sibling('div', class_='td-image-container')
        image = image_container.find('span', class_='entry-thumb')['data-img-url']
        r = requests.get(htmllink, headers=headers, timeout=10)
        html = r.content.decode('utf-8')
        if "youtube.com" in html or "youtu.be" in html:
            name += " [COLOR green](YouTube)[/COLOR]"
            youtube = re.search(r'<div class="youtube-embed"(.*?)</div>', html, re.DOTALL|re.MULTILINE).group(1)
            link = re.search(r'data-video_id="(.*?)"', youtube).group(1) if re.search(r'data-video_id="(.*?)"', youtube) else re.search(r'/embed/([^?\s]+)', youtube).group(1)
            url = f"plugin://plugin.video.youtube/play/?video_id={link}"
            li = xbmcgui.ListItem(name); li.setProperty('IsPlayable', 'true'); li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
        elif "bandcamp.com" in html:
            name += " [COLOR green](Bandcamp)[/COLOR]"
            link = re.search(r'https://bandcamp\.com[^"]+', html).group()
            bandcamp = requests.get(link, headers=headers, timeout=10)
            url = re.search(r'mp3-128&quot;:&quot;(.*?)&quot;', bandcamp.content.decode('utf-8')).group(1)
            li = xbmcgui.ListItem(name); li.setProperty('IsPlayable', 'true'); li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
        else:
            name += " [COLOR red](not available)[/COLOR]"
            url = build_url({'mode': 'error-song', 'foldername': name})
            li = xbmcgui.ListItem(name); li.setProperty('IsPlayable', 'false'); li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    
def liste_albums(match):
    soup = BeautifulSoup(match, 'html.parser')
    items = soup.find_all('div', class_="td-module-meta-info")
    for item in items:
        title_tag = item.find('h3', class_='entry-title')
        name = title_tag.text.strip()
        htmllink = title_tag.find('a')['href']
        category_tag = item.find('a', class_='td-post-category')
        if category_tag:
            category_text = category_tag.text.strip()
            rank = category_text[:2]
            name = f"[COLOR blue]{name}[/COLOR]" if rank == "00" else f"[COLOR yellow]{rank}[/COLOR] - [COLOR blue]{name}[/COLOR]"
        else:
            name = f"[COLOR blue]{name}[/COLOR]"
        image_container = item.find_previous_sibling('div', class_='td-image-container')
        image = image_container.find('span', class_='entry-thumb')['data-img-url']
        r = requests.get(htmllink, headers=headers, timeout=10)
        html = r.content.decode('utf-8')
        if "bandcamp.com/album" in html:
            name += " [COLOR green](Bandcamp)[/COLOR]"
            links = re.search(r'seamless><a href="(.*?)"', html).group(1)
            url = build_url({'mode': 'bandcamp-album' + links, 'foldername': name})
            li = xbmcgui.ListItem(name); li.setProperty('IsPlayable', 'false'); li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
        elif "youtube.com" in html or "youtu.be" in html:
            try:
                name += " [COLOR green](YouTube)[/COLOR]"
                youtube = re.search(r'<div class="youtube-embed"(.*?)</div>', html, re.DOTALL|re.MULTILINE).group(1)
                link = re.search(r'list=(.*?)"', youtube).group(1)
                url = f"plugin://plugin.video.youtube/channel/mine/playlist/{link}/?category_label={name}"
                li = xbmcgui.ListItem(name); li.setProperty('IsPlayable', 'false'); li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
            except:
                name += " [COLOR red](not available)[/COLOR]"
                url = build_url({'mode': 'error-album', 'foldername': name})
                li = xbmcgui.ListItem(name); li.setProperty('IsPlayable', 'false'); li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        else:
            name += " [COLOR red](not available)[/COLOR]"
            url = build_url({'mode': 'error-album', 'foldername': name})
            li = xbmcgui.ListItem(name); li.setProperty('IsPlayable', 'false'); li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    
def bandcampalbumresolver(bandcampurl):
    r = requests.get(bandcampurl, headers=headers, timeout=10)
    image = re.search(r'<link rel="image_src" href="(.*?)"', r.content.decode('utf-8')).group(1)
    artist = re.search(r'<meta name="title" content="(.*?), by (.*?)"', r.content.decode('utf-8')).group(2)
    matches = re.findall(r'&quot;artist&quot;:null,&quot;title&quot;:&quot;(.+?)&quot;,&quot;', r.content.decode('utf-8'))
    urls = re.findall(r'mp3-128&quot;:&quot;(.*?)&quot;', r.content.decode('utf-8'))
    for i, name in enumerate(matches):
        name = html.unescape(name)
        track = str(i + 1)
        if i < len(urls):
            url = urls[i]
            name = f"[COLOR yellow]{track}[/COLOR] - [COLOR blue]{artist} - {name}[/COLOR] [COLOR green](Bandcamp)[/COLOR]"
        else:
            url = build_url({'mode': 'error-song', 'foldername': name})
            name = f"[COLOR yellow]{track}[/COLOR] - [COLOR blue]{artist} - {name}[/COLOR] [COLOR red](not available)[/COLOR]"
        li = xbmcgui.ListItem(name); li.setProperty('IsPlayable', 'true'); li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

menu_items = [
    {'mode': 'reload', 'foldername': datum(), 'title': datum()},
    {'mode': 'top15', 'foldername': 'GEWC - Top 15 - Tracks', 'title': 'GEWC - Top 15 - Tracks'},
    {'mode': 'neuvorstellungen', 'foldername': 'GEWC - Neuvorstellungen - Tracks', 'title': 'GEWC - Neuvorstellungen - Tracks'},
    {'mode': 'top15alben', 'foldername': 'GEWC - Top 15 - Alben', 'title': 'GEWC - Top 15 - Alben'},
    {'mode': 'neuvorstellungenalben', 'foldername': 'GEWC - Neuvorstellungen - Alben', 'title': 'GEWC - Neuvorstellungen - Alben'},
    {'mode': 'warteliste', 'foldername': 'GEWC - Warteliste - Tracks', 'title': 'GEWC - Warteliste - Tracks'},
    {'mode': 'wartelistealben', 'foldername': 'GEWC - Warteliste - Alben', 'title': 'GEWC - Warteliste - Alben'}
]

url_map = {
    'top15': (baseurl + "top-15-charts/", '<span class="td-pulldown-size">Top 15 Tracks</span>(.*?)<span class="td-pulldown-size">Top 15 Alben</span>', liste_songs),
    'neuvorstellungen': (baseurl + "top-15-charts/", '<span class="td-pulldown-size">Top 15 Tracks -  Neuvorstellungen</span>(.*?)<span class="td-pulldown-size">Top 15 Alben -  Neuvorstellungen</span>', liste_songs),
    'top15alben': (baseurl + "top-15-charts/", '<span class="td-pulldown-size">Top 15 Alben</span>(.*?)<span class="td-pulldown-size">Top 15 Tracks -  Neuvorstellungen</span>', liste_albums),
    'neuvorstellungenalben': (baseurl + "top-15-charts/", '<span class="td-pulldown-size">Top 15 Alben -  Neuvorstellungen</span>(.*?)<div class="td-footer-template-wrap"', liste_albums),
    'warteliste': (baseurl + 'warteliste/', '<span class="td-pulldown-size">Top 15 Tracks</span>(.*?)<span class="td-pulldown-size">Top 15 Alben</span>', liste_songs),
    'wartelistealben': (baseurl + 'warteliste/', '<span class="td-pulldown-size">Top 15 Alben</span>(.*?)<div class="td-footer-template-wrap"', liste_albums)
}

def create_list_item(title, url, is_folder=True):
    li = xbmcgui.ListItem(title)
    li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb': addon_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=is_folder)

if mode is None:
    for item in menu_items:
        url = build_url({'mode': item['mode'], 'foldername': item['foldername']})
        create_list_item(item['title'], url)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

elif mode[0] in url_map:
    url, pattern, func = url_map[mode[0]]
    r = requests.get(url, headers=headers, timeout=10)
    match = re.search(pattern, r.content.decode('utf-8'), re.DOTALL | re.MULTILINE).group(1)
    func(match)

elif 'bandcamp-album' in mode[0]:
    bandcampurl = mode[0].replace("bandcamp-album", "")
    bandcampalbumresolver(bandcampurl)

elif mode[0] == 'error-song':
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Song not available.', 5000, addon_icon))

elif mode[0] == 'error-album':
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('[B]Error[/B]', 'Album not available.', 5000, addon_icon))

elif mode[0] == 'reload':
    xbmc.executebuiltin('Container.Refresh')