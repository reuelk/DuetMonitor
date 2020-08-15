config = {
	# Printer Configuration
	'printerURL': 'http://192.168.7.50', # URL of printer
	'statusInterval': 3, # Interval to check printer status in seconds
	'printerTimeout': 5, # Number of seconds to wait for a response from the printer before timing out
	'printerRetryInterval': 10, # Interval in seconds to try reconnecting to printer if it's turned off or unreachable. This wait time is in addition to the timeout.

	# Notification Triggers
	'printStart': True,  # Notify when print is started
	'printPause': True,  # Notify when print is paused. Useful for out-of-filament notifications.
	'printFinish': True,  # Notify when print is finished
	'printDisconnect': True, # Notify when the printer is disconnected during a print. This may happen due to a power failure or network outage.
	'layers': [2, 10, 15], # Notify at these layers. Separate multiple values with commas. Ex: [10, 15, 20]
	'printPercentages': [20, 50, 90],  # Notify at these percentages. Separate multiple values with commas. Ex: [25, 50, 90]

	# Pushover Configuration
	'pushoverAppToken': 'an15sk9yz31swedoz4bouxenb8hgon',
	'pushoverUserKey': 'u652xeqkzj1bmmrer7vzx8mw5ci347',

	# Pushover Notification Settings
	'includeImage': True, # Include a snapshot image from the camera in the notification. Images must not be larger than 2.5 megabytes.
	'includeDWCLink': True, # Include a link to the printer's Duet Web Control interface.
	'notifyDevices': "", # A comma-separated list of devices from the Pushover account to send notifications to. Leave empty to send to all devices.
	'notificationSound': "", # Use a notification sound listed here https://pushover.net/api#sounds instead of the default one. Leave empty to use the default sound.
	'highPriorityStart': False, # Make print start notifications high priority, overriding do-not-disturb settings on the device.
	'highPriorityPause': False, # Make print pause notifications high priority, overriding do-not-disturb settings on the device.
	'highPriorityFinish': False, # Make print finish notifications high priority, overriding do-not-disturb settings on the device.
	'highPriorityDisconnect': False, # Make notifications for disconnection during print high priority, overriding do-not-disturb settings on the device.
	'highPriorityLayers': False, # Make print layer notifications high priority, overriding do-not-disturb settings on the device.
	'highPriorityPercentages': False, # Make print percentage notifications high priority, overriding do-not-disturb settings on the device.
	'emergencyPriorityStart': False, # Make print start notifications emergency priority, repeating notifications until user acknowledges it.
	'emergencyPriorityPause': True, # Make print pause notifications emergency priority, repeating notifications until user acknowledges it.
	'emergencyPriorityFinish': False, # Make print finish notifications emergency priority, repeating notifications until user acknowledges it.
	'emergencyPriorityDisconnect': True, # Make notifications for disconnection during print emergency priority, repeating notifications until user acknowledges it.
	'emergencyPriorityLayers': False, # Make print layer notifications emergency priority, repeating notifications until user acknowledges it.
	'emergencyPriorityPercentages': False, # Make print percentage notifications emergency priority, repeating notifications until user acknowledges it.
	'emergencyRetryInterval': 30, # Number of seconds between repeated emergency notifications if user does not acknowledge it.
	'emergencyExpireTime': 120, # Number of seconds after which emergency notifications will stop repeating if user does not acknowledge it.
	
	# Camera Settings
	'timelapseFolder': "/Users/rkim/Desktop/timelapses", #"/var/www/picam/timelapses", # The folder to place the snapshots and timelapse videos in
	'cameraURL': "http://192.168.7.101:8080/picam/cam_pic.php", # The URL for retrieving the current image from the camera
	'cameraAuthUser': "", # If the camera requires authentication, enter the username. Leave blank if no authentication is required.
	'cameraAuthPassword': "", # If the camera requires authentication, enter the password. Leave blank if no authentication is required.
	'httpsVerification': True, # Whether to check for valid HTTPS certificate from camera URL
	'makeVideos': True, # Whether to use ffmpeg to create videos from snapshots
	'keepSnapshots': False, # Whether to keep the camera snapshots or delete them after making a video

	# Debug Options
	'debug': False, # Show debug information in the terminal while running
	'logErrorsOnly': False # Only record errors to the log file
}