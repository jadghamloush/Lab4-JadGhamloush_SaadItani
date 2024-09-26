import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import re  # For email validation

class Database:
    def __init__(self, db_name='school1.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Create tables if they don't exist
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
        query = "SELECT instructor_id FROM instructors WHERE name = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (instructor_name,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_course_id_by_name(self, course_name):
        query = "SELECT course_id FROM courses WHERE course_name = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (course_name,))
        result = cursor.fetchone()
        return result[0] if result else None

    def add_student(self, student):
        if not self.validate_email(student.email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        if student.age <= 0:
            messagebox.showerror("Error", "Age must be positive.")
            return

        try:
            self.cursor.execute('''INSERT INTO students (name, age, email) VALUES (?, ?, ?)''',
                                (student.name, student.age, student.email))
            self.connection.commit()
            messagebox.showinfo("Success", "Student added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Student ID {student.student_id} already exists.")

    def add_instructor(self, instructor):
        if not self.validate_email(instructor.email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        if instructor.age <= 0:
            messagebox.showerror("Error", "Age must be positive.")
            return

        try:
            self.cursor.execute('''INSERT INTO instructors (name, age, email) VALUES (?, ?, ?)''',
                                (instructor.name, instructor.age, instructor.email))
            self.connection.commit()
            messagebox.showinfo("Success", "Instructor added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Instructor ID {instructor.instructor_id} already exists.")

    def add_course(self, course):
        # Check if the instructor ID exists in the instructors table
        self.cursor.execute('SELECT * FROM instructors WHERE instructor_id = ?', (course.instructor_id,))
        instructor = self.cursor.fetchone()

        if instructor is None:
            messagebox.showerror("Error", f"Instructor ID {course.instructor_id} does not exist.")
            return

        # Check if the course name already exists
        self.cursor.execute('SELECT * FROM courses WHERE course_name = ?', (course.course_name,))
        existing_course = self.cursor.fetchone()

        if existing_course is not None:
            messagebox.showerror("Error", f"Course with name '{course.course_name}' already exists.")
            return

        try:
            # Insert the course without specifying the course_id; it will auto-increment
            self.cursor.execute('''INSERT INTO courses (course_name, instructor_id) VALUES (?, ?)''',
                                (course.course_name, course.instructor_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Course added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "An error occurred while adding the course.")

    def validate_email(self, email):
        # Basic email validation regex
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(regex, email) is not None

    def get_students(self):
        self.cursor.execute('SELECT * FROM students')
        return self.cursor.fetchall()

    def get_instructors(self):
        self.cursor.execute('SELECT * FROM instructors')
        return self.cursor.fetchall()

    def get_courses(self):
        self.cursor.execute('SELECT * FROM courses')
        return self.cursor.fetchall()

    def register_student_course(self, student_id, course_id):
        try:
            self.cursor.execute('''INSERT INTO student_courses (student_id, course_id) VALUES (?, ?)''',
                                (student_id, course_id))
            self.connection.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Registration failed. This student is already registered for this course.")


    def update_course_instructor(self, course_id, instructor_id):
        """Update the instructor ID for the specified course ID."""
        with self.connection:  
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE courses
                SET instructor_id = ?
                WHERE course_id = ?
            """, (instructor_id, course_id))


    def filter_students(self, search_term):
        query = "SELECT * FROM students WHERE name LIKE ? OR student_id = ?"
        self.cursor.execute(query, (f'%{search_term}%', search_term))
        return self.cursor.fetchall()

    def filter_instructors(self, search_term):
        query = "SELECT * FROM instructors WHERE name LIKE ? OR instructor_id = ?"
        self.cursor.execute(query, (f'%{search_term}%', search_term))
        return self.cursor.fetchall()

    def filter_courses(self, search_term):
        query = "SELECT * FROM courses WHERE course_name LIKE ? OR course_id = ?"
        self.cursor.execute(query, (f'%{search_term}%', search_term))
        return self.cursor.fetchall()

    def update_student(self, student_id, name, age, email):
        query = """UPDATE students 
                SET name = ?, age = ?, email = ? 
                WHERE student_id = ?"""
        self.cursor.execute(query, (name, age, email, student_id))
        self.connection.commit()

    def update_instructor(self, instructor_id, name, age, email):
        query = """UPDATE instructors 
                SET name = ?, age = ?, email = ? 
                WHERE instructor_id = ?"""
        self.cursor.execute(query, (name, age, email, instructor_id))
        self.connection.commit()

    def update_course(self, course_id, course_name, instructor_id):
        query = """UPDATE courses 
                SET course_name = ?, instructor_id = ? 
                WHERE course_id = ?"""
        self.cursor.execute(query, (course_name, instructor_id, course_id))
        self.connection.commit()

        # Delete methods
    def delete_student(self, student_id):
        self.cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        self.connection.commit()

    def delete_instructor(self, instructor_id):
        self.cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (instructor_id,))
        self.connection.commit()

    def delete_course(self, course_id):
        self.cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        self.connection.commit()


    def close(self):
        self.connection.close()

class Student:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

class Instructor:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

class Course:
    def __init__(self, course_name, instructor_id):
        self.course_name = course_name
        self.instructor_id = instructor_id

class SchoolManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")

        self.db = Database()

        # Creating main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        canvas = tk.Canvas(self.main_frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        scrollbar = ttk.Scrollbar(self.main_frame, orient="horizontal", command=canvas.xview)
        scrollbar.pack(side="bottom", fill="x")

        canvas.configure(yscrollcommand=scrollbar.set)

        target_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=target_frame, anchor="nw")

        target_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        

        
        self.create_input_frames(target_frame)
        self.create_treeview_frames(target_frame)

        self.populate_student_dropdown()
        self.populate_course_dropdown()

    

    def edit_student(self):
        selected_item = self.student_tree.selection()[0]
        values = self.student_tree.item(selected_item)['values']
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Student")

        ttk.Label(edit_window, text="Name:").grid(row=0, column=0)
        name_entry = ttk.Entry(edit_window)
        name_entry.insert(0, values[1])
        name_entry.grid(row=0, column=1)

        ttk.Label(edit_window, text="Age:").grid(row=1, column=0)
        age_entry = ttk.Entry(edit_window)
        age_entry.insert(0, values[2])
        age_entry.grid(row=1, column=1)

        ttk.Label(edit_window, text="Email:").grid(row=2, column=0)
        email_entry = ttk.Entry(edit_window)
        email_entry.insert(0, values[3])
        email_entry.grid(row=2, column=1)

        def save_changes():
            self.db.update_student(values[0], name_entry.get(), int(age_entry.get()), email_entry.get())
            self.student_tree.item(selected_item, values=(values[0], name_entry.get(), age_entry.get(), email_entry.get()))
            edit_window.destroy()

        ttk.Button(edit_window, text="Save", command=save_changes).grid(row=3, column=0, columnspan=2)

    def edit_instructor(self):
        selected_item = self.instructor_tree.selection()[0]
        values = self.instructor_tree.item(selected_item)['values']
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Instructor")

        ttk.Label(edit_window, text="Name:").grid(row=0, column=0)
        name_entry = ttk.Entry(edit_window)
        name_entry.insert(0, values[1])
        name_entry.grid(row=0, column=1)

        ttk.Label(edit_window, text="Age:").grid(row=1, column=0)
        age_entry = ttk.Entry(edit_window)
        age_entry.insert(0, values[2])
        age_entry.grid(row=1, column=1)

        ttk.Label(edit_window, text="Email:").grid(row=2, column=0)
        email_entry = ttk.Entry(edit_window)
        email_entry.insert(0, values[3])
        email_entry.grid(row=2, column=1)

        def save_changes():
            self.db.update_instructor(values[0], name_entry.get(), int(age_entry.get()), email_entry.get())
            self.instructor_tree.item(selected_item, values=(values[0], name_entry.get(), age_entry.get(), email_entry.get()))
            edit_window.destroy()

        ttk.Button(edit_window, text="Save", command=save_changes).grid(row=3, column=0, columnspan=2)

    def edit_course(self):
        selected_item = self.course_tree.selection()[0]
        values = self.course_tree.item(selected_item)['values']
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Course")

        ttk.Label(edit_window, text="Course Name:").grid(row=0, column=0)
        name_entry = ttk.Entry(edit_window)
        name_entry.insert(0, values[1])
        name_entry.grid(row=0, column=1)

        ttk.Label(edit_window, text="Instructor ID:").grid(row=1, column=0)
        instructor_id_entry = ttk.Entry(edit_window)
        instructor_id_entry.insert(0, values[2])
        instructor_id_entry.grid(row=1, column=1)

        def save_changes():
            self.db.update_course(values[0], name_entry.get(), int(instructor_id_entry.get()))
            self.course_tree.item(selected_item, values=(values[0], name_entry.get(), instructor_id_entry.get()))
            edit_window.destroy()

        ttk.Button(edit_window, text="Save", command=save_changes).grid(row=2, column=0, columnspan=2)

    def populate_student_dropdown(self):
        students = self.db.get_students()
        student_names = [f"{student[1]}" for student in students]  
        self.student_dropdown['values'] = student_names

    def populate_course_dropdown(self):
        courses = self.db.get_courses()
        course_names = [f"{course[1]}" for course in courses]  
        self.course_dropdown['values'] = course_names

    def populate_instructor_dropdown(self):
        instructors = self.db.get_instructors()
        instructor_names = [f"{instructor[1]}" for instructor in instructors]  
        self.instructor_dropdown['values'] = instructor_names

    def assign_instructor(self):
        instructor_name = self.instructor_dropdown.get()
        course_name = self.course_dropdown.get()

        # Ensure instructor_name and course_name are not empty
        if not instructor_name:
            messagebox.showerror("Error", "Please select an instructor.")
            return
        
        if not course_name:
            messagebox.showerror("Error", "Please select a course.")
            return

        # Fetch instructor ID from the database using the instructor name
        instructor_id = self.db.get_instructor_id_by_name(instructor_name)
        if instructor_id is None:
            messagebox.showerror("Error", "Invalid instructor selection. Please check the database.")
            return

        # Fetch course ID from the database using the course name
        course_id = self.db.get_course_id_by_name(course_name)
        if course_id is None:
            messagebox.showerror("Error", "Invalid course selection. Please check the database.")
            return

        # Update the instructor ID for the course
        self.db.update_course_instructor(course_id, instructor_id)
        messagebox.showinfo("Success", f"Instructor {instructor_name} assigned to {course_name}!")

        # Refresh the Treeview to show the new instructor
        self.update_treeview()



    def update_treeview(self):
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)

        courses = self.load_courses()  

        for course in courses:
            self.treeview.insert('', 'end', values=(course.id, course.name, course.instructor_name)) 


    def register_course(self):
        selected_student = self.student_dropdown.get()
        selected_course = self.course_dropdown.get()

        if not selected_student or not selected_course:
            messagebox.showerror("Error", "Please select both a student and a course.")
            return

        # Extract the student ID and course ID from the selected text
        student_id = int(selected_student.split(" (ID: ")[1][:-1])
        course_id = int(selected_course.split(" (ID: ")[1][:-1])

        # Here, you would implement the registration logic
        self.db.register_student_course(student_id, course_id)  # Make sure to implement this method in your Database class
        messagebox.showinfo("Success", "Student registered for course successfully.")

    def create_input_frames(self, target_frame):

        # Student frame
        self.student_frame = tk.LabelFrame(target_frame, text="Add Student", padx=10, pady=10)
        self.student_frame.pack(padx=10, pady=10, fill="both", expand="yes")

        ttk.Label(self.student_frame, text="Name:").grid(row=0, column=0)
        self.student_name = ttk.Entry(self.student_frame)
        self.student_name.grid(row=0, column=1)

        ttk.Label(self.student_frame, text="Age:").grid(row=1, column=0)
        self.student_age = ttk.Entry(self.student_frame)
        self.student_age.grid(row=1, column=1)

        ttk.Label(self.student_frame, text="Email:").grid(row=2, column=0)
        self.student_email = ttk.Entry(self.student_frame)
        self.student_email.grid(row=2, column=1)

        ttk.Button(self.student_frame, text="Add Student", command=self.add_student).grid(row=3, columnspan=2)

        # Instructor frame
        self.instructor_frame = tk.LabelFrame(target_frame, text="Add Instructor", padx=10, pady=10)
        self.instructor_frame.pack(padx=10, pady=10, fill="both", expand="yes")

        ttk.Label(self.instructor_frame, text="Name:").grid(row=0, column=0)
        self.instructor_name = ttk.Entry(self.instructor_frame)
        self.instructor_name.grid(row=0, column=1)

        ttk.Label(self.instructor_frame, text="Age:").grid(row=1, column=0)
        self.instructor_age = ttk.Entry(self.instructor_frame)
        self.instructor_age.grid(row=1, column=1)

        ttk.Label(self.instructor_frame, text="Email:").grid(row=2, column=0)
        self.instructor_email = ttk.Entry(self.instructor_frame)
        self.instructor_email.grid(row=2, column=1)

        ttk.Button(self.instructor_frame, text="Add Instructor", command=self.add_instructor).grid(row=3, columnspan=2)

        # Course frame
        self.course_frame = tk.LabelFrame(target_frame, text="Add Course", padx=10, pady=10)
        self.course_frame.pack(padx=10, pady=10, fill="both", expand="yes")

        ttk.Label(self.course_frame, text="Course Name:").grid(row=0, column=0)
        self.course_name = ttk.Entry(self.course_frame)
        self.course_name.grid(row=0, column=1)

        ttk.Label(self.course_frame, text="Instructor ID:").grid(row=1, column=0)
        self.course_instructor_id = ttk.Entry(self.course_frame)
        self.course_instructor_id.grid(row=1, column=1)

        ttk.Button(self.course_frame, text="Add Course", command=self.add_course).grid(row=2, columnspan=2)

        # Registration frame for courses
        self.register_frame = tk.LabelFrame(target_frame, text="Register for Course", padx=10, pady=10)
        self.register_frame.pack(padx=10, pady=10, fill="both", expand="yes")

        ttk.Label(self.register_frame, text="Select Student:").grid(row=0, column=0, padx=5, pady=5)
        self.student_dropdown = ttk.Combobox(self.register_frame)
        self.student_dropdown.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.register_frame, text="Select Course:").grid(row=1, column=0, padx=5, pady=5)
        self.course_dropdown = ttk.Combobox(self.register_frame)
        self.course_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.populate_course_dropdown()

        ttk.Button(self.register_frame, text="Register", command=self.register_course).grid(row=2, column=0, columnspan=2, pady=10)


        # assign instructor frame
        self.assign_frame = tk.LabelFrame(target_frame, text="Assign Instructor to Course", padx=10, pady=10)
        self.assign_frame.pack(padx=10, pady=10, fill="both", expand="yes")

        ttk.Label(self.assign_frame, text="Select Instructor:").grid(row=0, column=0, padx=5, pady=5)
        self.instructor_dropdown = ttk.Combobox(self.assign_frame)
        self.populate_instructor_dropdown() 
        self.instructor_dropdown.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.assign_frame, text="Select Course:").grid(row=1, column=0, padx=5, pady=5)
        self.course_dropdown = ttk.Combobox(self.assign_frame)
        self.course_dropdown['values'] = self.load_courses
        self.course_dropdown.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.assign_frame, text="Assign Instructor", command=self.assign_instructor).grid(row=2, column=0, columnspan=2, pady=10)




    def register_course():
        return



    def add_student(self):
        student = Student(
            name=self.student_name.get(),
            age=int(self.student_age.get()),
            email=self.student_email.get()
        )
        self.db.add_student(student)
        self.student_name.delete(0, tk.END)
        self.student_age.delete(0, tk.END)
        self.student_email.delete(0, tk.END)
    
    # Refresh the student treeview
        self.load_students()
        self.populate_student_dropdown()

    def add_instructor(self):
        instructor = Instructor(
            name=self.instructor_name.get(),
            age=int(self.instructor_age.get()),
            email=self.instructor_email.get()
        )
        self.db.add_instructor(instructor)
            # Clear the input fields
        self.instructor_name.delete(0, tk.END)
        self.instructor_age.delete(0, tk.END)
        self.instructor_email.delete(0, tk.END)
        
        # Refresh the instructor treeview
        self.load_instructors()

        self.populate_instructor_dropdown()

    def add_course(self):
        course = Course(
            course_name=self.course_name.get(),
            instructor_id=int(self.course_instructor_id.get())
        )
        self.db.add_course(course)
            # Clear the input fields
        self.course_name.delete(0, tk.END)
        self.course_instructor_id.delete(0, tk.END)
    
    # Refresh the course treeview
        self.load_courses()
        self.populate_course_dropdown()

    # Delete student
    def delete_student(self):
        selected_item = self.student_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a student to delete.")
            return
        student_id = self.student_tree.item(selected_item)['values'][0]
        self.db.delete_student(student_id)
        self.student_tree.delete(selected_item)
        messagebox.showinfo("Success", "Student deleted successfully.")

    # Delete instructor
    def delete_instructor(self):
        selected_item = self.instructor_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an instructor to delete.")
            return
        instructor_id = self.instructor_tree.item(selected_item)['values'][0]
        self.db.delete_instructor(instructor_id)
        self.instructor_tree.delete(selected_item)
        messagebox.showinfo("Success", "Instructor deleted successfully.")

    # Delete course
    def delete_course(self):
        selected_item = self.course_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a course to delete.")
            return
        course_id = self.course_tree.item(selected_item)['values'][0]
        self.db.delete_course(course_id)
        self.course_tree.delete(selected_item)
        messagebox.showinfo("Success", "Course deleted successfully.")

    def create_treeview_frames(self, frame):
        # Student Treeview
        self.student_tree = ttk.Treeview(frame, columns=('ID', 'Name', 'Age', 'Email'), show='headings')
        self.student_tree.heading('ID', text='Student ID')
        self.student_tree.heading('Name', text='Name')
        self.student_tree.heading('Age', text='Age')
        self.student_tree.heading('Email', text='Email')
        self.student_tree.pack(padx=10, pady=10, fill="x")

        ttk.Button(frame, text="Delete Student", command=self.delete_student).pack(padx=10, pady=5, fill="x")
        ttk.Button(frame, text="Edit Student", command=self.edit_student).pack(padx=10, pady=5, fill="x")

        # Instructor Treeview
        self.instructor_tree = ttk.Treeview(frame, columns=('ID', 'Name', 'Age', 'Email'), show='headings')
        self.instructor_tree.heading('ID', text='Instructor ID')
        self.instructor_tree.heading('Name', text='Name')
        self.instructor_tree.heading('Age', text='Age')
        self.instructor_tree.heading('Email', text='Email')
        self.instructor_tree.pack(padx=10, pady=10, fill="x")

        ttk.Button(frame, text="Delete Instructor", command=self.delete_instructor).pack(padx=10, pady=5, fill="x")
        ttk.Button(frame, text="Edit Instructor", command=self.edit_instructor).pack(padx=10, pady=5, fill="x")

        # Course Treeview
        self.course_tree = ttk.Treeview(frame, columns=('ID', 'Course Name', 'Instructor ID'), show='headings')
        self.course_tree.heading('ID', text='Course ID')
        self.course_tree.heading('Course Name', text='Course Name')
        self.course_tree.heading('Instructor ID', text='Instructor ID')
        self.course_tree.pack(padx=10, pady=10, fill="x")

        ttk.Button(frame, text="Delete Course", command=self.delete_course).pack(padx=10, pady=5, fill="x")
        ttk.Button(frame, text="Edit Course", command=self.edit_course).pack(padx=10, pady=5, fill="x")


        # Student filter frame
        self.student_filter_frame = tk.LabelFrame(frame, text="Filter Students", padx=10, pady=10)
        self.student_filter_frame.pack(padx=10, pady=10, fill="both", expand="yes")

        ttk.Label(self.student_filter_frame, text="Search (Name/ID):").grid(row=0, column=0)
        self.student_search_entry = ttk.Entry(self.student_filter_frame)
        self.student_search_entry.grid(row=0, column=1)

        ttk.Button(self.student_filter_frame, text="Filter", command=self.filter_students).grid(row=1, columnspan=2)

        # Instructor filter frame
        self.instructor_filter_frame = tk.LabelFrame(frame, text="Filter Instructors", padx=10, pady=10)
        self.instructor_filter_frame.pack(padx=10, pady=10, fill="both", expand="yes")

        ttk.Label(self.instructor_filter_frame, text="Search (Name/ID):").grid(row=0, column=0)
        self.instructor_search_entry = ttk.Entry(self.instructor_filter_frame)
        self.instructor_search_entry.grid(row=0, column=1)

        ttk.Button(self.instructor_filter_frame, text="Filter", command=self.filter_instructors).grid(row=1, columnspan=2)

        # Course filter frame
        self.course_filter_frame = tk.LabelFrame(frame, text="Filter Courses", padx=10, pady=10)
        self.course_filter_frame.pack(padx=10, pady=10, fill="both", expand="yes")

        ttk.Label(self.course_filter_frame, text="Search (Course Name/ID):").grid(row=0, column=0)
        self.course_search_entry = ttk.Entry(self.course_filter_frame)
        self.course_search_entry.grid(row=0, column=1)

        ttk.Button(self.course_filter_frame, text="Filter", command=self.filter_courses).grid(row=1, columnspan=2)


        # Load students and instructors to treeviews
        self.load_students()
        self.load_instructors()
        self.load_courses()

    
    
    def filter_students(self):
        search_term = self.student_search_entry.get()
        filtered_students = self.db.filter_students(search_term)

        # Clear previous entries in the Treeview
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        # Insert filtered students into the Treeview
        for student in filtered_students:
            self.student_tree.insert('', 'end', values=(student[0], student[1], student[2], student[3])) 

    def filter_instructors(self):
        search_term = self.instructor_search_entry.get()
        filtered_instructors = self.db.filter_instructors(search_term)

        # Clear previous entries in the Treeview
        for item in self.instructor_tree.get_children():
            self.instructor_tree.delete(item)

        # Insert filtered instructors into the Treeview
        for instructor in filtered_instructors:
            self.instructor_tree.insert('', 'end', values=(instructor[0], instructor[1], instructor[2], instructor[3]))  

    def filter_courses(self):
        search_term = self.course_search_entry.get()
        filtered_courses = self.db.filter_courses(search_term)

        # Clear previous entries in the Treeview
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)

        # Insert filtered courses into the Treeview
        for course in filtered_courses:
            self.course_tree.insert('', 'end', values=(course[0], course[1], course[2]))


    def load_students(self):
        for student in self.db.get_students():
            self.student_tree.insert('', 'end', values=student)

    def load_instructors(self):
        for instructor in self.db.get_instructors():
            self.instructor_tree.insert('', 'end', values=instructor)

    def load_courses(self):
        for course in self.db.get_courses():
            self.course_tree.insert('', 'end', values=course)

    def close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.db.close()  # Close the database connection
            self.root.destroy()  # Close the Tkinter window 

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolManagementGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
