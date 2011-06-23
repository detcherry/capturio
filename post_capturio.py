from __future__ import with_statement

import logging

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext import db
from google.appengine.api import files
from google.appengine.ext import blobstore
from google.appengine.api import images

from models.user import User
from models.usertemp import Usertemp
from models.vcard_storage import VcardStorage
from models.image_storage import ImageStorage

from config import Config
from incoming_mail import IncomingMailHandler
from post_capturio_mail import PostMailHandler
from encryption import Encryption
from moodstocks import Moodstocks

class PostCapturioHandler(InboundMailHandler):
			
	def receive(self, message):
		logging.info("post@captur.io request")
		
		self.senderMail = None
		self.senderLabel = None
		self.vcardName = None
		self.vcardContent = None
		self.imageContent = None
		self.blobKey = None
		self.imageURL = None
		self.statusImage = None
		self.statusVcard = None

		# Get the sender of the mail
		mailWithLabel = message.sender
		
		# Get mail attachments
		try:
			attachments = message.attachments
		except AttributeError, e:
			attachments = []
						
		self.incomingMailHandler = IncomingMailHandler(mailWithLabel, attachments)
		
		# Extract Mail address and build Response Handler
		mailAndLabel = self.incomingMailHandler.extractMailAndLabel()
		self.senderMail = mailAndLabel[0]
		self.senderLabel = mailAndLabel[1]
		logging.info("Message sender: 1) Mail: " + self.senderMail + " 2) Label: " + self.senderLabel)
		self.responseHandler = PostMailHandler(self.senderMail)	
		
		# Dispatch the response according to the number of attachments
		numberOfAttachments = self.incomingMailHandler.getNumberOfAttachments()		
		self.dispatchAccordingToAttachments(numberOfAttachments)
		
				
	def dispatchAccordingToAttachments(self, numberOfAttachments):
		if(numberOfAttachments == 0):
			logging.info("No attachment")
			self.responseHandler.sendResponse("noAttachment")
		elif(numberOfAttachments > 2):
			logging.info("Too many attachments")
			self.responseHandler.sendResponse("tooManyAttachments")			
		else:
			logging.info("Number of attachments < 2")
			# We instantiate the vcard and/or image
			self.initAttachments()	
	
	# This function instantiates the image and vcard (if found in the mail)	and calls the image checking function
	def initAttachments(self):
		
		# We instantiate the vcard
		try:
			vcard = self.incomingMailHandler.getVcardNameAndContent()		
		except Exception, e:
			logging.info("Something went wrong with the processing of the vcard in the mail attachments")
			logging.error(e)
			vcardNameAndContent = None
		
		if(vcard):
			self.vcardName = vcard[0]			
			self.vcardContent = vcard[1]
			logging.info("Vcard OK (name: "+ self.vcardName + ")")	
		
		# We instantiate the image
		try:
			self.imageContent = self.incomingMailHandler.getImageContent()	
		except Exception, e:
			logging.info("Something went wrong with the processing of the image in the mail attachments")
			logging.error(e)
			imageContent = None
		
		# If no picture and no vcard have been found in the attachments, we send a warning mail. Otherwise, we handle them
		if(not(self.imageContent) and not(self.vcardContent)):
			self.responseHandler.sendResponse("noImageNoVcard")
		else:
			self.saveUsertemp()
	
 	# It's high time saving the user with its new information in an entity called "usertemp"
	def saveUsertemp(self):
		
		# Retrieval of information concerning the mail sender
		existingUser = None
		user_query = User.all().filter("mail", self.senderMail)
		existingUser = user_query.get()	
		
		try:
			existingUserImage = existingUser.imageRef
		except AttributeError, e:
			existingUserImage = None
		try:
			existingUserVcard = existingUser.vcardRef
		except AttributeError, e:
			existingUserVcard = None
			
		if(existingUser):
			logging.info("User already existed")
		else:
			logging.info("User didn't exist before")
			
		#-------------------------------------------------------------
			
		newUser = Usertemp()
		newUser.label = self.senderLabel
		newUser.mail = db.Email(self.senderMail)
				
		if(self.imageContent):		
			
			# Image insertion in the blobstore
			file_name = files.blobstore.create(mime_type='image/jpeg')
			with files.open(file_name, 'a') as f:
				f.write(self.imageContent)
			files.finalize(file_name)
			self.blobKey = files.blobstore.get_blob_key(file_name)
			logging.info("Blobkey: "+str(self.blobKey))
			
			# ImageRef insertion in the datastore
			imageRef = ImageStorage()
			imageRef.blobKey = self.blobKey
			imageRef.put()
			
			# ImageRef insertion in the user entity
			imageRefKey = imageRef.key()
			newUser.imageRef = imageRefKey
			
			# Image insertion in Moodstocks DB
			imageRefID = str(imageRefKey.id())
			self.imageURL = images.get_serving_url(self.blobKey)
			moodstocksHandler = Moodstocks()
			moodstocksHandler.addObject(imageRefID, self.imageURL)
			
			self.statusImage = "justAdded"
		else:
			if(existingUserImage):
				self.statusImage = "isThere"
			else:
				self.statusImage = "stillMissing"
		logging.info("statusImage: %s", self.statusImage)

		if(self.vcardContent):
			
			vcard = VcardStorage()
			vcard.content = self.vcardContent			
			vcard.name = self.vcardName
			vcard.put()
			
			vcardKey = vcard.key()
			newUser.vcardRef = vcardKey
			self.statusVcard = "justAdded"
		else:
			if(existingUserVcard):
				self.statusVcard = "isThere"
			else:
				self.statusVcard = "stillMissing"
		logging.info("statusVcard: %s", self.statusVcard)
		
		newUser.put()
		logging.info("Usertemp has been saved")
		
		self.buildResponseMailType(str(newUser.key().id()))
	
	def buildResponseMailType(self,usertempID):
		
		encryptedID = Encryption.getEncryptedIDForConfirmation(usertempID)
		
		config = Config()
		site_url = config.site_url
		
		# We build the url with encrypted Usertemp Key
		url = site_url + "confirm?id=%s&crypt=%s" % (usertempID, encryptedID)
		logging.info("Confirmation URL: %s", url)
		
		if(self.blobKey):
			if(self.vcardContent):
				typeOfResponse = "newImageNewVcard"
			else:
				if(self.statusVcard == "stillMissing"):
					typeOfResponse = "newImageNoVcardAndMissing"
				else:
					typeOfResponse = "newImageNoVcardButOk"
		else:
			if(self.statusImage == "stillMissing"):
				typeOfResponse = "noImageAndMissingNewVcard"
			else:
				typeOfResponse = "noImageButOkNewVcard"
		
		logging.info("Type of the change: %s", typeOfResponse)
		self.responseHandler.sendResponse(typeOfResponse, url)

application = webapp.WSGIApplication([PostCapturioHandler.mapping()], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
	
