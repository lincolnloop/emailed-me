"""Handles all the Oauth nitty-gritty"""
import logging
import time
import urllib

from flask import abort
import httplib2
import oauth2 as oauth

import secrets

CONSUMER = oauth.Consumer(secrets.CONSUMER_KEY, secrets.CONSUMER_SECRET)

class NotAuthenticated(Exception):
    """User is not properly authenticated"""
    pass
    
def get_authorize_url(urls, request, session):
    """
    Handle Google's Oauth request token
    
    Gets request token from Google and URL of page at Google
    allowing them to authorize our app to access their Gmail data.
    """
    request_url = 'https://www.google.com/accounts/OAuthGetRequestToken'
    auth_url = 'https://www.google.com/accounts/OAuthAuthorizeToken'
    
    # if the user already has a request token, we can skip this step
    if 'request_token' not in session:
        host = '/'.join(request.url_root.split('/')[:3])
        params = {
            'oauth_version': '1.0',
            'scope': urls, 
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': str(int(time.time())),
            'oauth_callback': '%s/login/' % host,
        }
        client = oauth.Client(CONSUMER)
        client.set_signature_method(oauth.SignatureMethod_HMAC_SHA1())
        resp, content = client.request(request_url, "POST", 
                                       body=urllib.urlencode(params))
    
        if resp['status'] != '200':
            logging.error("Invalid response %s.", resp['status'])
            raise Exception("Invalid response")

        token_dict = dict(oauth.parse_qsl(content))
        
        # store tokens in the user session
        session['request_token'] = token_dict['oauth_token']
        session['request_secret'] = token_dict['oauth_token_secret']

    return '%s?oauth_token=%s' % (auth_url, session['request_token'])

def authorize_app(request, session):
    """
    Used by callback view that takes the oauth token and verifier from Google 
    and converts them into an access token and secret for this user with 
    our consumer key. If this works we redirect the user to the page which
    actually checks their Gmail feed.
    """
    
    access_url = 'https://www.google.com/accounts/OAuthGetAccessToken'
    
    # this view should only be accessed by Google
    # with the correct request args
    try:
        key = request.args['oauth_token']
        oauth_verifier = request.args['oauth_verifier']
    except KeyError:
        abort(404)
    if session.get('request_token', None) != key:
        raise Exception("Tokens don't match")
    token = oauth.Token(key, session['request_secret'])
    
    token.set_verifier(oauth_verifier)
    client = oauth.Client(CONSUMER, token)
    params = {
        'oauth_consumer_key': CONSUMER.key,
        'oauth_token': token.key,
        'oauth_verifier': oauth_verifier,
        'oauth_timestamp': str(int(time.time())),
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_version': '1.0',
    }
    client.set_signature_method(oauth.SignatureMethod_HMAC_SHA1())
    resp, content = client.request(access_url, "POST", 
                                   body=urllib.urlencode(params))
    if resp['status'] != '200':
        logging.error("Invalid response %s.", resp['status'])
        raise Exception("Invalid response")
    
    token_dict = dict(oauth.parse_qsl(content))
    session['access_token'] = token_dict['oauth_token']
    session['access_secret'] = token_dict['oauth_token_secret']
    
def grab_raw_feed(url, request, session):
    """
    Grabs the Gmail feed and raises a NotAuthenticated error if the user
    isn't authenticated

    """
    # is user authenticated?
    try:
        access_key = session['access_token']
        access_secret = session['access_secret']
    except KeyError:
        # user isn't properly authorized
        # "invalidate" any previous session data
        session.clear()
        # stash the search term in their session while we authorize
        if 'search' in request.form:
            session['search'] = request.form['search']
        raise NotAuthenticated

    access_token = oauth.Token(access_key, access_secret)
    params = {
        'oauth_consumer_key': CONSUMER.key,
        'oauth_token': access_token.key,
        'oauth_timestamp': str(int(time.time())),
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_version': '1.0',
    }
    req = oauth.Request(method="GET", url=url, parameters=params)

    # Sign the request
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, CONSUMER, access_token)
    http = httplib2.Http()
    resp, content = http.request(url, "GET", headers=req.to_header())

    if resp['status'] != '200':
        logging.error("Invalid response %s.", resp['status'])
        raise Exception("Invalid response")
    
    return content