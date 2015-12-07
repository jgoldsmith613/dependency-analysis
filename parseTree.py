import gav
import sys
import getopt

def parseOpts():
	opts, args = getopt.getopt(sys.argv[1:], "i:o:s:", ["inputFile=","outputFile=", "skip="])
	return opts, args	


opts, args = parseOpts()
outputFile = "deafult_output.csv"
inputFile = "default_input"
skips = []
for opt, val in opts:
	if opt in ("-o", "--outputFile"):
		outputFile = val
	if opt in ("-i", "--inputFile"):
		inputFile = val
	if opt in ("-s", "--skip"):
		skips = val.split(",")
	
	
f = open(inputFile, 'r')
w = open(outputFile, 'w')
for line in f:
        gavToProcess = gav.makeGAV(line[line.rfind(' ')+1:])
        isSkipped = None
        for skip in skips:
                isSkipped = isSkipped or skip in gavToProcess.group
        if not isSkipped:
                line = gavToProcess.group + ',' + gavToProcess.artifact + ',' + gavToProcess.version
                print line
        	w.write(line + '\n')
print "Done"
