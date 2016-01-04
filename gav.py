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
