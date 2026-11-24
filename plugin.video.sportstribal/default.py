import os
import sys
import re
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json
from datetime import datetime
import html

UNREEL_API_URL = 'https://epg.unreel.me/v2/sites/freelivesports/live-channels/public/90e79153782dc65c49b824d17b2dcb56'
GIZMOTT_SCHEDULE_URL = 'https://api.gizmott.com/api/v1/schedule/fastchannelsv2'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:160.0) Gecko/20100101 Firefox/160.0'
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGVjayI6dHJ1ZSwicHViaWQiOiI1MDE4MyIsInVpZCI6IjEwMjkxNDMwIiwiY291bnRyeV9jb2RlIjoiREUiLCJkZXZpY2VfdHlwZSI6IndlYiIsImlhdCI6MTc5NTUxMDA0MCwiZXhwIjoxODAzMjg2MDQwfQ.-aEP9JEbW5-geZ878hZHBChXk1bZ-D9ADHR3toyu0Ts'

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
sportstribal = xbmcaddon.Addon('plugin.video.sportstribal')

addon_icon = 'special://home/addons/plugin.video.sportstribal/icon.png'
addon_fanart = 'special://home/addons/plugin.video.sportstribal/fanart.jpg'


def get_local_tz():
    return datetime.now().astimezone().tzinfo


def get_api_timezone_name():
    try:
        import tzlocal
        tz_name = tzlocal.get_localzone_name()
        if tz_name:
            return tz_name
    except Exception:
        pass

    env_tz = os.environ.get('TZ')
    if env_tz:
        return env_tz.strip()

    return datetime.now().astimezone().tzname()


unreel_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
    'Origin': 'https://www.freelivesports.tv',
    'Referer': 'https://www.freelivesports.tv/',
}

gizmott_headers = {
    'User-Agent': USER_AGENT,
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'de,en-US;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Access-Control-Allow-Origin': 'true',
    'crossorigin': 'true',
    'access-token': ACCESS_TOKEN,
    'uid': '10291430',
    'pubid': '50183',
    'country_code': 'DE',
    'channelid': '516',
    'dev_id': 'c35c56f8cf84cdb3e38e962191e405a3',
    'device_type': 'web',
    'Origin': 'https://freelivesports.tv',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://freelivesports.tv/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
}


def norm_name(name):
    if not name:
        return ''
    return re.sub(r'[^a-z0-9]+', '', str(name).lower())


def set_item_metadata(listitem, title, plot):
    info_tag = listitem.getVideoInfoTag() if hasattr(listitem, 'getVideoInfoTag') else None
    if info_tag and hasattr(info_tag, 'setTitle') and hasattr(info_tag, 'setPlot'):
        info_tag.setTitle(title)
        info_tag.setPlot(plot)
    else:
        listitem.setInfo('Video', {'title': title, 'plot': plot})


def parse_schedule_dt(value, local_tz):
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    dt = None
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f'):
            try:
                dt = datetime.strptime(text, fmt)
                break
            except ValueError:
                dt = None
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=local_tz)
    return dt.astimezone(local_tz)


def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)


def fetch_gizmott_data(api_tz_name, local_tz):
    schedules_by_id = {}
    schedules_by_norm_name = {}
    gizmott_channels_by_norm = {}
    fallback_min = datetime.min.replace(tzinfo=local_tz)

    try:
        r = requests.get(
            GIZMOTT_SCHEDULE_URL,
            params={'timezone': api_tz_name},
            headers=gizmott_headers,
            timeout=10,
        )
        r.raise_for_status()
        payload = r.json()
        data = (payload or {}).get('data') or {}
        schedules = data.get('schedules') or []
        g_channels = data.get('channels') or []

        id_to_norm_name = {}
        if isinstance(g_channels, list):
            for ch in g_channels:
                if not isinstance(ch, dict):
                    continue
                ch_name = ch.get('name') or ch.get('title') or ch.get('channel_name') or ''
                n_key = norm_name(ch_name)
                if n_key:
                    gizmott_channels_by_norm[n_key] = ch
                for id_key in ('id', 'channel_id', 'channelId', '_id'):
                    val = ch.get(id_key)
                    if val is not None and n_key:
                        id_to_norm_name[str(val)] = n_key

        for item in schedules:
            if not isinstance(item, dict):
                continue
            ch_id = item.get('channel_id')
            if ch_id is None:
                continue
            key = str(ch_id)
            schedules_by_id.setdefault(key, []).append(item)
            n_key = id_to_norm_name.get(key)
            if n_key:
                schedules_by_norm_name.setdefault(n_key, []).append(item)

        for key in schedules_by_id:
            schedules_by_id[key].sort(key=lambda s: parse_schedule_dt(s.get('start'), local_tz) or fallback_min)
        for key in schedules_by_norm_name:
            schedules_by_norm_name[key].sort(key=lambda s: parse_schedule_dt(s.get('start'), local_tz) or fallback_min)
    except Exception as e:
        xbmc.log(f"Error fetching Gizmott data: {e}", xbmc.LOGERROR)

    return schedules_by_id, schedules_by_norm_name, gizmott_channels_by_norm


def match_gizmott_entries(channel, schedules_by_id, schedules_by_norm_name, gizmott_channels_by_norm):
    name = channel.get('name', '')
    n_key = norm_name(name)

    possible_ids = [
        str(channel.get(k))
        for k in ('channel_id', 'channelId', 'id', '_id', 'channelNumber')
        if channel.get(k) is not None
    ]
    for cid in possible_ids:
        if cid in schedules_by_id and schedules_by_id[cid]:
            return schedules_by_id[cid], gizmott_channels_by_norm.get(n_key)

    if n_key and n_key in schedules_by_norm_name and schedules_by_norm_name[n_key]:
        return schedules_by_norm_name[n_key], gizmott_channels_by_norm.get(n_key)

    if n_key:
        for g_key, entries in schedules_by_norm_name.items():
            if entries and (n_key in g_key or g_key in n_key):
                return entries, gizmott_channels_by_norm.get(g_key)

    return [], gizmott_channels_by_norm.get(n_key)


def get_current_and_next_show(entries, now_local, local_tz):
    current_show = None
    next_show = None

    for show in entries:
        start_dt = parse_schedule_dt(show.get('start'), local_tz)
        end_dt = parse_schedule_dt(show.get('end'), local_tz)
        if not start_dt or not end_dt:
            continue
        if start_dt <= now_local < end_dt:
            current_show = show
        elif start_dt > now_local and next_show is None:
            next_show = show
            if current_show is not None:
                break

    return current_show, next_show


def format_show_info(current_show, next_show, local_tz):
    lines = []

    if current_show:
        s_dt = parse_schedule_dt(current_show.get('start'), local_tz)
        e_dt = parse_schedule_dt(current_show.get('end'), local_tz)
        title = html.unescape(current_show.get('title', 'Unknown'))
        if s_dt and e_dt:
            lines.append(f"[COLOR green]Now:[/COLOR] [COLOR blue]({s_dt.strftime('%H:%M')} - {e_dt.strftime('%H:%M')})[/COLOR]\n{title}")
        else:
            lines.append(f"[COLOR green]Now:[/COLOR] {title}")

    if next_show:
        ns_dt = parse_schedule_dt(next_show.get('start'), local_tz)
        ne_dt = parse_schedule_dt(next_show.get('end'), local_tz)
        n_title = html.unescape(next_show.get('title', 'Unknown'))
        if ns_dt and ne_dt:
            lines.append(f"[COLOR yellow]Next:[/COLOR] [COLOR blue]({ns_dt.strftime('%H:%M')} - {ne_dt.strftime('%H:%M')})[/COLOR]\n{n_title}")
        else:
            lines.append(f"[COLOR yellow]Next:[/COLOR] {n_title}")

    return "\n".join(lines) if lines else "No show information available"


def format_full_epg(entries, local_tz):
    epg_text = ""
    for show in entries:
        s_dt = parse_schedule_dt(show.get('start'), local_tz)
        e_dt = parse_schedule_dt(show.get('end'), local_tz)
        title = html.unescape(show.get('title', 'Unknown'))
        if s_dt and e_dt:
            epg_text += f"[COLOR green]{s_dt.strftime('%d.%m.%Y %H:%M')}[/COLOR] - [COLOR yellow]{e_dt.strftime('%d.%m.%Y %H:%M')}[/COLOR] {title}\n"
    return epg_text or "No EPG entries available"


def get_channels():
    local_tz = get_local_tz()
    now_local = datetime.now(local_tz)
    api_tz_name = get_api_timezone_name()
    schedules_by_id, schedules_by_norm_name, gizmott_channels_by_norm = fetch_gizmott_data(api_tz_name, local_tz)

    try:
        r = requests.get(
            UNREEL_API_URL,
            params={'__site': 'freelivesports', '__source': 'web'},
            headers=unreel_headers,
            timeout=10,
        )
        r.raise_for_status()
        channels = r.json()

        for channel in channels:
            if not isinstance(channel, dict):
                continue
            name = channel.get('name', 'Unknown Channel')
            logo = channel.get('thumbnail') or ''
            raw_url = channel.get('url') or ''
            stream = raw_url.split('?')[0]

            epg_entries, g_ch = match_gizmott_entries(
                channel, schedules_by_id, schedules_by_norm_name, gizmott_channels_by_norm
            )

            if not logo and isinstance(g_ch, dict):
                logo = g_ch.get('thumbnail') or g_ch.get('logo') or ''
            if not stream and isinstance(g_ch, dict):
                g_url = g_ch.get('url') or g_ch.get('stream_url') or ''
                stream = g_url.split('?')[0]

            if not epg_entries:
                epg_entries = (channel.get('epg') or {}).get('entries') or []

            current_show, next_show = get_current_and_next_show(epg_entries, now_local, local_tz)
            desc = format_show_info(current_show, next_show, local_tz)

            url = build_url({'mode': 'play', 'stream': stream, 'name': name, 'desc': desc, 'logo': logo})
            li = xbmcgui.ListItem(name)
            set_item_metadata(li, name, desc)
            li.setArt({'fanart': addon_fanart, 'icon': logo, 'thumb': logo})
            commands = []
            commands.append(("Full EPG", f"RunPlugin({build_url({'mode': 'full_epg', 'epg': json.dumps(epg_entries), 'name': name})})"))
            li.addContextMenuItems(commands)
            xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
    except requests.exceptions.RequestException as e:
        xbmc.log(f"Error fetching channels: {e}", xbmc.LOGERROR)
        xbmcplugin.endOfDirectory(addon_handle, succeeded=False, cacheToDisc=False)


def play(stream, name, desc, logo):
    play_item = xbmcgui.ListItem(path=stream)
    play_item.setContentLookup(False)
    play_item.setProperty('IsPlayable', 'true')
    set_item_metadata(play_item, name, desc)
    play_item.setArt({'fanart': addon_fanart, 'thumb': logo, 'icon': logo})
    xbmcplugin.setResolvedUrl(addon_handle, True, play_item)
    xbmc.Player().play(item=stream, listitem=play_item)


def show_full_epg(epg, name):
    local_tz = get_local_tz()
    epg_text = format_full_epg(json.loads(epg), local_tz)
    dialog = xbmcgui.Dialog()
    dialog.textviewer(name, epg_text)


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