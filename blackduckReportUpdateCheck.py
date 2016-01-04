import requests, json, time, datetime, smtplib
from email.mime.text import MIMEText

def sendNotificationEmail(msgText):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("redhat.jpmc.pilot", "redhat123")
	msg = MIMEText(msgText)
	msg['Subject'] = "Vulnerability update notification"
        server.sendmail("redhat.jpmc.pilot@gmail.com", "jgoldsmith@redhat.com", msg.as_string())
        server.quit()


authenticationUrl="http://10.3.10.47:8080/j_spring_security_check"

reportsUrl = 'http://10.3.10.47:8080/api/vulnerability-update-reports'
projectUrl = 'http://10.3.10.47:8080/api/projects/%s'


credentials = {'j_username':'sysadmin', 'j_password':'blackduck'}

#make start and stop dates
#endDate = str(datetime.date.today()) + 'T04:59:59.000Z'
#startDate = str(datetime.date.today() - datetime.date.resolution) + 'T05:00:00.000Z' 

#To ENable Testting Day of
endDate = str(datetime.date.today() + datetime.date.resolution) + 'T04:59:59.000Z'
startDate = str(datetime.date.today()) + 'T05:00:00.000Z'



payload = json.dumps({"endDate": endDate,"startDate": startDate})

session = requests.Session()

authResponse = session.post(authenticationUrl, data=credentials)

createReportsResponse = session.post(reportsUrl, data=payload, headers={'Content-Type': 'application/json'})
print createReportsResponse
reportsJson = json.loads(session.get(createReportsResponse.headers["location"]).text)

def makeEmailMessage(fileContent):
	projectSet = set()
	for voln in fileContent["newVulnerabilities"]:
		projectSet.add(voln["versionSummary"]["projectId"])
	for voln in fileContent["updatedVulnerabilities"]:
                projectSet.add(voln["versionSummary"]["projectId"])
	updatedCount = fileContent["numberOfUpdatedVulnerabilities"]
	newCount = fileContent["numberOfNewVulnerabilities"]
	msg = "Please check the following projects in Blackduck Hub. There are %s new vulnerablities and %s updated vulnerabilities in the past 24 hours.\n\n" % (newCount, updatedCount)
	msg += "Projects:\n"
	for projectId in projectSet:
		project = json.loads(session.get(projectUrl % (projectId)).text)
		msg += project["name"] + "\n"
	return msg

	

for link in reportsJson["_meta"]["links"]:
	if(link["rel"]=="content"):
		while("errorMessage" in json.loads(session.get(link["href"]).text)):
			print "report not generated... waiting 5 seconds"
			time.sleep(5)
		reportData = json.loads(session.get(link["href"]).text)
		for reportEntry in reportData["reportContent"]:
			if( reportEntry["fileContent"]["numberOfNewVulnerabilities"] != 0 or reportEntry["fileContent"]["numberOfUpdatedVulnerabilities"] != 0 ):
				msg = makeEmailMessage(reportEntry["fileContent"])
				sendNotificationEmail(msg)



