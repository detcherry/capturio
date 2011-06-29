import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, None))

class WhatIsCapturio(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/what_is_capturio.html')
		self.response.out.write(template.render(path, None))
		
class HowToGetSetUp(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/how_to_get_set_up.html')
		self.response.out.write(template.render(path, None))

class UseCases(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/use_cases.html')
		self.response.out.write(template.render(path, None))

class ComingFeatures(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/coming_features.html')
		self.response.out.write(template.render(path, None))

class About(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/about.html')
		self.response.out.write(template.render(path, None))

class FAQ(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/faq.html')
		self.response.out.write(template.render(path, None))

application = webapp.WSGIApplication([
	("/", MainPage),
	("/what_is_capturio", WhatIsCapturio),
	("/how_to_get_set_up", HowToGetSetUp),
	("/use_cases", UseCases),
	("/coming_features", ComingFeatures),
	("/about", About),
	("/faq", FAQ),
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()