from google.appengine.ext import db

from vcard_storage import VcardStorage
from image_storage import ImageStorage

class Usertemp(db.Model):
	label = db.StringProperty()
	mail = db.EmailProperty()
	imageRef = db.ReferenceProperty(ImageStorage,
									required = False,
									collection_name = "tempImageRef")
	vcardRef = db.ReferenceProperty(VcardStorage,
									required = False,
									collection_name = "tempVcardRef")