import logging, email, re

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext import blobstore

from models.user import User

class StatusCapturioHandler(InboundMailHandler):
	
	def receive(self,message):
		logging.info("status@captur.io request")
		
		self.mail = message
		self.senderMail = None
		self.existingUser = None
		self.existingImage = None
		self.responseMail = None
		
		# We extract mail information with a regex
		mailRegexMatch = re.search(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}',self.mail.sender)
		self.senderMail = mailRegexMatch.group()
		logging.info("Received a message from: " + self.senderMail)
		
		# We look if this user is in our database
		user_query = User.all().filter("mail", self.senderMail)
		self.existingUser = user_query.get()
		
		# We look if there is user and if the user provided an image
		try:
			imageRef = self.existingUser.imageRef
		except:
			imageRef = None
		
		if(imageRef):
			logging.info("Image found")
			blobKey = imageRef.blobKey
			blobReader = blobstore.BlobReader(blobKey)
			self.existingImage = blobReader.read()
		
		self.sendResponseMail()
			
	def sendResponseMail(self):
		
		# Build the beginnning of the responseMail
		self.responseMail = mail.EmailMessage(
			sender = "Capturio crew <crew@captur.io>",
			to = self.senderMail
		)
		
		# If there is an image
		if(self.existingImage):
			self.responseMail.subject = "Please find attached your image!"
			self.responseMail.body = """
Hey,

Please find attached the image you provided to Capturio.

Feel free to change this image if you want: just email a new image at post@captur.io

Ping us again, soon!

			
Capturio Crew			
			"""
			attachmentName = "Your Capturio image.jpeg"
			attachmentFile = self.existingImage
			attachment = (attachmentName,attachmentFile)
			attachments = [attachment]
			self.responseMail.attachments = attachments
			
		# If there is no image 
		else:
			self.responseMail.subject = "No image found in Capturio"
			self.responseMail.body = """
Hey,

Please find attached the image you provided to Capturio.

Feel free to change this image if you want: just email a new image at post@captur.io

Ping us again, soon!

Capturio Crew			
			"""
		
		self.responseMail.send()
		logging.info("responseMail sent")
	

application = webapp.WSGIApplication([StatusCapturioHandler.mapping()], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()