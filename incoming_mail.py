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
		
		mailWithLabelTuple = email.header.decode_header(self.mailWithLabel)[0]
		mailWithLabelEncoded = mailWithLabelTuple[0]
		mailWithLabelEncoding = mailWithLabelTuple[1]
		
		if(mailWithLabelEncoding):
			mailWithLabelDecoded = mailWithLabelEncoded.decode(mailWithLabelEncoding)
		else:
			mailWithLabelDecoded = mailWithLabelEncoded.decode()
		
		mailRegexMatch = re.search(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}', self.mailWithLabel)
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
			
			# According the RFC2047
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
					UTF8Filename = encodedFilename.decode()
								
			# According the RFC2231
			# Example: ('utf-8', '', 'C\xc3\xa9dric Deltheil.vcf')
			else:
				tupleWithEncodedFilenameAndEncoding = filename
				encoding = tupleWithEncodedFilenameAndEncoding[0]
				encodedFilename = tupleWithEncodedFilenameAndEncoding[2]
				
				UTF8Filename = encodedFilename.decode(encoding)
				
			filetype = UTF8Filename[-4:].lower()
			if(filetype == ".vcf"):
				vcardName = UTF8Filename
				
				logging.info(vcardName)
				
				encodedVcardData = attachment[1]
				vcardContent = encodedVcardData.decode()
				
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
				
				
				
	
	