

def token(request):
    if 'oauth_token' in request.session and 'oauth_token_secret' in request.session:
        return request.session['oauth_token'], request.session['oauth_token_secret']
    else:
        raise KeyError('ログインされていません')
