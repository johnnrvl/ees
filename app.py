from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = '123'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'eval'

mysql = MySQL(app)

users = {
    "user1": "password1",
    "user2": "password2",
    "john1": "naraval1",
    "rbj": "comtrex",
    "1": "1",
}


@app.route("/dashboard/departments")
def show_departments():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM departments")
    departments_data = cur.fetchall()

    departments_with_employees = []

    for department in departments_data:
        department_id, department_name = department[0], department[1]
        cur.execute("SELECT * FROM position WHERE EmployeeDepartment = %s", (department_name,))
        employees_data = cur.fetchall()
        department_with_employees = {
            "DepartmentID": department_id,
            "DepartmentName": department_name,
            "employees": employees_data,
        }
        departments_with_employees.append(department_with_employees)

    cur.close()
    return render_template("departments.html", departments=departments_with_employees)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials. Please try again."
            return render_template("login.html", error=error)

    return render_template("login.html", error=None)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/dashboard/positions")
def positions():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM position")
    positions_data = cur.fetchall()
    cur.close()
    return render_template("positions.html", product=positions_data)


@app.route("/dashboard/evaluations")
def evaluations():
    return render_template("evaluations.html")


@app.route("/dashboard/questionnaires")
def evalform():
    return render_template("evaluation_form.html")


@app.route("/results")
def show_results():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM evaluations")
    evaluation_data = cur.fetchall()

    result_data = []
    for row in evaluation_data:
        result_data.append({
            "id": row[0],
            "evaluator_name": row[1],
            "evaluated_name": row[2],
            "teamwork_total": row[3],
            "communication_total": row[4],
            "attendance_total": row[5],
            "productivity_total": row[6],
            "initiative_total": row[7],
            "judgment_total": row[8],
            "dependability_total": row[9],
            "attitude_total": row[10],
            "professionalism_total": row[11],
            "overall_total": row[12]
        })

    cur.close()
    return render_template('results.html', evaluation_data=result_data)


@app.route('/position')
def position():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM position")
    data = cur.fetchall()
    cur.close()
    return render_template('positions.html', product=data)


@app.route('/addposition', methods=['POST'])
def addposition():
    if request.method == "POST":
        en, ep, ed, department_name = request.form['en'], request.form['ep'], request.form['ed'], request.form['ed']

        cur = mysql.connection.cursor()
        cur.execute("SELECT DepartmentID FROM departments WHERE DepartmentName = %s", (department_name,))
        department_id_row = cur.fetchone()

        if department_id_row:
            department_id = department_id_row[0]
            cur.execute("INSERT INTO position (EmployeeName, EmployeePosition, EmployeeDepartment, DepartmentID) VALUES (%s, %s, %s, %s)",
                        (en, ep, ed, department_id))
            mysql.connection.commit()
            return redirect(url_for('position'))
        else:
            error = "Invalid Department Name. Please provide a valid Department Name."
            cur.execute("SELECT * FROM position")
            positions_data = cur.fetchall()
            cur.close()
            return render_template('positions.html', error=error, product=positions_data)

@app.route("/delete_evaluation/<int:id_data>", methods=["POST", "DELETE"])
def delete_evaluation(id_data):
    if request.method == "POST" or request.method == "DELETE":
        try:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM evaluations WHERE id = %s", (id_data,))
            mysql.connection.commit()
            cur.close()
            flash("Evaluation deleted successfully!")
        except Exception as e:
            print(e)
            flash("Failed to delete the evaluation. Please try again.")
    return redirect("/results")


@app.route('/updateposition', methods=['POST'])
def updateposition():
    if request.method == 'POST':
        en, ep, ed, employee_id = request.form['en'], request.form['ep'], request.form['ed'], request.form['id']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE position SET EmployeeName = %s, EmployeePosition = %s, EmployeeDepartment = %s WHERE EmployeeID = %s",
                    (en, ep, ed, employee_id))
        mysql.connection.commit()
        cur.close()

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM departments")
        departments = cur.fetchall()

        departments_with_employees = []

        for department in departments:
            department_id, department_name = department[0], department[1]
            cur.execute("SELECT * FROM position WHERE EmployeeDepartment = %s", (department_name,))
            employees_data = cur.fetchall()
            department_with_employees = {
                "DepartmentID": department_id,
                "DepartmentName": department_name,
                "employees": employees_data,
            }
            departments_with_employees.append(department_with_employees)

        cur.close()
        return render_template("departments.html", departments=departments_with_employees)


@app.route('/deleteposition/<string:id_data>', methods=['GET'])
def deleteposition(id_data):
    flash("Your position has been Deleted!")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM position WHERE EmployeeID=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('position'))


@app.route('/submit_evaluation', methods=['POST'])
def submit_evaluation():
    if request.method == "POST":
        evaluator_name = request.form["evaluator_name"]
        evaluated_name = request.form["evaluated_name"]
        scores = [int(request.form[f'q{i}']) for i in range(1, 26)]

        teamwork_total = sum(scores[0:5])
        communication_total = sum(scores[5:10])
        attendance_total = sum(scores[10:13])
        productivity_total = sum(scores[13:19])
        initiative_total = sum(scores[19:25])
        judgment_total = sum(scores[25:28])
        dependability_total = sum(scores[28:33])
        attitude_total = sum(scores[33:38])
        professionalism_total = sum(scores[38:44])
        overall_total = sum(scores)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO evaluations (evaluator_name, evaluated_name, teamwork_total, communication_total, attendance_total, productivity_total, initiative_total, judgment_total, dependability_total, attitude_total, professionalism_total, overall_total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (evaluator_name, evaluated_name, teamwork_total, communication_total, attendance_total, productivity_total, initiative_total, judgment_total, dependability_total, attitude_total, professionalism_total, overall_total))
        mysql.connection.commit()
        cur.close()

        flash("Evaluation submitted successfully!")

        return redirect(url_for('evalform'))

@app.route("/dashboard/performance_evaluation", methods=["GET", "POST"])
def performance_evaluation():
    cursor = None  # Initialize the cursor variable outside the try block
    if request.method == "POST":
        try:
            # Retrieve form data
            evaluator_name = request.form["evaluator_name"]
            evaluated_name = request.form["evaluated_name"]
            status = request.form["status"]
            job_title = request.form["job_title"]

            # Retrieve form data for major tasks
            major_task_scores = [int(request.form[f'q{i}']) for i in range(1, 9)]
            major_total_score = sum(major_task_scores)

            # Retrieve form data for other tasks
            other_task_scores = [int(request.form[f'q{i}']) for i in range(9, 27)]
            other_total_score = sum(other_task_scores)

            # Insert data into the "performance_evaluations" table
            conn = mysql.connection
            cursor = conn.cursor()

            # Corrected SQL query with placeholders for all columns
            query = (
                "INSERT INTO performance_evaluations (evaluator_name, evaluated_name, status, job_title, "
                "major_task_1, major_task_2, major_task_3, major_task_4, major_task_5, major_task_6, major_task_7, major_task_8, major_total_score, "
                "other_task_1, other_task_2, other_task_3, other_task_4, other_task_5, other_task_6, other_task_7, other_task_8, "
                "other_task_9, other_task_10, other_task_11, other_task_12, other_task_13, other_task_14, other_task_15, other_task_16, "
                "other_task_17, other_task_18, other_total_score) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"  # 33 placeholders
            )

            # Ensure you provide 33 values in the tuple
            values = (
                evaluator_name, evaluated_name, status, job_title,
                *major_task_scores, major_total_score, *other_task_scores, other_total_score
            )

            # Execute the query with the provided values
            cursor.execute(query, values)

            conn.commit()
            flash("Evaluation submitted successfully!")

        except Exception as e:
            print(e)  # Add this line to print the error to the console
            flash("Failed to submit the evaluation. Please try again.")

        finally:
            if cursor:
                cursor.close()  # Close the cursor if it's not None

    return render_template("performance.html")

if __name__ == "__main__":
    app.run(debug=True)
