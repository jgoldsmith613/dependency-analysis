import sys
import urllib2
import xml.etree.ElementTree as ET

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
		release = versioning.find('release')
		if release is None:
			versions = versioning.find('versions').findall('version')
			largest = findLargest(versions)
			return largest
		else: 
			return release.text	
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
	return 'true'

f = open('tempFile', 'r')
w = open('output.csv', 'w')
w.write('group,artifact,included version,latest maven central,latest red hat provided,latest fusesource provided\n')
for line in f:
        gav = makeGAV(line[line.rfind(' ')+1:])
	if sys.argv[1] not in gav.group:
		line = gav.group + ',' + gav.artifact + ',' + gav.version
		line += ',' + getMavenMetaData(gav, 'http://central.maven.org/maven2/')
		line += ',' + getMavenMetaData(gav, 'https://maven.repository.redhat.com/ga/')
		line += ',' + getMavenMetaData(gav, 'https://repo.fusesource.com/nexus/content/groups/public/')
		w.write(line + '\n')
print "Done"
