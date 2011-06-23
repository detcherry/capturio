import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from models.image_recognition import ImageRecognition
from encryption import Encryption

class ReportErrorRequesterHandler(webapp.RequestHandler):
	def get(self):
		logging.info("[SCAM TYPE] Error reported by the requester after a get@captur.io")
		
		self.recognitionID = self.request.get("id")
		self.encryptedID = self.request.get("crypt")
		self.recognition = None
		
		self.checkRecognition()

	# This function checks if the reporting link is valid
	def checkRecognition(self):
		if((self.recognitionID) and (self.encryptedID)):
			logging.info("Error reporting submitted: 1) RecognitionID: %s 2) EncryptedID: %s" %(self.recognitionID, self.encryptedID))
			encryptedCheckingID = Encryption.getEncryptedIDForRequesterError(self.recognitionID)
			
			if(encryptedCheckingID == self.encryptedID):
				logging.info("Error reporting link valid")
				self.retrieveRecognition()
				
			else:
				logging.info("Error reporting link invalid")
				self.response.out.write("Invalid error reporting link. Please retry")
		
		else:
			logging.info("Error reporting link invalid")
			self.response.out.write("Invalid error reporting link. Please retry.")		

	# This function retrieves the recognition event
	def retrieveRecognition(self):
		recognitionKey = db.Key.from_path("ImageRecognition", int(self.recognitionID))
		self.recognition = ImageRecognition.get(recognitionKey)
		if(self.recognition):
			logging.info("Recognition event retrieved")
			self.putErrorToTrue()
		else:
			logging.warning("No recognition event retrieved. The link was valid but nothing came out of the DB. Something went wrong...")
			self.response.out.write("Sorry but we didn't find anything matching your request.")
	
	# This function puts the error according to the requester to true
	def putErrorToTrue(self):
		self.recognition.errorRequester = True;
		self.recognition.put()
		logging.info("The errorRequester field is now True")
		self.response.out.write("Sorry for this matching error. It's a really exceptional event. We'll investigate this and get back to you as soon as possible. Thanks for reporting this problem and help us improve our service.")

application = webapp.WSGIApplication([
	("/reportrequester", ReportErrorRequesterHandler)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()