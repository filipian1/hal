#!/usr/bin/env python

import serial
import sys
import rospy
import time
import numpy as np
from rospy.numpy_msg import numpy_msg
from hal.msg import Floats
from libnmea_navsat_driver.driver import RosNMEADriver
import re
import calendar
import math
import logging

#GPS Class
class GPS:

	def __init__(self):
		#ser must be declared for each fxn used
		self.baudrate = 9600
		self.port = '/dev/ttyUSB1'
		self.timeout=2
		self.ser_id = ser1
		self.logger = logging.getLogger('rosout')
		self.topic="/gps" +self.port
		self.pub=rospy.Publisher(self.topic, numpy_msg(Floats)) 


		#function allowing for cennection two separate GPS
	def open_serial_port(self):
		try:
			self.ser_id = serial.Serial(port=self.port, baudrate=self.baudrate,timeout=self.timeout)
			print("Opened port:"+self.ser_id.port)
		except:
			print("Failed to open port:"+self.port)
		
	    
	def readGPS(self, sentence_type_of_interest):
		frame_id = RosNMEADriver.get_frame_id()

		#Reading Data from GPS
		try:
			#get a line of data from serial port
			data = self.ser_id.readline().strip()
			#get a numpy array of floats 
			temp= self.parse_nmea_sentence(data, sentence_type_of_interest)
			
			if temp is not None:
				numpy_parsed_sentence=Floats()
				numpy_parsed_sentence.header.stamp = rospy.get_rostime()
				numpy_parsed_sentence.header.frame_id = frame_id
				numpy_parsed_sentence.data=temp
				print(numpy_parsed_sentence)
				self.pub.publish(numpy_parsed_sentence)
		except:
			pass
			

	def safe_float(self, field):
		try:
			return float(field)
		except ValueError:
			return float('NaN')


	def safe_int(self, field):
		try:
			return int(field)
		except ValueError:
			return 0


	def convert_latitude(self, field):
		return self.safe_float(field[0:2]) + self.safe_float(field[2:]) / 60.0


	def convert_longitude(self, field):
		return self.safe_float(field[0:3]) + self.safe_float(field[3:]) / 60.0


	def convert_time(self, nmea_utc):
		# Get current time in UTC for date information
		utc_struct = time.gmtime()  # immutable, so cannot modify this one
		utc_list = list(utc_struct)
		# If one of the time fields is empty, return NaN seconds
		if not nmea_utc[0:2] or not nmea_utc[2:4] or not nmea_utc[4:6]:
			return float('NaN')
		else:
			hours = int(nmea_utc[0:2])
			minutes = int(nmea_utc[2:4])
			seconds = int(nmea_utc[4:6])
			utc_list[3] = hours
			utc_list[4] = minutes
			utc_list[5] = seconds
			unix_time = calendar.timegm(tuple(utc_list))
			return unix_time


	def convert_status_flag(self,status_flag):
		#A means that the fix is valid
		if status_flag == "A":
			return 1
		elif status_flag == "V":
			return 0
		else:
			return -1


	def convert_knots_to_mps(self,knots):
		return self.safe_float(knots) * 0.514444444444


	# Need this wrapper because math.radians doesn't auto convert inputs
	def convert_deg_to_rads(self,degs):
		return math.radians(self.safe_float(degs))


	def latitude_direction_to_number(self,field):
		temp=str(field)
		if temp=='N': #North
			return 1

		elif temp =='S': #South
			return 0
		else:
			return -1


	def longitude_direction_to_number(self,field):
		temp=str(field)
	
		if temp=='E': #East
			return 1

		elif temp =='W': #West
			return 0
		else:
			return -1	


	def parse_nmea_sentence(self,nmea_sentence,sentence_type_of_interest):
		#Parsing maps
		parse_maps = {
			"GGA": [
				("utc_time", self.convert_time, 1),
				("fix_type", self.safe_float, 6),
				("latitude", self.convert_latitude, 2),
				("latitude_direction", self.latitude_direction_to_number, 3),
				("longitude", self.convert_longitude, 4),
				("longitude_direction", self.longitude_direction_to_number, 5),
				("altitude", self.safe_float, 9),
				("mean_sea_level", self.safe_float, 11),
				("hdop", self.safe_float, 8),
				("num_satellites", self.safe_int, 7),
				
				],
			"RMC": [
				("utc_time", self.convert_time, 1),
				("fix_valid", self.convert_status_flag, 2),
				("latitude", self.convert_latitude, 3),
				("latitude_direction", self.latitude_direction_to_number, 4),
				("longitude", self.convert_longitude, 5),
				("longitude_direction", self.longitude_direction_to_number, 6),
				("speed", self.convert_knots_to_mps, 7),
				("true_course", self.convert_deg_to_rads, 8),
				] }

		
 	   # Check for a valid nmea sentence
		if not re.match('(^\$GP|^\$GN|^\$GL|^\$IN).*\*[0-9A-Fa-f]{2}$', nmea_sentence):
			logger.debug("Regex didn't match, sentence not valid NMEA? Sentence was: %s"
						% repr(nmea_sentence))
			return False
			
		# Devide each sentence into fields
		fields = [field.strip(',') for field in nmea_sentence.split(',')]
		sentence_type = fields[0][3:]
		#parse only the sentence type that we are interested in (either GGA or RME)
		if sentence_type == sentence_type_of_interest:
			parse_map = parse_maps[sentence_type]
			parsed_sentence = {}

			numpiezed_parsed_sentence=np.array([])
			#create numpy array called numpiezed_parsed_sentence, from entries in parse_map dictionary.
			for entry in parse_map:
				numpiezed_parsed_sentence=np.append(numpiezed_parsed_sentence, entry[1](fields[entry[2]]))
			
			return numpiezed_parsed_sentence



def main(args):
	#declare global serial variables
	global ser1
	global ser2
	ser1 = serial.Serial()
	ser2 = serial.Serial()


	rospy.init_node("GPS_data", anonymous=True)
	#make objects of class GPS
	gps1=GPS()
	gps2=GPS()
	
	#additional setting for gps2
	gps2.ser_id=ser2
	gps2.port='/dev/ttyUSB1'

	gps1.open_serial_port()
	# gps2.open_serial_port()

#provide the type of nmea sentence we are interested in(either GGA or RME)
	sentence_type_of_interest="RMC"
	while not rospy.is_shutdown():
		gps1.readGPS(sentence_type_of_interest)
		gps2.readGPS(sentence_type_of_interest)
		
	try:
		rospy.spin()
	except:
		pass

if __name__=='__main__':
	main(sys.argv)
