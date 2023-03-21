# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  Copyright (C) 2023  David King <dave@daveking.com>
#
#  This Source Code Form is subject to the terms of the Mozilla Public License,
#  v. 2.0.  If a copy of the MPL was not distbuted with this file, You can
#  obtain one at https://mozilla.org/MPL/2.0/.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  Turn a SmartThings switch on and off or just get the current status of the
#  device
#
#  SmartThings API token is required, see https://account.smartthings.com/tokens
#  to get one 
#
#  Usage:
#     import smartthings
#     device = smartthings.Thing(device_label, SmartThings API Token)
#     status = device.getStatus()  #  Returns JSON or False
#     device.onoff('on')  #  or 'off'.  Returns True or False
#

import logging
import requests
import json

class Thing:

	def __init__(self, device_label, api_token):

		self.device_label = device_label		
		self.headers = {
			'Authorization': 'Bearer {}'.format(api_token)
		}
		self.url = 'https://api.smartthings.com/v1/'

		try:
			#  Get the device id for the "device_label" device
			logging.debug('{}: requesting device_id for "{}" device from SmartThings'.format(__name__, self.device_label))
			self.device_id = None
			_r = requests.get(self.url + 'devices', headers=self.headers)
			if _r.status_code != 200:
				logging.critical('{}: request to SmartThings API for device list failed with status code {}:\n{}'.format(__name__, _r.status_code, _r.text))
				return False
			_devices = _r.json()
			logging.debug('{}: device_list:\n{}'.format(__name__, json.dumps(_devices, indent=4)))
			for _device in _devices['items']:
				if _device['label'] == self.device_label:
					self.device_id = _device['deviceId']
					logging.debug('{}: device_id: {}'.format(__name__, self.device_id))
			if not self.device_id:
				logging.critical('{}: failed to get device_id for "{}" device from SmartThings:\n{}'.format(__name__, self.device_label, _devices))
				return False
		except Exception as e:
			logging.exception('{}: unexpected exception while get the device_id for the "{}" device'.format(__name__, self.device_label), exc_info=True)

	def getStatus(self):
		
		try:
			#  Get the current state of the device
			logging.debug('{}: querying the the "{}" device from SmartThings'.format(__name__, self.device_label))
			_r = requests.get(self.url + 'devices/' + self.device_id + '/components/main/status', headers=self.headers)
			if _r.status_code != 200:
				logging.critical('{}: request to SmartThings API for status of "{}" device failed with status code {}:\n{}'.format(__name__, _r.status_code, _r.text))
				return False
			_status = _r.json()
			logging.debug('{}: device status:\n{}'.format(__name__, json.dumps(_status, indent=4)))
			return _status
		except Exception as e:
			logging.exception('{}: unexpected exception while trying to get the status of the "{}" device'.format(__name__, _value, self.device_label), exc_info=True)
			return False
		
	def onoff(self, _value):
		
		try:
			#  Get the current state of the device
			_current_state = None
			_status = self.getStatus()
			if _status:
				_current_state = _status['switch']['switch']['value']
				logging.debug('{}: current_state: {}'.format(__name__, _current_state))
			if not _current_state:
				logging.critical('{}: failed to get the current state of the "{}" device from SmartThings:\n{}'.format(__name__, self.device_label, _status))
				return False

			#  If the device isn't already in the requested state, send a command
			#  to make it so
			if _current_state != _value:
				logging.info('The "{}" device is {}, turning it {}'.format(device_label, _current_state, _value))
				_data = {
					'commands': [
						{
							'capability': 'switch',
							'command': _value
						}
					]
				}
				_r = requests.post(self.url + 'devices/' + self.device_id + '/commands', headers=self.headers, data=json.dumps(_data))
				if _r.status_code == 200:
					logging.info('Successfully turned the "{}" device {}'.format(self.device_label, _value))
				else:
					logging.critical('{}: request to SmartThings API to turn the "{}" device {} failed with status code {}:\n{}'.format(__name__, self.device_label, _value, _r.status_code, _r.text))
					return False
			else:
				logging.info('The "{}" devcice is already {}, nothing to be done.'.format(self.device_label, _value))

			return True

		except Exception as e:
			logging.exception('{}: unexpected exception while trying to turn {} the "{}" device'.format(__name__, _value, self.device_label), exc_info=True)
			return False
