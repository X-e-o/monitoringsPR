import tkinter as tk
import tkinter.ttk as ttk
import sqlite3
from tkinter import messagebox 

# Database setup
conn = sqlite3.connect('performance_tracking.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS teachers
            (id INTEGER PRIMARY KEY, name TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS classes
            (id INTEGER PRIMARY KEY, name TEXT, teacher_id INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS students
            (id INTEGER PRIMARY KEY, name TEXT, class_id INTEGER, FOREIGN KEY (class_id) REFERENCES classes (id))''')

c.execute('''CREATE TABLE IF NOT EXISTS grades
            (id INTEGER PRIMARY KEY, student_id INTEGER, subject TEXT, grade REAL, FOREIGN KEY (student_id) REFERENCES students (id))''')

conn.commit()
conn.close()

class Teacher:
    """Teacher class to manage teacher-related functionality."""

    def __init__(self, name, id):
        self.name = name
        self.id = id

    def add_student(self, student):
        # Add student to the database
        # Pievienojiet studentu datu bāzei
        conn = sqlite3.connect('performance_tracking.db')
        c = conn.cursor()
        print("Student name:", student.name)
        print("Student class ID:", student.class_id)
        c.execute("INSERT INTO students (name, class_id) VALUES (?,?)", (student.name, student.class_id))
        student_id = c.lastrowid
        c.execute("UPDATE students SET id =? WHERE rowid =?", (student_id, student_id))
        c.execute("UPDATE classes SET num_students = num_students + 1 WHERE id =?", (student.class_id,))
        conn.commit()
        conn.close()

    def edit_grade(self, student_id, subject, grade):
        # Edit grade in the database
        # Rediģēt atzīmi datu bāzē
        conn = sqlite3.connect('performance_tracking.db')
        c = conn.cursor()
        c.execute("UPDATE grades SET grade = ? WHERE student_id = ? AND subject = ?", (grade, student_id, subject))
        conn.commit()
        conn.close()
        
        #Delete student
        #Noņemt studentu
    def delete_student(self):
        selection = self.treeview.selection()
        if selection:
            self.treeview.delete(selection)

class Student:
    """Student class to manage student-related functionality."""

    def __init__(self, name, id, class_id):
        self.name = name
        self.id = id
        self.class_id = class_id
        self.grades = []

    def add_grade(self, subject, grade):
        # Add grade to the student's grades list
        self.grades.append((subject, grade))

    def edit_grade(self, subject, grade):
        # Edit grade in the student's grades list
        for i, (s, g) in enumerate(self.grades):
            if s == subject:
                self.grades[i] = (s, grade)
                break
            
            
    def delete_grade(self, subject):
        # Delete grade from the student's grades list
        
            for i, (s, g) in enumerate(self.grades):
                if s == subject:
                    del self.grades[i]
                    break



class PerformanceTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Progresa reģistrēšanas sistēma (By Xeo_mrgt)")
        self.conn = sqlite3.connect("performance_tracking.db")
        self.c = self.conn.cursor()

        self.root.geometry("1920x1080") # Set the window size to 1920x1080 pixels
        icon_photo = tk.PhotoImage(file="programm/ico.png")
        root.iconphoto(False, icon_photo)
        
        self.frame_class = ttk.LabelFrame(self.root, text="Classes")
        self.frame_class.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.frame_class.columnconfigure(0, weight=1) # Make the first column expand to fill the available space

        self.teacher_combobox = ttk.Combobox(self.frame_class, state="readonly", values=[])
        self.teacher_combobox.grid(row=1, column=1, padx=0, pady=0, sticky="w")

        self.populate_teacher_combobox()


        #Klases interfeiss
        
        self.class_tree = ttk.Treeview(self.frame_class, columns=("CN", "CID", "TID"), show="headings")
        self.class_tree.heading("CN", text="Class_Name")
        self.class_tree.heading("CID", text="Class_ID")
        self.class_tree.heading("TID", text="Teacher ID")
        self.class_tree.column("CID", width=85)
        self.class_tree.column("CN", width=100)
        self.class_tree.column("TID", width=100)
        self.class_tree.grid(row=0, column=0, sticky="nsew")
        self.populate_class_tree()
        self.create_tables()

        #Pedagogu interfeiss
        
        self.frame_teacher = ttk.LabelFrame(self.root, text="Teachers")
        self.frame_teacher.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.teacher_tree = ttk.Treeview(self.frame_teacher, columns=("id", "name"), show="headings")
        self.teacher_tree.heading("#0", text="id")
        self.teacher_tree.heading("id", text="ID")
        self.teacher_tree.heading("name", text="Name")
        self.teacher_tree.grid(row=0, column=0, sticky="nsew")
        self.populate_teacher_tree()


        # Create a frame for the student information
        # Izveidojiet rāmi studenta informācijai
        self.frame_student = ttk.LabelFrame(self.root, text="Students")
        self.frame_student.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.frame_student.columnconfigure(0, weight=1)

        # Create a treeview widget for displaying the students
        # Izveidojiet koka skatījuma logrīku skolēnu parādīšanai
        self.student_tree = ttk.Treeview(self.frame_student, columns=("ID", "class", "class_id"), show="headings")
        self.student_tree.heading("ID", text="ID")
        self.student_tree.heading("class", text="Name")
        self.student_tree.heading("class_id", text="Class_ID")
        self.student_tree.column("ID", width=50)
        self.student_tree.column("class", width=150)
        self.student_tree.column("class_id", width=90)
        self.student_tree.grid(row=0, column=0, sticky="nsew")
        self.populate_student_tree()


        tk.Label(self.root, text="Teacher Name:").grid(row=1, column=0, padx=10, pady=1, sticky="w")
        self.teacher_name_entry = ttk.Entry(self.root)
        self.teacher_name_entry.grid(row=1, column=0, padx=100, pady=0, sticky="w")

        tk.Label(self.root, text="Class Name:").grid(row=2, column=0, padx=10, pady=1, sticky="w")
        self.class_name_entry = ttk.Entry(self.root)
        self.class_name_entry.grid(row=2, column=0, padx=100, pady=0, sticky="w")

        tk.Label(self.root, text="Student Name:").grid(row=3, column=0, padx=10, pady=1, sticky="w")
        self.student_name_entry = ttk.Entry(self.root)
        self.student_name_entry.grid(row=3, column=0, padx=100, pady=1, sticky="w")

        tk.Label(self.root, text="Subject name:").grid(row=4, column=0, padx=10, pady=1, sticky="w")
        self.subject_name_entry = ttk.Entry(self.root)
        self.subject_name_entry.grid(row=4, column=0, padx=100, pady=0, sticky="w")

        tk.Label(self.root, text="Grade:").grid(row=5, column=0, padx=10, pady=1, sticky="w")
        self.grade_entry = ttk.Entry(self.root)
        self.grade_entry.grid(row=5, column=0, padx=100, pady=0, sticky="w")

        tk.Button(self.root, text="Add Teacher", command=self.on_add_teacher_button_click).grid(row=6, column=0, padx=10, pady=10, sticky="w")
        tk.Button(self.root, text="Delete Teacher", command=self.on_delete_teacher_button_click).grid(row=6, column=1, padx=10, pady=10, sticky="w")

        tk.Button(self.root, text="Add Class", command=self.on_add_class_button_click).grid(row=7, column=0, padx=10, pady=10, sticky="w")
        tk.Button(self.root, text="Delete Class", command=self.on_delete_class_button_click).grid(row=7, column=1, padx=10, pady=10, sticky="w")

        tk.Button(self.root, text="Add Student", command=self.on_add_student_button_click).grid(row=8, column=0, padx=10, pady=10, sticky="w")
        tk.Button(self.root, text="Remove Student", command=self.on_remove_student_button_click).grid(row=8, column=1, padx=10, pady=10, sticky="w")

        tk.Button(self.root, text="Add Grade", command=self.on_add_grade_button_click).grid(row=9, column=0, padx=10, pady=10, sticky="w")
        tk.Button(self.root, text="Edit Grade", command=self.on_edit_grade_button_click).grid(row=9, column=1, padx=10, pady=10, sticky="w")

        tk.Button(self.root, text="Delete Grade", command=self.on_delete_grade_button_click).grid(row=10, column=0, padx=10, pady=10, sticky="w")

        tk.Button(self.root, text="Add Teacher", command=self.on_add_teacher_button_click)
        
        about_button = tk.Button(self.root, text="Об авторе", command=self.on_about_button_click)
        about_button.grid(row=10, column=2, padx=10, pady=10, sticky="se")
        
        
        
    
    
        
    
        
    def create_tables(self):
    # Create the 'teachers' table
    # Izveido "skolotāju" tabulu
        self.c.execute('''CREATE TABLE IF NOT EXISTS teachers
                            (id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE)''')

        # Create the 'classes' table
        # Izveido 'klases' tabulu
        self.c.execute('''CREATE TABLE IF NOT EXISTS classes
                            (id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE,
                            teacher_id INTEGER,
                            FOREIGN KEY (teacher_id) REFERENCES teachers (id))''')

        # Create the 'students' table
        # Izveido "skolēnu" tabulu
        self.c.execute('''CREATE TABLE IF NOT EXISTS students
                            (id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE,
                            class_id INTEGER,
                            FOREIGN KEY (class_id) REFERENCES classes (id))''')

        # Create the 'subjects' table
        # Izveido 'priekšmetu' tabulu
        self.c.execute('''CREATE TABLE IF NOT EXISTS subjects
                            (id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE)''')

        # Create the 'grades' table
        # Izveido "atzīmju" tabulu
        self.c.execute('''CREATE TABLE IF NOT EXISTS grades
                            (id INTEGER PRIMARY KEY,
                            student_id INTEGER,
                            subject_id INTEGER,
                            grade REAL NOT NULL,
                            FOREIGN KEY (student_id) REFERENCES students (id),
                            FOREIGN KEY (subject_id) REFERENCES subjects (id))''')

        # Unfinished
        # Nepabeigts
        self.c.execute('''CREATE TABLE IF NOT EXISTS class_students
                            (class_id INTEGER NOT NULL,
                            student_id INTEGER NOT NULL,
                            PRIMARY KEY (class_id, student_id),
                            FOREIGN KEY (class_id) REFERENCES classes (id),
                            FOREIGN KEY (student_id) REFERENCES students (id))''')

        # Commit the changes to the database
        # Veic izmaiņas datu bāzē
        self.conn.commit()

    def populate_student_tree(self):
        # Clear the existing treeview content
        # Notīra esošo koka skatījuma saturu
        self.student_tree.delete(*self.student_tree.get_children())

        # Retrieve the students from the database and populate the treeview
        # Izgūst studentus no datu bāzes un aizpilda koka skatījumu
        students = self.c.execute('''SELECT id, name, class_id FROM students ORDER BY name''').fetchall()
        for student in students:
            self.student_tree.insert('', 'end', values=student)

    def populate_class_tree(self):
            # Clear the existing treeview content
            # Notīra esošo koka skatījuma saturu
            self.class_tree.delete(*self.class_tree.get_children())

            # Retrieve the students from the database and populate the treeview
            # Izgūst klases no datu bāzes un aizpilda koka skatījumu
            classes = self.c.execute('''SELECT name, id, teacher_id FROM classes ORDER BY name''').fetchall()
            for c in classes:
                self.class_tree.insert('', 'end', values=c)


    def populate_grades_tree(self, student_id=None):
        # Clear the existing treeview content
        self.grade_tree.delete(*self.grade_tree.get_children())

        # Retrieve the grades from the database and populate the treeview
        if student_id:
            grades = self.c.execute('''SELECT subject, grade FROM grades WHERE student_id=? ORDER BY subject''', (student_id,)).fetchall()
        else:
            grades = self.c.execute('''SELECT subject, grade FROM grades ORDER BY subject''').fetchall()
        for grade in grades:
            self.grade_tree.insert('', 'end', values=grade)
            
    def on_student_tree_select(self, event):
        selected_student = self.student_tree.focus()
        if selected_student:
            student_id = int(self.student_tree.item(selected_student)['values'][0])
            self.populate_grades_tree(student_id)
        
    def populate_teacher_tree(self):
        # Clear the existing treeview content
        # Notīra esošo koka skatījuma saturu
        self.teacher_tree.delete(*self.teacher_tree.get_children())

        # Retrieve the teachers from the database and populate the treeview
        # Izgūst skolotājus no datu bāzes un aizpilda koka skatījumu
        teachers = self.c.execute('''SELECT id, name FROM teachers ORDER BY name''').fetchall()
        for teacher in teachers:
            self.teacher_tree.insert('', 'end', values=teacher)

    def on_add_teacher_button_click(self):
        teacher_name = self.teacher_name_entry.get()

        if not teacher_name:
            return

        self.c.execute("SELECT name FROM teachers WHERE name=?", (teacher_name,))
        result = self.c.fetchone()

        if result:
            print("Teacher name already exists.")
            return

        self.c.execute("INSERT INTO teachers (name) VALUES (?)", (teacher_name,))
        self.conn.commit()

        self.populate_teacher_tree()
        self.teacher_name_entry.delete(0, tk.END)

    def on_delete_teacher_button_click(self, event=None):
        # Get the selected teacher from the teacher_tree widget
        selected_teacher = self.teacher_tree.focus()
        if selected_teacher:
            teacher_id = int(self.teacher_tree.item(selected_teacher)['values'][0])

            # Check if the selected teacher exists in the teachers table
            self.c.execute("SELECT id FROM teachers WHERE id=?", (teacher_id,))
            result = self.c.fetchone()

            if not result:
                print("Selected teacher does not exist.")
                return

            # Delete the teacher from the database
            self.c.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
            self.conn.commit()

            # Remove the teacher from the teacher_tree widget
            self.teacher_tree.delete(selected_teacher)

            # Remove the classes associated with the deleted teacher
            self.c.execute("DELETE FROM classes WHERE teacher_id=?", (teacher_id,))
            self.conn.commit()

            # Remove the classes from the class_tree widget
            for class_ in self.class_tree.get_children():
                class_teacher_id = int(self.class_tree.item(class_)['values'][2])
                if class_teacher_id == teacher_id:
                    self.class_tree.delete(class_)


    def on_add_class_button_click(self, event=None):
        # Get the selected teacher from the teacher_combobox widget
        selected_teacher = self.teacher_combobox.get()

        # Check if the selected teacher exists in the teachers table
        self.c.execute("SELECT id FROM teachers WHERE name=?", (selected_teacher,))
        result = self.c.fetchone()

        if not result:
            print("Selected teacher does not exist.")
            return

        teacher_id = result[0]

        # Get the class name from the class_name_entry widget
        class_name = self.class_name_entry.get()

        # Insert the new class into the database
        self.c.execute('''INSERT INTO classes (name, teacher_id) VALUES (?,?)''', (class_name, teacher_id))
        self.conn.commit()

        # Add the class to the class_tree widget
        class_id = self.c.execute('''SELECT id FROM classes WHERE name=? AND teacher_id=?''', (class_name, teacher_id)).fetchone()[0]
        self.class_tree.insert('', 'end', values=(class_name, class_id, teacher_id))

        # Clear the class_name_entry widget
        self.class_name_entry.delete(0, tk.END)

        
    def get_teacher_id_by_name(self, name):
        self.c.execute("SELECT id FROM teachers WHERE name=?", (name,))
        result = self.c.fetchone()
        return result[0] if result else None
    
    
    def on_delete_class_button_click(self, event=None):
        # Get the selected class from the class_tree widget
        selected_class = self.class_tree.focus()
        if selected_class:
            class_id_text = self.class_tree.item(selected_class)['values'][1]
            
            # Check if the selected class exists in the classes table
            self.c.execute("SELECT id FROM classes WHERE id=?", (class_id_text,))
            result = self.c.fetchone()

            if not result:
                print("Selected class does not exist.")
                return

            # Remove the students associated with the deleted class
            self.c.execute("DELETE FROM students WHERE class_id=?", (class_id_text,))
            self.conn.commit()

            # Remove the class from the class_tree widget
            self.class_tree.delete(selected_class)

            # Remove the class from the classes table
            self.c.execute("DELETE FROM classes WHERE id=?", (class_id_text,))
            self.conn.commit()

            # Remove the classes from the frame_class widget
            for class_ in self.frame_class.winfo_children():
                if class_.winfo_class() == "TLabel" and "Class_ID" in class_.cget("text"):
                    class_id_text = class_.cget("text").split(": ")[-1]
                    if class_id_text == class_id_text:
                        class_.destroy()


    def on_add_student_button_click(self):
        selected_class = self.class_tree.focus()
        if selected_class:
            class_name = self.class_tree.item(selected_class)['values'][0]
        else:
            tk.messagebox.showerror("Error", "No class selected.")
            return

        student_name = self.student_name_entry.get()

        # Retrieve the class_id of the selected class
        self.c.execute("SELECT id FROM classes WHERE name=?", (class_name,))
        class_row = self.c.fetchone()
        if class_row:
            class_id = class_row[0]
        else:
            tk.messagebox.showerror("Error", "Selected class does not exist.")
            return

        # Add the student to the database
        self.c.execute("INSERT INTO students (name, class_id) VALUES (?,?)", (student_name, class_id))
        self.conn.commit()

        # Clear the student_name_entry widget
        self.student_name_entry.delete(0, tk.END)

        # Update the student_tree widget
        self.populate_student_tree()


    def on_remove_student_button_click(self, event=None):
        selected_student = self.student_tree.focus()
        if selected_student:
            student_name = self.student_tree.item(selected_student)['values'][1]
            class_id = self.student_tree.item(selected_student)['values'][2]

            # Retrieve the student_id from the database
            self.c.execute("SELECT id FROM students WHERE name=? AND class_id=?", (student_name, class_id))
            student_row = self.c.fetchone()

            if student_row:
                student_id = student_row[0]

                # Delete the student from the database
                self.c.execute("DELETE FROM students WHERE id=?", (student_id,))
                self.conn.commit()

            # Remove the student from the student_tree widget
            self.student_tree.delete(selected_student)
        else:
            tk.messagebox.showerror("Error", "Student not found in the database.")
            
    def on_add_grade_button_click(self):
        # Get the selected student from the student_tree widget
        selected_student = self.student_tree.focus()
        if selected_student:
            student_id = int(self.student_tree.item(selected_student)['values'][0])

            # Get the subject and grade from the subject_name_entry and grade_entry widgets
            subject = self.subject_name_entry.get()
            grade = float(self.grade_entry.get())

            # Add the grade to the database
            self.c.execute("INSERT INTO grades (student_id, subject, grade) VALUES (?,?,?)", (student_id, subject, grade))
            self.conn.commit()

            # Clear the subject_name_entry and grade_entry widgets
            self.subject_name_entry.delete(0, tk.END)
            self.grade_entry.delete(0, tk.END)

            # Populate the grade_tree widget with the grades of the selected student
            self.populate_grades_tree(student_id)

    def on_edit_grade_button_click(self):
        # Get the selected grade from the grade_tree widget
        selected_grade = self.grade_tree.focus()
        if selected_grade:
            student_id = int(self.grade_tree.item(selected_grade)['values'][0])
            subject = self.grade_tree.item(selected_grade)['values'][1]

            # Get the new grade from the grade_entry widget
            grade = float(self.grade_entry.get())

            # Update the grade in the database
            self.c.execute("UPDATE grades SET grade=? WHERE student_id=? AND subject=?", (grade, student_id, subject))
            self.conn.commit()

            # Clear the grade_entry widget
            self.grade_entry.delete(0, tk.END)

            # Populate the grade_tree widget with the grades of the selected student
            self.populate_grades_tree(student_id)
            
    def populate_teacher_combobox(self):
        self.c.execute("SELECT name FROM teachers")
        teachers = [row[0] for row in self.c.fetchall()]
        self.teacher_combobox["values"] = teachers

    def on_delete_grade_button_click(self):
        # Get the selected grade from the grade_tree widget
        selected_grade = self.grade_tree.focus()
        if selected_grade:
            student_id = int(self.grade_tree.item(selected_grade)['values'][0])
            subject = self.grade_tree.item(selected_grade)['values'][1]

            # Delete the grade from the database
            self.c.execute("DELETE FROM grades WHERE student_id=? AND subject=?", (student_id, subject))
            self.conn.commit()

            # Populate the grade_tree widget with the grades of the selected student
            self.populate_grades_tree(student_id)



    def on_about_button_click(self):
        about_info = f"Версия программы: Beta 0.5\nАвтор программы: Алексей Смирнов\nДата последнего обновления: 16.05.2024"
        tk.messagebox.showinfo("Об авторе", about_info)
        
    
    def __del__(self):
        # Close the database connection when the object is destroyed
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PerformanceTrackingApp(root)
    root.mainloop()