#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import SERIALIZATION_TYPE, SERIALIZATION_FILE_TYPE, USE_ZLIB


if SERIALIZATION_TYPE == 'json':
	from json import loads as mloads, dumps as mdumps

elif SERIALIZATION_TYPE == 'marshal':
	from marshal import loads as mloads, dumps as mdumps
else:
	raise RuntimeError('Invalid SERIALIZATION_TYPE', SERIALIZATION_TYPE)


if USE_ZLIB:
	from zlib import compress, decompress
	loads = lambda source: mloads(decompress(source))
	dumps = lambda data: compress(mdumps(data))

else:
	loads = lambda source: mloads(source)
	dumps = lambda data: mdumps(data)


def load(filename):
	with open(filename,'rb') as source_file:
		source = source_file.read()
	source = str(source)
	return loads(source)

def dump(data, filename):
	source = dumps(data)

	with open(filename,'wb') as source_file:
		source_file.write(source)