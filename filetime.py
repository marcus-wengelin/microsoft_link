import struct

class FileTime():
	def __init__(self, lowDateTime, highDateTime):
		self.dwLowDateTime = lowDateTime
		self.dwHighDateTime = highDateTime

	def __bytes__(self):
		return struct.pack('<II', self.dwLowDateTime, self.dwHighDateTime)
