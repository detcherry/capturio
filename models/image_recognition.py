from google.appengine.ext import db
from google.appengine.ext import blobstore

from user import User

class ImageRecognition(db.Model):
	userRequester = db.ReferenceProperty(User,
										  required = False,
										  collection_name = "userRequester")
	picProvidedRef = blobstore.BlobReferenceProperty()
	userRequested = db.ReferenceProperty(User,
										required = False,
										collection_name = "userRequested")
	errorRequester = db.BooleanProperty()
	errorRequested = db.BooleanProperty()