import sys
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json
from datetime import datetime, timezone
import tzlocal
import html

# Constants
API_URL = 'https://epg.unreel.me/v2/sites/freelivesports/live-channels/public/90e79153782dc65c49b824d17b2dcb56'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'

# Plugin setup
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
sportstribal = xbmcaddon.Addon('plugin.video.sportstribal')

# Assets
addon_icon = 'special://home/addons/plugin.video.sportstribal/icon.png'
addon_fanart = 'special://home/addons/plugin.video.sportstribal/fanart.jpg'

# Request headers
headers = {
    'User-Agent': USER_AGENT,
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

# Request parameters
params = {
    '__site': 'freelivesports',
    '__source': 'web',
}

def build_url(query):
    """Builds a URL for the plugin."""
    return base_url + '?' + urllib.parse.urlencode(query)

def get_current_and_next_show(epg, current_time):
    """Gets the current and next show from the EPG data."""
    current_show = None
    next_show = None
    for show in epg:
        if 'start' in show and 'stop' in show:
            try:
                start_time = datetime.strptime(show['start'], '%Y-%m-%dT%H:%M:%S.%fZ')
                stop_time = datetime.strptime(show['stop'], '%Y-%m-%dT%H:%M:%S.%fZ')
                if start_time <= current_time < stop_time:
                    current_show = show
                elif current_show and start_time > current_time and not next_show:
                    next_show = show
            except ValueError:
                # Handle invalid date format
                xbmc.log(f"Invalid date format for show: {show}", xbmc.LOGERROR)
        else:
            # Handle missing 'start' or 'stop' key
            xbmc.log(f"Missing 'start' or 'stop' key for show: {show}", xbmc.LOGERROR)
    return current_show, next_show

def format_show_info(current_show, next_show, local_tz):
    """Formats the show information for display."""
    if current_show and next_show:
        if 'start' in current_show and 'stop' in current_show and 'start' in next_show and 'stop' in next_show:
            start_time = datetime.strptime(current_show['start'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
            end_time = datetime.strptime(current_show['stop'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
            next_start_time = datetime.strptime(next_show['start'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
            next_end_time = datetime.strptime(next_show['stop'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
            title = html.unescape(current_show.get('title', 'Unknown'))
            next_title = html.unescape(next_show.get('title', 'Unknown'))
            return f"[COLOR green]Now:[/COLOR] [COLOR blue]({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')})[/COLOR]\n{title}\n[COLOR yellow]Next:[/COLOR] [COLOR blue]({next_start_time.strftime('%H:%M')} - {next_end_time.strftime('%H:%M')})[/COLOR]\n{next_title}"
        else:
            return "No show information available"
    elif current_show:
        if 'start' in current_show and 'stop' in current_show:
            start_time = datetime.strptime(current_show['start'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
            end_time = datetime.strptime(current_show['stop'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
            title = html.unescape(current_show.get('title', 'Unknown'))
            return f"[COLOR green]Now:[/COLOR] [COLOR blue]({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')})[/COLOR]\n{title}"
        else:
            return "No show information available"
    else:
        return "No show information available"

def format_full_epg(epg, local_tz):
    """Formats the full EPG for display."""
    epg_text = ""
    for show in epg:
        if 'start' in show and 'stop' in show:
            try:
                start_time = datetime.strptime(show['start'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
                end_time = datetime.strptime(show['stop'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
                title = html.unescape(show.get('title', 'Unknown'))
                epg_text += f"[COLOR green]{start_time.strftime('%d.%m.%Y %H:%M')}[/COLOR] - [COLOR yellow]{end_time.strftime('%d.%m.%Y %H:%M')}[/COLOR] {title}\n"
            except ValueError:
                # Handle invalid date format
                xbmc.log(f"Invalid date format for show: {show}", xbmc.LOGERROR)
        else:
            # Handle missing 'start' or 'stop' key
            xbmc.log(f"Missing 'start' or 'stop' key for show: {show}", xbmc.LOGERROR)
    return epg_text

def get_channels():
    """Fetches and lists the channels."""
    current_time = datetime.utcnow()
    local_tz = tzlocal.get_localzone()
    try:
        r = requests.get(API_URL, params=params, headers=headers, timeout=5)
        json_data = json.loads(r.content.decode())
        for channel in json_data:
            name = channel['name']
            logo = channel['thumbnail']
            stream = channel['url'].split("?")[0]
            epg_data = channel.get('epg', {}).get('entries', [])
            current_show, next_show = get_current_and_next_show(epg_data, current_time)
            desc = format_show_info(current_show, next_show, local_tz)
            url = build_url({'mode': 'play', 'stream': stream, 'name': name, 'desc': desc, 'logo': logo})
            li = xbmcgui.ListItem(name)
            li.setInfo('Video', {"title": name, "plot": desc})
            li.setArt({'fanart': addon_fanart, 'icon': logo, 'thumb': logo})
            commands = []
            commands.append(( "Full EPG", f"RunPlugin({build_url({'mode': 'full_epg', 'epg': json.dumps(epg_data), 'name': name})})", ))
            li.addContextMenuItems(commands)
            xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
    except requests.exceptions.RequestException as e:
        xbmc.log(f"Error fetching channels: {e}", xbmc.LOGERROR)

def play(stream, name, desc, logo):
    """Plays the selected stream."""
    play_item = xbmcgui.ListItem(path=stream)
    play_item.setContentLookup(False)
    play_item.setProperty('IsPlayable', 'true')
    play_item.setInfo("Video", {"title": name, 'plot': desc})
    play_item.setArt({'fanart': addon_fanart, 'thumb': logo, 'icon': logo})
    xbmcplugin.setResolvedUrl(addon_handle, True, play_item)
    xbmc.Player().play(item=stream, listitem=play_item)

def show_full_epg(epg, name):
    """Shows the full EPG for the selected channel."""
    local_tz = tzlocal.get_localzone()
    epg_text = format_full_epg(json.loads(epg), local_tz)
    dialog = xbmcgui.Dialog()
    dialog.textviewer(name, epg_text)

# Main logic
mode = args.get('mode', None)
if mode is None:
    get_channels()
elif mode[0] == "play":
    stream = args['stream'][0]
    name = args['name'][0]
    desc = args['desc'][0]
    logo = args['logo'][0]
    play(stream, name, desc, logo)
elif mode[0] == "full_epg":
    epg = args['epg'][0]
    name = args['name'][0]
    show_full_epg(epg, name)