from django.views.generic import View
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from Root.settings import ORIGIN

import os
from urllib.parse import parse_qsl
import json

from requests_oauthlib import OAuth1Session

# Create your views here.


TWI_KEY = os.environ.get('TWI_KEY')
TWI_S_KEY = os.environ.get('TWI_S_KEY')

request_token_url = 'https://api.twitter.com/oauth/request_token'
base_authenticate_url = 'https://api.twitter.com/oauth/authenticate'
base_callback_url = ORIGIN + '/api/twitter_login/callback'
access_token_url = 'https://api.twitter.com/oauth/access_token'


def get_authenticate_url_view(request):
    try:
        callback_url = base_callback_url + '?next=' + request.GET['next']
    except KeyError:
        return JsonResponse({'message': 'require next parameter'}, status=400)

    if 'oauth_token' in request.session and 'oauth_token_secret' in request.session:
        return JsonResponse({'message': 'session had auth data', 'url': request.GET['next']}, status=303)

    twitter = OAuth1Session(TWI_KEY, TWI_S_KEY)
    res = twitter.post(
        request_token_url,
        params={'oauth_callback': callback_url}
    )

    if res.status_code != 200:
        try:
            res_res = json.loads(res.text)
        except json.decoder.JSONDecodeError:
            res_res = res.text
        return JsonResponse({'message': 'twitter api oauth/request_token return not 200 response', 'response': res_res},
                            status=400)

    request_token = dict(parse_qsl(res.text))

    authenticate_url = base_authenticate_url + f'?oauth_token={request_token["oauth_token"]}'

    return JsonResponse({'message': 'ok', 'url': authenticate_url})


def callback_routing(request):
    error_res = '<html><body><script>alert("ログインエラー");setTimeout(()=>{location="%s"},300)</script></body></html>'

    try:
        next_url = request.GET['next']
    except KeyError:
        next_url = ORIGIN + '/'

    try:
        oauth_token = request.GET['oauth_token']
        oauth_verifier = request.GET['oauth_verifier']
    except KeyError:
        return HttpResponse(error_res % next_url)

    twitter = OAuth1Session(TWI_KEY, TWI_S_KEY, oauth_token, oauth_verifier)

    res = twitter.post(access_token_url, params={'oauth_verifier': oauth_verifier})

    access_token = dict(parse_qsl(res.text))

    request.session['oauth_token'] = access_token['oauth_token']
    request.session['oauth_token_secret'] = access_token['oauth_token_secret']

    return HttpResponseRedirect(next_url)


def logined(request):
    if 'oauth_token' in request.session and 'oauth_token_secret' in request.session:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)


def logout(request):
    if 'oauth_token' in request.session:
        del request.session['oauth_token']
    if 'oauth_token_secret' in request.session:
        del request.session['oauth_token_secret']

    return HttpResponse()
