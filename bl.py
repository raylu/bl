#!/usr/bin/env python3

import os
import urllib.parse

from bs4 import BeautifulSoup
import cleancss
import tornado.gen
import tornado.httpclient
import tornado.ioloop
import tornado.web

import config

class BaseHandler(tornado.web.RequestHandler):
	def render_string(self, *args, **kwargs):
		s = super(BaseHandler, self).render_string(*args, **kwargs)
		return s.replace(b'\n', b'') # this is like Django's {% spaceless %}

class HomeHandler(BaseHandler):
	def get(self):
		self.render('home.html')

class EveboardPasswordException(Exception):
	pass
def parse_skills(html):
	soup = BeautifulSoup(html)
	try:
		table = soup.find_all('center')[1].find_next_sibling('table')
	except IndexError:
		raise EveboardPasswordException()
	table = table.find('table').find('table')
	dotted = table.find_all('td', class_='dotted')
	for td in dotted:
		if not td.string:
			continue
		split = td.string.split('/')
		if split == ['\xa0']:
			continue
		skill = split[0].rstrip()
		level = int(split[2][-2])
		yield skill, level

doctrines = [
	('Tengu', ['Caldari Offensive Systems', 'Caldari Defensive Systems',
		'Caldari Propulsion Systems', 'Caldari Electronic Systems', 'Caldari Engineering Systems',
		'Medium Hybrid Turret', 'Medium Railgun Specialization', 'Trajectory Analysis']),
	('Scimitar', ['Logistics', 'Minmatar Cruiser', 'Shield Emission Systems', 'Capacitor Management']),
	('Loki', ['Minmatar Offensive Systems', 'Minmatar Defensive Systems',
		'Minmatar Propulsion Systems', 'Minmatar Electronic Systems', 'Minmatar Engineering Systems',
		'Medium Projectile Turret', 'Medium Artillery Specialization', 'Trajectory Analysis']),
	('Maelstrom', ['Minmatar Battleship', 'Large Projectile Turret', 'Trajectory Analysis']),
	('Ishtar', ['Gallente Cruiser', 'Heavy Assault Cruisers', 'Sentry Drone Interfacing', 'Drone Interfacing']),
	('Zealot', ['Amarr Cruiser', 'Heavy Assault Cruisers', 'Medium Energy Turret', 'Controlled Bursts']),
]

class SkillCheckHandler(BaseHandler):
	@tornado.gen.coroutine
	def get(self, char):
		client = tornado.httpclient.AsyncHTTPClient()
		request = tornado.httpclient.HTTPRequest('http://eveboard.com/pilot/' + char)
		password = self.get_query_argument('pass', default=None)
		if password:
			request.method = 'POST'
			request.body = urllib.parse.urlencode({'pw': password})
		response = yield client.fetch(request)

		try:
			skills = dict(parse_skills(response.body))
		except EveboardPasswordException:
			self.render('skillcheck.html', error='passworded eveboard')
		doctrine_skills = []
		for doctrine, relevant_skills in doctrines:
			ds = []
			for skill in relevant_skills:
				level = skills.get(skill, 0)
				ds.append((skill, level))
			doctrine_skills.append((doctrine, ds))
		self.render('skillcheck.html', doctrine_skills=doctrine_skills)

class CSSHandler(tornado.web.RequestHandler):
	def get(self, css_path):
		css_path = os.path.join(os.path.dirname(__file__), 'static', css_path) + '.ccss'
		with open(css_path, 'r') as f:
			self.set_header('Content-Type', 'text/css')
			self.write(cleancss.convert(f))

if __name__ == '__main__':
	tornado.web.Application(
		handlers=[
			(r'/', HomeHandler),
			(r'/skillcheck/(.+)', SkillCheckHandler),
			(r'/(css/.+)\.css', CSSHandler),
		],
		template_path=os.path.join(os.path.dirname(__file__), 'templates'),
		static_path=os.path.join(os.path.dirname(__file__), 'static'),
		debug=config.debug,
	).listen(config.port)
	print('Listening on :%d' % config.port)
	tornado.ioloop.IOLoop.instance().start()
