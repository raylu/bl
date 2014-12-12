#!/usr/bin/env python3

import os

import cleancss
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

class SkillCheckHandler(BaseHandler):
	def get(self, char):
		self.render('skillcheck.html')

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
		debug=True,
	).listen(config.port)
	print('Listening on :%d' % config.port)
	tornado.ioloop.IOLoop.instance().start()
