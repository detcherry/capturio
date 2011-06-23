import logging, email

from google.appengine.api import mail

class PostMailHandler():
	
	def __init__(self, senderMail):
		self.responseMail = mail.EmailMessage(
			sender = "Capturio's crew <crew@captur.io>",
			to = senderMail
		)
	
	def sendResponse(self, typeOfResponse, URL = ""):
		
		if(typeOfResponse == "noAttachment"):
			self.responseMail.subject = "No vcard or image of your ID found in your last email"
			self.responseMail.body = """			
We're sorry but we didn't find any image of your ID or vcard in your last email. Please double check and make sure you've got at least one picture of your ID or one vcard attached so that we can start setting up your profile.
			"""		
		elif(typeOfResponse == "tooManyAttachments"):
			self.responseMail.subject = "Too many files in your last email. We only need one vcard and one image of your ID :-)"
			self.responseMail.body = """
We're sorry but we received too many files from you. We don't know which one to pick up! We only need one vcard and one image of your ID. Please make sure to send only one picture and one vcard we will link together!			
			"""
		elif(typeOfResponse == "noImageNoVcard"):
			self.responseMail.subject = "No image (.jpg, .jpeg, .png, .gif) and no vcard (.vcf) have been found in your last email"
			self.responseMail.body = """
We're sorry but we didn't find any image (.jpg, .jpeg, .png, .gif) or vcard (.vcf) in your last email. Please double check the files you submitted and send us only one image of your ID and one vcard in the formats mentioned earlier.
			"""
		elif(typeOfResponse == "newImageNewVcard"):
			self.responseMail.subject = "[Confirmation] Your ID image and your vcard linked together with Captur.io"
			self.responseMail.body = """
Your ID image and your vcard have just been linked together with Captur.io. Please, click the following link to confirm: %s
			""" % (URL)
		elif(typeOfResponse == "newImageNoVcardAndMissing"):
			self.responseMail.subject = "[Confirmation] New ID image in your Captur.io profile. Send now your vcard to post@captur.io"
			self.responseMail.body = """
A new ID image has just been saved into your Captur.io profile. Please, click the following link to confirm: %s
			""" % (URL)
		elif(typeOfResponse == "newImageNoVcardButOk"):
			self.responseMail.subject = "[Confirmation] New ID image in your Captur.io profile"
			self.responseMail.body = """
A new ID image has just been saved into your Captur.io profile. Please, click the following link to confirm: %s
			"""	% (URL)		
		elif(typeOfResponse == "noImageAndMissingNewVcard"):
			self.responseMail.subject = "[Confirmation] New vcard in your Captur.io profile. Send now an image of your ID to post@captur.io"
			self.responseMail.body = """
A new vcard has just been saved into your Captur.io profile. Please, click the following link to confirm: %s
			""" % (URL)
		elif(typeOfResponse == "noImageButOkNewVcard"):
			self.responseMail.subject = "[Confirmation] New vcard in your Captur.io profile"
			self.responseMail.body = """
A new vcard has just been saved into your Captur.io profile. Please, click the following link to confirm: %s
			""" % (URL)	
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

Capturio's crew
		"""

		self.responseMail.body = hello + self.responseMail.body + signature

		self.responseMail.send()	
		logging.info("responseMail sent")		
