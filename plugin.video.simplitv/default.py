import sys
import json
import traceback
import urllib.parse
import concurrent.futures
import requests
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import inputstreamhelper
from datetime import datetime, timezone, timedelta
import string
import random

addon = xbmcaddon.Addon()
addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])

API_BASE = "https://api.app.austrostream.at"
TENANT = "simplitv"

api_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:160.0) Gecko/20100101 Firefox/160.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'de',
    'Origin': 'https://streaming.simpli.at',
    'Referer': 'https://streaming.simpli.at/',
    'X-Api-Date-Format': 'iso',
    'X-Api-Resource-Language-Context': 'de',
    'X-Api-Camel-Case': 'true',
    'X-Tenant-Codename': TENANT
}

def get_auth_token():
    username = addon.getSetting('username')
    password = addon.getSetting('password')
    
    if not username or not password:
        xbmcgui.Dialog().ok("SimpliTV", "Bitte trage E-Mail und Passwort in den Addon-Einstellungen ein.")
        return None

    try:
        login_url = f"{API_BASE}/v1/OrsUser/Authenticate"
        payload = {
            "platformCodename": "www",
            "login": username,
            "password": password
        }
        resp = requests.post(login_url, json=payload, headers=api_headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('token') or data.get('accessToken')
    except Exception:
        pass
    
    return None

def devicekey():
    token = get_auth_token()
    if not token:
        return None

    headers = api_headers.copy()
    headers["Authorization"] = f"Bearer {token}"

    try:
        key_url = f"{API_BASE}/v1/Devices/GetDevices?platformCodename=www&token={token}"
        key_page = requests.get(key_url, timeout=15, headers=headers, allow_redirects=False)
        if key_page.status_code == 200:
            key_resp = key_page.json()
            devices = key_resp.get('devices', [])
            if devices and len(devices) > 0:
                return devices[0]['key']
    except Exception:
        pass

    try:
        reg_url = f"{API_BASE}/v1/Devices/RegisterDevice"
        
        reg_headers = headers.copy()
        reg_headers["Content-Type"] = "application/json;charset=utf-8"

        new_device_key = generate_key()
        payload = {
            "platformCodename": "www",
            "deviceKey": new_device_key,
            "userToken": token,
            "pushToken": "",
            "generalDeviceType": "2",
            "deviceName": "Firefox",
            "browserVersion": "160.0",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:160.0) Gecko/20100101 Firefox/160.0",
            "operatingSystem": "Windows",
            "versionOs": "10"
        }

        resp = requests.post(reg_url, headers=reg_headers, json=payload, timeout=15)
        if resp.status_code in [200, 201]:
            key_url = f"{API_BASE}/v1/Devices/GetDevices?platformCodename=www&token={token}"
            key_page = requests.get(key_url, timeout=15, headers=headers, allow_redirects=False)
            if key_page.status_code == 200:
                key_resp = key_page.json()
                devices = key_resp.get('devices', [])
                if devices and len(devices) > 0:
                    return devices[0]['key']
    except Exception:
        pass

    return None
            
def generate_key():
    generate = string.ascii_letters.lower() + string.digits
    devicekey = ''.join((random.choice(generate) for i in range(32)))
    return devicekey

def fetch_tile_chunk(chunk_ids, headers):
    prg_url = f"{API_BASE}/v2/Tile/GetTiles"
    requested_tiles = [{"id": tid} for tid in chunk_ids]
    prg_post = {
        "platformCodename": "www",
        "requestedTiles": requested_tiles
    }
    try:
        prg_resp = requests.post(prg_url, headers=headers, json=prg_post, timeout=15)
        if prg_resp.status_code == 200:
            return prg_resp.json().get("tiles", [])
    except Exception:
        pass
    return []

def list_channels():
    try:
        token = get_auth_token()
        if not token:
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            return

        headers = api_headers.copy()
        headers["Authorization"] = f"Bearer {token}"

        now_utc = datetime.now(timezone.utc)
        time_start = now_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        time_end = (now_utc + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        epg_url = f"{API_BASE}/v1/EpgTile/FilterProgramTiles"
        epg_post = {
            "platformCodename": "www",
            "from": time_start,
            "to": time_end
        }
        
        resp = requests.post(epg_url, headers=headers, json=epg_post, timeout=15)
        if resp.status_code != 200:
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            return
            
        epg_resp = resp.json().get("programs", {})

        tile_ids = []
        for ch_key, progs in epg_resp.items():
            if isinstance(progs, list) and len(progs) > 0:
                prog_id = progs[0].get("id")
                if prog_id and prog_id not in tile_ids:
                    tile_ids.append(prog_id)

        if not tile_ids:
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            return

        chunk_size = 25
        chunks = [tile_ids[i:i + chunk_size] for i in range(0, len(tile_ids), chunk_size)]
        
        channels = []
        seen_codenames = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_tile_chunk, chunk, headers) for chunk in chunks]
            for future in concurrent.futures.as_completed(futures):
                tiles_data = future.result()
                for tile in tiles_data:
                    tile_channel = tile.get("tileChannel", {})
                    codename = tile_channel.get("codename")
                    title = tile_channel.get("title")
                    logo = tile_channel.get("logoUrlOnDark") or tile_channel.get("logoUrl", "")
                    
                    if codename and title and codename not in seen_codenames:
                        seen_codenames.add(codename)
                        channels.append({
                            'title': title,
                            'codename': codename,
                            'logo': logo
                        })

        channels.sort(key=lambda x: x['title'].lower())

        for channel in channels:
            liz = xbmcgui.ListItem(label=channel['title'])
            liz.setProperty('IsPlayable', 'true')
            
            info = liz.getVideoInfoTag()
            info.setTitle(channel['title'])
            info.setMediaType('video')
            
            if channel['logo']:
                liz.setArt({'icon': channel['logo'], 'thumb': channel['logo']})
            
            play_url = f"{addon_url}?action=play&codename={channel['codename']}&token={token}"
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=play_url, listitem=liz, isFolder=False)
                
    except Exception:
        pass

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def play_channel(codename, token):
    try:
        headers = api_headers.copy()
        headers["Authorization"] = f"Bearer {token}"

        dev_key = devicekey()

        acquire_url = f"{API_BASE}/v1/Player/AcquireContent?platformCodename=www&deviceKey={dev_key}&token={token}&codename={codename}"
        resp = requests.get(acquire_url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            res_data = resp.json()
            stream_url = ""
            license_server_url = ""
            custom_data = ""
            
            def find_url(obj):
                nonlocal stream_url
                if stream_url:
                    return
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, str) and ('http://' in v or 'https://' in v) and ('.mpd' in v.lower() or '.m3u8' in v.lower() or 'manifest' in v.lower() or 'playlist' in v.lower()):
                            stream_url = v
                            return
                        elif isinstance(v, (dict, list)):
                            find_url(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_url(item)

            for media_file in res_data.get('MediaFiles', []) or res_data.get('mediaFiles', []):
                for fmt in media_file.get('Formats', []) or media_file.get('formats', []):
                    url = fmt.get('Url', '') or fmt.get('url', '')
                    if url:
                        stream_url = url
                        if '.mpd' in url.lower():
                            break
                if stream_url and '.mpd' in stream_url.lower():
                    break

            if not stream_url:
                find_url(res_data)

            drm_list = res_data.get('DrmInfo', []) or res_data.get('drmInfo', [])
            for drm in drm_list:
                if (drm.get('DrmSystem') or drm.get('drmSystem')) == 'Widevine':
                    license_server_url = drm.get('LicenseServerUrl') or drm.get('licenseServerUrl')
                    custom_data = drm.get('DrmChallengeCustomData') or drm.get('drmChallengeCustomData')
                    break

            if stream_url:
                is_dash = '.mpd' in stream_url.lower()
                protocol = 'mpd' if is_dash else 'hls'
                
                helper = inputstreamhelper.Helper(protocol, drm='com.widevine.alpha')
                if helper.check_inputstream():
                    liz = xbmcgui.ListItem(path=stream_url)
                    liz.setMimeType('application/dash+xml' if is_dash else 'application/vnd.apple.mpegurl')
                    liz.setContentLookup(False)
                    liz.setProperty('inputstream', helper.inputstream_addon)
                    liz.setProperty('inputstream.adaptive.stream_type', protocol)
                    
                    if license_server_url:
                        liz.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
                        
                        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                        quoted_custom_data = urllib.parse.quote(custom_data) if custom_data else ""
                        
                        license_key = f"{license_server_url}|User-Agent={user_agent}&drmchallengecustomdata={quoted_custom_data}&Content-Type=application/octet-stream|R{{SSM}}|"
                        liz.setProperty('inputstream.adaptive.license_key', license_key)

                    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=liz)
                    return
    except Exception:
        pass

    xbmcplugin.setResolvedUrl(addon_handle, False, listitem=xbmcgui.ListItem())
    xbmcgui.Dialog().ok("SimpliTV", "Fehler beim Abspielen. Stream konnte nicht gestartet werden.")

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring[1:]))
    action = params.get('action')

    if not action:
        list_channels()
    elif action == 'play':
        play_channel(params['codename'], params['token'])

if __name__ == '__main__':
    router(sys.argv[2])