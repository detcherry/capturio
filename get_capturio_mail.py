import logging, email

from google.appengine.api import mail

class GetMailHandler():
	
	def __init__(self, senderMail):
		self.responseMail = mail.EmailMessage(
			sender = "Capturio's crew <crew@captur.io>",
			to = senderMail
		)
	
	def sendResponse(self, typeOfResponse, attachments = None, url = None):
		if(typeOfResponse == "noAttachment"):
			self.responseMail.subject = "We didn't find any ID image in your last email"
			self.responseMail.body = """			
We're sorry but we didn't find any ID image in your last email. Please double check and make sure you've got one ID image so that we can send you the associated contact information.
			"""
		elif(typeOfResponse == "tooManyAttachments"):
			self.responseMail.subject = "Too many files in your last email. We process only one image per email"
			self.responseMail.body = """
We're sorry but we received too many files from you. For the moment, we only process one image per email. Please send us only one image and we will send you the associated contact information			
			"""
		elif(typeOfResponse == "imageExtensionInvalid"):
			self.responseMail.subject = "Image extension not recognized. Please send us a .jpeg/.jpg, .png or .gif image"
			self.responseMail.body = """
We're sorry but we did not recognize the extension of your image. Please make sure to send a .jpeg/.jpg , .png or .gif image.		
			"""				
		elif(typeOfResponse == "noMatchingImage"):
			self.responseMail.subject = "We didn't find any vcard associated with your image"
			self.responseMail.body = """
We're sorry but we don't know this image. Please retry with a picture with more light and/or precision.
			"""
		elif(typeOfResponse == "noVcardAssociated"):		
			self.responseMail.subject = "The user we found did not associate any vcard"
			self.responseMail.body = """
We're sorry but the user matching your image did not associate any vcard. We'll ping him so that he'll input this information!
			"""	
		elif(typeOfResponse == "vcardAttached"):
			self.responseMail.subject = "[Capturio rocks] Please find attached the vcard you requested"
			self.responseMail.body = """
Please find attached the vcard associated with the image you sent earlier. Isn't it magical? Feel free to send us other images. 

If this is not the right vcard (more than exceptional), please click the following link to report it: %s. Our team will take a look at it ASAP. Thanks for helping us improve our service.
			""" % (url)
			self.responseMail.attachments = attachments	
		elif(typeOfResponse == "error"):
			self.responseMail.subject = "An error occurred"
			self.responseMail.body = """
We're sorry but an error occurred. Please retry in a couple of minutes.
			"""

		hello = """
Hey,
		"""
		signature = """
Ping us soon again!

Captur.io's crew

PS: If your vcard is not associated yet with your ID, send both to post@captur.io. For more information, go to http://captur.io		
		"""

		self.responseMail.body = hello + self.responseMail.body + signature	
			
		self.responseMail.send()
		logging.info("responseMail sent")
		
		
	def sendAlert(self, typeOfResponse, attachments = None, url = None, label = None, mail = None):

		if(typeOfResponse == "justCapturedRequesterWithVcard"):
			self.responseMail.subject = "You have been captured by another person on Captur.io"
			self.responseMail.body = """
The following person: %s (%s) captured you with Capturio! He just receives your vcard because you have probably shown him your ID! Please find also attached his own vcard.

If you think there is an error, please click the following link to report it: %s. Our team will take a look at it ASAP. Thanks for helping us improve our service.
			""" % (label, mail, url)
			self.responseMail.attachments = attachments		
		elif(typeOfResponse == "justCapturedRequesterWithoutVcard"):
			self.responseMail.subject = "You have been captured by another person on Captur.io"
			self.responseMail.body = """
The following person: %s (%s) captured you with Capturio! He just receives your vcard because you have probably shown him your ID!

If you think there is an error, please click the following link to report it: %s. Our team will take a look at it ASAP. Thanks for helping us improve our service.
			""" % (label, mail, url)
	
		hello = """
Hey,
		"""
		signature = """
Ping us soon again!

Capturio's crew
		"""

		self.responseMail.body = hello + self.responseMail.body + signature	
		self.responseMail.send()
		logging.info("alert sent")





