# Copyright (c) 2023, sals and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, getdate
from frappe import _
from datetime import date
class LeaveApplication(Document):
	def validate(self):
		self.validate_from_date_application()
		self.validate_applicable_after()
		self.calculate_total_leave_days()
		self.get_total_leave_allocation()
		self.validate_max_continuous_days()
		self.validate_total_leave_days()
		
	def on_submit(self):
		self.update_leave_balance_before_application()
	
	def on_cancel(self):
		self.update_total_leave_allocation_on_cancel()
		
	
	def validate_from_date_application(self):	
		if self.from_date and self.to_date and getdate(self.to_date) < getdate(self.from_date):
				frappe.throw(_("To date cannot be before from date"))
			


	def validate_applicable_after(self):
		if self.leave_type and self.from_date :
			applicable_days=frappe.db.sql("""select applicable_after from `tabLeave Type` where leave_name=%s""", self.leave_type, as_dict=1)
			if date.today() > getdate(self.from_date):
				frappe.throw(_("you must choose the date in future"))
			else:
				if date_diff(getdate(self.from_date),date.today()) != applicable_days[0].applicable_after:
					frappe.throw(_("you must apply for the holiday before  "+str(applicable_days[0].applicable_after)+" days"))
				
	def validate_max_continuous_days(self):
		if self.from_date  and self.to_date:
			max_allowed_days=frappe.db.sql(""" select max_continuous_days_allowed from `tabLeave Type` where leave_name=%s""", self.leave_type, as_dict=1)
			if self.total_leave_days> float(max_allowed_days [0].max_continuous_days_allowed):
				frappe.throw(_("It Doesn't allow taking a "+ str(self.total_leave_days )+
				" continuous days for "+self.leave_type) )
		
	def calculate_total_leave_days(self):
		if self.from_date  and self.to_date:
			total_leave_days= date_diff(self.to_date, self.from_date)+1
			if total_leave_days>=0:
				self.total_leave_days= total_leave_days
	
	def get_total_leave_allocation(self):
		if self.employee and self.from_date and self.to_date and self.leave_type:
			total_leave_allocation = frappe.db.sql(""" select total_leave_allocation from `tabLeave Allocation` 
			where employee=%s and leave_type=%s and from_date<=%s  and to_date >=%s""",(self.employee,self.leave_type,self.from_date,self.to_date), as_dict=1)
			if total_leave_allocation:
				self.leave_balance_before_application= float(total_leave_allocation[0].total_leave_allocation )
		
	
	def validate_total_leave_days(self):
		allow_negative= frappe.get_value("Leave Type", self.leave_type,'allow_negative_balance')
		if allow_negative:
			return 
		if self.total_leave_days and self.leave_balance_before_application:
			if float(self.leave_balance_before_application) < float(self.total_leave_days):
				frappe.throw(_('You don\'t have a leave day for leave type: ')+ self.leave_type)
					
					
	def update_leave_balance_before_application(self):
		update_leave_balance_before_application= self.leave_balance_before_application-self.total_leave_days
		frappe.db.sql(""" update `tabLeave Allocation` set total_leave_allocation=%s
			where employee=%s and leave_type=%s and from_date<=%s  and to_date >=%s""",(
			update_leave_balance_before_application, self.employee,self.leave_type,self.from_date,self.to_date), as_dict=1)
		
	
	def update_total_leave_allocation_on_cancel(self):
		total_leave_allocation = frappe.db.sql(""" select total_leave_allocation from `tabLeave Allocation` where employee=%s and leave_type=%s and from_date<=%s  and to_date >=%s""",(self.employee, self.leave_type, self.from_date, self.to_date),as_dict=1)
		if total_leave_allocation:
			self.leave_balance_before_application = float(total_leave_allocation)
			update_leave_allocated = self.leave_balance_before_application + self.total_leave_days
			frappe.db.sql(""" update `tabLeave Allocation` set total_leave_allocation=%s where employee=%s and leave_type=%s and from_date<=%s  and to_date >=%s""", (update_leave_allocated, self.employee, self.leave_type, self.from_date, self.to_date),as_dict=1)
			


			
			
			
			
			
			
			
			
			
			
