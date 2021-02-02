from __future__ import unicode_literals

import urllib.request, urllib.parse, urllib.error

from kodi_six import xbmc, xbmcgui


def log(x):
    xbmc.log(repr(x), xbmc.LOGERROR)


channel = xbmc.getInfoLabel('ListItem.Label')
try:
    channel = channel.decode()
except:
    pass
try:
    channel = channel.encode()
except:
    pass
channel = urllib.parse.quote_plus(channel)

try:

    d = xbmcgui.Dialog()
    select = d.select("IPTV Recorder", ["Add Timed Recording",
                                        "Add Daily Timed Recording",
                                        "Add Weekly Timed Recording",
                                        "Record and Play"])

    if select != -1:
        if select == 0:
            cmd = "ActivateWindow(videos,plugin://plugin.video.iptv.recorder/record_one_time/%s,return)" % (channel)
            result = xbmc.executebuiltin(cmd)
        elif select == 1:
            cmd = "ActivateWindow(videos,plugin://plugin.video.iptv.recorder/record_daily_time/%s,return)" % (channel)
            result = xbmc.executebuiltin(cmd)
        elif select == 2:
            cmd = "ActivateWindow(videos,plugin://plugin.video.iptv.recorder/record_weekly_time/%s,return)" % (channel)
            result = xbmc.executebuiltin(cmd)
        elif select == 3:
            cmd = "ActivateWindow(videos,plugin://plugin.video.iptv.recorder/record_and_play/%s,return)" % (channel)
            result = xbmc.executebuiltin(cmd)

except:
    xbmcgui.Dialog().notification("IPTV Recorder", "channel not found", xbmcgui.NOTIFICATION_WARNING)
