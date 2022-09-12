import struct

from constants import MAX_SHORT

class StringData():
	""" Represents a StringData object 
	STRING_DATA = [NAME_STRING] [RELATIVE_PATH] [WORKING_DIR]
				  [COMMAND_LINE_ARGUMENTS] [ICON_LOCATION]

	Each field is present if the corresponding
	flag is set in the ShellLinkHeader	
	"""
	def __init__(self, s):
		if len(s) > MAX_SHORT:
			raise ValueError('`String` can not be longer than 0xffff')

		if type(s) != str:
			raise ValueError('`s` must be of type str!')

		if not s.endswith('\x00'):
			s += '\x00'

		self.CountCharacters = len(s) # 2 times length for wchar_t
		self.String = s.encode('utf-16-le')

	def __bytes__(self):
		return (struct.pack('<H', self.CountCharacters) +
			    self.String)

