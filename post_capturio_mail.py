import logging, email

from google.appengine.api import mail

class PostMailHandler():
	
	def __init__(self, senderMail):
		self.responseMail = mail.EmailMessage(
			sender = "Capturio crew <crew@captur.io>",
			to = senderMail
		)
	
	def sendResponse(self, typeOfResponse, URL = ""):
		
		if(typeOfResponse == "noAttachment"):
			self.responseMail.subject = "No contact information or image of your tshirt found in your last email"
			self.responseMail.body = """			
We're sorry but we didn't find any image of your tshirt or contact information in your last email. Please double check and make sure you've got at least one picture of your tshirt or your contact information attached (a .vcf file) so that we can start setting up your profile.
			"""		
		elif(typeOfResponse == "tooManyAttachments"):
			self.responseMail.subject = "Too many files in your last email. We only need one contact information and one image of your tshirt :-)"
			self.responseMail.body = """
We're sorry but we received too many files from you. We don't know which one to pick up! We only need one contact information file (.vcf) and one image of your tshirt. Please make sure to send only one picture and one contact information file (.vcf) we will link together!			
			"""
		elif(typeOfResponse == "noImageNocontact information"):
			self.responseMail.subject = "No image (.jpg, .jpeg, .png, .gif) and no contact information (.vcf) have been found in your last email"
			self.responseMail.body = """
We're sorry but we didn't find any image (.jpg, .jpeg, .png, .gif) or contact information (.vcf) in your last email. Please double check the files you submitted and send us only one image of your tshirt and one contact information file in the formats mentioned earlier.
			"""
		elif(typeOfResponse == "imageInMoodstocksDatabase"):
			self.responseMail.subject = "Your image or a similar image is already in our database"
			self.responseMail.body = """
We're sorry but it looks like your image/ or a very similar image to yours is already in our database. Once an image is in our database and linked to someone's profile, someone else cannot use the same. Try to submit a different image!		
			"""
		elif(typeOfResponse == "signupWithImageAndcontact information"):
			self.responseMail.subject = "[Confirmation] Your image and contact information linked together in your Capturio profile"
			self.responseMail.body = """
Your image and contact information are now linked together in your Capturio profile! You can let people take a pic of your capturio object and send it to get@captur.io. They will receive instantly your contact information!
			"""	
		elif(typeOfResponse == "signupWithImagecontact informationMissing"):
			self.responseMail.subject = "[Confirmation] New image in your Capturio profile. Send now your contact information to post@captur.io"
			self.responseMail.body = """
Your image has just been added to your Capturio profile. Send now your contact information to post@captur.io to complete the association!
			"""
		elif(typeOfResponse == "signupWithImagecontact informationAlreadyThere"):
			self.responseMail.subject = "[Confirmation] New image in your Capturio profile. You're now all set!"
			self.responseMail.body = """
Your image has just been added to your Capturio profile. You're now all set! You can start let people take a pic of your tshirt and send it to get@captur.io. They will receive instantly your contact information!
			"""
		elif(typeOfResponse == "signupWithcontact informationImageMissing"):
			self.responseMail.subject = "[Confirmation] New contact information in your Capturio profile. Send now your image to post@captur.io"
			self.responseMail.body = """
Your contact information has just been added to your Capturio profile. Send now your image to post@captur.io to complete the association!
			"""
		elif(typeOfResponse == "signupWithcontact informationImageAlreadyThere"):
			self.responseMail.subject = "[Confirmation] New contact information in your Capturio profile. You're now all set!"
			self.responseMail.body = """
Your contact information has just been added to your Capturio profile. You're now all set! You can start let people take a pic of your tshirt and send it to get@captur.io. They will receive instantly your contact information!
			"""		
		elif(typeOfResponse == "informationReplaced"):
			self.responseMail.subject = "[Confirmation] New information in your Capturio profile"
			self.responseMail.body = """
New information has just been sent into your Capturio profile. Please, click the following link to confirm (if you do so, old data will be replaced): %s
			""" % (URL)	
		elif(typeOfResponse == "error"):
			self.responseMail.subject = "An error occurred"
			self.responseMail.body = """
We're sorry but an error occurred. Please retry in a couple of minutes.
			"""
					
		hello = """Hey,
"""
		signature = """
Ping us again, soon!

Capturio crew
		"""

		self.responseMail.body = hello + self.responseMail.body + signature

		self.responseMail.send()	
		logging.info("responseMail sent")		
