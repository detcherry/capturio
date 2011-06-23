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

class PostConfirmationHandler(webapp.RequestHandler):
	def get(self):
		logging.info("Confirmation request for post@captur.io")
		
		self.usertempID = self.request.get("id")
		self.encryptedID = self.request.get("crypt")
		self.usertemp = None
		
		self.checkUsertemp()
	
	# This function checks if the confirmation link is valid
	def checkUsertemp(self):
		if((self.usertempID) and (self.encryptedID)):
			logging.info("Confirmation page: 1) UsertempID: %s 2) EncryptedID: %s" %(self.usertempID, self.encryptedID))
			encryptedCheckingID = Encryption.getEncryptedIDForConfirmation(self.usertempID)
			
			if(encryptedCheckingID == self.encryptedID):
				logging.info("Confirmation link valid")
				self.retrieveUsertemp()
				
			else:
				logging.info("Confimation link invalid")
				self.response.out.write("Invalid confirmation link. Please retry")
		
		else:
			logging.info("Confimation link invalid")
			self.response.out.write("Invalid confirmation link. Please retry.")

	#This function retrieves the usertemp data (if it hadn't been already deleted)
	def retrieveUsertemp(self):
		usertempKey = db.Key.from_path("Usertemp", int(self.usertempID))
		self.usertemp = Usertemp.get(usertempKey)
		if(self.usertemp):
			logging.info("Usertemp retrieved: %s" % self.usertemp.mail)
			self.saveUsertemp()
		else:
			logging.info("No usertemp found. This operation has certainly already been confirmed")
			self.response.out.write("This operation has already been confirmed.")

	# This function saves the new user information in the database
	def saveUsertemp(self):
		# We determine first if some user information was already in the database
		user_query = User.all().filter("mail", self.usertemp.mail)
		existingUser = user_query.get()
		
		if(existingUser):
			user = existingUser
			user.label =  self.usertemp.label
			oldVcardRef = user.vcardRef
			oldImageRef= user.imageRef
			if(oldImageRef):
				oldImageRefID = str(oldImageRef.key().id())
			logging.info("User found: %s, %s" % (user.label, user.mail))
		else:
			user = User()
			oldVcardRef = None
			oldImageRef = None
			user.label =  self.usertemp.label
			user.mail = self.usertemp.mail
				
		if(self.usertemp.imageRef):
			# We replace the old image Ref/ (or if not found) add the new image Ref
			user.imageRef = self.usertemp.imageRef
			
			# If there was an old image ref, we have to delete the image in the blobstore, in the Moodstocks DB and the reference in the Datastore
			if(oldImageRef):
				
				# We delete the image from Moodstocks DB
				moodstocksHandler = Moodstocks()
				moodstocksHandler.deleteObject(oldImageRefID)
				
				# We delete the image in the blobstore
				blobInfo = oldImageRef.blobKey
				oldBlobKey = blobInfo.key()
				blobstore.delete(oldBlobKey)
				
				# We delete the existing image Ref
				oldImageRef.delete()
						
		if(self.usertemp.vcardRef):
			# We replace the old vcard Ref/ (or if not found) by the new vcard Ref
			user.vcardRef = self.usertemp.vcardRef
			
			# If there was an old vcard ref, we have to delete it from to datastore
			if(oldVcardRef):
				oldVcardRef.delete()

		user.put()
		self.usertemp.delete()
		if(user.imageRef):
			if(user.vcardRef):
				self.response.out.write("""
				Thanks for confirming. You're now fully set up. You can start letting people take a pic of your ID to get your contact information<br/>
				<br/>
				PS: We're now in a very closed alpha beta gamma version. Please feel free to email us if you have any trouble using our app.""")
			else:
				self.response.out.write("""
				Thanks for confirming. The image of your ID has been added to Captur.io. Now send your vcard to post@captur.io to complete the association!<br/>
				<br/>
				PS: We're now in a very closed alpha beta gamma version. Please feel free to email us if you have any trouble using our app.
				""")
		else:
			self.response.out.write("""
			Thanks for confirming. Your vcard has been added to Captur.io. Now send an image of your ID to post@captur.io to complete the association.<br/>
			<br/>
			PS: We're now in a very closed alpha beta gamma version. Please feel free to email us if you have any trouble using our app.
			""")
		

application = webapp.WSGIApplication([
	("/confirm", PostConfirmationHandler)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()