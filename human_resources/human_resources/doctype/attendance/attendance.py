# Copyright (c) 2023, sals and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, get_datetime
from frappe.utils.data import time_diff_in_hours
from datetime import datetime,timedelta

class Attendance(Document):
	
	def validate(self):
		self.calculate_work_hours()	
		self.calculate_late_hours()
		self.update_status_value()
		
	def float_to_time(self,float_time):
    		hours = 0
    		minutes = int(float_time)
    		seconds = 0
    		return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    		
	def check_out_early(self):
		attendance_setting = frappe.get_single("Attendance Setting")
		early_exit_grace_period = attendance_setting.early_exit_grace_period
		end_time = attendance_setting.end_time
		# conver early_exit_grace to str
		early_exit_grace= self.float_to_time(early_exit_grace_period)
		# convert early_exit_grace to time 
		early_exit_grace_time = datetime.strptime(early_exit_grace, "%H:%M:%S").time() 
		# convert check out to time 
		check_out_time = datetime.strptime(self.check_out, "%H:%M:%S").time()
		# convert early_exit_grace_time to timedelta to make it add to another time
		time1= timedelta(hours=early_exit_grace_time.hour,minutes=early_exit_grace_time.minute,seconds= early_exit_grace_time. second )
		# convert check_out_time to timedelta to make it add to another time
		time2= timedelta(hours=check_out_time.hour,minutes=check_out_time.minute,seconds= check_out_time. second )
		# check_out = self.check_out + early_exit_grace
		check_out_new= time1 +time2
		check_out_new = check_out_new.total_seconds() / 3600
		check_out_new = str(timedelta(hours=check_out_new) )
		return time_diff_in_hours(end_time, check_out_new) 
		
	def check_in_late(self):
		attendance_setting = frappe.get_single("Attendance Setting")
		late_entry_grace_period = attendance_setting.late_entry_grace_period
		start_time = attendance_setting.start_time
		late_entry_grace = self.float_to_time(late_entry_grace_period)
		check_in = time_diff_in_hours(self.check_in, late_entry_grace)
		check_in_time = str(timedelta(hours=check_in) )
		return time_diff_in_hours(check_in_time, start_time)
		
	def calculate_late_hours(self):
		attendance_setting = frappe.get_single("Attendance Setting")
		start_time = attendance_setting.start_time
		end_time = attendance_setting.end_time
		# if check_in late only:
		if self.check_in > start_time and self.check_out >= end_time :
			self.late_hours = self.check_in_late()
		# if check_out early only:
		elif self.check_out < end_time and self.check_in <= start_time:
			self.late_hours =self.check_out_early()
		# if check_in late and check_out early:	
		elif self.check_in > start_time and self.check_out < end_time :
			self.late_hours= self.check_in_late() + self.check_out_early()
		else:
			self.late_hours=0	
	
	def calculate_work_hours(self):
		attendance_setting = frappe.get_single("Attendance Setting")
		start_time = attendance_setting.start_time
		end_time = attendance_setting.end_time
		late_entry_grace_period = attendance_setting.late_entry_grace_period
		early_exit_grace_period = attendance_setting.early_exit_grace_period
		
		# convert early_exit_grace to str
		early_exit_grace= self.float_to_time(early_exit_grace_period)
		# convert early_exit_grace to time 
		early_exit_grace_time = datetime.strptime(early_exit_grace, "%H:%M:%S").time() 
		early_exit_grace_time= timedelta(hours=early_exit_grace_time.hour,minutes=early_exit_grace_time.minute,seconds= early_exit_grace_time. second )
		
		# convert early_exit_grace to str
		late_entry_grace= self.float_to_time(late_entry_grace_period)
		# convert early_exit_grace to time 
		late_entry_grace_time = datetime.strptime(late_entry_grace, "%H:%M:%S").time() 
		late_entry_grace_time= timedelta(hours=late_entry_grace_time.hour,minutes=late_entry_grace_time.minute,seconds= late_entry_grace_time. second )
		
		# any check_in before start_time, it doesn't calculate 
		if self.check_in < start_time:
			check_in = start_time
		elif self.check_in > start_time:
			# convert check-in to time 
			check_in_time= datetime.strptime(self.check_in,"%H:%M:%S").time()
			check_in_time= timedelta(hours=check_in_time.hour,minutes=check_in_time.minute,seconds= check_in_time. second )
			check_in =  check_in_time-late_entry_grace_time
			
		else:
			check_in = self.check_in
			check_in= datetime.strptime(self.check_in,"%H:%M:%S").time()
			check_in= timedelta(hours=check_in.hour,minutes=check_in.minute,seconds= check_in. second )

		# any check_out after end_time, it doesn't calculate
		if self.check_out > end_time :
			check_out = end_time
		elif self.check_out < end_time :
			# convert check-out to time 
			check_out=datetime.strptime(self.check_out, "%H:%M:%S").time() 
			check_out= timedelta(hours=check_out.hour,minutes=check_out.minute,seconds= check_out. second )
			check_out = check_out + early_exit_grace_time
		else:
			check_out = self.check_out
			check_out= datetime.strptime(self.check_out,"%H:%M:%S").time()
			check_out= timedelta(hours=check_out.hour,minutes=check_out.minute,seconds= check_out. second )
		result= check_out - check_in
		seconds_results= result.total_seconds()
		work_hours= seconds_results/ (60*60)
		self.work_hours = work_hours
		
	def update_status_value(self):
		attendance_setting = frappe.get_single("Attendance Setting")
		working_hours_threshold_for_absent= attendance_setting.working_hours_threshold_for_absent
		if self.work_hours <=working_hours_threshold_for_absent:
			self.status= "Absent"
