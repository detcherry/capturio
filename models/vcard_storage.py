from google.appengine.ext import db

class VcardStorage(db.Model):
	name = db.StringProperty()
	content = db.BlobProperty()