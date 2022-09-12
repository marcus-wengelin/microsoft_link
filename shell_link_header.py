import struct
import os

from filetime import FileTime
from bitflags import BitFlags

class ShellLinkHeader():
	""" Contains identification information, timestamps, and flags
		that specify the presence of optional structures like
		LinkTargetIDList, LinkInfo and StringData
	"""

	# LNK Class identifier, must be the following
	CLSID = [1, 20, 2, 0, 0, 0, 0, 0, 192, 0, 0, 0, 0, 0, 0, 70] 

	def __init__(self):
		self.HeaderSize = 0x4C			# Must be 0x0000004C
		self.LinkCLSID  = bytes(self.CLSID)
		self.LinkFlags  = BitFlags([
			'HasLinkTargetIDList',
			'HasLinkInfo',
			'HasName',
			'HasRelativePath',
			'HasWorkingDir',
			'HasArguments',
			'HasIconLocation',
			'IsUnicode',
			'ForceNoLinkInfo',
			'HasExpString',
			'RunInSeparateProcess',
			'Unused1',
			'HasDawinID',
			'RunAsUser',					# <- Run as what user?
			'HasExpIcon',
			'NoPidlAlias',
			'Unused2',
			'RunWithShimLayer',
			'ForceNoLinkTrack',
			'EnableTargetMetadata',
			'DisableLinkPathTracking',
			'DisableKnownFolderTracking',
			'DisableKnownFolderAlias',
			'AllowLinkToLink',
			'UnaliasOnSave',
			'PreferEnvironmentPath',
			'KeepLocalIDListForUNCTarget'])
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
		])

		self.CreationTime = FileTime(0,0)
		self.AccessTime   = FileTime(0,0)
		self.WriteTime    = FileTime(0,0)
		self.FileSize	  = 0
		self.IconIndex    = 0
		self.ShowCommand  = 0
		self.HotKey		  = bytes(2)
		self.Reserved1	  = bytes(2)
		self.Reserved2	  = 0
		self.Reserved3    = 0

	def __bytes__(self):
		bs = struct.pack('<I', self.HeaderSize)
		bs += self.LinkCLSID
		bs += bytes(self.LinkFlags)
		bs += bytes(self.FileAttributes)
		bs += bytes(self.CreationTime)
		bs += bytes(self.AccessTime)
		bs += bytes(self.WriteTime)
		bs += struct.pack('<III',
				self.FileSize, self.IconIndex, self.ShowCommand)
		bs += self.HotKey
		bs += self.Reserved1
		bs += struct.pack('<II', self.Reserved2, self.Reserved3)

		return bs
