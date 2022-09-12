import struct

# TODO: Not implemented yet, need to implement
#		the different DataBlocks.
#
#		Currently only supports the TerminalBlock,
#		which indicates the end of the the ExtraData
#		structure.

class FileDataBlock():
	""" Source: 010editor LNK template """

	# MFT File Reference struct?
	FILE_REFERENCE = 0x4B00000000006C57
	SIGNATURE      = 0xBEEF0004

	def __init__(self, fname):
		self.Size = 0x0000			# Short
		self.Version = 0x0009		# Short
		self.Signature = self.SIGNATURE
		self.Created = 0
		self.Accessed = 0
		self.Identifier = 0x002E	# Short

		self.Unknown0 = 0			# Short
		self.FileReference = 0		# Long
		self.Unknown1 = 0			# Long
		self.LongStringSize = 0		# Short
		self.Unknown2 = 0
		self.Unknown3 = 0
		self.Name = fname.encode('utf-16-le')	# wstring

		self.VersionOffset = 0x14

	def build(self):
		bs = b''
		bs += struct.pack('<HHIIIHHQQHII',
				self.Size,
				self.Version,
				self.Signature,
				self.Created,
				self.Accessed,
				self.Identifier,
				self.Unknown0,
				self.FileReference,
				self.Unknown1,
				self.LongStringSize,
				self.Unknown2,
				self.Unknown3)

		bs += self.Name
		bs += struct.pack('<H', self.VersionOffset)

		self.Size = len(bs)
		return bs

	def __bytes__(self):
		if not self.Size:
			self.build()
		return self.build()

class EnvironmentVariableDataBlock():
	SIGNATURE = 0xA0000001
	MAX_LEN   = 259
	def __init__(self, target):
		self.Size = 0
		self.Signature = self.SIGNATURE

		if not type(target) == str:
			raise ValueError('`target` must be type `str`')
		if len(target) > self.MAX_LEN:
			raise ValueError('`target` is too long')
		target = target.ljust(self.MAX_LEN+1, '\x00')
		
		self.TargetANSI = target.encode('ascii')
		self.TargetUnicode = target.encode('utf-16-le')

	def build(self):
		bs = struct.pack('<II',
				self.Size,
				self.Signature) 
		bs += self.TargetANSI
		bs += self.TargetUnicode
		self.Size = len(bs)

		return bs

	def __bytes__(self):
		if not self.Size:
			self.build()
		return self.build()

class ConsoleDataBlock():
	SIGNATURE = 0xA0000002
	def __init__(self):
		self.Size = 0
		self.Signature = self.SIGNATURE
		self.FillAttributes = 0x7			# Short
		self.PopupFillAttributes = 0xF5		# Short
		self.ScreenBufferSizeX = 0x78		# Short
		self.ScreenBufferSizeY = 0x2329		# Short
		self.WindowSizeX	   = 0x78		# Short
		self.WindowSizeY	   = 0x1E		# Short
		self.WindowOriginX     = 0x0		# Short
		self.WindowOriginY	   = 0x0		# Short
		self.Unused0		   = 0x0
		self.Unused1		   = 0x0
		self.FontSize		   = 0x100000
		self.FontFamily		   = 0x36
		self.FontWeight		   = 0x190
		self.FaceName		   = 'Consolas\x00'.ljust(32, '\x00').encode('utf-16-le')
		self.CursorSize		   = 0x19
		self.FullScreen		   = 0x0
		self.QuickEdit		   = 0x1
		self.InsertMode		   = 0x1
		self.AutoPosition      = 0x1
		self.HistoryBufferSize = 0x32
		self.NumberOfHistoryBuffers = 0x4
		self.HistoryNoDup      = 0x0
		self.ColorTable        = [
			0x00000000, 0x00800000, 0x00008000, 0x00808000,
			0x00000080, 0x00800080, 0x00008080, 0x00C0C0C0,
			0x00808080, 0x00FF0000, 0x0000FF00, 0x00FFFF00,
			0x000000FF, 0x00FF00FF, 0x0000FFFF, 0x00FFFFFF
		]

	def build(self):
		bs = struct.pack('<2I8H5I',
				self.Size, self.Signature,
				self.FillAttributes, self.PopupFillAttributes,
				self.ScreenBufferSizeX, self.ScreenBufferSizeY,
				self.WindowSizeX, self.WindowSizeY,
				self.WindowOriginX, self.WindowOriginY,
				self.Unused0, self.Unused1,
				self.FontSize, self.FontFamily, self.FontWeight)
		# TODO: Seems to be more to this struct than just face name
		bs += self.FaceName
		bs += struct.pack('<8I',
				self.CursorSize,
				self.FullScreen,
				self.QuickEdit,
				self.InsertMode,
				self.AutoPosition,
				self.HistoryBufferSize,
				self.NumberOfHistoryBuffers,
				self.HistoryNoDup)

		for c in self.ColorTable:
			bs += struct.pack('<I', c)

		self.Size = len(bs)
		return bs

	def __bytes__(self):
		if not self.Size:
			self.build()
		return self.build()


class ExtraData():
	""" ExtraData refers to a set of structures that convey
		additional information about a link target. These
		optional structes can be present in an extra data
		section that is appended to the basic 
		Shell Link Binary File Format. """

	def __init__(self):
		self.DataBlocks = []

	def __bytes__(self):
		bs = b''
		for db in self.DataBlocks:
			bs += bytes(db)

		return bs + struct.pack('<I',0x0) # Terminal Block
