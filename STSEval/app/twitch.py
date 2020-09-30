from app.models import Twitch
import urllib
import requests
import datetime

class TwitchAPI(object):
    
    #have user sign in to twitch
    def authenticate(self,code):
        secret = '1jkelf3kiu79nzwqbg48c9rpalupn7'
        client = '2qc1kgbap6qm1ecltg0ad9kv9uqunv'
        resp = requests.post(
            'https://id.twitch.tv/oauth2/token',
            data={
                'client_id': '2qc1kgbap6qm1ecltg0ad9kv9uqunv',
                'client_secret': '1jkelf3kiu79nzwqbg48c9rpalupn7',
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'http://localhost:64820/twitch_auth'
            })
        try:
            data = resp.json()
        except ValueError:
            return 'Error reading json'

        if 'access_token' in data:
            token = data['access_token']
            Twitch.objects.all().delete()
            t = Twitch(code=code,access_token=data['access_token'],refresh_token=data['refresh_token'],expiration=datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in']))
            t.save()
        else:
            return 'Twitch auth service returned bad response'

        #now get userid
        resp = requests.get(
            'https://api.twitch.tv/helix/users',
             headers={'Client-ID': '2qc1kgbap6qm1ecltg0ad9kv9uqunv',
                     'Authorization': 'Bearer ' + Twitch.objects.all().first().access_token}
            )
        try:
            data = resp.json()
        except ValueError:
            return 'Error reading json'

        t = Twitch.objects.all().first()
        t.user_id = data['data'][0]['id']
        t.user_stream=data['data'][0]['display_name']
        t.save()

    #refresh token
    def refresh(self):
        resp = requests.post(
            'https://id.twitch.tv/oauth2/token',
            data={
                'client_id': '2qc1kgbap6qm1ecltg0ad9kv9uqunv',
                'client_secret': '1jkelf3kiu79nzwqbg48c9rpalupn7',
                'grant_type': 'refresh_token',
                'refresh_token': Twitch.objects.all().first().refresh_token,
                'redirect_uri': 'http://localhost:64820/twitch_auth'
            })
        try:
            data = resp.json()
        except ValueError:
            return 'Error reading json'

        if 'access_token' in data:
            t = Twitch.objects.all().first()
            t.access_token = data['access_token']
            t.refresh_token=data['refresh_token']
            t.save()
        else:
            return 'Twitch auth service returned bad response'

        return 'Refreshed'

    #validate token and refresh if its expired
    def validate(self):
        resp = requests.get(
            'https://id.twitch.tv/oauth2/validate',
             headers={'Authorization': 'OAuth ' + Twitch.objects.all().first().access_token})
        try:
            data = resp.json()
        except ValueError:
            return 'Error reading json'

        if 'client_id' in data:
            return True
        else:
            if self.refresh() == 'Refreshed':
                return True
            else:
                return False

    #mark stream time
    def mark_stream(self,desc):
        if self.validate():
            resp = requests.post(
                'https://api.twitch.tv/helix/streams/markers',
                headers={'Client-ID': '2qc1kgbap6qm1ecltg0ad9kv9uqunv',
                         'Authorization': 'Bearer ' + Twitch.objects.all().first().access_token},
                data={
                    'user_id': Twitch.objects.all().first().user_id,
                    'description': desc,
                })
            try:
                data = resp.json()
            except ValueError:
                return 'Error reading json'
        else:
            return 'Invalid token'
        vid_id = self.get_current_video_id()
        return data['data'][0]['position_seconds'], vid_id

    def get_current_video_id(self):
        resp = requests.get(
            'https://api.twitch.tv/helix/videos?user_id=' + Twitch.objects.all().first().user_id + '&period=day',
             headers={'Client-ID': '2qc1kgbap6qm1ecltg0ad9kv9uqunv',
                      'Authorization': 'Bearer ' + Twitch.objects.all().first().access_token},
            )
        try:
             data = resp.json()
        except ValueError:
            return 'Error reading json'

        vid_id = 0

        if 'data' in data:
            #should just be first one...
            vid_id = data['data'][0]['id']


        return vid_id
