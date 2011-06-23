import hashlib, hmac

class Encryption():
	
	confirmationCode = "704dc86644c7e3751aa2465112da35fc"
	deletionCode = "aa2466644dc8fc4c7e372da3504dc"
	errorRequesterCode = "kjbdhsbjks8263ks920dk7261codiah1"
	errorRequestedCode = "njci2830sd10sdkj190xchbuqs26239dsv"
	
	@staticmethod
	def getEncryptedIDForConfirmation(inputID):
		return hmac.new(Encryption.confirmationCode, inputID, hashlib.sha512).hexdigest()[:20]
	
	@staticmethod
	def getEncryptedIDForDeletion(inputID):
		return hmac.new(Encryption.deletionCode, inputID, hashlib.sha512).hexdigest()[:20]
	
	@staticmethod
	def getEncryptedIDForRequesterError(inputID):
		return hmac.new(Encryption.errorRequesterCode, inputID, hashlib.sha512).hexdigest()[:20]
	
	@staticmethod
	def getEncryptedIDForRequestedError(inputID):
		return hmac.new(Encryption.errorRequestedCode, inputID, hashlib.sha512).hexdigest()[:20]
