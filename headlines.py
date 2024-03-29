import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib3
import urllib
import datetime
from flask import make_response

app = Flask(__name__)

RSS_FEED = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': "http://rss.cnn.com/rss/edition.rss",
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': "http://rss.iol.io/iol/news",
            }
WEATHER_API = '851ae73a2d9696486aadf1ecb23e1f67'
DEFAULTS = {
    'publication': 'bbc',
    'city': 'London, UK',
    'currency_from': 'GBP', x
        'currency_to': 'USD'
}

@app.route('/')
def home():
    publication = request.args.get('publication')
    if not publication:
        publication = request.cookies.get("publication") or DEFAULTS['publication']
    articles = get_news(publication)

    city = request.args.get('city')
    if not city:
        city = request.cookies.get("city") or DEFAULTS['city']
    weather = get_weather(city)

    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = request.cookies.get("currency_from") or DEFAULTS['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = request.cookies.get("currency_to") or DEFAULTS['currency_to']
    rate, currencies = get_currency(currency_from, currency_to)

    response = make_response(
        render_template('index.html', publication=publication, articles=articles, weather=weather, rate=rate,
                        currency_from=currency_from,
                        currency_to=currency_to, currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)

    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEED:
        publication = "bbc"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEED[publication])
    return feed['entries']


def get_weather(query):
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={query}&units=metric&appid={WEATHER_API}'
    url = api_url.format(query)
    http = urllib3.PoolManager()
    data = http.request('GET', url).data
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {
            "description": parsed['weather'][0]["description"],
            "temperature": parsed['main']["temp"],
            "city": parsed['name'],
            'country': parsed['sys']['country']
        }
    return weather


def get_currency(frm, to):
    currency_url = 'https://api.exchangeratesapi.io/latest'
    all_currency = urllib.request.urlopen(currency_url).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())


if __name__ == '__main__':
    app.run(port=5000, debug=True)
