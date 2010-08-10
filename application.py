"""Main application code"""
import datetime
import time

import feedparser
from flask import redirect, url_for, request, render_template, session, g
from flask import Flask
from oauth2 import parse_qsl

import secrets
from oauth_utils import get_authorize_url, authorize_app, \
                                   grab_raw_feed, NotAuthenticated

app = Flask(__name__)
app.secret_key = secrets.SECRET_KEY

FEED_URL = 'https://mail.google.com/mail/feed/atom'

@app.before_request
def before_request():
    """Adds Analytics code to the global context for use in templates"""
    g.analytics_code = secrets.ANALYTICS_CODE

@app.route('/')
def index():
    """Display home page"""
    
    return render_template('index.html')

@app.route('/information/')
def information():
    """Display privacy and other information"""
    
    return render_template('information.html')

@app.route('/oauth/')
def oauth_request():
    """
    Redirects user to Google's Oauth page
    """
    
    authorize_url = get_authorize_url(FEED_URL, request, session)
    return redirect(authorize_url)

@app.route('/login/')
def oauth_access():
    """
    Authorize our app to access user's Gmail data
    """
    
    authorize_app(request, session)
    return redirect('/check/')
    
@app.route('/check/', methods=['GET', 'POST'])
def check_mail():
    """
    Grabs Gmail feed and checks it for supplied values.
    
    If user is not authenticated, this view redirects to request Oauth creds
    """
    
    try:
        content = grab_raw_feed(FEED_URL, request, session)
    except NotAuthenticated:
        return redirect(url_for('oauth_request'))
    
    feed = feedparser.parse(content)
    search = request.form.get('search', '') or session.pop('search', '')
    found = []
    # Feed title should show the email address so we can glean the domain name
    # Example: "Gmail - Inbox for me@gmail.com"
    text, domain = feed['feed']['title'].split('@')
    for email in feed.entries:
        if email['author'].lower().find(search.lower()) >= 0:
            # build single message URL
            message_id = dict(parse_qsl(email['link']))['message_id']
            if domain == 'gmail.com':
                path = 'mail'
            else: # send to GAFYD
                path = 'a/%s' % domain
            print_view = 'https://mail.google.com/%s/h/?v=pt&th=%s' % (path, 
                                                                    message_id)
            timestamp = time.mktime(email['published_parsed'])
            found.append({
                'from': email['author'],
                'subject': email['title'],
                'summary': email['summary'],
                'url': print_view,
                'date': datetime.datetime.fromtimestamp(timestamp),
            })
    return render_template('results.html',
                            feed=found,
                            search=search)
                            

if __name__ == '__main__':
    app.run()
