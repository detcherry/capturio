from google.appengine.ext import db
from google.appengine.ext import blobstore

class ImageStorage(db.Model):
	blobKey = blobstore.BlobReferenceProperty()