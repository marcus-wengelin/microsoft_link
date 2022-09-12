import struct

class BitFlags():
	""" A class representing a BitFlags object
		Stored as a 32-bit le integer
		Field names represent bits 0-32
	"""

	def __init__(self, field_names, storage_size=32):
		self.storage_size = storage_size
		if self.storage_size == 8:
			self.fmts = 'B' # unsigned byte
		elif self.storage_size == 16:
			self.fmts = 'H' # unsigned short
		elif self.storage_size == 32:
			self.fmts = 'I'	# unsigned int
		elif self.storage_size == 64: 
			self.fmts = 'Q'	# unsigned long long
		else:
			raise ValueError(f'Invalid storage size ({self.storage_size})')

		self.size = len(field_names)
		if self.size > self.storage_size:
			raise ValueError('Number of fields in flag may not exceed storage size')

		for fn in field_names:
			if field_names.count(fn) > 1:
				raise ValueError(f'Field {fn} occurs more than once!')

		self.field_names = field_names
		self.field_states = [0 for _ in range(self.size)]

	def __bytes__(self):
		for s in self.field_states:
			if s > 1 or s < 0:
				raise ValueError('Invalid bit state')

		bits = ''.join(
			[str(s) for s in self.field_states][::-1]
		).rjust(self.storage_size, '0')

		return struct.pack('<'+self.fmts, int(bits,2))

	def get(self, field_name):
		i = 0
		for fn in self.field_names:
			if field_name == fn:
				return self.field_states[i]
			i += 1
		raise ValueError(f'Field {field_name} does not exist')

	def set(self, field_name, state):
		if state < 0 or state > 1:
			raise ValueError(f'State can only be 0 or 1')

		i = 0
		for fn in self.field_names:
			if field_name == fn:
				self.field_states[i] = state
				return
			i += 1
		raise ValueError(f'Field {field_name} does not exist')
