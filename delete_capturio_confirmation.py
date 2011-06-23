import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext import blobstore

from models.user import User
from models.usertemp import Usertemp
from models.image_storage import ImageStorage
from encryption import Encryption
from moodstocks import Moodstocks

class DeleteConfirmationHandler(webapp.RequestHandler):
	def get(self):		
		logging.info("Confirmation request for delete@captur.io")
		
		self.userID = self.request.get("id")
		self.encryptedID = self.request.get("crypt")
		self.user = None
		
		self.checkUser()
	
	def checkUser(self):
		if((self.userID) and (self.encryptedID)):
			logging.info("Deletion page: 1) User ID: %s 2) Encrypted ID: %s" %(self.userID, self.encryptedID))
			encryptedCheckingID = Encryption.getEncryptedIDForDeletion(self.userID)
			
			if(encryptedCheckingID == self.encryptedID):
				logging.info("Deletion link valid")
				self.retrieveUser()
			else:
				logging.info("Deletion link invalid")
				self.response.out.write("Invalid deletion link. Please retry.")				
			
		else:
			logging.info("Deletion link invalid")
			self.response.out.write("Invalid deletion link. Please retry.")
			
	def retrieveUser(self):
		userKey = db.Key.from_path("User", int(self.userID))
		self.user = User.get(userKey)
		
		if(self.user):
			logging.info("User retrieved: %s" % self.user.mail)
			self.deleteUser()
		else:
			logging.info("No user found. This deletion has certainly already been confirmed")
			self.response.out.write("This operation has already been confirmed.")
	
	def deleteUser(self):
				
		# We first have to remove the user's image from the blobstore, the Moodstocks DB and his reference in the Datastore
		image = self.user.imageRef
		if(image):
			imageID = str(image.key().id())
			
			# We delete the image from Moodstocks DB
			moodstocksHandler = Moodstocks()
			moodstocksHandler.deleteObject(imageID)
			
			# We delete the image in the blobstore
			blobInfo = image.blobKey
			blobKey = blobInfo.key()
			blobstore.delete(blobKey)
			
			# We can now remove the image reference
			image.delete() 
		
		# We first remove the vcard
		vcard = self.user.vcardRef
		if(vcard):
			vcard.delete()
		
		self.user.delete()
		logging.info("User has been removed from Captur.io")
		
		self.response.out.write("Your information has been removed from Captur.io. We hope to see you again soon though.")
		
application = webapp.WSGIApplication([
	("/delete", DeleteConfirmationHandler)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()