import chardet
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import time
import urllib.error
import urllib.error
import urllib.parse
import urllib.parse
import urllib.request
import urllib.request
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
from io import StringIO
from io import BytesIO

AddonID = 'plugin.video.playlistloader'
Addon = xbmcaddon.Addon(AddonID)
icon = Addon.getAddonInfo('icon')
AddonName = Addon.getAddonInfo("name")
addon_data_dir = xbmcvfs.translatePath(Addon.getAddonInfo("profile"))
cacheDir = os.path.join(addon_data_dir, "cache")
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'


class SmartRedirectHandler(urllib.request.HTTPRedirectHandler):
	def http_error_301(self, req, fp, code, msg, headers):
		result = urllib.request.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
		return result

	def http_error_302(self, req, fp, code, msg, headers):
		result = urllib.request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
		return result


def getFinalUrl(url):
	link = url
	try:
		req = urllib.request.Request(url)
		req.add_header('User-Agent', UA)
		opener = urllib.request.build_opener(SmartRedirectHandler())
		f = opener.open(req)
		link = f.url
		if link is None or link == '':
			link = url
	except Exception as ex:
		xbmc.log(str(ex), 3)
	return link

def OpenURL(url, headers={}, user_data={}, cookieJar=None, justCookie=False):
    if isinstance(url, str):
        url = url
    #url = urllib.quote(url, ':/')
    cookie_handler = urllib.request.HTTPCookieProcessor(cookieJar)
    opener = urllib.request.build_opener(cookie_handler, urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPHandler())
    if user_data:
        user_data = urllib.parse.urlencode(user_data)
        req = urllib.request.Request(url, user_data)
    else:
        req = urllib.request.Request(url)
    req.add_header('Accept-encoding', 'txt')
    for k, v in list(headers.items()):
        req.add_header(k, v)
    if 'User-Agent' not in req.headers or req.headers['User-Agent'] == '':
        req.add_header('User-Agent', UA)
    response = opener.open(req)
    if justCookie == True:
        if "Set-Cookie" in response.info():
            data = response.info()['Set-Cookie']
        else:
            data = None
    else:
        if response.info().get('Content-Encoding') == 'txt':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read().decode('utf-8').replace("\r", "")
        else:
            dati = response.read()
            try:
                data = dati.decode('utf-8').replace("\r", "")
            except:
                data = dati.decode(chardet.detect(dati)["encoding"]).replace("\r", "")
    response.close()
    return data

def ReadFile(fileName):
    try:
        f = xbmcvfs.File(fileName)
        content = f.read().replace("\n\n", "\n")
        f.close()
    except Exception as ex:
        xbmc.log(str(ex), 3)
        content = ""
    return content


def SaveFile(fileName, text):
	try:
		f = xbmcvfs.File(fileName, 'w')
		f.write(text)
		f.close()
	except:
		return False
	return True


def ReadList(fileName):
	try:
		with open(fileName, 'r') as handle:
			content = json.load(handle)
	except Exception as ex:
		xbmc.log(str(ex), 5)
		if os.path.isfile(fileName):
			shutil.copyfile(fileName, "{0}_bak.txt".format(fileName[:fileName.rfind('.')]))
			xbmc.executebuiltin('Notification({0}, Cannot read file: "{1}". \nBackup createad, {2}, {3})'.format(AddonName, os.path.basename(fileName), 5000, icon))
		content=[]

	return content


def SaveList(filname, chList):
	try:
		with io.open(filname, 'w') as handle:
			handle.write(str(json.dumps(chList, indent=4, ensure_ascii=False)))
		success = True
	except Exception as ex:
		xbmc.log(str(ex), 3)
		success = False
	return success


def OKmsg(title, line1):
	dlg = xbmcgui.Dialog()
	dlg.ok(title, line1)
	

def isFileNew(file, deltaInSec):
	lastUpdate = 0 if not os.path.isfile(file) else int(os.path.getmtime(file))
	now = int(time.time())
	return False if (now - lastUpdate) > deltaInSec else True 
	

def GetList(address, cache=0):
	if address.startswith('http'):
		fileLocation = os.path.join(cacheDir, hashlib.md5(address.encode()).hexdigest())
		fromCache = isFileNew(fileLocation, cache*60)
		if fromCache:
			response = ReadFile(fileLocation)
		else:
			response = OpenURL(address)
			if cache > 0:
				SaveFile(fileLocation, response)
	else:
		response = ReadFile(address)
	return response


def plx2list(url, cache):
	response = GetList(url, cache)
	matches = re.compile("^background=(.*?)$", re.I+re.M+re.U+re.S).findall(response)
	background = None if len(matches) < 1 else matches[0]
	chList = [{"background": background}]
	matches = re.compile('^type(.*?)#$',re.I+re.M+re.U+re.S).findall(response)
	for match in matches:
		item=re.compile('^(.*?)=(.*?)$',re.I+re.M+re.U+re.S).findall("type{0}".format(match))
		item_data = {}
		for field, value in item:
			item_data[field.strip().lower()] = value.strip()
		item_data['group'] = 'Main'
		chList.append(item_data)
	return chList


def m3u2list(url, cache):
	response = GetList(url, cache)	
	matches=re.compile('^#EXTINF:-?[0-9]*(.*?),([^\"]*?)\n(.*?)$', re.M).findall(response)
	li = []
	for params, display_name, url in matches:
		item_data = {"params": params, "display_name": display_name.strip(), "url": url.strip()}
		li.append(item_data)
	chList = []
	for channel in li:
		item_data = {"display_name": (channel["display_name"]), "url": channel["url"]}
		matches=re.compile(' (.*?)="(.*?)"').findall(channel["params"])
		for field, value in matches:
			item_data[field.strip().lower().replace('-', '_')] = value.strip()
		chList.append(item_data)
	return chList
	

def GetEncodeString(str):
	try:
		str = str.decode(chardet.detect(str)["encoding"])
	except:
		try:
			str = str
		except:
			pass
	return str


def DelFile(filname):
	try:
		if os.path.isfile(filname):
			os.unlink(filname)
	except Exception as ex:
		xbmc.log(str(ex), 3)
		

def strptime2(string_date, sformat):
	from datetime import datetime as dt
	try:
		res = dt.strptime(string_date, sformat)
	except TypeError:
		res = dt(*(time.strptime(string_date, sformat)[0:6]))
	return res
