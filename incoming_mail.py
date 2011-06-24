import logging, re, email

from incoming_image import IncomingImageHandler

class IncomingMailHandler():
	
	# sender: string - total string representing the sender mail address and (if found) his name
	# attachments: list of tuple, 1st element of the tuple: filename, 2nd element of tuple: filecontent
	
	def __init__(self, mailWithLabel, attachments):
		self.mailWithLabel = mailWithLabel
		self.attachments = attachments

	def getNumberOfAttachments(self):
		numberOfAttachments = len(self.attachments)
		return numberOfAttachments
	
	def extractMailAndLabel(self):
		
		logging.info("MailWithLabel: " + self.mailWithLabel)
		
		listWithMailAndLabelAndEncoding = email.header.decode_header(self.mailWithLabel)
		tupleWithMailAndLabelAndEncoding = listWithMailAndLabelAndEncoding[0]
		mailWithLabelEncoded = tupleWithMailAndLabelAndEncoding[0]
		mailWithLabelEncoding = tupleWithMailAndLabelAndEncoding[1]
		
		if(mailWithLabelEncoding):
			mailWithLabelDecoded = mailWithLabelEncoded.decode(mailWithLabelEncoding)
		else:
			mailWithLabelDecoded = mailWithLabelEncoded.decode()
		
		logging.info("MailWithLabelDecoded: "+ mailWithLabelDecoded)
		
		mailRegexMatch = re.search(u'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}', mailWithLabelDecoded)
		mail = mailRegexMatch.group()
		
		labelRegex = re.compile("<"+mail+">")
		label = labelRegex.sub("",mailWithLabelDecoded)
		
		mailAndLabel = (mail,label)	
		
		return mailAndLabel		
			
	def getVcardNameAndContent(self):
		vcard = None
		
		for attachment in self.attachments:
			filename = attachment[0]
			UTF8Filename = ""
			
			# According the RF2047
			# Example: =?ISO-8859-1?Q?Rapha=EBl_Labb=E9=2Evcf?=
			if isinstance(filename, str):
				listWithEncodedFilenameAndEncoding = email.header.decode_header(filename)
				tupleWithEncodedFilenameAndEncoding = listWithEncodedFilenameAndEncoding[0]
				
				# After this operation we have a tuple like this
				# [('Rapha\xebl Labb\xe9.vcf', 'iso-8859-1')]
				
				encodedFilename = tupleWithEncodedFilenameAndEncoding[0]
				encoding = tupleWithEncodedFilenameAndEncoding[1]
				
				if(encoding):
					UTF8Filename = encodedFilename.decode(encoding)
				else:
					UTF8Filename = encodedFilename
			
			# I've also accountered tuples...
			# Example: ('utf-8', '', 'C\xc3\xa9dric Deltheil.vcf')
			else:
				tupleWithEncodedFilenameAndEncoding = filename
				encoding = tupleWithEncodedFilenameAndEncoding[0]
				encodedFilename = tupleWithEncodedFilenameAndEncoding[2]
				
				UTF8Filename = encodedFilename.decode(encoding)
				
			filetype = UTF8Filename[-4:].lower()
			if(filetype == ".vcf"):
				vcardName = UTF8Filename
				
				encodedVcardData = attachment[1]
				vcardPayload = encodedVcardData.payload
				vcardEncoding = encodedVcardData.encoding
				
				if(vcardEncoding):
					decodedVcard = vcardPayload.decode(vcardEncoding)
				
				vcardContent = decodedVcard.encode("utf-8")
				vcard = (vcardName, vcardContent)
		
		return vcard
	
	def getImageContent(self):
		imageContent = None
		
		for attachment in self.attachments:
			filename = attachment[0]
			UTF8Filename = ""
			
			# According the RF2047
			if isinstance(filename, str):
				listWithEncodedFilenameAndEncoding = email.header.decode_header(filename)
				tupleWithEncodedFilenameAndEncoding = listWithEncodedFilenameAndEncoding[0]
				encodedFilename = tupleWithEncodedFilenameAndEncoding[0]
				encoding = tupleWithEncodedFilenameAndEncoding[1]
				
				if(encoding):
					UTF8Filename = encodedFilename.decode(encoding)
				else:
					UTF8Filename = encodedFilename
			
			filetype = UTF8Filename[-4:].lower()
			if((filetype == ".gif") or (filetype == "jpeg") or (filetype == ".jpg") or (filetype == ".png")):
				
				encodedImageData = attachment[1]
				imagePayload = encodedImageData.payload
				imageEncoding = encodedImageData.encoding
				
				if(imageEncoding):
					decodedImageData = imagePayload.decode(imageEncoding)
					
					incomingImageHandler = IncomingImageHandler(decodedImageData)
					imageContent = incomingImageHandler.processImage()
				
		return imageContent
				
				
				
	
	