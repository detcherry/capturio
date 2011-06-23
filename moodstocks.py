import logging, urllib, urllib2

from django.utils import simplejson as json

from config import Config
from multipartposthandler import MultipartPostHandler

class Moodstocks():
	
	def __init__(self):
		# Key and secret key for application "capturiodev"
		config = Config()
		self.key = config.moodstocks_key 
		self.secret = config.moodstocks_secret   

		# urllib boilerplate
		self.api_ep_base = "http://api.moodstocks.com"
		self.api_ep = self.api_ep_base + "/v2"
		self.pass_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
		self.pass_manager.add_password(None, self.api_ep_base, self.key, self.secret)
		self.auth_handler = urllib2.HTTPDigestAuthHandler(self.pass_manager)
		self.opener = urllib2.build_opener(self.auth_handler)
		self.multipart_opener = urllib2.build_opener(self.auth_handler,MultipartPostHandler)

	# Make echo based on the URL served by the blobstore
	def makeEcho(self, url):
		qstring = urllib.urlencode({"image_url": url})
		totalString = "%s?%s" % (self.api_ep+"/echo",qstring)
		r = self.opener.open(totalString)
		jsonPackage = json.loads(r.read())
		logging.info(jsonPackage)
	
	# Look for the object behind the URL served by the blobstore
	def lookForObject(self, url):
		qstring = urllib.urlencode({"image_url":url})
		totalString = "%s?%s" % (self.api_ep+"/search",qstring)
		r = self.opener.open(totalString)
		jsonPackage = json.loads(r.read())
		
		booleanResponse = jsonPackage["found"]
		logging.info("The image in Moodstocks DB? => "+ str(booleanResponse))
		if(booleanResponse):
			moodstocksID = int(jsonPackage["id"])
			logging.info("ID of image in Moodstocks DB: "+str(moodstocksID))
		else:
			moodstocksID = None
		response = (booleanResponse, moodstocksID)
		
		return response

	# Add object behind the URL served by the blobstore
	def addObject(self, imgID, url):
		req = urllib2.Request(self.api_ep+"/ref/"+imgID,{"image_url":url})
		req.get_method = lambda: "PUT"
		r = self.multipart_opener.open(req)
		jsonPackage = json.loads(r.read())
		logging.info(jsonPackage)
	
	# Delete object from Moodstocks DB
	def deleteObject(self, imgID):
		req = urllib2.Request(self.api_ep+"/ref/"+imgID,"")
		req.get_method = lambda: "DELETE"
		r = self.multipart_opener.open(req)
		jsonPackage = json.loads(r.read())
		logging.info(jsonPackage)		
		
		
		
		
