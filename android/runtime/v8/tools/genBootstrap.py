#!/usr/bin/env python
#
# Appcelerator Titanium Mobile
# Copyright (c) 2011-2012 by Appcelerator, Inc. All Rights Reserved.
# Licensed under the terms of the Apache Public License
# Please see the LICENSE included with this distribution for details.
#
# Generates javascript bootstrapping code for Titanium Mobile
#

import os, re, sys, optparse

thisDir = os.path.abspath(os.path.dirname(__file__))
genDir = os.path.join(os.path.dirname(thisDir), "generated")
androidDir = os.path.abspath(os.path.join(thisDir, "..", "..", ".."))
sdkRootDir = os.path.dirname(androidDir)

# For bootstrap.py
sys.path.append(os.path.join(sdkRootDir, "module", "android"))
import bootstrap

# Third-party python modules.
thirdPartyDir = os.path.abspath(os.path.join(androidDir, "..", "thirdparty"))
sys.path.append(thirdPartyDir)

try:
	import json
except:
	import simplejson as json

jsonDir = os.path.abspath(os.path.join(androidDir, "..", "dist", "android", "json"))

if not os.path.exists(genDir):
	os.makedirs(genDir)

def loadBindings():
	bindingPaths = []
	bindings = { "proxies": {}, "modules": {} }
	for module in os.listdir(jsonDir):
		bindingsDir = os.path.join(jsonDir, "org", "appcelerator", "titanium", "bindings")
		for binding in os.listdir(bindingsDir):
			jsonPath = os.path.join(bindingsDir, binding)
			if os.path.exists(jsonPath):
				bindingPaths.append(jsonPath)

	def mergeModules(source, dest):
		for k in source.keys():
			if k not in dest:
				dest[k] = source[k]
			else:
				origEntry = dest[k]
				newEntry = source[k]

				if "apiName" in newEntry and "apiName" not in origEntry:
					origEntry["apiName"] = newEntry["apiName"]

				for listName in ("childModules", "createProxies"):
					if listName in newEntry and listName not in origEntry:
						origEntry[listName] = newEntry[listName]
					elif listName in newEntry:
						origIds = [c["id"] for c in origEntry[listName]]
						newMembers = [c for c in newEntry[listName] if c["id"] not in origIds]
						if newMembers:
							origEntry[listName].extend(newMembers)

	for bindingPath in bindingPaths:
		moduleName = os.path.basename(bindingPath).replace(".json", "")
		binding = json.load(open(bindingPath))
		bindings["proxies"].update(binding["proxies"])
		mergeModules(binding["modules"], bindings["modules"])

	return bindings

def main():
	parser = optparse.OptionParser()
	parser.add_option("-r", "--runtime", dest="runtime", default=None)
	parser.add_option("-o", "--output", dest="output", default=None)

	(options, args) = parser.parse_args()

	if not options.runtime:
		print >>sys.stderr, "Error: --runtime is required"
		sys.exit(1)

	runtime = options.runtime
	bindings = loadBindings()

	b = bootstrap.Bootstrap(runtime, bindings,
		moduleId="titanium", moduleName="Titanium")

	jsTemplate = open(os.path.join(thisDir, "bootstrap.js")).read()
	gperfTemplate = open(os.path.join(thisDir, "bootstrap.gperf")).read()

	outDir = genDir
	if options.output != None:
		outDir = options.output

	b.generateJS(jsTemplate, gperfTemplate, outDir)

if __name__ == "__main__":
	main()

