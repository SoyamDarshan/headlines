import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib3
import urllib

app = Flask(__name__)

RSS_FEED = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': "http://rss.cnn.com/rss/edition.rss",
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': "http://rss.iol.io/iol/news",
            }
WEATHER_API = 'e0ee0f93ee5a7ecdfec640ca18e2bf0a'
DEFAULTS = {
    'publication': 'bbc',
    'city': 'London, UK'
}


@app.route('/')
def home():
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    return render_template('index.html', articles=articles, weather=weather)


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


if __name__ == '__main__':
    app.run(port=5000, debug=True)
