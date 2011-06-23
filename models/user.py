from google.appengine.ext import db

from vcard_storage import VcardStorage
from image_storage import ImageStorage

class User(db.Model):
	label = db.StringProperty()
	mail = db.EmailProperty()
	imageRef = db.ReferenceProperty(ImageStorage,
									required = False,
									collection_name = "imageRef")
	vcardRef = db.ReferenceProperty(VcardStorage,
									required = False,
									collection_name = "vcardRef")
