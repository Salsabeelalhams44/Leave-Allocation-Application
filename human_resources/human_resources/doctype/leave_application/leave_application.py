# Copyright (c) 2023, sals and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff
from frappe import _
class LeaveApplication(Document):
	def validate(self):
		self.calculate_total_leave_days()
		self.get_total_leave_allocation()
		self.validate_total_leave_days()
		
	def on_submit(self):
		self.update_leave_balance_before_application()
		
		
	def calculate_total_leave_days(self):
	 	if self.from_date  and self.to_date:
	 		total_leave_days= date_diff(self.to_date, self.from_date)+1
	 		if total_leave_days>=0:
	 			self.total_leave_days= total_leave_days
	
	def get_total_leave_allocation(self):
		if self.employee and self.from_date and self.to_date and self.leave_type:
			total_leave_allocation = frappe.db.sql(""" select total_leave_allocation from `tabLeave Allocation` 
			where employee=%s and leave_type=%s and from_date<=%s  and to_date >=%s""",(self.employee,self.leave_type,self.from_date,self.to_date), as_dict=1)[0]['total_leave_allocation']
			if total_leave_allocation:
				self.leave_balance_before_application= float(total_leave_allocation )
		
	
	def validate_total_leave_days(self):
		if self.total_leave_days and self.leave_balance_before_application:
			if self.total_leave_days > self.leave_balance_before_application:
				frappe.throw(_('You don\'t have a leave day for leave type: ')+ self.leave_type)
			
	def update_leave_balance_before_application(self):
		update_leave_balance_before_application= self.leave_balance_before_application-self.total_leave_days
		frappe.db.sql(""" update `tabLeave Allocation` set total_leave_allocation=%s
			where employee=%s and leave_type=%s and from_date<=%s  and to_date >=%s""",(update_leave_balance_before_application, self.employee,self.leave_type,self.from_date,self.to_date), as_dict=1)
		
	
			
			
			
