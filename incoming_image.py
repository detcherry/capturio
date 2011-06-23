import logging

from google.appengine.api import images

class IncomingImageHandler():
	
	def __init__(self, image):
		self.image = image
	
	# This function returns the image to a jpeg format and a reduced size: max 450px
	def processImage(self):
		imageProcessed = None
		
		# images.Image encapsulate an image to perform transformation using the execute_transforms function
		imageWrapper = images.Image(self.image)

		# Reduce image size
		if(imageWrapper.width > 450):
			imageWrapper.resize(width = 450)
			if(imageWrapper.height > 450):
				imageWrapper.resize(width = 450)
			logging.info("Image resized")
		else:
			logging.info("No need to resize the image")
		
		# Because we need at least one change before "executing the transformation"
		imageWrapper.im_feeling_lucky()
		
		imageProcessed = imageWrapper.execute_transforms(output_encoding = images.JPEG)
		logging.info("Image converted to .JPEG format")
		
		return imageProcessed