import struct

from bitflags import BitFlags

class CommonNetworkRelativeLink():
	""" Specifies information about the network location
		where a link target is stored, including the mapped drive
		letter and UNC path prefix """

	def __init__(self, use_opt=False):
		""" :param: use_opt		use optional unicode fields
		"""
		self.CommonNetworkRelativeLinkSize = 0x14 # MUST be >= 0x14
		self.CommonNetworkRelativeLinkFlags = BitFlags([
			'ValidDevice', # If set, DeviceNameOffset field is set
			'ValidNetType'
		])

		self.NetNameOffset = 0
		self.DeviceNameOffset = 0
		self.NetworkProviderType = 0
		self.NetNameOffsetUnicode = 0 			# Optional
		self.DeviceNameOffsetUnicode = 0 		# Optional
		self.NetName = b'net_name'			 	# Variable
		self.DeviceName = b'device_name'		# Variable
		self.NetNameUnicode = b'\x00'		 	# Variable
		self.DeviceNameUnicode = b'\x00'	 	# Variable

		self.use_opt = use_opt

	# Getters/setters for this objects flags
	def set(self, field_name, field_value):
		self.CommonNetworkRelativeLinkFlags.set(field_name, field_value)
	def get(self, field_name):
		return self.CommonNetworkRelativeLinkFlags.get(field_name)

	def build(self):
		bs = struct.pack('<I', self.CommonNetworkRelativeLinkSize)
		bs += bytes(self.CommonNetworkRelativeLinkFlags)

		bs += struct.pack('<III',
				self.NetNameOffset,
				self.DeviceNameOffset,
				self.NetworkProviderType)

		if self.use_opt:
			bs += struct.pack('<II',
					self.NetNameOffsetUnicode,
					self.DeviceNameOffsetUnicode)

		self.NetNameOffset = len(bs)
		bs += self.NetName
		self.DeviceNamOffset = len(bs)
		bs += self.DeviceName

		if self.use_opt:
			self.NetNameOffsetUnicode = len(bs)
			bs += self.NetNameUnicode
			self.DeviceNameOffsetUnicode = len(bs)
			bs += self.DeviceNameUnicode

		self.CommonNetworkRelativeLinkSize = len(bs)

		return bs

	def __bytes__(self):
		if not self.CommonNetworkRelativeLinkSize:
			self.build()
		return self.build()

class VolumeID():
	""" Specifies information about the volume that a link target was on
		when the link was created, for resolving links not found in
		their original location """

	def __init__(self, use_opt=False):
		self.VolumeIDSize = 0 # MUST be > 0x10
		self.DriveType 	  = 0
		self.DriveSerialNumber = 0
		self.VolumeLabelOffset = 0
		self.VolumeLabelOffsetUnicode = 0 # Optional
		self.Data = b'\x00\x00\x00\x00'

		self.use_opt = use_opt

	def build(self):
		bs = struct.pack('<IIII',
			self.VolumeIDSize,
			self.DriveType,
			self.DriveSerialNumber,
			self.VolumeLabelOffset)

		# VolumeLabelOffsetUnicode
		if self.use_opt:
			bs += struct.pack('<I', self.VolumeLabelOffsetUnicode)

		# Data 
		self.VolumeLabelOffset = len(bs)
		if self.use_opt:
			self.VolumeLabelOffsetUnicode = len(bs)
		bs += self.Data

		self.VolumeIDSize = len(bs)

		return bs
	
	def __bytes__(self):
		# Build twice to fill in offsets and size
		if not self.VolumeIDSize:
			self.build()
		return self.build()

class LinkInfo():
	def __init__(self, use_opt=False):
		""" :param: use_opt		Use optional unicode structures
		"""

		# The size of the entire structure
		self.LinkInfoSize = 0
		if use_opt:
			self.LinkInfoHeaderSize = 0x24
		else:
			self.LinkInfoHeaderSize = 0x1C

		self.LinkInfoFlags = BitFlags([
			'VolumeIDAndLocalBasePath',
			'CommonNetworkRelativeLinkAndPathSuffix'])
		self.VolumeIDOffset = 0
		self.LocalBasePathOffset = 0
		self.CommonNetworkRelativeLinkOffset = 0
		self.CommonPathSuffixOffset = 0
		self.LocalBasePathOffsetUnicode = 0   	# Optional
		self.CommonPathSuffixOffsetUnicode = 0	# Optional 
		self.VolumeID = VolumeID(use_opt) 		# Variable, optional
		self.LocalBasePath = b'local_base_path'	# Variable, optional
		# Variable, optional
		self.CommonNetworkRelativeLink = CommonNetworkRelativeLink(use_opt)
		self.CommonPathSuffix = b'common_path_suffix'	# Variable, optional
		self.LocalBasePathUnicode = b''			   		# Variable, optional
		self.CommonPathSuffixUnicode = b''				# Variable, optional

		self.use_opt = use_opt # Use optional unicode fields

	# Getters/Setters for LinkInfoFlags
	def set(self, field_name, field_state):
		self.LinkInfoFlags.set(field_name, field_state)
	def get(self, field_name):
		return self.LinkInfoFlags.get(field_name)

	def build(self):
		bs = struct.pack('<II',
				self.LinkInfoSize,
				self.LinkInfoHeaderSize)

		bs += bytes(self.LinkInfoFlags)

		# VolumeIDOffset
		if self.get('VolumeIDAndLocalBasePath'):
			bs += struct.pack('<I', self.VolumeIDOffset)
		else:
			bs += b'\x00\x00\x00\x00'

		# LocalBasePathOffset
		if self.get('VolumeIDAndLocalBasePath'):
			bs += struct.pack('<I', self.LocalBasePathOffset)
		else:
			bs += b'\x00\x00\x00\x00'

		# CommonNetworkRelativeLinkOffset
		if self.get('CommonNetworkRelativeLinkAndPathSuffix'):
			bs += struct.pack('<I', self.CommonNetworkRelativeLinkOffset)
		else:
			bs += b'\x00\x00\x00\x00'

		# CommonPathSuffixOffset
		bs += struct.pack('<I', self.CommonPathSuffixOffset)

		if self.use_opt:
			# LocalBasePathOffsetUnicode
			if self.get('VolumeIDAndLocalBasePath'):
				bs += struct.pack('<I', self.LocalBasePathOffsetUnicode)
			else:
				bs += b'\x00\x00\x00\x00'

			# CommonPathSuffixOffsetUnicode
			bs += struct.pack('<I', self.CommonPathSuffixUnicode)

		if self.get('VolumeIDAndLocalBasePath'):
			# VolumeID
			self.VolumeIDOffset = len(bs)
			bs += bytes(self.VolumeID)

			# LocalBasePath
			self.LocalBasePathOffset = len(bs)
			bs += self.LocalBasePath

		# CommonNetworkRelativeLink
		if self.get('CommonNetworkRelativeLinkAndPathSuffix'):
			self.CommonNetworkRelativeLinkOffset = len(bs)
			bs += bytes(self.CommonNetworkRelativeLink)

		# CommonPathSuffix
		self.CommonPathSuffixOffset = len(bs)
		bs += self.CommonPathSuffix

		if self.use_opt:
			self.LocalBasePathOffsetUnicode = len(bs)
			bs += self.LocalBasePathUnicode
			self.CommonPathSuffixOffsetUnicode = len(bs)
			bs += self.CommonPathSuffixUnicode

		self.LinkInfoSize = len(bs)
		return bs


	def __bytes__(self):
		# Need to build twice to fill in offsets
		if self.LinkInfoSize == 0:
			self.build()
		return self.build()
