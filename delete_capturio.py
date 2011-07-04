import logging, email, re

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import mail
from google.appengine.ext import db

from config import Config
from models.user import User
from encryption import Encryption

class DeleteCapturioHandler(InboundMailHandler):
	
	def receive(self, message):
		logging.info("delete@captur.io request")
		
		self.mail = message
		self.senderMail = None
		self.existingUser = None
		self.responseMail = None
		
		# We extract mail information with a regex
		mailRegexMatch = re.search(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}',self.mail.sender)
		self.senderMail = mailRegexMatch.group()
		logging.info("Received a message from: " + self.senderMail)
		
		# We look if this user is in our database
		user_query = User.all().filter("mail", self.senderMail)
		self.existingUser = user_query.get()
		
		# If the user is in our database, we build and send him a confirmation URL to delete his account
		if(self.existingUser):
			existingUserID = str(self.existingUser.key().id())
			encryptedID = Encryption.getEncryptedIDForDeletion(existingUserID)
			
			config = Config()
			site_url = config.site_url
			
			url = site_url + "delete?id=%s&crypt=%s" %(existingUserID, encryptedID)
			logging.info("%s" % url)
			
			self.responseMail = mail.EmailMessage(
				sender = "Capturio crew <crew@captur.io>",
				to = self.senderMail,
				subject = "[Deletion] Please confirm to remove your information from Captur.io",
				body = """
Hey,

If you want to remove all your information from Captur.io, please click on the following link: %s

We hope to see you again soon!

Captur.io crew
				""" % (url)
			)
			
			self.responseMail.send()
			logging.info("responseMail sent")
			
		else:
			logging.info("User behind address email %s wants to be removed whereas he doesn't belong to our database." % self.senderMail)
		
application = webapp.WSGIApplication([DeleteCapturioHandler.mapping()], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()