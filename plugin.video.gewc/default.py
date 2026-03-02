import sys, urllib.parse, xbmc, xbmcgui, xbmcplugin, xbmcaddon, html, re, requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
gewc = xbmcaddon.Addon('plugin.video.gewc')
addon_icon = 'special://home/addons/plugin.video.gewc/icon.png'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"}
mode = args.get('mode', [None])[0]

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

def datum():
    try:
        r = requests.get("https://www.gewc.de/top-15-charts/", headers=headers, timeout=10)
        match = re.search(r'KW (.*?) - (.*?)</span>', r.text)
        if match:
            kw, date = match.groups()
            return f"[COLOR blue]KW {kw}[/COLOR] - [COLOR yellow]{date}[/COLOR]"
    except: pass
    return "[COLOR yellow]GEWC Charts[/COLOR]"

def process_item(item, index, is_album, is_top15):
    try:
        title_tag = item.find('h3', class_='entry-title')
        if not title_tag: return None
        raw_name = title_tag.text.strip()
        htmllink = title_tag.find('a')['href']
        cat_tag = item.find('a', class_='td-post-category')
        rank = cat_tag.text.strip()[:2] if cat_tag else "00"
        if is_top15 and rank == "00": rank = str(index + 1).zfill(2)
        name = f"[COLOR yellow]{rank}[/COLOR] - [COLOR blue]{raw_name}[/COLOR]" if rank != "00" else f"[COLOR blue]{raw_name}[/COLOR]"
        img_cont = item.find_previous_sibling('div', class_='td-image-container')
        image = img_cont.find('span', class_='entry-thumb')['data-img-url'] if img_cont else addon_icon
        r = requests.get(htmllink, headers=headers, timeout=10).text
        play_url = None
        if is_album:
            bc_s = re.search(r'href="(https?://[^"]*?bandcamp\.com/album/[^"]+)"', r)
            if bc_s:
                play_url = build_url({'mode': 'resolve-album', 'url': bc_s.group(1)})
                name += " [COLOR green](Bandcamp)[/COLOR]"
            elif "youtube.com" in r:
                yt_s = re.search(r'list=([a-zA-Z0-9_-]+)', r)
                if yt_s:
                    play_url = f"plugin://plugin.video.youtube/channel/mine/playlist/{yt_s.group(1)}/"
                    name += " [COLOR green](YouTube)[/COLOR]"
        else:
            if "youtube.com" in r or "youtu.be" in r:
                yt_m = re.search(r'data-video_id="(.*?)"', r) or re.search(r'/embed/([^?\s"]+)', r)
                if yt_m:
                    play_url = f"plugin://plugin.video.youtube/play/?video_id={yt_m.group(1)}"
                    name += " [COLOR green](YouTube)[/COLOR]"
            if not play_url and "bandcamp.com" in r:
                bc_m = re.search(r'https://bandcamp\.com/EmbeddedPlayer/[^"]+', r)
                if bc_m:
                    bc_p = requests.get(bc_m.group(), headers=headers, timeout=10).text
                    st = re.search(r'mp3-128&quot;:&quot;(.*?)&quot;', bc_p)
                    if st:
                        play_url = st.group(1).replace('&amp;', '&')
                        name += " [COLOR green](Bandcamp)[/COLOR]"
        playable = 'true'
        if not play_url:
            name += " [COLOR red](not available)[/COLOR]"
            play_url = build_url({'mode': 'error-msg'})
            playable = 'false'
        li = xbmcgui.ListItem(name)
        li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
        li.setInfo('video', {'title': name})
        li.setProperty('IsPlayable', playable)
        return {"index": index, "url": play_url, "li": li, "is_folder": is_album}
    except: return None

def liste_items(match, is_album=False, is_top15=False):
    soup = BeautifulSoup(match, 'html.parser')
    items = soup.find_all('div', class_="td-module-meta-info")
    results = [None] * len(items)
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_item, item, i, is_album, is_top15): i for i, item in enumerate(items)}
        for f in as_completed(futures):
            res = f.result()
            if res: results[res["index"]] = res
    for r in results:
        if r: xbmcplugin.addDirectoryItem(handle=addon_handle, url=r["url"], listitem=r["li"], isFolder=r["is_folder"])
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def bandcampalbumresolver(url):
    try:
        r = requests.get(url, headers=headers, timeout=15).content.decode('utf-8')
        img_m = re.search(r'<link rel="image_src" href="(.*?)"', r)
        image = img_m.group(1) if img_m else addon_icon
        art_m = re.search(r'<meta name="title" content="(.*?), by (.*?)"', r)
        artist = html.unescape(art_m.group(2)) if art_m else "Unknown Artist"
        tracks = re.findall(r'&quot;artist&quot;:null,&quot;title&quot;:&quot;(.+?)&quot;,&quot;', r)
        urls = re.findall(r'mp3-128&quot;:&quot;(.*?)&quot;', r)
        for i, n in enumerate(tracks):
            n, t = html.unescape(n), str(i + 1).zfill(2)
            if i < len(urls):
                u = urls[i].replace('&amp;', '&')
                dn = f"[COLOR yellow]{t}[/COLOR] - [COLOR blue]{artist} - {n}[/COLOR] [COLOR green](Bandcamp)[/COLOR]"
                li = xbmcgui.ListItem(dn, path=u); li.setProperty('IsPlayable', 'true')
                li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
                li.setInfo('video', {'title': dn})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=li, isFolder=False)
            else:
                dn = f"[COLOR yellow]{t}[/COLOR] - [COLOR blue]{artist} - {n}[/COLOR] [COLOR red](not available)[/COLOR]"
                li = xbmcgui.ListItem(dn); li.setProperty('IsPlayable', 'false')
                li.setArt({'icon': image, 'thumb': image, 'poster': image, 'fanart': gewc.getAddonInfo('fanart')})
                li.setInfo('video', {'title': dn})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li, isFolder=False)
    except: pass
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

if mode is None:
    d = datum()
    menus = [
        {'m': 'reload', 't': d},
        {'m': 'top15', 't': 'GEWC - Top 15 - Tracks'},
        {'m': 'neuvorstellungen', 't': 'GEWC - Neuvorstellungen - Tracks'},
        {'m': 'top15alben', 't': 'GEWC - Top 15 - Alben'},
        {'m': 'neuvorstellungenalben', 't': 'GEWC - Neuvorstellungen - Alben'},
        {'m': 'warteliste', 't': 'GEWC - Warteliste - Tracks'},
        {'m': 'wartelistealben', 't': 'GEWC - Warteliste - Alben'}
    ]
    for i in menus:
        li = xbmcgui.ListItem(i['t'])
        li.setArt({'fanart': gewc.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb': addon_icon})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=build_url({'mode': i['m']}), listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

elif mode in ['top15', 'neuvorstellungen', 'top15alben', 'neuvorstellungenalben', 'warteliste', 'wartelistealben']:
    url_map = {
        'top15': ("https://www.gewc.de/top-15-charts/", r'>Top 15 Tracks</span>(.*?)>Top 15 Alben</span>', False, True),
        'neuvorstellungen': ("https://www.gewc.de/top-15-charts/", r'>Top 15 Tracks -  Neuvorstellungen</span>(.*?)>Top 15 Alben -  Neuvorstellungen</span>', False, False),
        'top15alben': ("https://www.gewc.de/top-15-charts/", r'>Top 15 Alben</span>(.*?)>Top 15 Tracks -  Neuvorstellungen</span>', True, True),
        'neuvorstellungenalben': ("https://www.gewc.de/top-15-charts/", r'>Top 15 Alben -  Neuvorstellungen</span>(.*?)<div class="td-footer-template-wrap"', True, False),
        'warteliste': ("https://www.gewc.de/warteliste/", r'>Top 15 Tracks</span>(.*?)>Top 15 Alben</span>', False, False),
        'wartelistealben': ("https://www.gewc.de/warteliste/", r'>Top 15 Alben</span>(.*?)<div class="td-footer-template-wrap"', True, False)
    }
    u, p, alb, rnk = url_map[mode]
    r = requests.get(u, headers=headers).text
    m = re.search(p, r, re.DOTALL | re.MULTILINE)
    if m: liste_items(m.group(1), is_album=alb, is_top15=rnk)

elif mode == 'resolve-album':
    u = args.get('url', [None])[0]
    if u: bandcampalbumresolver(u)

elif mode == 'error-msg':
    xbmcgui.Dialog().notification('Info', 'Link nicht verfügbar', 5000, addon_icon)

elif mode == 'reload':
    xbmc.executebuiltin('Container.Refresh')