import sys
import urllib2
import xml.etree.ElementTree as ET
import re

class GAV:
        group = ""
        artifact = ""
        version = ""

        def __init__(self, group, artifact, version):
                self.group = group
                self.artifact = artifact
                self.version = version


def makeGAV( str ):
	list = str.split(':')
	return GAV(list[0], list[1], list[3])

def getMavenMetaData(gav, baseUrl):
	group = gav.group.replace('.', '/')
	artifact = gav.artifact

	try:
		url = baseUrl + group + '/' + artifact + '/maven-metadata.xml'
		metadata = urllib2.urlopen(url).read()
		root = ET.fromstring(metadata)
		versioning = root.find('versioning')
	       	#latest = versioning.find('latest')
		#if latest is None or not isUsable(latest.text):
		versions = versioning.find('versions').findall('version')
		print gav.group + ":" + gav.artifact
		largest = findLargest(versions)
		return largest
		#else: 
		#	return latest.text	
	except urllib2.HTTPError, e:
		#No Maven Meta data seeing if artifact exists
		try:
			url = baseUrl + group + '/' + artifact 
                	urllib2.urlopen(url).read()
			#for some reason in the fust repo there is a sha1 and a md5 the maven-metatdata.xml but no content, so checking if this is true
			try:
				if urllib2.urlopen(url + '/maven-metadata.xml.sha1').getcode() != 404:
					return "not available - fuse"
			except urllib2.HTTPError, e:
				return "no metadata provided - please manually check repo"
			return "no metadata provided - please manually check repo"
		except urllib2.HTTPError, e:
			return "not available"

def findLargest(versions):
	max = "0.0.0"
	for versionRoot in versions:
		version = versionRoot.text
		if(isHigher(version, max)):
			max = version
	return max

def isHigher(version, max):
	#For not it seems last result is always the highest, but should not rely on this assumption
	if(isUsable(version)):
		versionSplit = getSplit(version)
		maxSplit = getSplit(max)
		if int(versionSplit[0]) > int(maxSplit[0]):
			return 'true'
		if int(maxSplit[0]) > int(versionSplit[0]):
			return None
		if(len(versionSplit) == 1 and len(maxSplit) ==1):
			return postfix(version) > postfix(max)
		if(len(versionSplit) == 1 and len(maxSplit) > 1):
			return None
		if(len(versionSplit) > 1 and len(maxSplit) == 1):
			return 'true'
		if int(versionSplit[1]) > int(maxSplit[1]):
                        return 'true'
                if int(maxSplit[1]) > int(versionSplit[1]):
                        return None 
		if len(versionSplit) > len(maxSplit):
			return 'true'
		if len(maxSplit) > len(versionSplit):
			return None
		if len(versionSplit) < 3 :
			return postfix(version) > postfix(max)
		if int(versionSplit[2]) > int(maxSplit[2]):
                        return 'true'
                if int(maxSplit[2]) > int(versionSplit[2]):
                        return None
		return postfix(version) > postfix(max)
	return None

def postfix( version ):
	postfix = re.sub('.*?([0-9]*)$',r'\1',version)
	if postfix:
		return int(postfix)
	return 0 

def getSplit(version):
	versionList = list()
	first = version.split('.', 1)
	versionList.append(strip(first[0]))
	if len(first) > 1:
		if '.' in first[1]:
			second = first[1].split('.', 1)
	       		versionList.append(second[0])
			incremental = strip(second[1])
                	if(incremental):
				versionList.append(incremental)
		else:
			minor = strip(first[1])
			if minor:
				versionList.append(minor)
	print versionList
	return versionList

def strip( str ):
	index = 0
	for c in str:
		if c.isdigit():
			index+=1
		else:
			break
	return str[:index]

def isUsable( str ):
	modified = str.replace('.', '')
	end = str[str.rfind('.')+1:]
	start = str[:str.find('.')]
	if (end.isdigit() and int(end) > 100 ) or (start.isdigit() and int(start)> 100):
		return None
        return modified.isdigit() or str.lower().find('redhat') != -1 or str.lower().endswith(('final','ga','release')) or re.search('[a-zA-Z]', str) is None


f = open('real', 'r')
w = open('output.csv', 'w')
w.write('group,artifact,included version,latest maven central,latest red hat provided,latest fusesource provided\n')
for line in f:
        gav = makeGAV(line[line.rfind(' ')+1:])
	isSkipped = None
	iterSkips = iter(sys.argv)
	next(iterSkips)
	for skip in iterSkips:
		isSkipped = isSkipped or skip in gav.group
	if not isSkipped:
		line = gav.group + ',' + gav.artifact + ',' + gav.version
		print line
		line += ',' + getMavenMetaData(gav, 'http://central.maven.org/maven2/')
		line += ',' + getMavenMetaData(gav, 'https://maven.repository.redhat.com/ga/')
		line += ',' + getMavenMetaData(gav, 'https://repo.fusesource.com/nexus/content/groups/public/')
		w.write(line + '\n')
print "Done"
