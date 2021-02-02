import requests
import urllib.request
import urllib.parse
import base64
from resources.lib.globals import *
import xbmc, xbmcaddon, xbmcgui
import time, uuid

LOGIN_URL = 'https://dce-frontoffice.imggaming.com/api/v2/login'
REFRESH_URL = 'https://dce-frontoffice.imggaming.com/api/v2/token/refresh'
STREAM_BASE_URL = 'https://dce-frontoffice.imggaming.com/api/v2/stream/'
EVENT_BASE_URL = 'https://dce-frontoffice.imggaming.com/api/v2/event/'

getsettings = xbmcaddon.Addon(id="plugin.video.wwenetwork")
proxymodus = getsettings.getSetting("proxymodus")

def getproxy():
    r = requests.get('https://pastebin.com/raw/TDw1YZnP')
    return base64.b64decode(r.text.strip('"')).decode()

proxies = {'https': 'https://' + getproxy()}

class Account:
    addon = xbmcaddon.Addon()
    username = ''
    password = ''
    session_key = ''
    icon = os.path.join(addon.getAddonInfo('path'), 'icon.png')
    verify = True

    def __init__(self):
        self.username = self.addon.getSetting('username')
        self.password = self.addon.getSetting('password')
        self.login_token = self.addon.getSetting('login_token')
        self.refresh_token = self.addon.getSetting('refresh_token')
        self.last_login = self.addon.getSetting('last_login')

    def login(self):
        # Check if username and password are provided
        if self.username == '':
            dialog = xbmcgui.Dialog()
            self.username = dialog.input('Please enter your username', type=xbmcgui.INPUT_ALPHANUM)

        if self.password == '':
            dialog = xbmcgui.Dialog()
            self.password = dialog.input('Please enter your password', type=xbmcgui.INPUT_ALPHANUM,
                                    option=xbmcgui.ALPHANUM_HIDE_INPUT)

        if self.username == '' or self.password == '':
            dialog.notification("Error Occured", "", self.icon, 5000, False)
            sys.exit()

        payload = '{{"id":"{}","secret":"{}"}}'.format(self.username, self.password)
        
        if proxymodus == "true":
            r = requests.post(LOGIN_URL, headers=SIMPLE_HEADER, proxies=proxies, data=payload, verify=self.verify)
        else:
            r = requests.post(LOGIN_URL, headers=SIMPLE_HEADER, data=payload, verify=self.verify)
        if not check_request_result(r, 201):
            sys.exit()

        self.login_token = r.json()['authorisationToken']
        self.refresh_token = r.json()['refreshToken']
        self.last_login = str(time.time())

        self.addon.setSetting('login_token', self.login_token)
        self.addon.setSetting('refresh_token', self.refresh_token)
        self.addon.setSetting('last_login', self.last_login)
        self.addon.setSetting('username', self.username)
        self.addon.setSetting('password', self.password)

    def reauthorize(self):
        payload = ('{"refreshToken":"%s"}') % (self.refresh_token)
        if proxymodus == "true":
            r = requests.post(REFRESH_URL, headers=generate_authorization_header(self.login_token), proxies=proxies, data=payload, verify=True)
        else:
            r = requests.post(REFRESH_URL, headers=generate_authorization_header(self.login_token), data=payload, verify=True)
        if not check_request_result(r, 201):
            self.login()
            return
        self.login_token = r.json()['authorisationToken']
        self.last_login = str(time.time())
        self.addon.setSetting('login_token', self.login_token)
        self.addon.setSetting('last_login', self.last_login)

    def get_stream(self, path):
        if((time.time() - float(self.last_login)) > 10740.0):
            self.reauthorize()

        url = STREAM_BASE_URL + path
        if proxymodus == "true":
            r = requests.get(url, headers=generate_authorization_header(self.login_token), proxies=proxies, verify=True)
        else:
            r = requests.get(url, headers=generate_authorization_header(self.login_token), verify=True)
        if not check_request_result(r, 200):
            sys.exit()
        url = r.json()['playerUrlCallback']
        
        # If we are using the live stream, adding dvr=true lets us rewind more than 6 seconds
        if "streaming/events" in url:
            url = url + "&dvr=true"
            
        if proxymodus == "true":
            r = requests.get(url, proxies=proxies)
        else:
            r = requests.get(url)
        hls_url = r.json()['hlsUrl']
        return hls_url

    def get_event_stream(self, content_id):
        if((time.time() - float(self.last_login)) > 10740.0):
            self.reauthorize()

        url = EVENT_BASE_URL + content_id
        if proxymodus == "true":
            r = requests.get(url, headers=generate_authorization_header(self.login_token), proxies=proxies, verify=True)
        else:
            r = requests.get(url, headers=generate_authorization_header(self.login_token), verify=True)
        if not check_request_result(r, 200):
            sys.exit()

        sportId = r.json()['events'][0]['sportId']
        propertyId = r.json()['events'][0]['propertyId']
        tournamentId = r.json()['events'][0]['tournamentId']
        id = r.json()['events'][0]['id']
        return self.get_stream('event/' + str(sportId) + '/'+ str(propertyId) + '/' + str(tournamentId) + '/' + str(id))
