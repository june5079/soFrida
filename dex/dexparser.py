"""
@author : bunseokbot@BoB
@description : DEX File parser?.. in BoB Advanced Project
@contact : admin@smishing.kr
"""

import mmap
import struct
import dex.disassembler as disassembler

class Dexparser:

	def __init__(self, filedir):
		f = open(filedir, 'rb')
		m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

		self.mmap = m

		magic           = m[0:8]
		checksum        = struct.unpack('<L', m[8:0xC])[0]
		signiture       = m[0xC:0x20]
		file_size       = struct.unpack('<L', m[0x20:0x24])[0]
		header_size     = struct.unpack('<L', m[0x24:0x28])[0]
		endian_tag      = struct.unpack('<L', m[0x28:0x2C])[0]
		link_size       = struct.unpack('<L', m[0x2C:0x30])[0]
		link_off        = struct.unpack('<L', m[0x30:0x34])[0]
		map_off         = struct.unpack('<L', m[0x34:0x38])[0]
		string_ids_size = struct.unpack('<L', m[0x38:0x3C])[0]		
		string_ids_off  = struct.unpack('<L', m[0x3C:0x40])[0]
		type_ids_size   = struct.unpack('<L', m[0x40:0x44])[0]
		type_ids_off    = struct.unpack('<L', m[0x44:0x48])[0]
		proto_ids_size  = struct.unpack('<L', m[0x48:0x4C])[0]
		proto_ids_off   = struct.unpack('<L', m[0x4C:0x50])[0]
		field_ids_size  = struct.unpack('<L', m[0x50:0x54])[0]
		field_ids_off   = struct.unpack('<L', m[0x54:0x58])[0]
		method_ids_size = struct.unpack('<L', m[0x58:0x5C])[0]
		method_ids_off  = struct.unpack('<L', m[0x5C:0x60])[0]
		class_defs_size = struct.unpack('<L', m[0x60:0x64])[0]
		class_defs_off  = struct.unpack('<L', m[0x64:0x68])[0]
		data_size       = struct.unpack('<L', m[0x68:0x6C])[0]
		data_off		= struct.unpack('<L', m[0x6C:0x70])[0]

		header_data = {}
		
		header_data['magic'          ] = magic
		header_data['checksum'       ] = checksum
		header_data['signiture'      ] = signiture
		header_data['file_size'      ] = file_size
		header_data['header_size'    ] = header_size
		header_data['endian_tag'     ] = endian_tag
		header_data['link_size'      ] = link_size
		header_data['link_off'       ] = link_off
		header_data['map_off'        ] = map_off
		header_data['string_ids_size'] = string_ids_size
		header_data['string_ids_off' ] = string_ids_off
		header_data['type_ids_size'  ] = type_ids_size
		header_data['type_ids_off'   ] = type_ids_off
		header_data['proto_ids_size' ] = proto_ids_size
		header_data['proto_ids_off'  ] = proto_ids_off
		header_data['field_ids_size' ] = field_ids_size
		header_data['field_ids_off'  ] = field_ids_off
		header_data['method_ids_size'] = method_ids_size
		header_data['method_ids_off' ] = method_ids_off
		header_data['class_defs_size'] = class_defs_size
		header_data['class_defs_off' ] = class_defs_off
		header_data['data_size'      ] = data_size
		header_data['data_off'       ] = data_off
		
		self.header = header_data

	def mmapdata(self):
		return self.mmap

	def header_info(self):
		return self.header

	def checksum(self):
		return "%x" %self.header['checksum']

	def string_list(self):
		string_data = []

		string_ids_size = self.header['string_ids_size']
		string_ids_off  = self.header['string_ids_off']

		for i in range(string_ids_size):
			off = struct.unpack('<L', self.mmap[string_ids_off + (i*4) : string_ids_off + (i*4) + 4 ])[0]
			c_size = self.mmap[off]
			c_char = self.mmap[off+1:off+1+c_size]
			string_data.append(c_char)

		self.string_data = string_data #for method_id_list
		return string_data


	def typeid_list(self):
		type_data = []
		type_ids_size = self.header['type_ids_size']
		type_ids_off  = self.header['type_ids_off']

		for i in range(type_ids_size):
			idx = struct.unpack('<L', self.mmap[type_ids_off + (i*4) : type_ids_off + (i*4) + 4])[0]
			type_data.append(idx)

		self.type_data = type_data
		return type_data

	def method_list(self):
		method_data = []

		method_ids_size = self.header['method_ids_size']
		method_ids_off  = self.header['method_ids_off']

		for i in range(method_ids_size):
			class_idx = struct.unpack('<H', self.mmap[method_ids_off+(i*8)  :method_ids_off+(i*8)+2])[0]
			proto_idx = struct.unpack('<H', self.mmap[method_ids_off+(i*8)+2:method_ids_off+(i*8)+4])[0]
			name_idx  = struct.unpack('<L', self.mmap[method_ids_off+(i*8)+4:method_ids_off+(i*8)+8])[0]
			method_data.append([class_idx, proto_idx, name_idx])

		return method_data

	def protoids_list(self):
		protoids_data = []

		proto_ids_off = self.header['proto_ids_off']
		proto_ids_size = self.header['proto_ids_size']

		for i in range(proto_ids_size):
			shorty_idx      = struct.unpack('<L', self.mmap[proto_ids_off+(i*12)  :proto_ids_off+(i*12)+ 4])[0]
			return_type_idx = struct.unpack('<L', self.mmap[proto_ids_off+(i*12)+4:proto_ids_off+(i*12)+ 8])[0]
			param_off       = struct.unpack('<L', self.mmap[proto_ids_off+(i*12)+8:proto_ids_off+(i*12)+12])[0]
			protoids_data.append([shorty_idx, return_type_idx, param_off])

		return protoids_data

	def fieldids_list(self):
		fieldids_data = []

		field_ids_off = self.header['field_ids_off']
		field_ids_size = self.header['field_ids_size']

		for i in range(field_ids_size):
			class_idx = struct.unpack('<H', self.mmap[field_ids_off+(i*8)  :field_ids_off+(i*8)+2])[0]
			type_idx  = struct.unpack('<H', self.mmap[field_ids_off+(i*8)+2:field_ids_off+(i*8)+4])[0]
			name_idx  = struct.unpack('<L', self.mmap[field_ids_off+(i*8)+4:field_ids_off+(i*8)+8])[0]
			fieldids_data.append([class_idx, type_idx, name_idx])

		return fieldids_data

	def classdef_list(self):
		classdef_data = []
		class_defs_off = self.header['class_defs_off']
		class_defs_size = self.header['class_defs_size']

		for i in range(class_defs_size):
			class_idx 			= struct.unpack('<L', self.mmap[class_defs_off+(i*32)   :class_defs_off+(i*32)+4])[0]
			access_flag 		= struct.unpack('<L', self.mmap[class_defs_off+(i*32)+4 :class_defs_off+(i*32)+8])[0]
			superclass_idx 		= struct.unpack('<L', self.mmap[class_defs_off+(i*32)+8 :class_defs_off+(i*32)+12])[0]
			interfaces_off 		= struct.unpack('<L', self.mmap[class_defs_off+(i*32)+12:class_defs_off+(i*32)+16])[0]
			source_file_idx 	= struct.unpack('<L', self.mmap[class_defs_off+(i*32)+16:class_defs_off+(i*32)+20])[0]
			annotation_off 		= struct.unpack('<L', self.mmap[class_defs_off+(i*32)+20:class_defs_off+(i*32)+24])[0]
			class_data_off 		= struct.unpack('<L', self.mmap[class_defs_off+(i*32)+24:class_defs_off+(i*32)+28])[0]
			static_values_off 	= struct.unpack('<L', self.mmap[class_defs_off+(i*32)+28:class_defs_off+(i*32)+32])[0]
			sorted_access = [i for i in disassembler.ACCESS_ORDER if i & access_flag]
			classdef_data.append([class_idx, [disassembler.access_flag_classes[flag] for flag in sorted_access], superclass_idx, interfaces_off, source_file_idx, annotation_off, class_data_off, static_values_off])

		return classdef_data

	def classdata_list(self, offset):
		static_field_list = []
		instance_field_list = []
		direct_method_list = []
		virtual_method_list = []

		static_fields, sf_size = uleb128_value(self.mmap, offset)
		offset += sf_size 
		instance_fields, if_size = uleb128_value(self.mmap, offset)
		offset += if_size
		direct_methods, dm_size = uleb128_value(self.mmap, offset)
		offset += dm_size
		virtual_methods, vm_size = uleb128_value(self.mmap, offset)
		offset += vm_size
		
		for i in range(static_fields):
			field_idx_diff, access_flags, size = encoded_field(self.mmap, offset)
			if i == 0:
				diff = field_idx_diff
			else:
				diff += field_idx_diff

			static_field_list.append([diff, access_flags])
			offset += size

		#print static_field_list

		for i in range(instance_fields):
			field_idx_diff, access_flags, size = encoded_field(self.mmap, offset)
			if i == 0:
				diff = field_idx_diff
			else:
				diff += field_idx_diff

			instance_field_list.append([diff, access_flags])
			offset += size
		#print instance_field_list


		for i in range(direct_methods):
			method_idx_diff, access_flags, code_off, size = encoded_method(self.mmap, offset)
			if i == 0:
				diff = method_idx_diff
			else:
				diff += method_idx_diff

			direct_method_list.append([diff, access_flags, code_off])
			offset += size
		#print direct_method_list

		for i in range(virtual_methods):
			method_idx_diff, access_flags, code_off, size = encoded_method(self.mmap, offset)
			if i == 0:
				diff = method_idx_diff
			else:
				diff += method_idx_diff

			virtual_method_list.append([diff, access_flags, code_off])
			offset += size
		#print virtual_method_list

		return [static_field_list, instance_field_list, direct_method_list, virtual_method_list]

	def annotation_list(self, offset):
		#annotation_data = []
		class_annotation_off = struct.unpack('<L', self.mmap[offset	:offset+4])[0]
		class_annotation_size = struct.unpack('<L', self.mmap[class_annotation_off:class_annotation_off+4])[0]
		annotation_off_item = struct.unpack('<L', self.mmap[class_annotation_off+4: class_annotation_off+8])[0]
		visibility = (self.mmap[annotation_off_item : annotation_off_item + 1])
		annotation = (self.mmap[annotation_off_item + 1 : annotation_off_item + 8])
		annotation_data = encoded_annotation(self.mmap, annotation_off_item + 1)
		type_idx_diff, size_diff, name_idx_diff, value_type, encoded_value = annotation_data
		#print annotation_element

		"""
		for i in range(0, class_annotation_size):
			#annotation_item = struct.unpack('<L', self.mmap[annotation_off_item+(i*4) : annotation_off_item+(i*4) + 4])[0]

			#visibility = struct.unpack('<B', self.mmap[annotation_off_item+(i*4) + 4 : annotation_off_item+(i*4) + 5])[0]
			#print hex(visibility)
			#annotation_item = struct.unpack('<Q', self.mmap[annotation_off_item+(i*4) : annotation_off_item+(i*4) + 8])[0]
			print (self.mmap[annotation_off_item+(i*4) : annotation_off_item+(i*4) + 4]).encode("hex")
			#print hex(annotation_item)

			#print annotation_off_item + (i*4) , ":" ,annotation_off_item + (i*4) + 4
		"""

		return [ord(visibility),  type_idx_diff, size_diff, name_idx_diff, ord(value_type), ord(encoded_value)]

	def virtualmethod_data(self, offset):
		print(hex(offset))

	def __del__(self):
		pass


#uleb128 decoder!
def uleb128_value(m, off): 
	size = 1
	result = ord(m[off+0])
	if result > 0x7f :
		cur = ord(m[off+1])
		result = (result & 0x7f) | ((cur & 0x7f) << 7)
		size += 1
		if cur > 0x7f :
			cur = ord(m[off+2])
			result |= ((cur & 0x7f) << 14) 
			size += 1
			if cur > 0x7f :
				cur = ord(m[off+3])
				result |= ((cur & 0x7f) << 21) 
				size += 1
				if cur > 0x7f :
					cur = ord(m[off+4])
					result |= (cur << 28)
					size += 1
	return result, size

def encoded_field(mmap, offset):
	myoff = offset

	field_idx_diff, size = uleb128_value(mmap, myoff)
	myoff += size
	access_flags, size = uleb128_value(mmap, myoff)
	myoff += size

	size = myoff - offset

	return [field_idx_diff, access_flags, size]

def encoded_method(mmap, offset):
	myoff = offset

	method_idx_diff, size = uleb128_value(mmap, myoff)
	myoff += size
	access_flags, size = uleb128_value(mmap, myoff)
	myoff += size
	code_off, size = uleb128_value(mmap, myoff)
	myoff += size

	size = myoff - offset

	return [method_idx_diff, access_flags, code_off, size]

def encoded_annotation(mmap, offset):
	myoff = offset

	type_idx_diff, size = uleb128_value(mmap, myoff)
	#print hex(type_idx_diff), size
	myoff += size
	size_diff, size = uleb128_value(mmap, myoff)
	#print hex(size_diff), size
	myoff += size
	name_idx_diff, size = uleb128_value(mmap, myoff)
	#print hex(name_idx_diff)
	myoff += size
	value_type = mmap[myoff:myoff+1]
	encoded_value = mmap[myoff+1:myoff+2]

	return [type_idx_diff, size_diff, name_idx_diff, value_type, encoded_value]


	#annotation_element = 



