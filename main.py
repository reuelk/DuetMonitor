import urllib.request
import requests
import json
import time
import os
import datetime
import shutil
import subprocess

from sys import stdout
from config import *

# Test notifications when printer disconnects while printing
# Add ability to change sound per notification type
# Add link for timelapse folder?
# Add in number of times to try reconnecting before pinging for network disconnect
# Add trigger for temperature raise to and temperature lower to.
# Add trigger for when timelapse video is finished being created. Notification includes link to timelapses folder.
# Multithread ffmpeg process
# Timelapse based on time vs layer

duetMonitorVersion = "1.0"
lastLogText = ""

def main():
	"The main loop."

	# Printer status variables
	status = {
		'printerName': '',
		'lastStatus': '',
		'currentLayer': 0,
		'lastPrintDuration': "",
		'lastPercentage': 0,
		'lastLayer': 0,
		'lastFileName': "",
		'printID': ""
	}

	print("")
	print("Duet Monitor")
	print("Version " + duetMonitorVersion)
	print("Written by Reuel Kim" + "\n")
	log("Duet Monitor started.")

	# Loop with time delay
	while True:

		printerResponse = getPrinterStatus(config['printerURL'])

		# Check to see if we got disconnected during a print and notify if configured to do so.
		if (printerResponse == None and status['lastStatus'] == "P"):
			if config['printDisconnect'] == True:
				notificationTitle = "Lost Connection During Print"
				notificationMessage = "\"" + currentFileName + "\" on " + printerName + ". Elapsed print time: " + status["lastPrintDuration"]
				log(notificationTitle + ": " + notificationMessage)
				postPushover(title=notificationTitle, msg=notificationMessage, highPriority=config['highPriorityDisconnect'], emergencyPriority=config['emergencyPriorityDisconnect'])

		# Retry connection
		while printerResponse == None:
			time.sleep(config['printerRetryInterval'])
			printerResponse = getPrinterStatus(config['printerURL'])

		# Get printer name if we don't have it already
		if status['printerName'] == "":
			status['printerName'] = getPrinterName(config['printerURL'])

		# Parse the response from the printer and check for triggers
		result = parseStatus(printerResponse, status['printerName'], status['lastStatus'], status['lastPercentage'], status['lastLayer'], status['lastFileName'], status['lastPrintDuration'], status['printID'])
		debug(result)
		
		if (result != None):
			status['lastStatus'] = result['lastStatus']
			status['lastPercentage'] = result['lastPercentage']
			status['lastLayer'] = result['lastLayer']
			status['lastFileName'] = result['lastFileName']
			status['lastPrintDuration'] = result['lastPrintDuration']
			status['printID'] = result['printID']
		
		time.sleep(config['statusInterval'])
	
	
def parseStatus(printerStatus, printerName, lastStatus, lastPercentage, lastLayer, lastFileName, lastPrintDuration, printID):
	"Checks printer status and executes tasks accordingly."
	
	# Printer is off
	if (printerStatus['status'] == "O"):
		log("Printer is off.", static=True)

		update = {
			'lastStatus': "O",
			'lastPercentage': 0,
			'lastLayer': 0,
			'lastFileName': "",
			'lastPrintDuration': "",
			'printID': ""
			}
		return update
	
	# Layer has changed
	if (lastLayer != printerStatus['currentLayer'] and printerStatus['currentLayer'] != 0):

		currentFileName = getFileName(config['printerURL'])
		log("Layer " + str(printerStatus['currentLayer']) +": \"" + currentFileName + "\"")

		if (printID == ""):
			printID = time.strftime("%Y%m%dT%H%M%S") + "-" + os.path.splitext(currentFileName)[0]
		getCameraSnapshot(printID)
	
	# Printing started
	if (config['printStart'] == True):
		if (printerStatus['status'] == "P" and (lastStatus == "I" or lastStatus == "O")):

			currentFileName = getFileName(config['printerURL'])

			notificationTitle = "Print Started"
			notificationMessage = "\"" + currentFileName + "\" on " + printerName + "."
			log(notificationTitle + ": " + notificationMessage)
			postPushover(title = notificationTitle, msg = notificationMessage, highPriority=config['highPriorityStart'], emergencyPriority=config['emergencyPriorityStart'])
			
			update = {
				'lastStatus': "P",
				'lastPercentage': 0,
				'lastLayer': printerStatus['currentLayer'],
				'lastFileName': currentFileName,
				'lastPrintDuration': printerStatus['printDuration'],
				'printID': printID
			}
			
			return update
	
	# Printing paused
	if (config['printPause'] == True):
		if (printerStatus['status'] == "S" and lastStatus == "P"):

			currentFileName = getFileName(config['printerURL'])

			notificationTitle = "Print Paused"
			notificationMessage = "\"" + currentFileName + "\" on " + printerName + ". Elapsed print time: " + printerStatus["printDuration"]
			log(notificationTitle + ": " + notificationMessage)
			postPushover(title = notificationTitle, msg = notificationMessage, highPriority=config['highPriorityPause'], emergencyPriority=config['emergencyPriorityPause'])
			
			update = {
				'lastStatus': "S",
				'lastPercentage': lastPercentage,
				'lastLayer': printerStatus['currentLayer'],
				'lastFileName': currentFileName,
				'lastPrintDuration': printerStatus['printDuration'],
				'printID': printID
			}
			
			return update
	
	# Printing finished
	if (config['printFinish'] == True):
		if (printerStatus["status"] == "I" and lastStatus == "P"):

			notificationTitle = "Print Finished"
			notificationMessage = "\"" + lastFileName + "\" on " + printerName + ". Total print time: " + lastPrintDuration
			log(notificationTitle + ": " + notificationMessage)
			postPushover(title = notificationTitle, msg = notificationMessage, highPriority=config['highPriorityFinish'], emergencyPriority=config['emergencyPriorityFinish'])

			if (config['makeVideos'] == True):
				createVideo(printID)

			update = {
				'lastStatus': "I",
				'lastPercentage': lastPercentage,
				'lastLayer': printerStatus['currentLayer'],
				'lastFileName': lastFileName,
				'lastPrintDuration': printerStatus['printDuration'],
				'printID': ""
			}

			return update
	
	# Specific layer, can be multiple values
	if (len(config['layers']) > 0):
		
		for layer in config['layers']:
			if (layer == printerStatus['currentLayer'] and lastLayer != printerStatus['currentLayer']):

				currentFileName = getFileName(config['printerURL'])

				notificationTitle = "Layer " + str(printerStatus['currentLayer']) + " Started"
				notificationMessage = "\"" + currentFileName + "\" on " + printerName + ". Elapsed print time: " + printerStatus["printDuration"]
				log(notificationTitle + ": " + notificationMessage)
				postPushover(title = notificationTitle, msg = notificationMessage, highPriority=config['highPriorityLayers'], emergencyPriority=config['emergencyPriorityLayers'])
				
				update = {
					'lastStatus': printerStatus['status'],
					'lastPercentage': lastPercentage,
					'lastLayer': printerStatus['currentLayer'],
					'lastFileName': currentFileName,
					'lastPrintDuration': printerStatus['printDuration'],
					'printID': printID
				}
				
				return update
	
	# Print percentage, can be multiple values
	if (len(config['printPercentages']) > 0):
		
		# Calculate whether percentage has been passed
		for percentage in config['printPercentages']:
			if (printerStatus['fractionPrinted'] >= percentage and percentage > lastPercentage ):

				currentFileName = getFileName(config['printerURL'])

				notificationTitle = str(percentage) + "% Printed"
				notificationMessage = "\"" + currentFileName + "\" on " + printerName + ". Elapsed print time: " + printerStatus["printDuration"]
				log(notificationTitle + ": " + notificationMessage)
				postPushover(title = notificationTitle, msg = notificationMessage, highPriority=config['highPriorityPercentages'], emergencyPriority=config['emergencyPriorityPercentages'])
				
				update = {
					'lastStatus': printerStatus['status'],
					'lastPercentage': percentage,
					'lastLayer': printerStatus['currentLayer'],
					'lastFileName': currentFileName,
					'lastPrintDuration': printerStatus['printDuration'],
					'printID': printID
				}
				
				return update
	
	# Nothing triggered, return current state.
	if printerStatus['status'] == "P" or printerStatus['status'] == "S":
		currentFileName = getFileName(config['printerURL'])
	else:
		currentFileName = ""

	if printerStatus['status'] == "I":
		log("Printer is idle.", static=True)

	update = {
		'lastStatus': printerStatus['status'],
		'lastPercentage': lastPercentage,
		'lastLayer': printerStatus['currentLayer'],
		'lastFileName': currentFileName,
		'lastPrintDuration': printerStatus['printDuration'],
		'printID': printID
	}
	
	return update


def getPrinterStatus(printerURL):
	"Pings the printer for status information."

	try:
		webURL = urllib.request.urlopen(printerURL + "/rr_status?type=3", timeout=config['printerTimeout'])
	except:
		log("Could not communicate with printer to check status.", error = True, static = True)
		return None
	
	if (webURL.getcode() == 200):
		data = webURL.read()
		debug(data)

		return parsePrinterStatus(data)
	else:
		log("Error reading status from printer.", error = True)
		return None
	

def parsePrinterStatus(data):
	"Parses the results from a status ping to the printer and returns data."
	
	rrStatus = json.loads(data)
	
	printer = {
		'status': rrStatus["status"],
		'currentLayer': rrStatus["currentLayer"],
		'fractionPrinted': rrStatus["fractionPrinted"],
		'printDuration': time.strftime("%-Hh%-Mm%-Ss", time.gmtime(rrStatus["printDuration"]))
	}
	
	return printer


def getPrinterName(printerURL):
	"Pings the printer for the printer name."

	try:
		webURL = urllib.request.urlopen(printerURL + "/rr_status?type=2", timeout=config['printerTimeout'])
	except:
		log("Could not communicate with printer to get printer name.", error=True)
		return ""
	
	if (webURL.getcode() == 200):
		data = webURL.read()
		debug(data)
		rrStatus = json.loads(data)
		return rrStatus["name"]	
	else:
		log("Error reading printer name.", error = True)
		return ""
		

def getFileName(printerURL):
	"Pings the printer for the current filename. Returns empty string if no file is printing or 'Unknown File' if there's an error getting the filename."
	
	try:
		webURL = urllib.request.urlopen(printerURL + "/rr_fileinfo", timeout=config['printerTimeout'])
	except:
		log("Could not reach printer to get filename of current print.", error = True)
		return "Unknown File"
	
	if (webURL.getcode() == 200):
		data = webURL.read()
		debug(data)
		rrStatus = json.loads(data)
		
		if (rrStatus["err"] == 0):
			filepath = rrStatus["fileName"]
			filename = os.path.split(filepath)
			return filename[1]
		else:
			return ""
	else:
		log("Error reading file information from printer.", error = True)
		return ""


def postPushover(title, msg, highPriority = False, emergencyPriority = False):
	"Posts a notification request to Pushover."
	
	pushoverURL = "https://api.pushover.net/1/messages.json"
	
	requestData = {
		"token": config['pushoverAppToken'],
		"user": config['pushoverUserKey'],
		"message": msg,
		"title": title,
		"device": config['notifyDevices'],
		"sound": config['notificationSound']
	}

	if config['includeDWCLink'] == True:
		requestData['url'] = config['printerURL']
		requestData['url_title'] = "Duet Web Control"

	if highPriority == True:
		requestData['priority'] = 1

	if emergencyPriority == True:
		requestData['priority'] = 2
		requestData['retry'] = config['emergencyRetryInterval']
		requestData['expire'] = config['emergencyExpireTime']

	try:
		if config['includeImage'] == True:
			snapshot = getCameraSnapshotForNotification()
			if snapshot != None:
				response = requests.post(pushoverURL, data = requestData, files = {"attachment": ("snapshot.jpg", open(snapshot, "rb"), "image/jpeg")})
				try:
					os.remove(snapshot)
				except:
					log("Could not delete temporary notification snapshot file " + snapshot, error = True)
			else:
				log("Could not get a snapshot for the notification.", error = True)
				return
		else:
			response = requests.post(pushoverURL, data = requestData)
	except:
		log("Could not reach Pushover server.", error = True)
		return

	responseObject = response.json()
	status = responseObject["status"]
	log("Posted to Pushover and got HTTP response " + str(response.status_code) + " with status " + str(status) + ".")


def getCameraSnapshot(subfolderName):

	try:
		response = requests.get(config['cameraURL'], auth=(config['cameraAuthUser'], config['cameraAuthPassword']), verify=config['httpsVerification'], timeout=5, stream=True)
	except:
		log("Failed to reach camera.", error = True)
		return None

	if (response.status_code == 200):
		time = datetime.datetime.now()
		subfolderPath = os.path.join(config['timelapseFolder'], subfolderName)

		if (os.path.exists(subfolderPath) == False):
			try:
				os.mkdir(subfolderPath)
			except:
				log("Could not create new timelapse folder: " + subfolderPath, error = True)
				return

		snapshot = os.path.join(subfolderPath, time.strftime("%Y%m%dT%H%M%S") + ".jpg")
		try:
			with open(snapshot, 'wb') as file:
				for chunk in response:
					file.write(chunk)
			log("Snapshot added: " + snapshot)
		except:
			log("Could not write new snapshot: " + snapshot, error = True)
	else:
		log('Reached camera but failed to get snapshot.', error = True)


def createVideo(subfolderName):
	videoFilePath = os.path.join(config['timelapseFolder'], subfolderName + ".mp4")
	snapshotFolder = os.path.join(config['timelapseFolder'], subfolderName)
	snapshotPath = os.path.join(snapshotFolder, "*.jpg")
	command = ["ffmpeg", "-r", "20", "-y", "-pattern_type", "glob", "-i", snapshotPath, "-vcodec", "libx264", videoFilePath]

	log("Running ffmpeg to create timelapse video from snapshots.")
	try:
		subprocess.run(command)
	except:
		log("Failed to run ffmpeg to create video.", error = True)
		return

	if (os.path.exists(videoFilePath) == True):
		log("Video created: " + videoFilePath)

		if (config['keepSnapshots'] == False):
			try:
				shutil.rmtree(snapshotFolder)
				log("Snapshot files deleted at: " + snapshotFolder)
			except:
				log("Failed to delete snapshot folder.", error = True)

	else:
		separator = " "
		log("Failed to create video using command: " + separator.join(command), error = True)


def getCameraSnapshotForNotification():

	try:
		response = requests.get(config['cameraURL'], auth=(config['cameraAuthUser'], config['cameraAuthPassword']), verify=config['httpsVerification'], timeout=5, stream=True)
	except:
		log("Failed to reach camera.", error = True)
		return None

	if (response.status_code == 200):
		time = datetime.datetime.now()
		snapshot = os.path.join(config['timelapseFolder'], time.strftime("%Y%m%dT%H%M%S") + ".jpg")

		try:
			with open(snapshot, 'wb') as file:
				for chunk in response:
					file.write(chunk)
			log("Snapshot created for notification: " + snapshot)
			return snapshot
		except:
			log("Could not write new snapshot for notification: " + snapshot, error = True)
			return None
	else:
		log('Reached camera but failed to get snapshot for notification.', error = True)
		return None


def printOver(text):
	stdout.write("\r" + text)
	stdout.flush()


def log(text, error = False, static = False):
	"Writes to the log."

	global lastLogText

	if (error == False and config['logErrorsOnly'] == True):
		pass
	else:
		currentTime = time.asctime(time.localtime(time.time()))

		if static == True:
			if lastLogText != text:
				file = open("duet_monitor.log", "a")
				file.write(currentTime + ": " + text + "\n")
				file.close()
				stdout.write("\n")  # move the cursor to the next line
			printOver(currentTime + ": " + text)
		else:
			file = open("duet_monitor.log", "a")
			file.write(currentTime + ": " + text + "\n")
			file.close()
			stdout.write("\n")  # move the cursor to the next line
			stdout.write(currentTime + ": " + text)
			stdout.flush()

		lastLogText = text
	return


def debug(text):
	if (config['debug'] == True):
		print(text)
	return

if __name__ == '__main__':
	main()
	