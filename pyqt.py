import sqlite3
import re
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QInputDialog, QComboBox


class Database:
    """
    The Database class manages the database connection and all CRUD (Create, Read, Update, Delete) operations 
    for students, instructors, courses, and their associations.

    :param db_name: The name of the database file to connect to, defaults to 'school1.db'
    :type db_name: str, optional
    """
    def __init__(self, db_name='school1.db'):

        """Initializes the database connection and creates the required tables.

        :param db_name: The name of the SQLite database file, defaults to 'school1.db'
        :type db_name: str, optional
        """
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates the necessary tables in the SQLite database if they do not already exist."""
        # SQL statements to create tables
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS instructors (
            instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            instructor_id INTEGER,
            FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS student_courses (
            student_id INTEGER,
            course_id INTEGER,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )''')
        self.connection.commit()

    def get_instructor_id_by_name(self, instructor_name):
        """
        Retrieves the instructor's ID by their name.

        :param instructor_name: The name of the instructor
        :type instructor_name: str
        :return: The ID of the instructor, or None if not found
        :rtype: int or None
        """
        # SQL query to get the instructor ID by name
        query = "SELECT instructor_id FROM instructors WHERE name = ?"
        self.cursor.execute(query, (instructor_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_course_id_by_name(self, course_name):
        """
        Retrieves the course's ID by its name.

        :param course_name: The name of the course
        :type course_name: str
        :return: The ID of the course, or None if not found
        :rtype: int or None
        """
        # SQL query to get the course ID by name
        query = "SELECT course_id FROM courses WHERE course_name = ?"
        self.cursor.execute(query, (course_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_student(self, student):
        """
        Adds a new student to the database after validating their email and age.

        :param student: The student object containing name, age, and email
        :type student: Student
        :raises sqlite3.IntegrityError: If a student with the same ID already exists
        """
        # Validation and insertion logic for adding student
        if not self.validate_email(student.email):
            self.show_error("Error", "Invalid email format.")
            return
        if student.age <= 0:
            self.show_error("Error", "Age must be positive.")
            return

        try:
            self.cursor.execute('''INSERT INTO students (name, age, email) VALUES (?, ?, ?)''',
                                (student.name, student.age, student.email))
            self.connection.commit()
            self.show_info("Success", "Student added successfully.")
        except sqlite3.IntegrityError:
            self.show_error("Error", f"Student ID {student.student_id} already exists.")

    def add_instructor(self, instructor):
        """
        Adds a new instructor to the database after validating their email and age.

        :param instructor: The instructor object containing name, age, and email
        :type instructor: Instructor
        :raises sqlite3.IntegrityError: If an instructor with the same ID already exists
        """
        # Validation and insertion logic for adding instructor 
        if not self.validate_email(instructor.email):
            self.show_error("Error", "Invalid email format.")
            return
        if instructor.age <= 0:
            self.show_error("Error", "Age must be positive.")
            return

        try:
            self.cursor.execute('''INSERT INTO instructors (name, age, email) VALUES (?, ?, ?)''',
                                (instructor.name, instructor.age, instructor.email))
            self.connection.commit()
            self.show_info("Success", "Instructor added successfully.")
        except sqlite3.IntegrityError:
            self.show_error("Error", f"Instructor ID {instructor.instructor_id} already exists.")

    def add_course(self, course):
        """
        Adds a new course to the database if the instructor exists and the course name does not already exist.

        :param course: The course object containing course_name and instructor_id
        :type course: Course
        :raises sqlite3.IntegrityError: If the course name already exists
        """


        self.cursor.execute('SELECT * FROM instructors WHERE instructor_id = ?', (course.instructor_id,))
        instructor = self.cursor.fetchone()

        if instructor is None:
            self.show_error("Error", f"Instructor ID {course.instructor_id} does not exist.")
            return

        self.cursor.execute('SELECT * FROM courses WHERE course_name = ?', (course.course_name,))
        existing_course = self.cursor.fetchone()

        if existing_course is not None:
            self.show_error("Error", f"Course with name '{course.course_name}' already exists.")
            return

        try:
            self.cursor.execute('''INSERT INTO courses (course_name, instructor_id) VALUES (?, ?)''',
                                (course.course_name, course.instructor_id))
            self.connection.commit()
            self.show_info("Success", "Course added successfully.")
        except sqlite3.IntegrityError:
            self.show_error("Error", "An error occurred while adding the course.")

    def validate_email(self, email):
        """
        Validates the format of the given email using a regular expression.

        :param email: The email to validate
        :type email: str
        :return: True if the email format is valid, otherwise False
        :rtype: bool
        """
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(regex, email) is not None

    def get_students(self):
        """
        Retrieves all students from the database.

        :return: A list of students
        :rtype: list of tuples
        """
        # SQL query for fetching all students
        self.cursor.execute('SELECT * FROM students')
        return self.cursor.fetchall()

    def get_instructors(self):
        """
        Retrieves all instructors from the database.

        :return: A list of instructors
        :rtype: list of tuples
        """
        # SQL query for fetching all instructors
        self.cursor.execute('SELECT * FROM instructors')
        return self.cursor.fetchall()

    def get_courses(self):
        """
        Retrieves all courses from the database.

        :return: A list of courses
        :rtype: list of tuples
        """
        # SQL query for fetching all courses
        self.cursor.execute('SELECT * FROM courses')
        return self.cursor.fetchall()

    def register_student_course(self, student_id, course_id):
        """
        Registers a student for a course.

        :param student_id: The ID of the student
        :type student_id: int
        :param course_id: The ID of the course
        :type course_id: int
        :raises sqlite3.IntegrityError: If the student is already registered for the course
        """
        try:
            self.cursor.execute('''INSERT INTO student_courses (student_id, course_id) VALUES (?, ?)''',
                                (student_id, course_id))
            self.connection.commit()
            self.show_info("Success", "Student registered for course successfully.")
        except sqlite3.IntegrityError:
            self.show_error("Error", "Registration failed. This student is already registered for this course.")

    def update_course_instructor(self, course_id, instructor_id):
        """
        Updates the instructor of a course.

        :param course_id: The ID of the course
        :type course_id: int
        :param instructor_id: The ID of the instructor
        :type instructor_id: int
        """
        with self.connection:
            self.cursor.execute("""
                UPDATE courses
                SET instructor_id = ?
                WHERE course_id = ?
            """, (instructor_id, course_id))

    def delete_student(self, student_id):
        """
        Deletes a student from the database.

        :param student_id: The ID of the student
        :type student_id: int
        """
        self.cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        self.connection.commit()

    def delete_instructor(self, instructor_id):
        """
        Deletes an instructor from the database.

        :param instructor_id: The ID of the instructor
        :type instructor_id: int
        """
        self.cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (instructor_id,))
        self.connection.commit()

    def delete_course(self, course_id):
        """
        Deletes a course from the database.

        :param course_id: The ID of the course
        :type course_id: int
        """
        self.cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        self.connection.commit()

    def update_student(self, student_id, name, age, email):
        """
        Updates a student's details.

        :param student_id: The ID of the student
        :type student_id: int
        :param name: The new name of the student
        :type name: str
        :param age: The new age of the student
        :type age: int
        :param email: The new email of the student
        :type email: str
        """
        query = """UPDATE students 
                SET name = ?, age = ?, email = ? 
                WHERE student_id = ?"""
        self.cursor.execute(query, (name, age, email, student_id))
        self.connection.commit()

    def update_instructor(self, instructor_id, name, age, email):
        """
        Updates an instructor's details.

        :param instructor_id: The ID of the instructor
        :type instructor_id: int
        :param name: The new name of the instructor
        :type name: str
        :param age: The new age of the instructor
        :type age: int
        :param email: The new email of the instructor
        :type email: str
        """
        query = """UPDATE instructors 
                SET name = ?, age = ?, email = ? 
                WHERE instructor_id = ?"""
        self.cursor.execute(query, (name, age, email, instructor_id))
        self.connection.commit()

    def update_course(self, course_id, course_name, instructor_id):
        """
        Updates a course's details.

        :param course_id: The ID of the course
        :type course_id: int
        :param course_name: The new name of the course
        :type course_name: str
        :param instructor_id: The new ID of the instructor
        :type instructor_id: int
        """
        query = """UPDATE courses 
                SET course_name = ?, instructor_id = ? 
                WHERE course_id = ?"""
        self.cursor.execute(query, (course_name, instructor_id, course_id))
        self.connection.commit()

    def show_error(self, title, message):
        """
        Displays an error message box with the given title and message.

        :param title: The title of the error message box
        :type title: str
        :param message: The message to display
        :type message: str
        """
        # QMessageBox logic for displaying error
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle(title)
        error_box.setText(message)
        error_box.exec_()

    def show_info(self, title, message):
        """
        Displays an informational message box with the given title and message.

        :param title: The title of the info message box
        :type title: str
        :param message: The message to display
        :type message: str
        """
        info_box = QMessageBox()
        info_box.setIcon(QMessageBox.Information)
        info_box.setWindowTitle(title)
        info_box.setText(message)
        info_box.exec_()


class Student:
    """
    A class representing a student.

    :param name: The name of the student
    :type name: str
    :param age: The age of the student
    :type age: int
    :param email: The email of the student
    :type email: str
    """
    def __init__(self, name, age, email):
        """Initializes a new student object with name, age, and email."""

        self.name = name
        self.age = age
        self.email = email


class Instructor:
    """
    A class representing an instructor.

    :param name: The name of the instructor
    :type name: str
    :param age: The age of the instructor
    :type age: int
    :param email: The email of the instructor
    :type email: str
    """
    def __init__(self, name, age, email):
        """Initializes a new instructor object with name, age, and email."""
        self.name = name
        self.age = age
        self.email = email


class Course:
    """
    A class representing a course.

    :param course_name: The name of the course
    :type course_name: str
    :param instructor_id: The ID of the instructor assigned to the course
    :type instructor_id: int
    """

    def __init__(self, course_name, instructor_id):
        """Initializes a new course object with course name and instructor ID."""

        self.course_name = course_name
        self.instructor_id = instructor_id


class SchoolManagementGUI(QtWidgets.QMainWindow):
    """
    A PyQt GUI class to manage the School Management System.

    This GUI allows the user to manage students, instructors, courses, student registrations, 
    and assigning instructors to courses.
    """
    def __init__(self):
        """Initializes the main window and sets up the UI."""

        super().__init__()
        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 1000, 700)
        self.db = Database()

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.initUI()

    def initUI(self):
        """Initializes the UI with tabs for managing students, instructors, courses, and registrations."""

        self.tabs = QtWidgets.QTabWidget(self.central_widget)
        self.layout.addWidget(self.tabs)

        self.create_student_tab()
        self.create_instructor_tab()
        self.create_course_tab()
        self.create_register_tab()
        self.create_assign_tab()

    def create_student_tab(self):
        """Creates the tab for managing students (adding, editing, deleting, viewing)."""

        student_tab = QtWidgets.QWidget()
        self.tabs.addTab(student_tab, "Students")

        layout = QtWidgets.QVBoxLayout(student_tab)

        form_layout = QtWidgets.QFormLayout()
        layout.addLayout(form_layout)

        self.student_name_input = QtWidgets.QLineEdit()
        self.student_age_input = QtWidgets.QLineEdit()
        self.student_email_input = QtWidgets.QLineEdit()

        form_layout.addRow("Name:", self.student_name_input)
        form_layout.addRow("Age:", self.student_age_input)
        form_layout.addRow("Email:", self.student_email_input)

        add_student_btn = QtWidgets.QPushButton("Add Student")
        add_student_btn.clicked.connect(self.add_student)
        layout.addWidget(add_student_btn)

        self.student_table = QtWidgets.QTableWidget()
        self.student_table.setColumnCount(4)
        self.student_table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email'])
        layout.addWidget(self.student_table)

        self.load_students()

        delete_student_btn = QtWidgets.QPushButton("Delete Selected Student")
        delete_student_btn.clicked.connect(self.delete_student)
        layout.addWidget(delete_student_btn)

        edit_student_btn = QtWidgets.QPushButton("Edit Selected Student")
        edit_student_btn.clicked.connect(self.edit_student)
        layout.addWidget(edit_student_btn)

    def add_student(self):
        """Adds a new student to the database using input from the UI."""

        student = Student(
            name=self.student_name_input.text(),
            age=int(self.student_age_input.text()),
            email=self.student_email_input.text()
        )
        self.db.add_student(student)
        self.load_students()

    def load_students(self):
        """Loads all students from the database and displays them in the student table."""

        students = self.db.get_students()
        self.student_table.setRowCount(len(students))
        for i, student in enumerate(students):
            self.student_table.setItem(i, 0, QTableWidgetItem(str(student[0])))
            self.student_table.setItem(i, 1, QTableWidgetItem(student[1]))
            self.student_table.setItem(i, 2, QTableWidgetItem(str(student[2])))
            self.student_table.setItem(i, 3, QTableWidgetItem(student[3]))

    def delete_student(self):
        """Deletes the selected student from the database."""

        selected_row = self.student_table.currentRow()
        if selected_row < 0:
            self.db.show_error("Error", "Please select a student to delete.")
            return

        student_id = int(self.student_table.item(selected_row, 0).text())
        self.db.delete_student(student_id)
        self.load_students()

    def edit_student(self):
        """Edits the details of the selected student."""

        selected_row = self.student_table.currentRow()
        if selected_row < 0:
            self.db.show_error("Error", "Please select a student to edit.")
            return

        student_id = int(self.student_table.item(selected_row, 0).text())
        name, _ = QInputDialog.getText(self, "Edit Name", "New Name:", text=self.student_table.item(selected_row, 1).text())
        age, _ = QInputDialog.getInt(self, "Edit Age", "New Age:", value=int(self.student_table.item(selected_row, 2).text()))
        email, _ = QInputDialog.getText(self, "Edit Email", "New Email:", text=self.student_table.item(selected_row, 3).text())

        if name and email:
            self.db.update_student(student_id, name, age, email)
            self.load_students()

    def create_instructor_tab(self):
        """Creates the tab for managing instructors (adding, editing, deleting, viewing)."""

        instructor_tab = QtWidgets.QWidget()
        self.tabs.addTab(instructor_tab, "Instructors")

        layout = QtWidgets.QVBoxLayout(instructor_tab)

        form_layout = QtWidgets.QFormLayout()
        layout.addLayout(form_layout)

        self.instructor_name_input = QtWidgets.QLineEdit()
        self.instructor_age_input = QtWidgets.QLineEdit()
        self.instructor_email_input = QtWidgets.QLineEdit()

        form_layout.addRow("Name:", self.instructor_name_input)
        form_layout.addRow("Age:", self.instructor_age_input)
        form_layout.addRow("Email:", self.instructor_email_input)

        add_instructor_btn = QtWidgets.QPushButton("Add Instructor")
        add_instructor_btn.clicked.connect(self.add_instructor)
        layout.addWidget(add_instructor_btn)

        self.instructor_table = QtWidgets.QTableWidget()
        self.instructor_table.setColumnCount(4)
        self.instructor_table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email'])
        layout.addWidget(self.instructor_table)

        self.load_instructors()

        delete_instructor_btn = QtWidgets.QPushButton("Delete Selected Instructor")
        delete_instructor_btn.clicked.connect(self.delete_instructor)
        layout.addWidget(delete_instructor_btn)

        edit_instructor_btn = QtWidgets.QPushButton("Edit Selected Instructor")
        edit_instructor_btn.clicked.connect(self.edit_instructor)
        layout.addWidget(edit_instructor_btn)

    def add_instructor(self):
        """Adds a new instructor to the database using input from the UI."""

        instructor = Instructor(
            name=self.instructor_name_input.text(),
            age=int(self.instructor_age_input.text()),
            email=self.instructor_email_input.text()
        )
        self.db.add_instructor(instructor)
        self.load_instructors()

    def load_instructors(self):
        """Loads all instructors from the database and displays them in the instructor table."""

        instructors = self.db.get_instructors()
        self.instructor_table.setRowCount(len(instructors))
        for i, instructor in enumerate(instructors):
            self.instructor_table.setItem(i, 0, QTableWidgetItem(str(instructor[0])))
            self.instructor_table.setItem(i, 1, QTableWidgetItem(instructor[1]))
            self.instructor_table.setItem(i, 2, QTableWidgetItem(str(instructor[2])))
            self.instructor_table.setItem(i, 3, QTableWidgetItem(instructor[3]))

    def delete_instructor(self):
        """Deletes the selected instructor from the database."""

        selected_row = self.instructor_table.currentRow()
        if selected_row < 0:
            self.db.show_error("Error", "Please select an instructor to delete.")
            return

        instructor_id = int(self.instructor_table.item(selected_row, 0).text())
        self.db.delete_instructor(instructor_id)
        self.load_instructors()

    def edit_instructor(self):
        """Edits the details of the selected instructor."""

        selected_row = self.instructor_table.currentRow()
        if selected_row < 0:
            self.db.show_error("Error", "Please select an instructor to edit.")
            return

        instructor_id = int(self.instructor_table.item(selected_row, 0).text())
        name, _ = QInputDialog.getText(self, "Edit Name", "New Name:", text=self.instructor_table.item(selected_row, 1).text())
        age, _ = QInputDialog.getInt(self, "Edit Age", "New Age:", value=int(self.instructor_table.item(selected_row, 2).text()))
        email, _ = QInputDialog.getText(self, "Edit Email", "New Email:", text=self.instructor_table.item(selected_row, 3).text())

        if name and email:
            self.db.update_instructor(instructor_id, name, age, email)
            self.load_instructors()

    def create_course_tab(self):
        """Creates the tab for managing courses (adding, editing, deleting, viewing)."""

        course_tab = QtWidgets.QWidget()
        self.tabs.addTab(course_tab, "Courses")

        layout = QtWidgets.QVBoxLayout(course_tab)

        form_layout = QtWidgets.QFormLayout()
        layout.addLayout(form_layout)

        self.course_name_input = QtWidgets.QLineEdit()
        self.course_instructor_input = QtWidgets.QLineEdit()

        form_layout.addRow("Course Name:", self.course_name_input)
        form_layout.addRow("Instructor ID:", self.course_instructor_input)

        add_course_btn = QtWidgets.QPushButton("Add Course")
        add_course_btn.clicked.connect(self.add_course)
        layout.addWidget(add_course_btn)

        self.course_table = QtWidgets.QTableWidget()
        self.course_table.setColumnCount(3)
        self.course_table.setHorizontalHeaderLabels(['ID', 'Course Name', 'Instructor ID'])
        layout.addWidget(self.course_table)

        self.load_courses()

        delete_course_btn = QtWidgets.QPushButton("Delete Selected Course")
        delete_course_btn.clicked.connect(self.delete_course)
        layout.addWidget(delete_course_btn)

        edit_course_btn = QtWidgets.QPushButton("Edit Selected Course")
        edit_course_btn.clicked.connect(self.edit_course)
        layout.addWidget(edit_course_btn)

    def add_course(self):
        """Adds a new course to the database using input from the UI."""

        course = Course(
            course_name=self.course_name_input.text(),
            instructor_id=int(self.course_instructor_input.text())
        )
        self.db.add_course(course)
        self.load_courses()

    def load_courses(self):
        """Loads all courses from the database and displays them in the course table."""

        courses = self.db.get_courses()
        self.course_table.setRowCount(len(courses))
        for i, course in enumerate(courses):
            self.course_table.setItem(i, 0, QTableWidgetItem(str(course[0])))
            self.course_table.setItem(i, 1, QTableWidgetItem(course[1]))
            self.course_table.setItem(i, 2, QTableWidgetItem(str(course[2])))

    def delete_course(self):
        """Deletes the selected course from the database."""

        selected_row = self.course_table.currentRow()
        if selected_row < 0:
            self.db.show_error("Error", "Please select a course to delete.")
            return

        course_id = int(self.course_table.item(selected_row, 0).text())
        self.db.delete_course(course_id)
        self.load_courses()

    def edit_course(self):
        """Edits the details of the selected course."""

        selected_row = self.course_table.currentRow()
        if selected_row < 0:
            self.db.show_error("Error", "Please select a course to edit.")
            return

        course_id = int(self.course_table.item(selected_row, 0).text())
        name, _ = QInputDialog.getText(self, "Edit Course Name", "New Course Name:", text=self.course_table.item(selected_row, 1).text())
        instructor_id, _ = QInputDialog.getInt(self, "Edit Instructor ID", "New Instructor ID:", value=int(self.course_table.item(selected_row, 2).text()))

        if name:
            self.db.update_course(course_id, name, instructor_id)
            self.load_courses()

    def create_register_tab(self):
        """Creates the tab for registering students to courses."""

        register_tab = QtWidgets.QWidget()
        self.tabs.addTab(register_tab, "Register")

        layout = QtWidgets.QVBoxLayout(register_tab)

        form_layout = QtWidgets.QFormLayout()
        layout.addLayout(form_layout)

        self.student_dropdown = QComboBox()
        self.course_dropdown = QComboBox()

        form_layout.addRow("Select Student:", self.student_dropdown)
        form_layout.addRow("Select Course:", self.course_dropdown)

        register_btn = QtWidgets.QPushButton("Register Student to Course")
        register_btn.clicked.connect(self.register_student)
        layout.addWidget(register_btn)

        self.load_student_course_dropdowns()

    def register_student(self):
        """Registers a student to a course."""

        student_id = self.student_dropdown.currentData()
        course_id = self.course_dropdown.currentData()
        self.db.register_student_course(student_id, course_id)

    def load_student_course_dropdowns(self):
        """Loads student and course data into dropdowns for registration."""

        self.student_dropdown.clear()
        self.course_dropdown.clear()

        students = self.db.get_students()
        courses = self.db.get_courses()

        for student in students:
            self.student_dropdown.addItem(f"{student[1]} (ID: {student[0]})", student[0])

        for course in courses:
            self.course_dropdown.addItem(f"{course[1]} (ID: {course[0]})", course[0])

    def create_assign_tab(self):
        """Creates the tab for assigning instructors to courses."""

        assign_tab = QtWidgets.QWidget()
        self.tabs.addTab(assign_tab, "Assign Instructor")

        layout = QtWidgets.QVBoxLayout(assign_tab)

        form_layout = QtWidgets.QFormLayout()
        layout.addLayout(form_layout)

        self.assign_course_dropdown = QComboBox()
        self.assign_instructor_dropdown = QComboBox()

        form_layout.addRow("Select Course:", self.assign_course_dropdown)
        form_layout.addRow("Select Instructor:", self.assign_instructor_dropdown)

        assign_btn = QtWidgets.QPushButton("Assign Instructor to Course")
        assign_btn.clicked.connect(self.assign_instructor)
        layout.addWidget(assign_btn)

        self.load_assign_dropdowns()

    def assign_instructor(self):
        """Assigns an instructor to a course."""

        course_id = self.assign_course_dropdown.currentData()
        instructor_id = self.assign_instructor_dropdown.currentData()
        self.db.update_course_instructor(course_id, instructor_id)

    def load_assign_dropdowns(self):
        """Loads course and instructor data into dropdowns for assignment."""
    
        self.assign_course_dropdown.clear()
        self.assign_instructor_dropdown.clear()

        courses = self.db.get_courses()
        instructors = self.db.get_instructors()

        for course in courses:
            self.assign_course_dropdown.addItem(f"{course[1]} (ID: {course[0]})", course[0])

        for instructor in instructors:
            self.assign_instructor_dropdown.addItem(f"{instructor[1]} (ID: {instructor[0]})", instructor[0])


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = SchoolManagementGUI()
    window.show()
    sys.exit(app.exec_())
