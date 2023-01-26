# Copyright (c) 2023, sals and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
import re
class Employee(Document):
# Q3
	def validate(doc):
    		if doc.first_name and doc.middle_name and doc.last_name:
        		doc.full_name = doc.first_name + " " + doc.middle_name + " " + doc.last_name
        
# Q4
    		if not doc.mobile.startswith("059") or len(doc.mobile)!=10:
        		frappe.throw("Invalid mobile number, you must enter 10 numbers start with 059")



