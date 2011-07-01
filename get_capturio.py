from __future__ import with_statement

import logging, email, re

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext import db
from google.appengine.api import files
from google.appengine.ext import blobstore
from google.appengine.api import images

from models.user import User
from models.vcard_storage import VcardStorage
from models.image_storage import ImageStorage
from models.image_recognition import ImageRecognition

from config import Config
from incoming_mail import IncomingMailHandler
from get_capturio_mail import GetMailHandler
from encryption import Encryption
from moodstocks import Moodstocks

class GetCapturioHandler(InboundMailHandler):
	
	def receive(self, message):
		logging.info("get@captur.io request")
	
		self.requesterMail = None
		self.requesterLabel = None
		self.blobKey = None
		self.requesterVcardName = None
		self.requesterVcardContent = None		

		self.moodstocksID = None
		self.requestedVcardContent = None
		self.requestedVcardName = None
		self.requestedMail = None
		self.requestedLabel = None
		
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
		self.requesterMail = mailAndLabel[0]
		self.requesterLabel = mailAndLabel[1]
		logging.info("Message sender: 1) Mail: " + self.requesterMail + " 2) Label: " + self.requesterLabel)
		self.responseHandler = GetMailHandler(self.requesterMail)
	
		# Dispatch the response according to the number of attachments
		numberOfAttachments = self.incomingMailHandler.getNumberOfAttachments()		
		self.dispatchAccordingToAttachments(numberOfAttachments)
	
	def dispatchAccordingToAttachments(self, numberOfAttachments):
		if(numberOfAttachments == 0):
			logging.info("No attachment")
			self.responseHandler.sendResponse("noAttachment")
		elif(numberOfAttachments > 1):
			# For the moment I don't wanna handle the case where there are too many attachments
			logging.info("Too many attachments")
			self.responseHandler.sendResponse("tooManyAttachments")	
		else:
			logging.info("Number of attachments = 1")
			self.initImage()
	
	def initImage(self):
		
		try:
			imageContent = self.incomingMailHandler.getImageContent()
		except Exception, e:
			logging.info("Something went wrong with the processing of the image in the mail attachments")
			logging.error(e)
			imageContent = None
			
		if(imageContent):	
			# We create a blob in the blostore
			file_name = files.blobstore.create(mime_type='image/jpeg')
			with files.open(file_name, 'a') as f:
				f.write(imageContent)
			files.finalize(file_name)
			
			# Sometimes blobKey is None
			self.blobKey = files.blobstore.get_blob_key(file_name)
			
			# We have to make it wait til it works!
			for i in range(1,3):	
				if(self.blobKey):
					break
				else:
					logging.info("BlobKey is still None")
					time.sleep(0.05)
					self.blobKey = files.blobstore.get_blob_key(file_name)
			
			logging.info("Blobkey: "+str(self.blobKey))
			self.dispatchAccordingToRecognition()
		else:
			logging.info("Image extension invalid")
			self.responseHandler.sendResponse("imageExtensionInvalid")	
	
	def dispatchAccordingToRecognition(self):		
		self.moodstocksID = self.getMoodstocksID()
		if(self.moodstocksID):
			self.collectInformation()
		else:
			logging.info("Moodstocks didn't find any matching image")
			
			# We delete the image in the blobstore
			blobstore.delete(self.blobKey)
			
			self.responseHandler.sendResponse("noMatchingImage")
	
	def getMoodstocksID(self):
		ID = None
		
		imageURL = images.get_serving_url(self.blobKey)
		logging.info("URL generated: " + imageURL)
		
		moodstocksHandler = Moodstocks()
		searchResponse = moodstocksHandler.lookForObject(imageURL)
		
		presenceInDB = searchResponse[0]
		if(presenceInDB):
			ID = searchResponse[1]
		
		return ID
	
	# This function essentially grabs the vcard associated to the Moodstocks ID and puts together a recognition entity	
	def collectInformation(self):
		
		recognition = ImageRecognition()
		recognition.picProvidedRef = self.blobKey
		
		# Collect information about the user making the request. 
		# If he doesn't exist, we put him in the DB. 
		# If he exists, we gather his information.
		
		user_query = User.all().filter("mail", self.requesterMail)
		existingUser = user_query.get()
		
		userRequester = None
		if(existingUser):
			userRequester = existingUser
			
			# This information will be provided to the person that has been captured
			if(existingUser.vcardRef):				
				existingUserVcard = existingUser.vcardRef
				self.requesterVcardName = "[Captur.io]"+existingUserVcard.name
				self.requesterVcardContent = existingUserVcard.content	
		else:
			userRequester = User()
			userRequester.label = self.requesterLabel
			userRequester.mail = self.requesterMail
			userRequester.put()
		
		recognition.userRequester = userRequester.key()
		
		# Collect information about the user returned 	
		
		# We first retrieved the image corresponding to the moodstocks ID
		imageRefKey = db.Key.from_path("ImageStorage", self.moodstocksID)
		
		# Then we retrieved the user owning this image
		userRequested_query = User.all().filter("imageRef", imageRefKey)
		userRequested = userRequested_query.get()
		
		if(userRequested):
			recognition.userRequested = userRequested.key()
			recognition.errorRequester = False
			recognition.errorRequested = False
			recognition.put()
			logging.info("Recognition event saved: 1) Target: %s 2) Recipient: %s" % (userRequested.mail, userRequester.mail) )
			recognitionID = str(recognition.key().id())
			
			self.requestedMail = userRequested.mail
			self.requestedLabel = userRequested.label
			
			requestedVcard = userRequested.vcardRef
			if(requestedVcard):				
				self.requestedVcardName = "[Captur.io]"+requestedVcard.name
				self.requestedVcardContent = requestedVcard.content
				self.buildResponseMail(recognitionID)
			else:
				self.responseHandler.sendResponse("noVcardAssociated")
		else:
			logging.warning("We found a Moodstocks ID but we didn't found a user matching it. There is something wrong somewhere...")
		
	# In this mail, we build the messages to the requester and the requested
	def buildResponseMail(self, recognitionID):
		logging.info("Recognition ID: %s" % recognitionID)
		
		# Instantiate the attachment for the requester
		requesterAttachment = (self.requestedVcardName, self.requestedVcardContent)
		requesterAttachments = [requesterAttachment]
		
		conf = Config()
		site_url = conf.site_url
		
		# We encrypt the recognition ID for the error reporting URL for the requester
		encryptedIDForRequester = Encryption.getEncryptedIDForRequesterError(recognitionID)
		logging.info("Encrypted ID for Requester: %s" % encryptedIDForRequester)
		
		urlForRequester = site_url + "reportrequester?id=%s&crypt=%s" % (recognitionID, encryptedIDForRequester)
		logging.info("URL that the requester can use to report an error: %s", urlForRequester)
		
		self.responseHandler.sendResponse("vcardAttached", requesterAttachments, urlForRequester)
		
		#----------------------------
		
		self.alertRecognition = GetMailHandler(self.requestedMail)
		
		# We encrypt the recognition ID for the error reporting URL for the requester
		encryptedIDForRequested = Encryption.getEncryptedIDForRequestedError(recognitionID)
		logging.info("Encrypted ID for Requested: %s" % encryptedIDForRequested)
		
		urlForRequested = site_url + "reportrequested?id=%s&crypt=%s" % (recognitionID, encryptedIDForRequested)
		logging.info("URL that the requested can use to report an error: %s", urlForRequested)	
		
		# We now instantiate the attachment for the requested 
		if((self.requesterVcardName) and (self.requesterVcardContent)):
			requestedAttachment = (self.requesterVcardName, self.requesterVcardContent)
			requestedAttachments = [requestedAttachment]
		
			self.alertRecognition.sendAlert("justCapturedRequesterWithVcard", requestedAttachments, urlForRequested, self.requesterLabel, self.requesterMail)
		
		else:
			self.alertRecognition.sendAlert("justCapturedRequesterWithoutVcard", None, urlForRequested, self.requesterLabel, self.requesterMail)
						
	
application = webapp.WSGIApplication([GetCapturioHandler.mapping()], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
