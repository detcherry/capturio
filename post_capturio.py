from __future__ import with_statement

import logging, time

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

from google.appengine.api.mail import _EmailMessageBase
def fix_check_attachment( func ):
       def fixed_check_attachment( self, attachment ):
               logging.debug( "run fix_check_attachment" )
               file_name, data = attachment
               if isinstance( file_name, tuple ) and len( file_name ) == 3:
                       func( self, ( file_name[ 2 ], data ) )
               else:
                       func( self, attachment )
       return fixed_check_attachment

_EmailMessageBase._check_attachment = fix_check_attachment( _EmailMessageBase._check_attachment )

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
		
		error = False
		
		# We instantiate the vcard
		try:
			vcard = self.incomingMailHandler.getVcardNameAndContent()		
		except Exception, e:
			logging.info("Something went wrong with the processing of the vcard in the mail attachments")
			logging.error(e)
			vcard = None
			error = True
		
		if(vcard):
			self.vcardName = vcard[0]			
			self.vcardContent = vcard[1]
		
		# We instantiate the image
		try:
			self.imageContent = self.incomingMailHandler.getImageContent()	
		except Exception, e:
			logging.info("Something went wrong with the processing of the image in the mail attachments")
			logging.error(e)
			imageContent = None
			error = True
		
		if(not(error)):
			# If no picture and no vcard have been found in the attachments, we send a warning mail. Otherwise, we handle them
			if(not(self.imageContent) and not(self.vcardContent)):
				self.responseHandler.sendResponse("noImageNoVcard")
			else:
				self.dispatchAccordingToRecognition()
		else:
			self.responseHandler.sendResponse("error")
	
	def dispatchAccordingToRecognition(self):
		
		#If there is an image, we have to figure out if it's already in Moodstocks DB
		if(self.imageContent):
			
			# Image insertion in the blobstore
			file_name = files.blobstore.create(mime_type='image/jpeg')
			with files.open(file_name, 'a') as f:
				f.write(self.imageContent)
			files.finalize(file_name)
			
			# Sometimes blobKey is None
			self.blobKey = files.blobstore.get_blob_key(file_name)
			
			# We have to make it wait til it works!
			for i in range(1,5):	
				if(self.blobKey):
					break
				else:
					logging.info("BlobKey is still None")
					time.sleep(0.05)
					self.blobKey = files.blobstore.get_blob_key(file_name)
			
			logging.info("Blobkey: "+str(self.blobKey))
		
			if(self.imageInMoodstocksDB()):
				logging.info("Moodstocks assumes the image is already in the database") 
				
				# We delete the image from the blobstore
				blobstore.delete(self.blobKey)
				
				self.responseHandler.sendResponse("imageInMoodstocksDatabase")
			else:
				logging.info("Image passed the Moodstocks test")
				self.saveUser()			
			
		else:
			logging.info("No image => No Moodstocks test necessary")
			self.saveUser()		
		
	def imageInMoodstocksDB(self):
		
		self.imageURL = images.get_serving_url(self.blobKey)
		logging.info("URL generated for new image: " + self.imageURL)
		
		self.moodstocksHandler = Moodstocks()
		searchResponse = self.moodstocksHandler.lookForObject(self.imageURL)
				
		presenceInDB = searchResponse[0]
		
		return presenceInDB	
	
 	# It's high time saving the user with its new information (if info is replacing existing data, need to send a confirmation email)
	def saveUser(self):
		
		# Retrieval of information concerning the mail sender
		userQuery = User.all().filter("mail", self.senderMail)
		userQueryResult = userQuery.get()	
		
		if(userQueryResult):
			user = userQueryResult
		else:
			user = User()
			user.label = self.senderLabel
			user.mail = db.Email(self.senderMail)
		
		# Was there already an image in the DB?
		try:
			userImage = user.imageRef
		except AttributeError, e:
			userImage = None
		if(userImage):
			self.statusImage = "alreadyExisted"
		else:
			self.statusImage = "didNotExist"
		logging.info("status Image: "+ self.statusImage)	
			
		# Was there already a vcard in the DB?
		try:
			userVcard = user.vcardRef
		except AttributeError, e:
			userVcard = None
		if(userVcard):
			self.statusVcard = "alreadyExisted"			
		else:
			self.statusVcard = "didNotExist"
		logging.info("status Vcard: "+self.statusVcard)
						
		# There are 2 different post requests
		# - no information replaced (information just added) => INFORMATION EMAIL
		# - some information replaced => CONFIRMATION EMAIL WITH A LINK
		
		# In the first case, there are 3 different situations
		# - SignupWithImageAndVcard: vcard:(True & didNotExist) & image:(True & didNotExist)
		# - SignupWithImage: vcard:(False & ...) & image:(True & didNotExist)
		# - SignupWithVcard: vcard:(True & didNotExist) & image:(False & ...)
		# In the second case, we just send a confirmation email saying: "new information in your account, please confirm"
		
		# SignupWithImageAndVcard
		if((self.vcardContent) and (self.statusVcard == "didNotExist") and (self.blobKey) and (self.statusImage == "didNotExist")):

			logging.info("SignupWithImageAndVcard")
		
			# VcardRef insertion in the user entity
			user.vcardRef = self.insertVcard()
				
			# ImageRef insertion in the user entity
			user.imageRef = self.insertImage()

			user.put()
			logging.info("User has been saved")
			self.responseHandler.sendResponse("signupWithImageAndVcard")
		
		# SignupWithImage
		elif(not(self.vcardContent) and (self.blobKey) and (self.statusImage == "didNotExist")):

			logging.info("SignupWithImage")
			
			# ImageRef insertion in the user entity
			user.imageRef = self.insertImage()
			user.put()
			logging.info("User has been saved")
			
			if(not(user.vcardRef)):
				typeOfResponse = "signupWithImageVcardMissing"
			else:
				typeOfResponse = "signupWithImageVcardAlreadyThere"
			
			self.responseHandler.sendResponse(typeOfResponse)
		
		# SignupWithVcard
		elif(not(self.blobKey) and (self.vcardContent) and (self.statusVcard == "didNotExist")):
			
			logging.info("SignupWithVcard")
			
			# VcardRef insertion in the user entity
			user.vcardRef = self.insertVcard()
			user.put()
			logging.info("User has been saved")
			
			if(not(user.imageRef)):
				typeOfResponse = "signupWithVcardImageMissing"
			else:
				typeOfResponse = "signupWithVcardImageAlreadyThere"
			
			self.responseHandler.sendResponse(typeOfResponse)			
					
		# Some information is replaced. We create a Usertemp entity
		else:
			newUser = Usertemp()
			newUser.label = self.senderLabel
			newUser.mail = db.Email(self.senderMail)
				
			if(self.blobKey):		
				newUser.imageRef = self.insertImage()

			if(self.vcardContent):
				newUser.vcardRef = self.insertVcard()
		
			newUser.put()
			logging.info("Usertemp has been saved")
		
			self.buildConfirmationMail(str(newUser.key().id()))
	
	# This function adds the vcard to the datastore
	def insertVcard(self):
		
		# Vcard insertion
		vcard = VcardStorage()
		vcard.name = self.vcardName
		try:
			vcard.content = self.vcardContent		
		except:
			logging.info("We have to encode it in UTF-8")
			vcard.content = self.vcardContent.encode("utf-8")
		vcard.put()
		
		vcardKey = vcard.key()
		return vcardKey
		
	# This function adds an imageRef to the datastore and the image to the Moodstocks DB	
	def insertImage(self):
		
		# Image insertion in the datastore
		imageRef = ImageStorage()
		imageRef.blobKey = self.blobKey
		imageRef.put()
		
		# Image insertion in Moodstocks DB
		imageRefKey = imageRef.key()
		imageRefID = str(imageRefKey.id())
		moodstocksHandler = Moodstocks()
		moodstocksHandler.addObject(imageRefID, self.imageURL)
		
		return imageRefKey

	def buildConfirmationMail(self,usertempID):
		
		encryptedID = Encryption.getEncryptedIDForConfirmation(usertempID)
		
		config = Config()
		site_url = config.site_url
		
		# We build the url with encrypted Usertemp Key
		url = site_url + "confirm?id=%s&crypt=%s" % (usertempID, encryptedID)
		logging.info("Confirmation URL: %s", url)
		
		self.responseHandler.sendResponse("informationReplaced", url)

application = webapp.WSGIApplication([PostCapturioHandler.mapping()], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
	
