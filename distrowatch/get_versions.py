import json

from distro import *

def get_libs():
	''' Get all the library from requirements.txt
	'''
	f = open('requirements.txt')
	lines = f.readlines()

	libs = {}
	for line in lines:
		if "==" in line and line[0] != '#':
			lib = line.split('==')
			libs[lib[0]] = lib[1]
	return libs

def get_versions(lib, version):
	''' Given a library and its version, check for the latest version.
	    Returns all versions of the library available. If there is an error,
	    an empty list is returned.
	'''
	req = InstallRequirement.from_line(lib, None)
	finder = MyPackageFinder([], ['http://pypi.python.org/simple/'])
	try:
		versions = finder.find_requirement(req, False)
	except:
		versions = []
	return versions

def check_lib(current, latest):
	current = current.strip().split('.')
	latest = latest.split('.')
	if current[0] < latest[0]:
		return "major"
	if current[1] < latest[1]:
		return "minor"
	if len(latest) > 2:
		if len(current) > 2:
			if current[2] < latest[2]:
				return "bug"
			else:
				return "none"
		elif latest[2] != "0":
			return "bug"
	return "none"

def create_json(distros):
	f = open("distros.json", "w")
	json.dump(distros, f, indent=4)
	f.close()

def main():
	libs = get_libs()
	counter = 0		# I get impatient.
	distros = {'none': [],
		   'bug': [],
       		   'minor': [],
     		   'major': [],
		   'error': []}

	for lib, version in libs.items():
		version = version.strip()
		versions = get_versions(lib, version)
		print lib
		print "\t",
		if versions:
			change = check_lib(version, versions[0][1])
			print "{change}: {current} ==> {latest}".format(
				change=change.title(),
				current=version,
				latest=versions[0][1])
			distros[change].append(lib)
		if not versions:
			print "Sorry, there was a problem."
			distros['error'].append(lib)
		counter += 1
		if counter > 20:
			#break
			pass
	print distros
	create_json(distros)

if __name__ == '__main__':
	main()
