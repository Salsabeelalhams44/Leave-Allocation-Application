// Copyright (c) 2023, sals and contributors
// For license information, please see license.txt

// Q1
 frappe.ui.form.on('Employee',  {
 refresh: function(frm) {
frm.set_df_property('age', 'read_only', '1');
 }
 });
frappe.ui.form.on("Employee", "date_of_birthday", function(frm) {
    if (frm.doc.date_of_birthday) {
        var date_of_birth = new Date(frm.doc.date_of_birthday);
        var today = new Date();
        var age = today.getFullYear() - date_of_birth.getFullYear();
        if (today.getMonth() < date_of_birth.getMonth() || (today.getMonth() == date_of_birth.getMonth() && today.getDate() < date_of_birth.getDate())) {
            age--;
        }
        frm.set_value("age", age);
    }
});

// Q2
frappe.ui.form.on("Employee", 
  'validate', function(frm){
    if(frm.doc.age>=60&& frm.doc.status=='Active'){
        frappe.throw('Your age must less than 60 and the status mustnot Active');
    }
  
});

// Q3

 // complete the code in employee.py
 
 
 // Q4 in employee.py

// Q5
frappe.ui.form.on("Employee", {validate:function(frm) {
    var total_education=0;
    $.each(frm.doc.employee_education, function(i,d){
        if(d.schooluniversity){
            total_education+=1;}
    });
    if (total_education<2){
        frappe.throw('Education must at least 2');
    }
    }});




