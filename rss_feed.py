#import gevent
#from gevent import monkey; monkey.patch_all()
import time
from datetime import datetime, timedelta

import feedparser as fp
import pytz


subscriptions = [
	'https://tengrinews.kz/news.rss',
	'https://www.nur.kz/rss/yandex.rss',
	'http://st.zakon.kz/rss/rss_all.xml',
	'http://www.aif.ru/rss/news.php',
	'https://lenta.ru/rss/news'
	'https://news.mail.ru/rss',
        'https://life.ru/xml/feed.xml?hashtag=%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D0%B8']

# Date and time setup. I want only posts from "today,"
# where the day lasts until 2 AM.
utc = pytz.utc
homeTZ = pytz.timezone('Asia/Almaty')
dt = datetime.now(homeTZ)
if dt.hour < 2:
	dt = dt - timedelta(hours=24)
start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
start = start.astimezone(utc)


# Collect all of today's posts and put them in a list of tuples.
posts = []


def get_posts():
	posts = []
	for s in subscriptions:
		f = fp.parse(s)
		try:
			blog = f['feed']['title']
		except KeyError:
			continue
		for e in f['entries']:
			try:
				when = e['published_parsed']
			except KeyError:
				when = e['updated_parsed']
			when = utc.localize(datetime.fromtimestamp(time.mktime(when)))
			if when > start:
				title = e['title']
				try:
					body = e['content'][0]['value']
				except KeyError:
					body = e['summary']
				link = e['link']
				posts.append((when, blog, title, link, body))

				# Sort the posts in reverse chronological order.
				posts.sort()
				posts.reverse()
	return posts

# def get_post_gv(s):
#     f = fp.parse(s)
#     try:
#         blog = f['feed']['title']
#     except KeyError:
#         blog = "blog"
#     for e in f['entries']:
#         try:
#             when = e['published_parsed']
#         except KeyError:
#             when = e['updated_parsed']
#         when = utc.localize(datetime.fromtimestamp(time.mktime(when)))
#         if when > start:
#             title = e['title']
#             try:
#                 body = e['content'][0]['value']
#             except KeyError:
#                 body = e['summary']
#             link = e['link']
#             posts.append((when, blog, title, link, body))
#
#             # Sort the posts in reverse chronological order.
#             posts.sort()
#             posts.reverse()
#     return posts

# def get_posts_call():
#     jobs = [gevent.spawn(get_post_gv, s) for s in subscriptions]
#     gevent.wait(jobs)

def get_single_blog(feed):
	'''Feed the all_posts path an individual blog/feed to parse and display from inside the template'''
	the_feed = fp.parse(feed)
	single_blog_posts = the_feed['entries']
	return single_blog_posts


def get_subscriptions():
	'''simple method to pass the subscriptions (will improve here)'''
	s = subscriptions
	return s


# TODO: pick the most efficient option: generate html in template or in code
def get_sorted_posts(sorted_posts):
	'''
	This method returns generated html with the days posts. Contrast to the get_single_blog method that
	generates the html inside the template.'''
	listTemplate = ''' <section>
				<h2 class="page-header no-margin-top"><a href="{3}">{2}</a></h2>
				<p>{4}</p>
			<div class="panel-footer">
						<div class="row">
							<div class="col-md-12">
								<i class="fa fa-clock-o"></i> {0} <i class="fa fa-user"> </i> <a href="{3}">{1}</a>.
							</div>
						</div>
					</div>
			</section>'''
	litems = []
	for p in sorted_posts:
		q = [x for x in p[1:]]
		timestamp = p[0].astimezone(homeTZ)
		q.insert(0, timestamp.strftime('%b %d, %Y %I:%M %p'))
		litems.append(listTemplate.format(*q))
	myitems = '</br>'.join(litems)
	return myitems



