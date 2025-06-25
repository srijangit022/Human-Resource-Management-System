import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import os
import base64

# Constants
EXCEL_FILE = "hrms_data.xlsx"
RESUME_DIR = "resumes"


# Helper Functions
def get_db_connection():
    try:
        if os.path.exists(EXCEL_FILE):
            return pd.read_excel(EXCEL_FILE, sheet_name=None)
        else:
            return {}
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return {}


def save_db(tables):
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for table_name, df in tables.items():
                if table_name == "employees":
                    df = df.astype({"id": int, "salary": float, "is_active": int}, errors="ignore")
                elif table_name == "users":
                    df = df.astype({"id": int, "password_changed": int}, errors="ignore")
                elif table_name == "attendance":
                    df = df.astype({"id": int, "employee_id": int}, errors="ignore")
                elif table_name == "performance":
                    df = df.astype({"id": int, "employee_id": int, "rating": float}, errors="ignore")
                elif table_name == "benefits":
                    df = df.astype({"id": int, "employee_id": int, "health_insurance": int, "provident_fund": int,
                                    "paid_time_off": int}, errors="ignore")
                elif table_name == "recruitment":
                    df = df.astype({"id": int}, errors="ignore")
                elif table_name == "leave_requests":
                    df = df.astype({"id": int, "employee_id": int}, errors="ignore")
                elif table_name == "payroll_transactions":
                    df = df.astype({"id": int, "employee_id": int, "gross_pay": float, "net_pay": float},
                                   errors="ignore")
                elif table_name == "payroll_deductions":
                    df = df.astype({"id": int, "employee_id": int, "amount": float}, errors="ignore")
                elif table_name == "payroll_allowances":
                    df = df.astype({"id": int, "employee_id": int, "amount": float}, errors="ignore")
                elif table_name == "bank_details":
                    df = df.astype({"id": int, "employee_id": int}, errors="ignore")
                df.to_excel(writer, sheet_name=table_name, index=False)
    except PermissionError:
        st.error("Permission denied: Cannot write to hrms_data.xlsx. Check file permissions.")
    except Exception as e:
        st.error(f"Error saving Excel file: {str(e)}")


def init_db():
    tables = {
        "users": pd.DataFrame(columns=["id", "email", "password", "role", "user_type", "password_changed"]),
        "employees": pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]),
        "attendance": pd.DataFrame(columns=["id", "employee_id", "check_in", "check_out"]),
        "performance": pd.DataFrame(columns=["id", "employee_id", "review_date", "rating", "comments"]),
        "benefits": pd.DataFrame(columns=["id", "employee_id", "health_insurance", "provident_fund", "paid_time_off"]),
        "recruitment": pd.DataFrame(
            columns=["id", "position", "department", "status", "applicant_name", "applicant_email", "application_date",
                     "resume_path"]),
        "leave_requests": pd.DataFrame(
            columns=["id", "employee_id", "start_date", "end_date", "leave_type", "reason", "status", "created_at"]),
        "payroll_transactions": pd.DataFrame(
            columns=["id", "employee_id", "transaction_date", "gross_pay", "net_pay", "payment_method", "status",
                     "created_at"]),
        "payroll_deductions": pd.DataFrame(columns=["id", "employee_id", "deduction_type", "amount", "effective_date"]),
        "payroll_allowances": pd.DataFrame(columns=["id", "employee_id", "allowance_type", "amount", "effective_date"]),
        "bank_details": pd.DataFrame(
            columns=["id", "employee_id", "bank_name", "account_number", "ifsc_code", "account_type"])
    }

    tables["users"] = tables["users"].astype({"id": int, "password_changed": int})
    tables["employees"] = tables["employees"].astype({"id": int, "salary": float, "is_active": int})
    tables["attendance"] = tables["attendance"].astype({"id": int, "employee_id": int})
    tables["performance"] = tables["performance"].astype({"id": int, "employee_id": int, "rating": float})
    tables["benefits"] = tables["benefits"].astype(
        {"id": int, "employee_id": int, "health_insurance": int, "provident_fund": int, "paid_time_off": int})
    tables["recruitment"] = tables["recruitment"].astype({"id": int})
    tables["leave_requests"] = tables["leave_requests"].astype({"id": int, "employee_id": int})
    tables["payroll_transactions"] = tables["payroll_transactions"].astype(
        {"id": int, "employee_id": int, "gross_pay": float, "net_pay": float})
    tables["payroll_deductions"] = tables["payroll_deductions"].astype({"id": int, "employee_id": int, "amount": float})
    tables["payroll_allowances"] = tables["payroll_allowances"].astype({"id": int, "employee_id": int, "amount": float})
    tables["bank_details"] = tables["bank_details"].astype({"id": int, "employee_id": int})

    hashed_password = bcrypt.hashpw("Admin@123".encode('utf-8'), bcrypt.gensalt())
    admin_user = pd.DataFrame([{
        "id": 1,
        "email": "admin@hrms.com",
        "password": hashed_password.decode('utf-8'),
        "role": "admin",
        "user_type": "admin",
        "password_changed": 0
    }])
    tables["users"] = pd.concat([tables["users"], admin_user], ignore_index=True)

    save_db(tables)


def validate_password(password, user_type):
    if user_type.lower() == "admin":
        if len(password) < 8:
            return False, "Admin password must be at least 8 characters long"
        if not any(c.isupper() for c in password):
            return False, "Admin password must contain at least one uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Admin password must contain at least one lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Admin password must contain at least one number"
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Admin password must contain at least one special character"
        return True, "Password valid"
    else:
        if len(password) < 6:
            return False, "Employee password must be at least 6 characters long"
        if not any(c.isdigit() for c in password):
            return False, "Employee password must contain at least one number"
        return True, "Password valid"


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def check_password(password, hashed):
    try:
        hashed_bytes = hashed.encode('utf-8') if isinstance(hashed, str) else hashed
        return bcrypt.checkpw(password.encode('utf-8'), hashed_bytes)
    except Exception as e:
        st.error(f"Password check error: {str(e)}")
        return False


def create_employee_user(email, password):
    is_valid, message = validate_password(password, "employee")
    if not is_valid:
        return False, message

    tables = get_db_connection()
    users = tables.get("users",
                       pd.DataFrame(columns=["id", "email", "password", "role", "user_type", "password_changed"]))

    if email in users["email"].values:
        return False, "Email already exists"

    new_id = users["id"].max() + 1 if not users.empty else 1
    hashed_password = hash_password(password)
    new_user = pd.DataFrame([{
        "id": new_id,
        "email": email,
        "password": hashed_password.decode('utf-8'),
        "role": "employee",
        "user_type": "employee",
        "password_changed": 0
    }])
    tables["users"] = pd.concat([users, new_user], ignore_index=True)
    save_db(tables)
    return True, "User created successfully"


def delete_employee(employee_id):
    tables = get_db_connection()
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))
    users = tables.get("users",
                       pd.DataFrame(columns=["id", "email", "password", "role", "user_type", "password_changed"]))

    employee = employees[employees["id"] == employee_id]
    if employee.empty:
        return False, "Employee not found"

    employee_email = employee["email"].iloc[0]
    employees.loc[employees["id"] == employee_id, "is_active"] = 0
    users = users[users["email"] != employee_email]
    tables["employees"] = employees
    tables["users"] = users
    save_db(tables)
    return True, "Employee deleted successfully"


def login_user(email, password, user_type):
    tables = get_db_connection()
    users = tables.get("users",
                       pd.DataFrame(columns=["id", "email", "password", "role", "user_type", "password_changed"]))

    user = users[(users["email"] == email) & (users["user_type"] == user_type.lower())]
    if not user.empty and check_password(password, user["password"].iloc[0]):
        return True, user["role"].iloc[0], user["user_type"].iloc[0]
    return False, None, None


def get_departments():
    tables = get_db_connection()
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))
    departments = employees[employees["is_active"] == 1]["department"].dropna().unique().tolist()
    return departments


def get_active_employees():
    tables = get_db_connection()
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))
    active_employees = employees[employees["is_active"] == 1][["id", "first_name", "last_name"]].sort_values(
        ["first_name", "last_name"]).values.tolist()
    return active_employees


def display_pdf(file_path):
    try:
        if file_path and os.path.exists(file_path) and file_path.endswith('.pdf'):
            with open(file_path, "rb") as f:
                pdf_data = f.read()
            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.warning("No valid PDF resume available to display.")
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")


def show_dashboard():
    st.title("HR Dashboard")
    tables = get_db_connection()
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))
    recruitment = tables.get("recruitment", pd.DataFrame(
        columns=["id", "position", "department", "status", "applicant_name", "applicant_email", "application_date",
                 "resume_path"]))
    leave_requests = tables.get("leave_requests", pd.DataFrame(
        columns=["id", "employee_id", "start_date", "end_date", "leave_type", "reason", "status", "created_at"]))
    attendance = tables.get("attendance", pd.DataFrame(columns=["id", "employee_id", "check_in", "check_out"]))

    col1, col2, col3, col4 = st.columns(4)
    total_employees = len(employees[employees["is_active"] == 1])
    col1.metric("Total Employees", total_employees)

    avg_salary = employees[employees["is_active"] == 1]["salary"].mean() if not employees[
        employees["is_active"] == 1].empty else 0
    col2.metric("Average Salary", f"₹{avg_salary:,.2f}")

    total_departments = len(employees[employees["is_active"] == 1]["department"].dropna().unique())
    col3.metric("Departments", total_departments)

    open_positions = len(recruitment[recruitment["status"] == "Open"])
    col4.metric("Open Positions", open_positions)

    dept_data = employees[employees["is_active"] == 1]["department"].value_counts().reset_index()
    dept_data.columns = ["Department", "Count"]

    if not dept_data.empty:
        fig = px.pie(dept_data, values="Count", names="Department", title="Employee Distribution by Department")
        st.plotly_chart(fig)

        salary_data = employees[employees["is_active"] == 1].groupby("department")["salary"].mean().reset_index()
        salary_data.columns = ["department", "avg_salary"]
        fig2 = px.bar(salary_data, x="department", y="avg_salary", title="Average Salary by Department (₹)")
        st.plotly_chart(fig2)
    else:
        st.info("No department data available yet.")

    st.subheader("Recent Activities")
    leaves = leave_requests.merge(
        employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
        left_on="employee_id",
        right_on="employee_id_ref",
        how="left"
    )
    leaves = leaves.sort_values("created_at", ascending=False).head(5)
    if not leaves.empty:
        st.write("Recent Leave Requests:")
        st.dataframe(leaves.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}))
    else:
        st.info("No recent leave requests.")

    attendance = attendance.merge(
        employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
        left_on="employee_id",
        right_on="employee_id_ref",
        how="left"
    )
    attendance = attendance.sort_values("check_in", ascending=False).head(5)
    if not attendance.empty:
        st.write("Recent Attendance:")
        st.dataframe(attendance.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}))
    else:
        st.info("No recent attendance records.")


def employee_management():
    st.title("Employee Management")
    tab1, tab2, tab3 = st.tabs(["Employee List", "Add Employee", "Delete Employee"])

    with tab1:
        tables = get_db_connection()
        employees = tables.get("employees", pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]))
        active_employees = employees[employees["is_active"] == 1][
            ["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title", "department",
             "salary"]]
        if not active_employees.empty:
            st.dataframe(
                active_employees.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No employees found in the database.")

    with tab2:
        with st.form("add_employee_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                employee_id = st.text_input("Employee ID*", key="emp_id")
                first_name = st.text_input("First Name*", key="first_name")
                email = st.text_input("Email*", key="email")
                phone = st.text_input("Phone*", key="phone")
                job_title = st.text_input("Job Title*", key="job_title")
                salary = st.number_input("Salary (₹)*", min_value=0.0, step=1000.0, key="salary")
            with col2:
                last_name = st.text_input("Last Name*", key="last_name")
                password = st.text_input("Password*", type="password", key="password")
                hire_date = st.date_input("Hire Date*", value=date.today(), key="hire_date")
                department = st.text_input("Department*", key="department")

            submitted = st.form_submit_button("Add Employee")
            if submitted:
                if not all([employee_id, first_name, last_name, email, password, phone, job_title, department]):
                    st.error("Please fill all required fields (*)")
                else:
                    tables = get_db_connection()
                    users = tables.get("users", pd.DataFrame(
                        columns=["id", "email", "password", "role", "user_type", "password_changed"]))
                    if email in users["email"].values:
                        st.error("Email already exists. Please use a unique email.")
                    else:
                        is_valid, message = validate_password(password, "employee")
                        if not is_valid:
                            st.error(message)
                        else:
                            employees = tables.get("employees", pd.DataFrame(
                                columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date",
                                         "job_title", "department", "salary", "is_active"]))
                            if employee_id in employees["employee_id"].values:
                                st.error("Employee ID already exists")
                            else:
                                success, message = create_employee_user(email, password)
                                if success:
                                    new_id = employees["id"].max() + 1 if not employees.empty else 1
                                    new_employee = pd.DataFrame([{
                                        "id": int(new_id),
                                        "employee_id": employee_id,
                                        "first_name": first_name,
                                        "last_name": last_name,
                                        "email": email,
                                        "phone": phone,
                                        "hire_date": hire_date,
                                        "job_title": job_title,
                                        "department": department,
                                        "salary": float(salary),
                                        "is_active": 1
                                    }])
                                    new_employee = new_employee.astype({"id": int, "salary": float, "is_active": int})
                                    tables["employees"] = pd.concat([employees, new_employee], ignore_index=True)
                                    save_db(tables)
                                    st.success("Employee added successfully!")
                                    st.rerun()
                                else:
                                    st.error(message)

    with tab3:
        st.subheader("Delete Employee")
        tables = get_db_connection()
        employees = tables.get("employees", pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]))
        active_employees = employees[employees["is_active"] == 1]
        if not active_employees.empty:
            col1, col2 = st.columns([3, 1])
            with col1:
                employee_to_delete = st.selectbox(
                    "Select Employee to Delete",
                    options=active_employees["id"].tolist(),
                    format_func=lambda
                        x: f"{active_employees[active_employees['id'] == x]['employee_id'].iloc[0]} - {active_employees[active_employees['id'] == x]['first_name'].iloc[0]} {active_employees[active_employees['id'] == x]['last_name'].iloc[0]}",
                    key="delete_employee_select"
                )
            with col2:
                if st.button("Delete Employee", key="delete_employee_button"):
                    success, message = delete_employee(employee_to_delete)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        else:
            st.info("No employees found in the database.")


def leave_management():
    st.title("Leave Management")
    tab1, tab2, tab3 = st.tabs(["Leave Requests", "Request Leave", "Delete Leave Request"])

    with tab1:
        tables = get_db_connection()
        leave_requests = tables.get("leave_requests", pd.DataFrame(
            columns=["id", "employee_id", "start_date", "end_date", "leave_type", "reason", "status", "created_at"]))
        employees = tables.get("employees", pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]))
        leaves = leave_requests.merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        leaves = leaves.sort_values("created_at", ascending=False)
        if not leaves.empty:
            st.dataframe(
                leaves.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=400
            )
            st.subheader("Manage Leave Request")
            if "id" in leaves.columns:
                leave_id = st.selectbox(
                    "Select Leave Request",
                    leaves["id"].tolist(),
                    format_func=lambda
                        x: f"Leave {x} - {leaves[leaves['id'] == x]['first_name'].iloc[0] if pd.notna(leaves[leaves['id'] == x]['first_name'].iloc[0]) else 'Unknown'} {leaves[leaves['id'] == x]['last_name'].iloc[0] if pd.notna(leaves[leaves['id'] == x]['last_name'].iloc[0]) else 'Employee'}",
                    key="manage_leave_select"
                )
                status = st.selectbox("Update Status", ["Pending", "Approved", "Rejected"], key="leave_status_select")
                if st.button("Update Status", key="update_leave_status_button"):
                    tables = get_db_connection()
                    leave_requests = tables.get("leave_requests", pd.DataFrame(
                        columns=["id", "employee_id", "start_date", "end_date", "leave_type", "reason", "status",
                                 "created_at"]))
                    leave_requests.loc[leave_requests["id"] == leave_id, "status"] = status
                    tables["leave_requests"] = leave_requests
                    save_db(tables)
                    st.success("Leave status updated!")
                    st.rerun()
            else:
                st.error("Error: 'id' column not found in leave requests. Please check the database.")
        else:
            st.info("No leave requests found.")

    with tab2:
        with st.form("request_leave_form", clear_on_submit=True):
            employee = st.selectbox(
                "Employee",
                options=get_active_employees(),
                format_func=lambda x: f"{x[1]} {x[2]}",
                key="request_leave_employee"
            )
            start_date = st.date_input("Start Date", value=date.today(), key="leave_start_date")
            end_date = st.date_input("End Date", value=date.today(), key="leave_end_date")
            leave_type = st.selectbox("Leave Type", ["Casual", "Sick", "Earned", "Maternity/Paternity"],
                                      key="leave_type")
            reason = st.text_area("Reason", key="leave_reason")
            if st.form_submit_button("Submit Leave Request"):
                if not employee or not reason:
                    st.error("Employee and reason are required!")
                elif start_date > end_date:
                    st.error("End date must be after start date!")
                else:
                    tables = get_db_connection()
                    leave_requests = tables.get("leave_requests", pd.DataFrame(
                        columns=["id", "employee_id", "start_date", "end_date", "leave_type", "reason", "status",
                                 "created_at"]))
                    new_id = leave_requests["id"].max() + 1 if not leave_requests.empty else 1
                    new_leave = pd.DataFrame([{
                        "id": new_id,
                        "employee_id": employee[0],
                        "start_date": start_date,
                        "end_date": end_date,
                        "leave_type": leave_type,
                        "reason": reason,
                        "status": "Pending",
                        "created_at": datetime.now()
                    }])
                    tables["leave_requests"] = pd.concat([leave_requests, new_leave], ignore_index=True)
                    save_db(tables)
                    st.success("Leave request submitted!")
                    st.rerun()

    with tab3:
        st.subheader("Delete Leave Request")
        tables = get_db_connection()
        leave_requests = tables.get("leave_requests", pd.DataFrame(
            columns=["id", "employee_id", "start_date", "end_date", "leave_type", "reason", "status", "created_at"]))
        employees = tables.get("employees", pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]))
        leaves = leave_requests.merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        leaves = leaves.sort_values("created_at", ascending=False)
        if not leaves.empty:
            if "id" in leaves.columns:
                col1, col2 = st.columns([3, 1])
                with col1:
                    leave_to_delete = st.selectbox(
                        "Select Leave Request to Delete",
                        options=leaves["id"].tolist(),
                        format_func=lambda
                            x: f"Leave {x} - {leaves[leaves['id'] == x]['first_name'].iloc[0] if pd.notna(leaves[leaves['id'] == x]['first_name'].iloc[0]) else 'Unknown'} {leaves[leaves['id'] == x]['last_name'].iloc[0] if pd.notna(leaves[leaves['id'] == x]['last_name'].iloc[0]) else 'Employee'}",
                        key="delete_leave_select"
                    )
                with col2:
                    if st.button("Delete Leave Request", key="delete_leave_button"):
                        tables = get_db_connection()
                        leave_requests = tables.get("leave_requests", pd.DataFrame(
                            columns=["id", "employee_id", "start_date", "end_date", "leave_type", "reason", "status",
                                     "created_at"]))
                        leave_requests = leave_requests[leave_requests["id"] != leave_to_delete]
                        tables["leave_requests"] = leave_requests
                        save_db(tables)
                        st.success("Leave request deleted successfully!")
                        st.rerun()
            else:
                st.error("Error: 'id' column not found in leave requests. Please check the database.")
        else:
            st.info("No leave requests found.")


def attendance_tracking():
    st.title("Attendance Tracking")
    tab1, tab2, tab3 = st.tabs(["Attendance Records", "Record Attendance", "Delete Attendance"])

    with tab1:
        tables = get_db_connection()
        attendance = tables.get("attendance", pd.DataFrame(columns=["id", "employee_id", "check_in", "check_out"]))
        employees = tables.get("employees", pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]))
        attendance_records = attendance.merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        attendance_records = attendance_records.sort_values("check_in", ascending=False)
        if not attendance_records.empty:
            st.dataframe(
                attendance_records.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No attendance records found.")

    with tab2:
        with st.form("record_attendance_form", clear_on_submit=True):
            employee = st.selectbox(
                "Employee",
                options=get_active_employees(),
                format_func=lambda x: f"{x[1]} {x[2]}",
                key="attendance_employee"
            )
            check_in_date = st.date_input("Check-In Date", value=date.today(), key="check_in_date")
            check_in_time = st.time_input("Check-In Time", value=datetime.now().time(), key="check_in_time")
            check_out_date = st.date_input("Check-Out Date (Optional)", value=None, key="check_out_date")
            check_out_time = st.time_input("Check-Out Time (Optional)", value=None, key="check_out_time")
            if st.form_submit_button("Record Attendance"):
                if not employee:
                    st.error("Employee is required!")
                else:
                    check_in = datetime.combine(check_in_date, check_in_time)
                    check_out = None
                    if check_out_date and check_out_time:
                        check_out = datetime.combine(check_out_date, check_out_time)
                        if check_out <= check_in:
                            st.error("Check-out time must be after check-in time!")
                            return
                    tables = get_db_connection()
                    attendance = tables.get("attendance",
                                            pd.DataFrame(columns=["id", "employee_id", "check_in", "check_out"]))
                    new_id = attendance["id"].max() + 1 if not attendance.empty else 1
                    new_attendance = pd.DataFrame([{
                        "id": new_id,
                        "employee_id": employee[0],
                        "check_in": check_in,
                        "check_out": check_out
                    }])
                    tables["attendance"] = pd.concat([attendance, new_attendance], ignore_index=True)
                    save_db(tables)
                    st.success("Attendance recorded!")
                    st.rerun()

    with tab3:
        st.subheader("Delete Attendance Record")
        tables = get_db_connection()
        attendance = tables.get("attendance", pd.DataFrame(columns=["id", "employee_id", "check_in", "check_out"]))
        employees = tables.get("employees", pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]))
        attendance_records = attendance.merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        attendance_records = attendance_records.sort_values("check_in", ascending=False)
        if not attendance_records.empty:
            if "id" in attendance_records.columns:
                col1, col2 = st.columns([3, 1])
                with col1:
                    attendance_to_delete = st.selectbox(
                        "Select Attendance Record to Delete",
                        options=attendance_records["id"].tolist(),
                        format_func=lambda
                            x: f"Attendance {x} - {attendance_records[attendance_records['id'] == x]['first_name'].iloc[0] if pd.notna(attendance_records[attendance_records['id'] == x]['first_name'].iloc[0]) else 'Unknown'} {attendance_records[attendance_records['id'] == x]['last_name'].iloc[0] if pd.notna(attendance_records[attendance_records['id'] == x]['last_name'].iloc[0]) else 'Employee'} - {attendance_records[attendance_records['id'] == x]['check_in'].iloc[0]}",
                        key="delete_attendance_select"
                    )
                with col2:
                    if st.button("Delete Attendance", key="delete_attendance_button"):
                        tables = get_db_connection()
                        attendance = tables.get("attendance",
                                                pd.DataFrame(columns=["id", "employee_id", "check_in", "check_out"]))
                        attendance = attendance[attendance["id"] != attendance_to_delete]
                        tables["attendance"] = attendance
                        save_db(tables)
                        st.success("Attendance record deleted successfully!")
                        st.rerun()
            else:
                st.error("Error: 'id' column not found in attendance records. Please check the database.")
        else:
            st.info("No attendance records found.")


def performance_management():
    st.title("Performance Management")
    tab1, tab2, tab3 = st.tabs(["Performance Reviews", "Add Review", "Delete Review"])

    with tab1:
        tables = get_db_connection()
        performance = tables.get("performance",
                                 pd.DataFrame(columns=["id", "employee_id", "review_date", "rating", "comments"]))
        employees = tables.get("employees", pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]))
        reviews = performance.merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        reviews = reviews.sort_values("review_date", ascending=False)
        if not reviews.empty:
            st.dataframe(
                reviews.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No performance reviews found.")

    with tab2:
        with st.form("add_review_form", clear_on_submit=True):
            employee = st.selectbox(
                "Employee",
                options=get_active_employees(),
                format_func=lambda x: f"{x[1]} {x[2]}",
                key="performance_employee"
            )
            review_date = st.date_input("Review Date", value=date.today(), key="review_date")
            rating = st.slider("Rating", 1.0, 5.0, 3.0, 0.1, key="review_rating")
            comments = st.text_area("Comments", key="review_comments")
            if st.form_submit_button("Submit Review"):
                if not employee or not comments:
                    st.error("Employee and comments are required!")
                else:
                    tables = get_db_connection()
                    performance = tables.get("performance", pd.DataFrame(
                        columns=["id", "employee_id", "review_date", "rating", "comments"]))
                    new_id = performance["id"].max() + 1 if not performance.empty else 1
                    new_review = pd.DataFrame([{
                        "id": new_id,
                        "employee_id": employee[0],
                        "review_date": review_date,
                        "rating": rating,
                        "comments": comments
                    }])
                    tables["performance"] = pd.concat([performance, new_review], ignore_index=True)
                    save_db(tables)
                    st.success("Performance review added!")
                    st.rerun()

    with tab3:
        st.subheader("Delete Performance Review")
        tables = get_db_connection()
        performance = tables.get("performance",
                                 pd.DataFrame(columns=["id", "employee_id", "review_date", "rating", "comments"]))
        employees = tables.get("employees", pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]))
        reviews = performance.merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        reviews = reviews.sort_values("review_date", ascending=False)
        if not reviews.empty:
            if "id" in reviews.columns:
                col1, col2 = st.columns([3, 1])
                with col1:
                    review_to_delete = st.selectbox(
                        "Select Review to Delete",
                        options=reviews["id"].tolist(),
                        format_func=lambda
                            x: f"Review {x} - {reviews[reviews['id'] == x]['first_name'].iloc[0] if pd.notna(reviews[reviews['id'] == x]['first_name'].iloc[0]) else 'Unknown'} {reviews[reviews['id'] == x]['last_name'].iloc[0] if pd.notna(reviews[reviews['id'] == x]['last_name'].iloc[0]) else 'Employee'} - {reviews[reviews['id'] == x]['review_date'].iloc[0]}",
                        key="delete_review_select"
                    )
                with col2:
                    if st.button("Delete Review", key="delete_review_button"):
                        tables = get_db_connection()
                        performance = tables.get("performance", pd.DataFrame(
                            columns=["id", "employee_id", "review_date", "rating", "comments"]))
                        performance = performance[performance["id"] != review_to_delete]
                        tables["performance"] = performance
                        save_db(tables)
                        st.success("Performance review deleted successfully!")
                        st.rerun()
            else:
                st.error("Error: 'id' column not found in performance reviews. Please check the database.")
        else:
            st.info("No performance reviews found.")


def recruitment_management(is_admin=True):
    st.title("Recruitment Management")
    tabs = ["Job Openings", "Add Job Opening", "Delete Job Opening"] if is_admin else ["Job Openings"]
    tab_objects = st.tabs(tabs)

    with tab_objects[0]:
        tables = get_db_connection()
        recruitment = tables.get("recruitment", pd.DataFrame(
            columns=["id", "position", "department", "status", "applicant_name", "applicant_email", "application_date",
                     "resume_path"]))
        recruitment = recruitment.sort_values("application_date", ascending=False)
        if not recruitment.empty:
            recruitment_display = recruitment.copy()
            recruitment_display["resume"] = recruitment["resume_path"].apply(
                lambda x: f"[Download Resume]({x})" if pd.notna(x) and os.path.exists(x) else "No Resume"
            )
            recruitment_display["view_resume"] = recruitment["resume_path"].apply(
                lambda x: x if pd.notna(x) and os.path.exists(x) else None
            )
            st.dataframe(
                recruitment_display[
                    ["id", "position", "department", "status", "applicant_name", "applicant_email", "application_date",
                     "resume", "view_resume"]].style.set_properties(
                    **{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=400
            )
            selected_job_id = st.selectbox(
                "Select Job to View Resume",
                recruitment["id"].tolist(),
                format_func=lambda
                    x: f"Job {x} - {recruitment[recruitment['id'] == x]['position'].iloc[0]} - {recruitment[recruitment['id'] == x]['applicant_name'].iloc[0]}",
                key="view_resume_select"
            )
            resume_path = recruitment[recruitment["id"] == selected_job_id]["resume_path"].iloc[0] if not recruitment[
                recruitment["id"] == selected_job_id].empty else None
            if resume_path and os.path.exists(resume_path):
                st.subheader("Resume Preview")
                display_pdf(resume_path)
                with open(resume_path, "rb") as f:
                    st.download_button(
                        label="Download Resume",
                        data=f,
                        file_name=os.path.basename(resume_path),
                        mime="application/pdf",
                        key=f"download_resume_{selected_job_id}"
                    )
            else:
                st.info("No resume available for this job opening.")
            if is_admin:
                st.subheader("Update Job Status")
                job_id = st.selectbox(
                    "Select Job Opening",
                    recruitment["id"].tolist(),
                    format_func=lambda
                        x: f"Job {x} - {recruitment[recruitment['id'] == x]['position'].iloc[0]} - {recruitment[recruitment['id'] == x]['applicant_name'].iloc[0]}",
                    key="manage_job_select"
                )
                status = st.selectbox("Update Status", ["Open", "Closed", "On Hold"], key="job_status_select")
                resume_path = recruitment[recruitment["id"] == job_id]["resume_path"].iloc[0] if not recruitment[
                    recruitment["id"] == job_id].empty else None
                if resume_path and os.path.exists(resume_path):
                    st.write("Resume for Selected Job:")
                    display_pdf(resume_path)
                if st.button("Update Status", key="update_job_status_button"):
                    tables = get_db_connection()
                    recruitment = tables.get("recruitment", pd.DataFrame(
                        columns=["id", "position", "department", "status", "applicant_name", "applicant_email",
                                 "application_date", "resume_path"]))
                    recruitment.loc[recruitment["id"] == job_id, "status"] = status
                    tables["recruitment"] = recruitment
                    save_db(tables)
                    st.success("Job status updated!")
                    st.rerun()
        else:
            st.info("No job openings found.")

    if is_admin:
        with tab_objects[1]:
            with st.form("add_job_form", clear_on_submit=True):
                position = st.text_input("Position", key="job_position")
                department = st.text_input("Department", key="job_department")
                applicant_name = st.text_input("Applicant Name", key="job_applicant_name")
                applicant_email = st.text_input("Applicant Email", key="job_applicant_email")
                application_date = st.date_input("Application Date", value=date.today(), key="job_application_date")
                resume = st.file_uploader("Upload Resume", type=['pdf'], key="job_resume")
                status = st.selectbox("Status", ["Open", "Closed", "On Hold"], key="job_status")
                if st.form_submit_button("Add Job Opening"):
                    if not all([position, department, applicant_name, applicant_email]):
                        st.error("All fields except resume are required!")
                    else:
                        resume_path = None
                        if resume:
                            if not os.path.exists(RESUME_DIR):
                                os.makedirs(RESUME_DIR)
                            resume_path = os.path.join(RESUME_DIR, f"{applicant_name}_{application_date}.pdf")
                            with open(resume_path, "wb") as f:
                                f.write(resume.read())
                        tables = get_db_connection()
                        recruitment = tables.get("recruitment", pd.DataFrame(
                            columns=["id", "position", "department", "status", "applicant_name", "applicant_email",
                                     "application_date", "resume_path"]))
                        new_id = recruitment["id"].max() + 1 if not recruitment.empty else 1
                        new_job = pd.DataFrame([{
                            "id": new_id,
                            "position": position,
                            "department": department,
                            "status": status,
                            "applicant_name": applicant_name,
                            "applicant_email": applicant_email,
                            "application_date": application_date,
                            "resume_path": resume_path
                        }])
                        tables["recruitment"] = pd.concat([recruitment, new_job], ignore_index=True)
                        save_db(tables)
                        st.success("Job opening added!")
                        st.rerun()

        with tab_objects[2]:
            st.subheader("Delete Job Opening")
            tables = get_db_connection()
            recruitment = tables.get("recruitment", pd.DataFrame(
                columns=["id", "position", "department", "status", "applicant_name", "applicant_email",
                         "application_date", "resume_path"]))
            recruitment = recruitment.sort_values("application_date", ascending=False)
            if not recruitment.empty:
                col1, col2 = st.columns([3, 1])
                with col1:
                    job_to_delete = st.selectbox(
                        "Select Job Opening to Delete",
                        options=recruitment["id"].tolist(),
                        format_func=lambda
                            x: f"Job {x} - {recruitment[recruitment['id'] == x]['position'].iloc[0]} - {recruitment[recruitment['id'] == x]['applicant_name'].iloc[0]}",
                        key="delete_job_select"
                    )
                with col2:
                    if st.button("Delete Job Opening", key="delete_job_button"):
                        tables = get_db_connection()
                        recruitment = tables.get("recruitment", pd.DataFrame(
                            columns=["id", "position", "department", "status", "applicant_name", "applicant_email",
                                     "application_date", "resume_path"]))
                        resume_path = recruitment[recruitment["id"] == job_to_delete]["resume_path"].iloc[0] if not \
                        recruitment[recruitment["id"] == job_to_delete].empty else None
                        if resume_path and os.path.exists(resume_path):
                            try:
                                os.remove(resume_path)
                            except Exception as e:
                                st.warning(f"Could not delete resume file: {str(e)}")
                        recruitment = recruitment[recruitment["id"] != job_to_delete]
                        tables["recruitment"] = recruitment
                        save_db(tables)
                        st.success("Job opening deleted successfully!")
                        st.rerun()
            else:
                st.info("No job openings found.")


def get_employees_for_payroll(department):
    tables = get_db_connection()
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))
    if department == "All":
        return employees[employees["is_active"] == 1].to_dict("records")
    else:
        return employees[(employees["is_active"] == 1) & (employees["department"] == department)].to_dict("records")


def calculate_overtime(employee_id, payroll_date):
    tables = get_db_connection()
    attendance = tables.get("attendance", pd.DataFrame(columns=["id", "employee_id", "check_in", "check_out"]))
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))

    payroll_date = pd.to_datetime(payroll_date)
    thirty_days_ago = payroll_date - pd.Timedelta(days=30)
    relevant_attendance = attendance[
        (attendance["employee_id"] == employee_id) & (pd.to_datetime(attendance["check_in"]) >= thirty_days_ago) & (
            attendance["check_out"].notna())]

    overtime_hours = 0
    for _, row in relevant_attendance.iterrows():
        check_in = pd.to_datetime(row["check_in"])
        check_out = pd.to_datetime(row["check_out"])
        hours = (check_out - check_in).total_seconds() / 3600
        if hours > 8:
            overtime_hours += hours - 8

    salary = employees[employees["id"] == employee_id]["salary"].iloc[0] if not employees[
        employees["id"] == employee_id].empty else 0
    if salary == 0:
        return 0
    hourly_rate = salary / (52 * 40)
    return overtime_hours * hourly_rate * 1.5


def calculate_gross_pay(employee_id, payroll_date):
    tables = get_db_connection()
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))
    allowances = tables.get("payroll_allowances",
                            pd.DataFrame(columns=["id", "employee_id", "allowance_type", "amount", "effective_date"]))

    base_salary = employees[employees["id"] == employee_id]["salary"].iloc[0] if not employees[
        employees["id"] == employee_id].empty else 0
    relevant_allowances = allowances[(allowances["employee_id"] == employee_id) & (
                pd.to_datetime(allowances["effective_date"]) <= pd.to_datetime(payroll_date))]
    allowances_total = relevant_allowances["amount"].sum() if not relevant_allowances.empty else 0
    overtime_pay = calculate_overtime(employee_id, payroll_date)
    return base_salary + allowances_total + overtime_pay


def calculate_deductions(employee_id, gross_pay):
    tables = get_db_connection()
    deductions = tables.get("payroll_deductions",
                            pd.DataFrame(columns=["id", "employee_id", "deduction_type", "amount", "effective_date"]))

    fixed_deductions = deductions[deductions["employee_id"] == employee_id]["amount"].sum() if not deductions[
        deductions["employee_id"] == employee_id].empty else 0

    annual_salary = gross_pay * 12
    if annual_salary <= 250000:
        income_tax = 0
    elif annual_salary <= 500000:
        income_tax = (annual_salary - 250000) * 0.05
    elif annual_salary <= 1000000:
        income_tax = 12500 + (annual_salary - 500000) * 0.20
    else:
        income_tax = 112500 + (annual_salary - 1000000) * 0.30
    monthly_tax = income_tax / 12

    provident_fund = gross_pay * 0.12
    professional_tax = 200
    total_deductions = fixed_deductions + monthly_tax + provident_fund + professional_tax
    return total_deductions


def process_payroll(payroll_date, department):
    tables = get_db_connection()
    payroll_transactions = tables.get("payroll_transactions", pd.DataFrame(
        columns=["id", "employee_id", "transaction_date", "gross_pay", "net_pay", "payment_method", "status",
                 "created_at"]))
    employees = get_employees_for_payroll(department)
    if not employees:
        st.error("No employees found for the selected department!")
        return
    new_transactions = []
    for employee in employees:
        gross_pay = calculate_gross_pay(employee["id"], payroll_date)
        deductions = calculate_deductions(employee["id"], gross_pay)
        net_pay = gross_pay - deductions
        new_id = payroll_transactions["id"].max() + 1 if not payroll_transactions.empty else 1
        new_transactions.append({
            "id": new_id,
            "employee_id": employee["id"],
            "transaction_date": payroll_date,
            "gross_pay": gross_pay,
            "net_pay": net_pay,
            "payment_method": "direct_deposit",
            "status": "pending",
            "created_at": datetime.now()
        })
    if new_transactions:
        new_transactions_df = pd.DataFrame(new_transactions)
        tables["payroll_transactions"] = pd.concat([payroll_transactions, new_transactions_df], ignore_index=True)
        save_db(tables)
        st.success("Payroll processed successfully!")
        show_payroll_summary(payroll_date)


def show_payroll_summary(payroll_date):
    tables = get_db_connection()
    payroll_transactions = tables.get("payroll_transactions", pd.DataFrame(
        columns=["id", "employee_id", "transaction_date", "gross_pay", "net_pay", "payment_method", "status",
                 "created_at"]))
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))

    summary = payroll_transactions[
        pd.to_datetime(payroll_transactions["transaction_date"]) == pd.to_datetime(payroll_date)].merge(
        employees[["id", "department"]], left_on="employee_id", right_on="id", how="left"
    ).groupby("department").agg({
        "employee_id": "count",
        "gross_pay": "sum",
        "net_pay": "sum"
    }).reset_index()
    summary.columns = ["department", "employee_count", "total_gross", "total_net"]

    if not summary.empty:
        st.subheader("Payroll Summary")
        st.dataframe(
            summary.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
            use_container_width=True
        )
        fig = go.Figure(data=[
            go.Bar(name="Gross Pay", x=summary["department"], y=summary["total_gross"]),
            go.Bar(name="Net Pay", x=summary["department"], y=summary["total_net"])
        ])
        fig.update_layout(title="Payroll Distribution by Department (₹)")
        st.plotly_chart(fig)
    else:
        st.info("No payroll data available for this date.")


def show_employee_compensation(employee_id):
    tables = get_db_connection()
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))
    allowances = tables.get("payroll_allowances",
                            pd.DataFrame(columns=["id", "employee_id", "allowance_type", "amount", "effective_date"]))
    deductions = tables.get("payroll_deductions",
                            pd.DataFrame(columns=["id", "employee_id", "deduction_type", "amount", "effective_date"]))
    bank_details = tables.get("bank_details", pd.DataFrame(
        columns=["id", "employee_id", "bank_name", "account_number", "ifsc_code", "account_type"]))

    employee = employees[employees["id"] == employee_id]
    if not employee.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("Base Salary:", f"₹{employee['salary'].iloc[0]:,.2f}")
            employee_allowances = allowances[allowances["employee_id"] == employee_id]
            if not employee_allowances.empty:
                st.write("Allowances:")
                st.dataframe(employee_allowances)
        with col2:
            employee_deductions = deductions[deductions["employee_id"] == employee_id]
            if not employee_deductions.empty:
                st.write("Deductions:")
                st.dataframe(employee_deductions)
            employee_bank_details = bank_details[bank_details["employee_id"] == employee_id]
            if not employee_bank_details.empty:
                st.write("Bank Details:")
                st.write(f"Account: {employee_bank_details['account_number'].iloc[0]}")
                st.write(f"Bank: {employee_bank_details['bank_name'].iloc[0]}")
    else:
        st.info("No compensation details found.")


def generate_payroll_report(report_type):
    tables = get_db_connection()
    payroll_transactions = tables.get("payroll_transactions", pd.DataFrame(columns=["id", "employee_id", "transaction_date", "gross_pay", "net_pay", "payment_method", "status", "created_at"]))
    employees = tables.get("employees", pd.DataFrame(columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title", "department", "salary", "is_active"]))
    deductions = tables.get("payroll_deductions", pd.DataFrame(columns=["id", "employee_id", "deduction_type", "amount", "effective_date"]))

    if report_type == "Payroll Summary":
        data = payroll_transactions.merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        data = data.sort_values("transaction_date", ascending=False)
        if not data.empty:
            st.dataframe(
                data.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=400
            )
            fig = px.bar(data, x="transaction_date", y="gross_pay", title="Payroll Trends (₹)")
            st.plotly_chart(fig)
        else:
            st.info("No payroll data available.")
    elif report_type == "Tax Withholding":
        data = deductions[deductions["deduction_type"].str.contains("tax", case=False)].merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        if not data.empty:
            st.dataframe(
                data.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No tax withholding data available.")
    elif report_type == "Benefits Deductions":
        data = deductions[deductions["deduction_type"].str.contains("benefit", case=False)].merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        if not data.empty:
            st.dataframe(
                data.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No benefits deductions data available.")

def show_tax_compliance():
    st.write("Tax Compliance Dashboard")
    st.info("""
    Current Tax Settings (India):
    - Income Tax: As per slabs (0% to 30%)
    - Provident Fund: 12% of gross pay
    - Professional Tax: ₹200/month
    - TDS Filing: Quarterly
    """)
    st.write("Compliance Checklist:")
    st.checkbox("TDS Deposited", value=True)
    st.checkbox("Form 16 Generated", value=True)
    st.checkbox("Quarterly TDS Returns Filed", value=True)
    st.checkbox("PF Contributions Deposited", value=True)


def payroll_management():
    st.title("Payroll Management")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Process Payroll", "Employee Compensation", "Payroll Reports", "Tax & Compliance", "Delete Payroll"])

    with tab1:
        st.subheader("Process Payroll")
        col1, col2 = st.columns(2)
        with col1:
            payroll_date = st.date_input("Payroll Date", value=date.today(), key="payroll_date")
        with col2:
            department = st.selectbox("Department", ["All"] + get_departments(), key="payroll_department")
        if st.button("Calculate Payroll", key="calculate_payroll_button"):
            process_payroll(payroll_date, department)

    with tab2:
        st.subheader("Employee Compensation")
        employees = get_active_employees()
        if employees:
            employee = st.selectbox(
                "Select Employee",
                options=employees,
                format_func=lambda x: f"{x[1]} {x[2]}",
                key="compensation_employee"
            )
            if employee:
                show_employee_compensation(employee[0])
        else:
            st.info("No active employees found.")

    with tab3:
        st.subheader("Payroll Reports")
        report_type = st.selectbox("Report Type", ["Payroll Summary", "Tax Withholding", "Benefits Deductions"],
                                   key="report_type")
        if st.button("Generate Report", key="generate_report_button"):
            generate_payroll_report(report_type)

    with tab4:
        st.subheader("Tax & Compliance")
        show_tax_compliance()

    with tab5:
        st.subheader("Delete Payroll Transaction")
        tables = get_db_connection()
        payroll_transactions = tables.get("payroll_transactions", pd.DataFrame(
            columns=["id", "employee_id", "transaction_date", "gross_pay", "net_pay", "payment_method", "status",
                     "created_at"]))
        employees = tables.get("employees", pd.DataFrame(
            columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                     "department", "salary", "is_active"]))
        payroll = payroll_transactions.merge(
            employees[["id", "first_name", "last_name"]].rename(columns={"id": "employee_id_ref"}),
            left_on="employee_id",
            right_on="employee_id_ref",
            how="left"
        )
        payroll = payroll.sort_values("transaction_date", ascending=False)
        if not payroll.empty:
            if "id" in payroll.columns:
                col1, col2 = st.columns([3, 1])
                with col1:
                    payroll_to_delete = st.selectbox(
                        "Select Payroll Transaction to Delete",
                        options=payroll["id"].tolist(),
                        format_func=lambda
                            x: f"Payroll {x} - {payroll[payroll['id'] == x]['first_name'].iloc[0] if pd.notna(payroll[payroll['id'] == x]['first_name'].iloc[0]) else 'Unknown'} {payroll[payroll['id'] == x]['last_name'].iloc[0] if pd.notna(payroll[payroll['id'] == x]['last_name'].iloc[0]) else 'Employee'} - {payroll[payroll['id'] == x]['transaction_date'].iloc[0]}",
                        key="delete_payroll_select"
                    )
                with col2:
                    if st.button("Delete Payroll", key="delete_payroll_button"):
                        tables = get_db_connection()
                        payroll_transactions = tables.get("payroll_transactions", pd.DataFrame(
                            columns=["id", "employee_id", "transaction_date", "gross_pay", "net_pay", "payment_method",
                                     "status", "created_at"]))
                        payroll_transactions = payroll_transactions[payroll_transactions["id"] != payroll_to_delete]
                        tables["payroll_transactions"] = payroll_transactions
                        save_db(tables)
                        st.success("Payroll transaction deleted successfully!")
                        st.rerun()
            else:
                st.error("Error: 'id' column not found in payroll transactions. Please check the database.")
        else:
            st.info("No payroll transactions found.")


def password_vault():
    st.title("Password Vault")
    st.warning("Note: Passwords are stored as bcrypt hashes for security and cannot be viewed in plain text.")
    tables = get_db_connection()
    users = tables.get("users",
                       pd.DataFrame(columns=["id", "email", "password", "role", "user_type", "password_changed"]))
    employee_users = users[users["user_type"] == "employee"][["email", "password"]]
    if not employee_users.empty:
        st.dataframe(
            employee_users.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No employee accounts found in the database.")


def employee_dashboard():
    st.title(f"Welcome, {st.session_state.employee_name}!")
    tables = get_db_connection()
    employees = tables.get("employees", pd.DataFrame(
        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date", "job_title",
                 "department", "salary", "is_active"]))
    attendance = tables.get("attendance", pd.DataFrame(columns=["id", "employee_id", "check_in", "check_out"]))
    leave_requests = tables.get("leave_requests", pd.DataFrame(
        columns=["id", "employee_id", "start_date", "end_date", "leave_type", "reason", "status", "created_at"]))
    performance = tables.get("performance",
                             pd.DataFrame(columns=["id", "employee_id", "review_date", "rating", "comments"]))
    payroll_transactions = tables.get("payroll_transactions", pd.DataFrame(
        columns=["id", "employee_id", "transaction_date", "gross_pay", "net_pay", "payment_method", "status",
                 "created_at"]))

    employee = employees[employees["id"] == st.session_state.employee_id]
    if not employee.empty:
        st.subheader("Your Details")
        st.write(f"Employee ID: {employee['employee_id'].iloc[0]}")
        st.write(f"Name: {employee['first_name'].iloc[0]} {employee['last_name'].iloc[0]}")
        st.write(f"Department: {employee['department'].iloc[0]}")
        st.write(f"Job Title: {employee['job_title'].iloc[0]}")

        st.subheader("Your Attendance")
        employee_attendance = attendance[attendance["employee_id"] == st.session_state.employee_id].sort_values(
            "check_in", ascending=False)
        if not employee_attendance.empty:
            st.dataframe(
                employee_attendance.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=300
            )
        else:
            st.info("No attendance records found.")

        st.subheader("Your Leave Requests")
        employee_leaves = leave_requests[leave_requests["employee_id"] == st.session_state.employee_id].sort_values(
            "created_at", ascending=False)
        if not employee_leaves.empty:
            st.dataframe(
                employee_leaves.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=300
            )
        else:
            st.info("No leave requests found.")

        st.subheader("Your Performance Reviews")
        employee_performance = performance[performance["employee_id"] == st.session_state.employee_id].sort_values(
            "review_date", ascending=False)
        if not employee_performance.empty:
            st.dataframe(
                employee_performance.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=300
            )
        else:
            st.info("No performance reviews found.")

        st.subheader("Your Payroll")
        employee_payroll = payroll_transactions[
            payroll_transactions["employee_id"] == st.session_state.employee_id].sort_values("transaction_date",
                                                                                             ascending=False).head(3)
        if not employee_payroll.empty:
            st.dataframe(
                employee_payroll.style.set_properties(**{"text-align": "left", "white-space": "pre-wrap"}),
                use_container_width=True,
                height=300
            )
        else:
            st.info("No payroll records found.")

        st.subheader("Job Openings")
        recruitment_management(is_admin=False)

    else:
        st.error("Employee data not found!")


def main():
    st.set_page_config(page_title="HR Management System", layout="wide")
    if not os.path.exists(EXCEL_FILE):
        init_db()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user_type = None
        st.session_state.employee_id = None
        st.session_state.employee_name = None

    if not st.session_state.logged_in:
        st.title("HR Management System - Login")
        user_type = st.selectbox("Login As", ["Admin", "Employee"], key="login_user_type")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_button"):
            success, role, user_type = login_user(email, password, user_type)
            if success:
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user_type = user_type
                if user_type.lower() == "employee":
                    tables = get_db_connection()
                    employees = tables.get("employees", pd.DataFrame(
                        columns=["id", "employee_id", "first_name", "last_name", "email", "phone", "hire_date",
                                 "job_title", "department", "salary", "is_active"]))
                    employee = employees[employees["email"] == email]
                    if not employee.empty:
                        st.session_state.employee_id = employee["id"].iloc[0]
                        st.session_state.employee_name = f"{employee['first_name'].iloc[0]} {employee['last_name'].iloc[0]}"
                    else:
                        st.error("Employee profile not found!")
                        return
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials!")
    else:
        st.sidebar.title(
            f"Welcome, {st.session_state.employee_name if st.session_state.user_type == 'employee' else 'Admin'}")
        if st.sidebar.button("Logout", key="logout_button"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logged out successfully!")
            st.rerun()

        if st.sidebar.button("Refresh Page", key="refresh_button"):
            st.rerun()

        if st.session_state.user_type.lower() == "admin":
            menu = st.sidebar.selectbox(
                "Menu",
                ["Dashboard", "Employee Management", "Leave Management", "Attendance Tracking",
                 "Performance Management", "Recruitment", "Payroll Management", "Password Vault"],
                key="admin_menu"
            )
            if menu == "Dashboard":
                show_dashboard()
            elif menu == "Employee Management":
                employee_management()
            elif menu == "Leave Management":
                leave_management()
            elif menu == "Attendance Tracking":
                attendance_tracking()
            elif menu == "Performance Management":
                performance_management()
            elif menu == "Recruitment":
                recruitment_management()
            elif menu == "Payroll Management":
                payroll_management()
            elif menu == "Password Vault":
                password_vault()
        else:
            employee_dashboard()


if __name__ == "__main__":
    main()