import sys
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import os

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

tplink = xbmcaddon.Addon('plugin.tplink.hs100')

__settings__ = xbmcaddon.Addon(id="plugin.tplink.hs100")

addon_icon = 'special://home/addons/plugin.tplink.hs100/icon.png'

poweron_icon = 'special://home/addons/plugin.tplink.hs100/resources/lib/power-on.png'
poweroff_icon = 'special://home/addons/plugin.tplink.hs100/resources/lib/power-off.png'
ledon_icon = 'special://home/addons/plugin.tplink.hs100/resources/lib/led-on.png'
ledoff_icon = 'special://home/addons/plugin.tplink.hs100/resources/lib/led-off.png'
reboot_icon = 'special://home/addons/plugin.tplink.hs100/resources/lib/reboot.png'
reset_icon = 'special://home/addons/plugin.tplink.hs100/resources/lib/reset.png'

ip = __settings__.getSetting("ip")
port = __settings__.getSetting("port")
name = __settings__.getSetting("name")
onoff = __settings__.getSetting("onoff")

ip2 = __settings__.getSetting("ip2")
port2 = __settings__.getSetting("port2")
name2 = __settings__.getSetting("name2")
onoff2 = __settings__.getSetting("onoff2")

ip3 = __settings__.getSetting("ip3")
port3 = __settings__.getSetting("port3")
name3 = __settings__.getSetting("name3")
onoff3 = __settings__.getSetting("onoff3")

ip4 = __settings__.getSetting("ip4")
port4 = __settings__.getSetting("port4")
name4 = __settings__.getSetting("name4")
onoff4 = __settings__.getSetting("onoff4")

ip5 = __settings__.getSetting("ip5")
port5 = __settings__.getSetting("port5")
name5 = __settings__.getSetting("name5")
onoff5 = __settings__.getSetting("onoff5")

mode = args.get('mode', None)

def plug():

    url = build_url({'mode': 'poweron', 'foldername': "POWER: ON"})
    li = xbmcgui.ListItem("POWER: ON")
    li.setInfo(type='video', infoLabels={'plot': "POWER: ON ("+name+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweron_icon, 'thumb' : poweron_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'poweroff', 'foldername': "POWER: OFF"})
    li = xbmcgui.ListItem("POWER: OFF")
    li.setInfo(type='video', infoLabels={'plot': "POWER: OFF ("+name+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweroff_icon, 'thumb' : poweroff_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)     

    url = build_url({'mode': 'ledon', 'foldername': "LED: ON"})
    li = xbmcgui.ListItem("LED: ON")
    li.setInfo(type='video', infoLabels={'plot': "LED: ON ("+name+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledon_icon, 'thumb' : ledon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'ledoff', 'foldername': "LED: OFF"})
    li = xbmcgui.ListItem("LED: OFF")
    li.setInfo(type='video', infoLabels={'plot': "LED: OFF ("+name+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledoff_icon, 'thumb' : ledoff_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reboot', 'foldername': "REBOOT"})
    li = xbmcgui.ListItem("REBOOT")
    li.setInfo(type='video', infoLabels={'plot': "REBOOT ("+name+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reboot_icon, 'thumb' : reboot_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reset', 'foldername': "RESET"})
    li = xbmcgui.ListItem("RESET")
    li.setInfo(type='video', infoLabels={'plot': "RESET ("+name+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reset_icon, 'thumb' : reset_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

def plug2():

    url = build_url({'mode': 'poweron2', 'foldername': "POWER: ON"})
    li = xbmcgui.ListItem("POWER: ON")
    li.setInfo(type='video', infoLabels={'plot': "POWER: ON ("+name2+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweron_icon, 'thumb' : poweron_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'poweroff2', 'foldername': "POWER: OFF"})
    li = xbmcgui.ListItem("POWER: OFF")
    li.setInfo(type='video', infoLabels={'plot': "POWER: OFF ("+name2+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweroff_icon, 'thumb' : poweroff_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)     

    url = build_url({'mode': 'ledon2', 'foldername': "LED: ON"})
    li = xbmcgui.ListItem("LED: ON")
    li.setInfo(type='video', infoLabels={'plot': "LED: ON ("+name2+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledon_icon, 'thumb' : ledon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'ledoff2', 'foldername': "LED: OFF"})
    li = xbmcgui.ListItem("LED: OFF")
    li.setInfo(type='video', infoLabels={'plot': "LED: OFF ("+name2+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledoff_icon, 'thumb' : ledoff_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reboot2', 'foldername': "REBOOT"})
    li = xbmcgui.ListItem("REBOOT")
    li.setInfo(type='video', infoLabels={'plot': "REBOOT ("+name2+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reboot_icon, 'thumb' : reboot_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reset2', 'foldername': "RESET"})
    li = xbmcgui.ListItem("RESET")
    li.setInfo(type='video', infoLabels={'plot': "RESET ("+name2+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reset_icon, 'thumb' : reset_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

def plug3():

    url = build_url({'mode': 'poweron3', 'foldername': "POWER: ON"})
    li = xbmcgui.ListItem("POWER: ON")
    li.setInfo(type='video', infoLabels={'plot': "POWER: ON ("+name3+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweron_icon, 'thumb' : poweron_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'poweroff3', 'foldername': "POWER: OFF"})
    li = xbmcgui.ListItem("POWER: OFF")
    li.setInfo(type='video', infoLabels={'plot': "POWER: OFF ("+name3+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweroff_icon, 'thumb' : poweroff_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)     

    url = build_url({'mode': 'ledon3', 'foldername': "LED: ON"})
    li = xbmcgui.ListItem("LED: ON")
    li.setInfo(type='video', infoLabels={'plot': "LED: ON ("+name3+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledon_icon, 'thumb' : ledon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'ledoff3', 'foldername': "LED: OFF"})
    li = xbmcgui.ListItem("LED: OFF")
    li.setInfo(type='video', infoLabels={'plot': "LED: OFF ("+name3+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledoff_icon, 'thumb' : ledoff_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reboot3', 'foldername': "REBOOT"})
    li = xbmcgui.ListItem("REBOOT")
    li.setInfo(type='video', infoLabels={'plot': "REBOOT ("+name3+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reboot_icon, 'thumb' : reboot_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reset3', 'foldername': "RESET"})
    li = xbmcgui.ListItem("RESET")
    li.setInfo(type='video', infoLabels={'plot': "RESET ("+name3+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reset_icon, 'thumb' : reset_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

def plug4():

    url = build_url({'mode': 'poweron4', 'foldername': "POWER: ON"})
    li = xbmcgui.ListItem("POWER: ON")
    li.setInfo(type='video', infoLabels={'plot': "POWER: ON ("+name4+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweron_icon, 'thumb' : poweron_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'poweroff4', 'foldername': "POWER: OFF"})
    li = xbmcgui.ListItem("POWER: OFF")
    li.setInfo(type='video', infoLabels={'plot': "POWER: OFF ("+name4+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweroff_icon, 'thumb' : poweroff_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)     

    url = build_url({'mode': 'ledon4', 'foldername': "LED: ON"})
    li = xbmcgui.ListItem("LED: ON")
    li.setInfo(type='video', infoLabels={'plot': "LED: ON ("+name4+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledon_icon, 'thumb' : ledon_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'ledoff4', 'foldername': "LED: OFF"})
    li = xbmcgui.ListItem("LED: OFF")
    li.setInfo(type='video', infoLabels={'plot': "LED: OFF ("+name4+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledoff_icon, 'thumb' : ledoff_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reboot4', 'foldername': "REBOOT"})
    li = xbmcgui.ListItem("REBOOT")
    li.setInfo(type='video', infoLabels={'plot': "REBOOT ("+name4+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reboot_icon, 'thumb' : reboot_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reset4', 'foldername': "RESET"})
    li = xbmcgui.ListItem("RESET")
    li.setInfo(type='video', infoLabels={'plot': "RESET ("+name4+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reset_icon, 'thumb' : reset_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

def plug5():

    url = build_url({'mode': 'poweron5', 'foldername': "POWER: ON"})
    li = xbmcgui.ListItem("POWER: ON")
    li.setInfo(type='video', infoLabels={'plot': "POWER: ON ("+name5+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweron_icon, 'thumb' : poweron_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'poweroff5', 'foldername': "POWER: OFF"})
    li = xbmcgui.ListItem("POWER: OFF")
    li.setInfo(type='video', infoLabels={'plot': "POWER: OFF ("+name5+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': poweroff_icon, 'thumb' : poweroff_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)     

    url = build_url({'mode': 'ledon5', 'foldername': "LED: ON"})
    li = xbmcgui.ListItem("LED: ON")
    li.setInfo(type='video', infoLabels={'plot': "LED: ON ("+name5+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledon_icon, 'thumb' : ledon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'ledoff5', 'foldername': "LED: OFF"})
    li = xbmcgui.ListItem("LED: OFF")
    li.setInfo(type='video', infoLabels={'plot': "LED: OFF ("+name5+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': ledoff_icon, 'thumb' : ledoff_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reboot5', 'foldername': "REBOOT"})
    li = xbmcgui.ListItem("REBOOT")
    li.setInfo(type='video', infoLabels={'plot': "REBOOT ("+name5+")"}) 
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reboot_icon, 'thumb' : reboot_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    url = build_url({'mode': 'reset5', 'foldername': "RESET"})
    li = xbmcgui.ListItem("RESET")
    li.setInfo(type='video', infoLabels={'plot': "RESET ("+name5+")"})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': reset_icon, 'thumb' : reset_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

if mode is None:
    
    if onoff == "true":
        url = build_url({'mode': 'plug', 'foldername': name})
        li = xbmcgui.ListItem(name)
        li.setInfo(type='video',infoLabels={'title': name, 'plot': name})
        li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    else:
        pass

    if onoff2 == "true":
        url = build_url({'mode': 'plug2', 'foldername': name2})
        li = xbmcgui.ListItem(name2)
        li.setInfo(type='video',infoLabels={'title': name2, 'plot': name2})
        li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    else:
        pass

    if onoff3 == "true":
        url = build_url({'mode': 'plug3', 'foldername': name3})
        li = xbmcgui.ListItem(name3)
        li.setInfo(type='video',infoLabels={'title': name3, 'plot': name3})
        li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    else:
        pass

    if onoff4 == "true":
        url = build_url({'mode': 'plug4', 'foldername': name4})
        li = xbmcgui.ListItem(name4)
        li.setInfo(type='video',infoLabels={'title': name4, 'plot': name4})
        li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    else:
        pass

    if onoff5 == "true":
        url = build_url({'mode': 'plug5', 'foldername': name5})
        li = xbmcgui.ListItem(name5)
        li.setInfo(type='video',infoLabels={'title': name5, 'plot': name5})
        li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    else:
        pass

    url = build_url({'mode': 'settings', 'foldername': __settings__.getLocalizedString(30060)})
    li = xbmcgui.ListItem(__settings__.getLocalizedString(30060))
    li.setInfo(type='video', infoLabels={'plot': __settings__.getLocalizedString(30060)})
    li.setArt({'fanart': tplink.getAddonInfo('fanart'), 'icon': addon_icon, 'thumb' : addon_icon}) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'plug':
    plug()

elif mode[0] == 'plug2':
    plug2()

elif mode[0] == 'plug3':
    plug3()

elif mode[0] == 'plug4':
    plug4()

elif mode[0] == 'plug5':
    plug5()

elif mode[0] == 'poweron':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip+', "-p", '+port+', "-c", "on")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'poweroff':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip+', "-p", '+port+', "-c", "off")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledon':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip+', "-p", '+port+', "-c", "ledon")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledoff':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip+', "-p", '+port+', "-c", "ledoff")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reboot':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip+', "-p", '+port+', "-c", "reboot")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reset':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip+', "-p", '+port+', "-c", "reset")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'poweron2':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip2+', "-p", '+port2+', "-c", "on")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'poweroff2':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip2+', "-p", '+port2+', "-c", "off")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledon2':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip2+', "-p", '+port2+', "-c", "ledon")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledoff2':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip2+', "-p", '+port2+', "-c", "ledoff")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reboot2':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip2+', "-p", '+port2+', "-c", "reboot")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reset2':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip2+', "-p", '+port2+', "-c", "reset")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'poweron3':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip3+', "-p", '+port3+', "-c", "on")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'poweroff3':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip3+', "-p", '+port3+', "-c", "off")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledon3':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip3+', "-p", '+port3+', "-c", "ledon")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledoff3':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip3+', "-p", '+port3+', "-c", "ledoff")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reboot3':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip3+', "-p", '+port3+', "-c", "reboot")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reset3':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip3+', "-p", '+port3+', "-c", "reset")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'poweron4':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip4+', "-p", '+port4+', "-c", "on")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'poweroff4':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip4+', "-p", '+port4+', "-c", "off")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledon4':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip4+', "-p", '+port4+', "-c", "ledon")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledoff4':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip4+', "-p", '+port4+', "-c", "ledoff")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reboot4':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip4+', "-p", '+port4+', "-c", "reboot")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reset4':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip4+', "-p", '+port4+', "-c", "reset")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'poweron5':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip5+', "-p", '+port5+', "-c", "on")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'poweroff5':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip5+', "-p", '+port5+', "-c", "off")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledon5':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip5+', "-p", '+port5+', "-c", "ledon")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'ledoff5':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip5+', "-p", '+port5+', "-c", "ledoff")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reboot5':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip5+', "-p", '+port5+', "-c", "reboot")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'reset5':
    xbmc.executebuiltin('RunScript("special://home/addons/plugin.tplink.hs100/resources/lib/tplink_smartplug.py", "-t", '+ip5+', "-p", '+port5+', "-c", "reset")')
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'settings':
    addon.openSettings()
    xbmc.executebuiltin('Container.Refresh')