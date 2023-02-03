# Copyright (c) 2023, sals and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, getdate
from frappe import _

class LeaveAllocation(Document):
	def validate(self):
		self.validate_from_date_allocation()
		self.validate_duplicate_allocation()
	
	
	def validate_from_date_allocation(self):	
		if self.from_date and self.to_date and (getdate(self.to_date) < getdate(self.from_date)):
			frappe.throw(_("To date cannot be before from date"))
	
	def validate_duplicate_allocation(self):
		if self.employee and self.from_date and self.to_date and self.leave_type and self.total_leave_allocation:
			check_duplicate = frappe.db.sql(""" select from_date, to_date, leave_type from `tabLeave Allocation` 
			where employee=%s and leave_type=%s and ((from_date=%s  and to_date=%s) 
			or ( from_date <=%s and to_date>= %s )or (from_date<=%s and to_date>=%s))""",
			(self.employee,self.leave_type,self.from_date,self.to_date,
			self.from_date,self.from_date,self.to_date,self.to_date), as_dict=1)
		
			if check_duplicate:
				frappe.throw(_("This leave Allocation Data Duplicated!!"))
	
