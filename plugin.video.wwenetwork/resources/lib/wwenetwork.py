from resources.lib.globals import *
from .account import Account

API_BASE_URL = 'https://cdn.watch.wwe.com/api'
SEARCH_PATH = '/lookup'
FILTER_EPISODES_PATH = '/filter/episodes'
ITEMS_CHILDREN_PATH = '/items/{}/children'
PAGE_PATH = '/page'
LISTS_PATH = '/lists/{}'

VIDEO_INFO = { 'codec': 'h264', 'width' : 1920, 'height' : 1080, 'aspect' : 1.78 }        
AUDIO_INFO = { 'codec': 'aac', 'language': 'en', 'channels': 2 }

def categories():
    add_stream('Live Stream', 'Live Stream', 'event', 'live', ICON, FANART)
    addDir('Featured', 100, ICON, FANART, '/')
    addDir('WWE PPV', 105, ICON, FANART, path='/wwe-ppv')
    addDir('Raw', 107, ICON, FANART, content_id='1007',path='/in-ring/1007')
    addDir('Smackdown', 107, ICON, FANART, content_id='3622', path='/in-ring/3622')
    addDir('NXT', 105, ICON, FANART, path='/nxt/1002')
    addDir('In-Ring', 100, ICON, FANART, '/in-rings')
    addDir('Originals', 100, ICON, FANART, '/originals')
    addDir('Search', 109, ICON, FANART)
    addDir('Logout', 400, ICON, FANART)

def play_event(content_id, content_name):
    account = Account()
    url = account.get_event_stream(content_id)
    play_stream(url, content_name)

def play_vod(content_id, content_name, start_point=None):
    account = Account()
    url = account.get_stream('vod/' + content_id)
    play_stream(url, content_name, start_point)

def play_stream(stream_url, content_name, start_point=None):
    listitem = stream_to_listitem(stream_url, content_name, start_point)
    xbmcplugin.setResolvedUrl(handle=addon_handle, succeeded=True, listitem=listitem)

def list_page(path):
    query_values = {
            'path': path,
            'ff': 'idp,ldp'
            }
    r = requests.get(API_BASE_URL + PAGE_PATH, params=query_values)
    for entry in r.json()['entries']:
        if entry['type'] == 'ListEntry':
            addDir(entry['title'],101,ICON,FANART,entry['list']['id'])

def list_decider(content_id, path):
    query_values = {
            'path': path,
            'ff': 'idp,ldp'
            }
    r = requests.get(API_BASE_URL + PAGE_PATH, params=query_values)
    template = r.json()['template']
    if template == 'WWE PPV':
        list_filters(path)
    elif template == 'Category':
        list_page(path)
    elif template == 'WWE Show Detail':
        list_seasons(content_id,path)
    else:
        dialog = xbmcgui.Dialog()
        dialog.notification('Error Occured', 'Unknown Template: ' + template, ICON, 5000, False)

def list_filters(path, target_sub_filter=None):
    query_values = {
            'path': path,
            'ff': 'idp,ldp'
            }
    r = requests.get(API_BASE_URL + PAGE_PATH, params=query_values)
    show_ids = ''
    entries = r.json()['entries']
    filters = None
    for entry in entries:
        if 'filters' in entry:
            filters = entry['filters']
    if filters is None:
        sys.exit()

    info = {}
    icon = ICON
    if 'item' in r.json():
        item = r.json()['item']
        plot = item['description']
        show_title = item['title']
        genre = next(iter(item['genres']), '')
        info = {'plot': plot, 'tvshowtitle': show_title, 'genre': genre, 'mediatype': 'video'}
        icon = item['images']['tile']
    matched_sub_filters = []
    for filter in filters:
        for filter_entry in filter['filterEntries']:
            if target_sub_filter==None:
                addDir(filter_entry['label'],105,icon,FANART,path=path,sub_filter=filter_entry['value'],info=info)
            elif target_sub_filter != 'all_shows' and filter_entry['value'] == target_sub_filter:
                show_ids = show_ids + filter_entry['value'] + ','
                sub_filters = filter_entry['subFilter']
                for sub_filter in sub_filters:
                    matched_sub_filters.append(sub_filter)
            elif target_sub_filter == 'all_shows':
                if filter_entry['value'] == 'all_shows':
                    sub_filters = filter_entry['subFilter']
                    for sub_filter in sub_filters:
                        matched_sub_filters.append(sub_filter)
                    continue
                show_ids = show_ids + filter_entry['value'] + ','

    show_ids = show_ids[:-1]
    for f in matched_sub_filters:
        addDir(f['label'],106,icon,FANART,show_ids,f['value'],info=info)

def process_items(items):
    for item in items:
        if 'axisItem' in item:
            item = item['axisItem']
        if item['type'] == 'show' or item['type'] == 'link':
            plot = item['shortDescription']
            if plot == 'LinkItem':
                plot = ''
            title = item['title']
            genre = next(iter(item['genres']), '')
            info = {'plot': plot, 'tvshowtitle': title, 'title': title, 'genre': genre, 'mediatype': 'video'}
            addDir(item['title'], 108, item['images']['tile'], FANART, content_id=item['id'],path=item['path'],info=info)
            continue
        if 'DiceVideoId' not in item['customFields']:
            continue
        start_point = None
        if 'StartPoint' in item['customFields']:
            start_point = str(item['customFields']['StartPoint'])
        aired = ''
        date = ''
        if 'firstBroadcastDate' in item:
            aired = item['firstBroadcastDate'].replace('T',' ').replace('Z','')
            date = aired[8:10]+'.'+aired[5:7]+'.'+aired[0:4]
        genre = next(iter(item['genres']), '')
        show_title = item['metadataLines'][0]['lines'][0]
        episode_title = item['metadataLines'][0]['lines'][1]
        plot = item['metadataLines'][2]['lines'][2]
        info = {'plot': plot, 'tvshowtitle': show_title, 'title': show_title + ' - ' + episode_title, 'aired': aired, 'date': date, 'genre': genre, 'mediatype': 'video'}
        icon = item['images']['tile'] + '|encoding=gzip&accept-encoding=gzip, deflate, br&accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
        fanart = item['images']['wallpaper'] + '|encoding=gzip&accept-encoding=gzip, deflate, br&accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
        add_stream(item['title'], item['title'], 'episode', item['customFields']['DiceVideoId'], icon=icon, fanart=fanart, info=info, video_info=VIDEO_INFO,audio_info=AUDIO_INFO,start_point=start_point)

def list_seasons(content_id, path):
    query_values = {
            'path': path,
            'ff': 'idp,ldp',
            'item_detail_expand': 'all',
            'item_detail_select_season': 'first'
            }
    r = requests.get(API_BASE_URL + PAGE_PATH, params=query_values)
    pre_text = ''

    info = {}
    icon = ICON
    if 'item' in r.json():
        item = r.json()['item']
        plot = item['description']
        show_title = item['title']
        genre = next(iter(item['genres']), '')
        info = {'plot': plot, 'tvshowtitle': show_title, 'genre': genre, 'mediatype': 'video'}
        icon = item['images']['tile']
        fanart = item['images']['wallpaper']

    if not r.json()['item']['customFields']['IsSeasonal']:
        addDir('Most Recent',106,icon,FANART,content_id,'most_recent',info=info)
    else:
        pre_text = 'Season '
    for item in r.json()['item']['seasons']['items']:
        addDir(pre_text + str(item['seasonNumber']),106,icon,fanart,content_id,str(item['seasonNumber']),season_id=str(item['id']),info=info)

def fetch_list(list_id):
    page = 1
    while True:
        query_values = {
                'ff': 'idp,ldp',
                'page_size': 100,
                'page': page
                }
        r = requests.get(API_BASE_URL + LISTS_PATH.format(list_id),params=query_values)
        process_items(r.json()['items'])
        if 'next' not in r.json()['paging']:
            break
        page = page + 1

def fetch_episodes(show_ids, season_number=None, season_id=None):
    query_values = {}
    if season_number is None or season_number == 'most_recent' or int(season_number) > 1900:
        url = API_BASE_URL + FILTER_EPISODES_PATH
        query_values = {
                'page_size': 50,
                'showIds': show_ids,
                'segments': 'us'
                }
        if(season_number is not None and season_number != 'most_recent'):
            query_values['year'] = season_number
    elif season_id is not None:
        url = API_BASE_URL + ITEMS_CHILDREN_PATH.format(season_id)
    else:
        sys.exit()
    page = 1
    while True:
        query_values['page'] = page
        r = requests.get(url, params=query_values)
        process_items(r.json()['items'])
        if 'next' not in r.json()['paging']:
            break
        page = page + 1

def search(term):
    query_values = {
            'max_list_prefetch': 0,
            'segments': 'us',
            'term': term
            }
    r = requests.get(API_BASE_URL + SEARCH_PATH, params=query_values)
    groups = r.json()['groups']
    for group in groups:
        if group['items'][0]['wweItem'] is None:
            addDir(group['id'], 110, ICON, FANART, content_id = term, path = '/' + group['id'])

def list_search_results(term, path):
    page = 1
    while True:
        query_values = {
                'segments': 'us',
                'term': term,
                'page': page
                }
        r = requests.get(API_BASE_URL + SEARCH_PATH + path, params=query_values)
        process_items(r.json()['groups'][0]['items'])
        if not r.json()['groups'][0]['nextResults']:
            break
        page = page + 1
