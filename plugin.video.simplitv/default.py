import sys
import urllib.parse
import concurrent.futures
import requests
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
PLATFORM = "www"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:160.0) Gecko/20100101 Firefox/160.0"

FREE_PRODUCT_CODENAMES = {
    "simplitv-simplitv-streaming-gratis",
    "simplitv-simpli-free-streaming",
    "simplitv-simpli-free-streaming-antenne-streaming",
    "simplitv-free-streaming",
    "simplitv-simpli-free-streaming-sat-streaming",
    #"simplitv-gratis-testphase-simpli-free-streaming",
    "simplitv-free-antenne-streaming",
    "simplitv-free-sat-streaming",
}

API_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "de",
    "Origin": "https://streaming.simpli.at",
    "Referer": "https://streaming.simpli.at/",
    "X-Api-Date-Format": "iso",
    "X-Api-Resource-Language-Context": "de",
    "X-Api-Camel-Case": "true",
    "X-Tenant-Codename": TENANT
}

LOGIN_PAYLOAD_TEMPLATE = {
    "platformCodename": PLATFORM,
    "login": "",
    "password": ""
}

DEVICE_REG_PAYLOAD_TEMPLATE = {
    "platformCodename": PLATFORM,
    "deviceKey": "",
    "userToken": "",
    "pushToken": "",
    "generalDeviceType": "2",
    "deviceName": "Firefox",
    "browserVersion": "160.0",
    "userAgent": USER_AGENT,
    "operatingSystem": "Windows",
    "versionOs": "10"
}

EPG_PAYLOAD_TEMPLATE = {
    "platformCodename": PLATFORM,
    "from": "",
    "to": ""
}

TILES_PAYLOAD_TEMPLATE = {
    "platformCodename": PLATFORM,
    "requestedTiles": []
}


def get_show_free_only():
    try:
        return addon.getSettingBool("show_free_only")
    except Exception:
        val = str(addon.getSetting("show_free_only") or "").strip().lower()
        return val in ("true", "1", "yes")


def tile_has_free_product(tile, space_codename=TENANT):
    if not isinstance(tile, dict):
        return False

    target_space = str(space_codename or "").lower()
    space_products = tile.get("spaceProductCodenames") or []
    found_matching_space = False

    if isinstance(space_products, list):
        for entry in space_products:
            if not isinstance(entry, dict):
                continue
            if str(entry.get("spaceCodename") or "").lower() == target_space:
                found_matching_space = True
                prod_list = entry.get("productCodenames") or []
                for p in prod_list:
                    if str(p).lower() in FREE_PRODUCT_CODENAMES:
                        return True

    if found_matching_space:
        return False

    flat_products = tile.get("productCodenames") or []
    if isinstance(flat_products, list):
        for p in flat_products:
            if str(p).lower() in FREE_PRODUCT_CODENAMES:
                return True

    return False


def build_auth_headers(token, content_type=None):
    headers = API_HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def get_auth_token():
    username = addon.getSetting("username")
    password = addon.getSetting("password")

    if not username or not password:
        xbmcgui.Dialog().ok("SimpliTV", "Bitte trage E-Mail und Passwort in den Addon-Einstellungen ein.")
        return None

    try:
        login_url = f"{API_BASE}/v1/OrsUser/Authenticate"
        payload = LOGIN_PAYLOAD_TEMPLATE.copy()
        payload["login"] = username
        payload["password"] = password

        resp = requests.post(login_url, json=payload, headers=API_HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("token") or data.get("accessToken")
    except Exception:
        pass

    return None


def fetch_existing_device_key(token, headers):
    try:
        key_url = f"{API_BASE}/v1/Devices/GetDevices?platformCodename={PLATFORM}&token={token}"
        key_page = requests.get(key_url, timeout=15, headers=headers, allow_redirects=False)
        if key_page.status_code == 200:
            devices = key_page.json().get("devices", [])
            if devices:
                return devices[0].get("key")
    except Exception:
        pass
    return None


def devicekey(token=None):
    auth_token = token or get_auth_token()
    if not auth_token:
        return None

    headers = build_auth_headers(auth_token)
    existing_key = fetch_existing_device_key(auth_token, headers)
    if existing_key:
        return existing_key

    try:
        reg_url = f"{API_BASE}/v1/Devices/RegisterDevice"
        reg_headers = build_auth_headers(auth_token, "application/json;charset=utf-8")

        payload = DEVICE_REG_PAYLOAD_TEMPLATE.copy()
        payload["deviceKey"] = generate_key()
        payload["userToken"] = auth_token

        resp = requests.post(reg_url, headers=reg_headers, json=payload, timeout=15)
        if resp.status_code in [200, 201]:
            return fetch_existing_device_key(auth_token, headers)
    except Exception:
        pass

    return None


def generate_key():
    alphabet = string.ascii_letters.lower() + string.digits
    return "".join(random.choice(alphabet) for _ in range(32))


def fetch_tile_chunk(chunk_ids, headers):
    prg_url = f"{API_BASE}/v2/Tile/GetTiles"
    payload = TILES_PAYLOAD_TEMPLATE.copy()
    payload["requestedTiles"] = [{"id": tid} for tid in chunk_ids]

    try:
        prg_resp = requests.post(prg_url, headers=headers, json=payload, timeout=15)
        if prg_resp.status_code == 200:
            return prg_resp.json().get("tiles", [])
    except Exception:
        pass
    return []


def parse_iso_local(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str).astimezone()
    except Exception:
        return None


def format_epg_plot(entries, now_local, max_items=4):
    if not entries:
        return ""

    sorted_entries = sorted(
        entries,
        key=lambda x: x["start_dt"] or datetime.min.replace(tzinfo=now_local.tzinfo)
    )

    relevant = [
        e for e in sorted_entries
        if e["title"] and (not e["stop_dt"] or e["stop_dt"] > now_local)
    ]
    if not relevant:
        relevant = [e for e in sorted_entries if e["title"]]

    lines = []
    for entry in relevant[:max_items]:
        start_str = entry["start_dt"].strftime("%H:%M") if entry["start_dt"] else ""
        stop_str = entry["stop_dt"].strftime("%H:%M") if entry["stop_dt"] else ""
        time_range = f"{start_str} - {stop_str}" if start_str and stop_str else (start_str or stop_str)
        if time_range:
            lines.append(f"{time_range}\n{entry['title']}")
        else:
            lines.append(entry["title"])

    return "\n\n".join(lines)


def list_channels():
    try:
        token = get_auth_token()
        if not token:
            xbmcplugin.endOfDirectory(addon_handle)
            return

        show_free_only = get_show_free_only()
        headers = build_auth_headers(token)

        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone()

        epg_url = f"{API_BASE}/v1/EpgTile/FilterProgramTiles"
        epg_payload = EPG_PAYLOAD_TEMPLATE.copy()
        epg_payload["from"] = (now_utc - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        epg_payload["to"] = (now_utc + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        resp = requests.post(epg_url, headers=headers, json=epg_payload, timeout=15)
        if resp.status_code != 200:
            xbmcplugin.endOfDirectory(addon_handle)
            return

        epg_resp = resp.json().get("programs", {})

        tile_ids = []
        id_to_codename = {}
        for ch_key, progs in epg_resp.items():
            if isinstance(progs, list):
                for prog in progs[:5]:
                    if not isinstance(prog, dict):
                        continue
                    prog_id = prog.get("id")
                    if prog_id:
                        if prog_id not in tile_ids:
                            tile_ids.append(prog_id)
                        id_to_codename[prog_id] = str(ch_key).lower()

        if not tile_ids:
            xbmcplugin.endOfDirectory(addon_handle)
            return

        chunk_size = 25
        chunks = [tile_ids[i:i + chunk_size] for i in range(0, len(tile_ids), chunk_size)]

        channel_meta = {}
        epg_by_channel = {}
        free_channels = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_tile_chunk, chunk, headers) for chunk in chunks]
            for future in concurrent.futures.as_completed(futures):
                for tile in future.result():
                    if not isinstance(tile, dict):
                        continue
                    tile_channel = tile.get("tileChannel") or {}
                    codename = (tile_channel.get("codename") or id_to_codename.get(tile.get("id")) or "").lower()
                    title = tile_channel.get("title")
                    logo = tile_channel.get("logoUrlOnDark") or tile_channel.get("logoUrl", "")

                    if codename and title and codename not in channel_meta:
                        channel_meta[codename] = {
                            "title": title,
                            "codename": codename,
                            "logo": logo
                        }

                    if codename and tile_has_free_product(tile, TENANT):
                        free_channels.add(codename)

                    if codename:
                        prog_title = tile.get("title") or tile.get("subTitle") or tile.get("subtitle") or ""
                        start_dt = parse_iso_local(tile.get("start"))
                        stop_dt = parse_iso_local(tile.get("stop"))
                        epg_by_channel.setdefault(codename, []).append({
                            "title": prog_title,
                            "start_dt": start_dt,
                            "stop_dt": stop_dt
                        })

        channels = sorted(channel_meta.values(), key=lambda x: x["title"].lower())
        if show_free_only:
            channels = [ch for ch in channels if ch["codename"] in free_channels]

        for channel in channels:
            codename = channel["codename"]
            plot_text = format_epg_plot(epg_by_channel.get(codename, []), now_local)

            liz = xbmcgui.ListItem(label=channel["title"])
            liz.setProperty("IsPlayable", "true")

            info = liz.getVideoInfoTag()
            info.setTitle(channel["title"])
            info.setMediaType("video")
            if plot_text:
                info.setPlot(plot_text)

            if channel["logo"]:
                liz.setArt({"icon": channel["logo"], "thumb": channel["logo"]})

            play_url = f"{addon_url}?action=play&codename={urllib.parse.quote(codename)}"
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=play_url, listitem=liz, isFolder=False)

    except Exception:
        pass

    xbmcplugin.endOfDirectory(addon_handle)


def extract_stream_and_drm(res_data):
    stream_url = ""
    license_server_url = ""
    custom_data = ""

    def find_url(obj):
        nonlocal stream_url
        if stream_url:
            return
        if isinstance(obj, dict):
            for v in obj.values():
                if isinstance(v, str) and ("http://" in v or "https://" in v) and any(
                    ext in v.lower() for ext in (".mpd", ".m3u8", "manifest", "playlist")
                ):
                    stream_url = v
                    return
                if isinstance(v, (dict, list)):
                    find_url(v)
        elif isinstance(obj, list):
            for item in obj:
                find_url(item)

    for media_file in res_data.get("MediaFiles", []) or res_data.get("mediaFiles", []):
        for fmt in media_file.get("Formats", []) or media_file.get("formats", []):
            url = fmt.get("Url", "") or fmt.get("url", "")
            if url:
                stream_url = url
                if ".mpd" in url.lower():
                    break
        if stream_url and ".mpd" in stream_url.lower():
            break

    if not stream_url:
        find_url(res_data)

    drm_list = res_data.get("DrmInfo", []) or res_data.get("drmInfo", [])
    for drm in drm_list:
        if (drm.get("DrmSystem") or drm.get("drmSystem")) == "Widevine":
            license_server_url = drm.get("LicenseServerUrl") or drm.get("licenseServerUrl")
            custom_data = drm.get("DrmChallengeCustomData") or drm.get("drmChallengeCustomData")
            break

    return stream_url, license_server_url, custom_data


def play_channel(codename):
    try:
        token = get_auth_token()
        if not token:
            xbmcplugin.setResolvedUrl(addon_handle, False, listitem=xbmcgui.ListItem())
            return

        headers = build_auth_headers(token)
        dev_key = devicekey(token)

        acquire_url = (
            f"{API_BASE}/v1/Player/AcquireContent"
            f"?platformCodename={PLATFORM}&deviceKey={dev_key}&token={token}&codename={urllib.parse.quote(codename)}"
        )
        resp = requests.get(acquire_url, headers=headers, timeout=15)

        if resp.status_code == 200:
            stream_url, license_server_url, custom_data = extract_stream_and_drm(resp.json())

            if stream_url:
                is_dash = ".mpd" in stream_url.lower()
                protocol = "mpd" if is_dash else "hls"

                helper = inputstreamhelper.Helper(protocol, drm="com.widevine.alpha")
                if helper.check_inputstream():
                    liz = xbmcgui.ListItem(path=stream_url)
                    liz.setMimeType("application/dash+xml" if is_dash else "application/vnd.apple.mpegurl")
                    liz.setContentLookup(False)
                    liz.setProperty("inputstream", helper.inputstream_addon)
                    liz.setProperty("inputstream.adaptive.stream_type", protocol)

                    if license_server_url:
                        liz.setProperty("inputstream.adaptive.license_type", "com.widevine.alpha")
                        quoted_custom_data = urllib.parse.quote(custom_data) if custom_data else ""
                        license_key = (
                            f"{license_server_url}|User-Agent={USER_AGENT}"
                            f"&drmchallengecustomdata={quoted_custom_data}"
                            f"&Content-Type=application/octet-stream|R{{SSM}}|"
                        )
                        liz.setProperty("inputstream.adaptive.license_key", license_key)

                    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=liz)
                    return
    except Exception:
        pass

    xbmcplugin.setResolvedUrl(addon_handle, False, listitem=xbmcgui.ListItem())
    xbmcgui.Dialog().ok("SimpliTV", "Fehler beim Abspielen. Stream konnte nicht gestartet werden.")


def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring[1:]))
    action = params.get("action")

    if not action:
        list_channels()
    elif action == "play":
        play_channel(params["codename"])


if __name__ == "__main__":
    router(sys.argv[2])