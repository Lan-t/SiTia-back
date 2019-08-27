from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import os
import json

from requests_oauthlib import OAuth1Session

from twitter_login.utils import token

# Create your views here.

require_login_response = JsonResponse({'code': 0, 'message': 'not logged in'})

TWI_KEY = os.environ.get('TWI_KEY')
TWI_S_KEY = os.environ.get('TWI_S_KEY')

twitter_api_url = 'https://api.twitter.com/1.1/'


@method_decorator(csrf_exempt, 'dispatch')
class WrapperView(View):
    def get(self, request, path):
        try:
            twi_t, twi_t_s = token(request)
        except KeyError:
            return require_login_response

        query = '&'.join([k + ('=' + request.GET[k] if request.GET[k] else '') for k in request.GET])
        if query:
            query = '?' + query
        uri = path + query
        url = twitter_api_url + uri

        if uri in request.session:
            res = request.session[uri]
            return JsonResponse({
                'url': url,
                'status': 200,
                'cache': True,
                'response': res
            })

        twitter = OAuth1Session(TWI_KEY, TWI_S_KEY, twi_t, twi_t_s)

        res = twitter.get(url)

        try:
            res_response = json.loads(res.text)
        except json.JSONDecodeError:
            res_response = res.text

        if res.status_code == 200:
            request.session[uri] = res_response

        return JsonResponse({
            'url': url,
            'status': res.status_code,
            'response': res_response
        }, status=res.status_code)

    def post(self, request, path):
        try:
            twi_t, twi_t_s = token(request)
        except KeyError:
            return require_login_response

        query = '&'.join([k + ('=' + request.GET[k] if request.GET[k] else '') for k in request.GET])
        if query:
            query = '?' + query
        uri = path + query
        url = twitter_api_url + uri

        twitter = OAuth1Session(TWI_KEY, TWI_S_KEY, twi_t, twi_t_s)

        res = twitter.post(url, data=request.body, headers={'Content-Type': 'application/x-www-form-urlencoded'})

        try:
            res_response = json.loads(res.text)
        except json.JSONDecodeError:
            res_response = res.text

        return JsonResponse({
            'url': url,
            'status': res.status_code,
            'response': res_response
        }, status=res.status_code)


def delete_cache(request):
    import re
    try:
        query_re = re.compile(request.GET['re'])
    except KeyError:
        query_re = None
    for key in list(request.session.keys()):
        if key not in ('oauth_token', 'oauth_token_secret'):
            if query_re is None or query_re.match(key):
                del request.session[key]

    return HttpResponse('')


def check_cache(request):
    return JsonResponse(dict(request.session))
