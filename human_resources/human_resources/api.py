import frappe
@frappe.whitelist()
def create_attendance(attendance_date, check_in, check_out):
	attendance = frappe.new_doc("Attendance")
	attendance.attendance_date= attendance_date
	attendance.check_in = check_in
	attendance.check_out= check_out
	attendance.employee= frappe.session.user
	attendance.insert()
	frappe.db.commit()
	return  attendance
