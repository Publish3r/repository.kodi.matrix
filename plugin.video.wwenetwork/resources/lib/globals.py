# coding=utf-8
import sys
import re, os
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, requests
import xbmc, xbmcplugin, xbmcvfs, xbmcgui, xbmcaddon

addon_handle = int(sys.argv[1])

#Addon Info
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
ADDON_PATH_PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
XBMC_VERSION = float(re.findall(r'\d{2}\.\d{1}', xbmc.getInfoLabel("System.BuildVersion"))[0])
LOCAL_STRING = ADDON.getLocalizedString
ROOTDIR = ADDON.getAddonInfo('path')

#Images
ICON = os.path.join(ROOTDIR,"icon.png")
FANART = os.path.join(ROOTDIR,"fanart.jpg")
PREV_ICON = os.path.join(ROOTDIR,"icon.png")
NEXT_ICON = os.path.join(ROOTDIR,"icon.png")

#Headers
SIMPLE_HEADER = {'User-Agent': 'okhttp/3.12.1',
        'Content-Type': 'application/json',
        'Realm': 'dce.wwe',
        'x-api-key': 'cca51ea0-7837-40df-a055-75eb6347b2e7'
        }

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
                            
    return param

def add_stream(name, title, content_type, content_id, icon, fanart=None, info=None, video_info=None, audio_info=None, start_point=None):
    ok=True
    mode=104
    if(content_type=='event'):
        mode=103

    u=sys.argv[0]+"?mode="+str(mode)+"&content_id="+urllib.parse.quote_plus(str(content_id))+"&content_name="+urllib.parse.quote_plus(name.encode('ascii','ignore'))
    if start_point is not None:
        u = u+"&start_point="+urllib.parse.quote_plus(start_point)

    liz=xbmcgui.ListItem(name)
    liz.setArt({'icon' : ICON, 'thumb' : icon})
    
    if fanart is not None:
        liz.setProperty('fanart_image', fanart)       
    else:
        liz.setProperty('fanart_image', FANART)

    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": title } )
    if info is not None:
        liz.setInfo( type="Video", infoLabels=info)
    if video_info is not None:
        liz.addStreamInfo('video', video_info)
    if audio_info is not None:
        liz.addStreamInfo('audio', audio_info)

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmcplugin.setContent(addon_handle, 'episodes')
    
    return ok

def addDir(name,mode,iconimage,fanart=None,content_id=None,year=None,sub_filter=None,season_id=None,path=None,info=None):
    ok=True

    u=sys.argv[0]+"?mode="+str(mode)+"&name="+urllib.parse.quote_plus(name.encode('ascii','ignore'))+"&icon="+urllib.parse.quote_plus(iconimage)
    if content_id is not None:
        u = u+"&content_id="+urllib.parse.quote_plus(content_id)
    if year is not None:
        u = u+"&year="+urllib.parse.quote_plus(year)
    if sub_filter is not None:
        u = u+"&sub_filter="+urllib.parse.quote_plus(sub_filter)
    if season_id is not None:
        u = u+"&season_id="+urllib.parse.quote_plus(season_id)
    if path is not None:
        u = u+"&path="+urllib.parse.quote_plus(path)

    if iconimage is not None:
        liz=xbmcgui.ListItem(name)
        liz.setArt({ 'icon': 'DefaultVideo.png', 'thumb' : iconimage })         
    else:
        liz=xbmcgui.ListItem(name) 
        liz.setArt({ 'icon': 'DefaultVideo.png', 'thumb' : ICON })
        

    liz.setInfo( type="Video", infoLabels={ "Title": name } )

    if fanart is not None:
        liz.setProperty('fanart_image', fanart)
    else:
        liz.setProperty('fanart_image', FANART)

    if info is not None:
        liz.setInfo( type="Video", infoLabels=info)

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    return ok

def stream_to_listitem(stream_url, content_name, start_point=None):
    listitem = xbmcgui.ListItem(content_name,path=stream_url,offscreen=True)
    listitem.setProperty('inputstream', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
    listitem.setProperty('IsPlayable', 'true')
    if start_point is not None:
        listitem.setProperty('TotalTime',start_point)
        listitem.setProperty('ResumeTime',start_point)
    listitem.setMimeType("application/vnd.apple.mpegurl")
    listitem.setContentLookup(False)
    return listitem

def check_request_result(r, status_code):
    if r.status_code != status_code:
        dialog = xbmcgui.Dialog()
        title = "Error Occured"
        msg = ""
        for item in r.json()['messages']:
            msg += item + '\n'
        dialog.notification(title, msg, ICON, 5000, False)
        return False
    return True

def generate_authorization_header(login_token):
    return {'User-Agent': 'okhttp/3.12.1',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Realm': 'dce.wwe',
            'x-api-key': 'cca51ea0-7837-40df-a055-75eb6347b2e7',
            'Authorization': 'Bearer ' + login_token
            }
