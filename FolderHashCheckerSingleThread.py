def set_procname(newname):
	newname = newname.encode("utf-8")
	from ctypes import cdll, byref, create_string_buffer
	libc = cdll.LoadLibrary('libc.so.6')    #Loading a 3rd party library C
	buff = create_string_buffer(len(newname)+1) #Note: One larger than the name (man prctl says that)
	buff.value = newname                 #Null terminated string as it should be
	libc.prctl(15, byref(buff), 0, 0, 0) #Refer to "#define" of "/usr/include/linux/prctl.h" for the misterious value 16 & arg[3..5] are zero as the man page says.
set_procname("FolderHashCheck")

import argparse
import hashlib
import os

parser = argparse.ArgumentParser()
parser.add_argument("original", default=None, help="Where to look.")
parser.add_argument("copied", default=None, help="Where to look for "
	"the second folder to check against.")
parser.add_argument("--chunk", "-c", type=int, default=4096, help="How big should the chunks be?")
parser.add_argument("--verbose", "-v", action="count", default=0)

failedChecks=[]


def run():
	#Root current dir, dirs folders in root, files files in root
	for root, dirs, files in os.walk(path):
		for name in files:
			if verbose >= 1:
				print("Checking file {}".format(name))
			checksum = hashlib.sha256()
			backupCheckSum = hashlib.sha256()
			notFound = False
			try:
				if verbose >= 2:
					print("Opening {} on Source".format(name))
				f = open("{}/{}".format(root, name), "rb")
				while True:
					chunk = f.read(chunkSize)
					if not chunk:
						break
					checksum.update(chunk)
			except FileNotFoundError:
				print("{} was not found through magic!".format(name))
				failedChecks.append("{} (Not found in Origin)".format(name))
				notFound = True
			try:
				if verbose >= 2:
					print("Opening {} on Destination".format(name))
				f = open("{}/{}".format(root.replace(path, backup), name), "rb")
				while True:
					chunk = f.read(chunkSize)
					if not chunk:
						break
					backupCheckSum.update(chunk)
			except FileNotFoundError:
				print("{} was not found!".format(name))
				failedChecks.append("{} (Not found in backup)".format(name))
				notFound = True
			if not notFound:
				if verbose >= 1:
					print("Calculating and Checking the "
						"Hash of {}".format(name))
				if checksum.hexdigest() != backupCheckSum.hexdigest():
					print("{} does not match!")
					failedChecks.append(name)
	if failedChecks == []:
		print("All checkes passed.")
	else:
		print("The follow checks failed:\n{}".format("\n".join(failedChecks)))

parsed = parser.parse_args()
path = parsed.original
backup = parsed.copied
chunkSize = parsed.chunk
verbose = parsed.verbose
if path == None or backup == None:
	print("You forgot to include the souce and destination of the copied files to "
		"check against.")
	parser.print_help()
else:
	run()
