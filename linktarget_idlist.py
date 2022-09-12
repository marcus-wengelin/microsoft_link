import struct

from constants import MAX_SHORT
from filetime import FileTime
from bitflags import BitFlags
from extra_data import FileDataBlock

# No need to prebuild any of these classes,
# no offsets present

class RootShellItem():
	""" Shell item representing the root folder """

	TYPE = 1
	TYPEDATA = 0xF

	def __init__(self, CLSID):
		self.SortIndex = 0x50 # MY_COMPUTER
		self.CLSID     = CLSID

	def __bytes__(self):
		return struct.pack('<B', self.SortIndex) + self.CLSID

class VolumeShellItem():
	""" Shell item representing the target volume """
	TYPE = 2
	TYPEDATA = 0xF

	def __init__(self, volname):
		self.Name = volname.encode('ascii')

	def __bytes__(self):
		return self.Name

class FileShellItem():
	TYPE = 3
	TYPEDATA = 1

	def __init__(self, fname, flags={}):
		self.FileSize = 0
		self.Modified = 0
		self.FileAttributes = BitFlags([
			'FILE_ATTRIBUTE_READONLY',
			'FILE_ATTRIBUTE_HIDDEN',
			'FILE_ATTRIBUTE_SYSTEM',
			'FILE_ATTRIBUTE_VOLUME_LABEL',
			'FILE_ATTRIBUTE_DIRECTORY',
			'FILE_ATTRIBUTE_ARCHIVE',
			'FILE_ATTRIBUTE_NORMAL',
			'FILE_ATTRIBUTE_TEMPORARY',
			'FILE_ATTRIBUTE_SPARSE_FILE',
			'FILE_ATTRIBUTE_REPARSE_POINT',
			'FILE_ATTRIBUTE_COMPRESSED',
			'FILE_ATTRIBUTE_OFFLINE',
			'FILE_ATTRIBUTE_NOT_CONTENT_INDEXED',
			'FILE_ATTRIBUTE_ENCRYPTED',
			'FILE_ATTRIBUTE_INTEGRITY_STREAM',
			'FILE_ATTRIBUTE_VIRTUAL'
		], storage_size=16)

		# Initialize flags
		for k in flags.keys():
			self.set(k, flags[k])

		# Null-termination of PrimaryName necessary?
		self.PrimaryName = fname.encode('ascii')

		# wchar-aligned PrimaryName?
		if len(self.PrimaryName) % 2 == 1:
			self.PrimaryName += b'\x00'

		self.FileDataBlock = FileDataBlock(fname)

	def set(self, field_name, field_state):
		self.FileAttributes.set(field_name, field_state)
	def get(self, field_name):
		return self.FileAttributes.get(field_name)

	def __bytes__(self):
		bs = struct.pack('<xII',
				self.FileSize,
				self.Modified)
		bs += bytes(self.FileAttributes)
		bs += self.PrimaryName
		bs += bytes(self.FileDataBlock)
		return bs
	
class ItemID():
	def __init__(self, Type, TypeData, bs):
		if not type(bs) == bytes:
			raise ValueError("`Data` argument must be of type `bytes`")
		if len(bs) > MAX_SHORT:
			raise ValueError("`Data` argument is too large")

		self.ItemIDSize = 0

		self.TypeData   = TypeData
		self.Type 		= Type
		self.Data       = bs

	def build(self):
		bs = struct.pack('<HB', 
				self.ItemIDSize,
				self.TypeData | self.Type << 4)
		bs += self.Data

		self.ItemIDSize = len(bs)
		return bs

	def __bytes__(self):
		if not self.ItemIDSize:
			self.build()
		return self.build()

class IDList():
	def __init__(self):
		self.ItemIDList = [] 		# An array of zero or more ItemID structures
		self.TerminalID = bytes(2)	# Must be zero

	def __bytes__(self):
		bs = b''
		for itemId in self.ItemIDList:
			bs += bytes(itemId)
		return bs + self.TerminalID

class LinkTargetIDList():
	def __init__(self):
		self.IDListSize = 0 # short
		self.IDList     = IDList()

	def add(self, Type, TypeData, bs):
		""" Adds an item to this list (raw bytes)"""
		self.IDList.ItemIDList.append(ItemID(Type, TypeData, bs))
		self.IDListSize = len(bytes(self.IDList))

	def add_payload(self, shitem):
		""" Adds a ShellItem object to this list """
		self.IDList.ItemIDList.append(
			ItemID(shitem.TYPE, shitem.TYPEDATA, bytes(shitem)))
		self.IDListSize = len(bytes(self.IDList))

	def __bytes__(self):
		return struct.pack('<H', self.IDListSize) + bytes(self.IDList)
