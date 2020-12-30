from __future__ import annotations
from tkinter import *
from tkinter.ttk import *
from courses import Assignment, Course
import sqlite3


class App:
    """A class that handles the creation and methods of the main application."""
    def __init__(self, master: Tk) -> None:
        # All widgets associated with this application will be placed on a frame
        self.frame = frame = Frame(master)
        frame.grid(row=0, column=0, padx=10, pady=10)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, minsize=80, weight=1)
        frame.grid_columnconfigure(2, minsize=80, weight=1)
        frame.grid_columnconfigure(3, minsize=150, weight=1)

        # Column headers for the main application
        Label(frame, text="Courses", font=("Arial", 12)).grid(row=0, column=0,
                                                              padx=50)
        Label(frame, text="Avg", font=("Arial", 12)).grid(row=0, column=3,
                                                          padx=50)
        self.button = Button(frame, text="Add course", command=self.add_course)
        self.button.grid(row=1, column=0, pady=10, padx=10)

    def add_course(self) -> None:
        """Add a new course by creating an instance of AddCourse."""
        self.button.grid_forget()
        AddCourse(self.frame)
        self.button.grid(column=0, pady=10, padx=10)


class CourseWidget:
    """A class that handles the creation of the widgets and associated methods
    for a single course.

    Each course has the following widgets, which are instantiated as instance
    attributes:
        - code: A Label widget that displays the course code
        - editor: A Toplevel widget that allows for the assignments associated
        with the course to be edited
        - edit: A Button widget that opens the assignment editor
        - delete: A Button widget that deletes the course
        - avg: A Label widget that displays the average for the course
    """

    def __init__(self, master: Frame, course_obj: Course) -> None:
        """Instantiate widgets associated with the given <course_obj> and place
        them onto <master>."""
        # All widgets for this course are slaves of a frame from the main app
        self.master = master

        # Records the associated Course object and its average grade as
        # instance variables
        self.course = course_obj
        self.average = average = DoubleVar()
        average.set(course_obj.calculate_average())

        # Create and place widgets associated with this course
        next_row = master.grid_size()[1]

        self.code = Label(master, text=self.course.code)
        self.code.grid(row=next_row, column=0)

        self.edit = Button(master, text="Edit assignments",
                           command=self.edit_assignments)
        self.edit.grid(row=next_row, column=1)

        self.delete = Button(master, text="Delete course",
                             command=self.delete_course)
        self.delete.grid(row=next_row, column=2)

        self.avg = Label(master, textvariable=average,
                         font=("arial", 10, "bold"))
        self.avg.grid(row=next_row, column=3, padx=50)

        # Create the assignment editor window associated with this course
        # This is done using a separate method for the sake of clarity
        self.editor = None
        self.button = None
        self.assignments = None
        self.create_editor()

    def create_editor(self) -> None:
        """Create the assignment editor window and its widgets for this course.
        """
        self.editor = editor = Toplevel(self.master)
        editor.title("Assignments for " + self.course.code)
        editor.geometry("+800+200")
        self.editor.withdraw()

        editor.protocol("WM_DELETE_WINDOW", self.update_assignments)

        editor.grid_columnconfigure(0, minsize=300, weight=1)
        editor.grid_columnconfigure(1, minsize=100, weight=1)
        editor.grid_columnconfigure(2, minsize=100, weight=1)
        editor.grid_columnconfigure(3, minsize=100, weight=1)

        # Column headers for assignment editor
        Label(editor, text="Assignment", font=("Arial", 10)).grid(row=0,
                                                                  column=0)
        Label(editor, text="Earned marks", font=("Arial", 10)).grid(row=0,
                                                                    column=1)
        Label(editor, text="Total marks", font=("Arial", 10)).grid(row=0,
                                                                   column=2)
        Label(editor, text="Weight", font=("Arial", 10)).grid(row=0, column=3)

        # Create first row of empty entry boxes
        name = Entry(self.editor, width=30)
        name.grid(row=1, column=0)

        earned = Entry(self.editor, width=5)
        earned.grid(row=1, column=1, pady=5)

        total = Entry(self.editor, width=5)
        total.grid(row=1, column=2, pady=5)

        weight = Entry(self.editor, width=5)
        weight.grid(row=1, column=3, pady=5)

        # Button allows for further rows to be added. Each row of Entry widgets
        # corresponds to a different assignment
        self.button = Button(editor, text="+", command=self.add_assignment)
        self.button.grid(row=2, column=0, pady=10, padx=10)

        # Store references to the Entry widgets in a dictionary that maps
        # row numbers to a list of the Entry widgets on that row
        self.assignments = {1: [name, earned, total, weight]}

    def delete_course(self) -> None:
        """Delete all widgets associated with this course from the GUI and
        delete all assignments of this course from the database.
        """
        self.code.destroy()
        self.edit.destroy()
        self.delete.destroy()
        self.avg.destroy()
        self.editor.destroy()

        c.execute('DELETE FROM assignments WHERE course=?', (self.course.code,))

    def edit_assignments(self) -> None:
        """Open the assignment editor window for this course."""
        self.editor.deiconify()
        self.editor.grab_set()

    def add_assignment_gui(self) -> None:
        """Add a new row of Entry widgets to this course's assignment editor."""
        self.button.grid_forget()

        next_row = self.editor.grid_size()[1]

        name = Entry(self.editor, width=30)
        name.grid(row=next_row, column=0)

        earned = Entry(self.editor, width=5)
        earned.grid(row=next_row, column=1, pady=5)

        total = Entry(self.editor, width=5)
        total.grid(row=next_row, column=2, pady=5)

        weight = Entry(self.editor, width=5)
        weight.grid(row=next_row, column=3, pady=5)

        self.button.grid(column=0, pady=10, padx=10)

        # References to Entry widgets are stored in the dictionary
        # self.assignments
        self.assignments[next_row] = [name, earned, total, weight]

    def add_assignment(self) -> None:
        """Add a new row of Entry widgets to this course's assignment editor and
        update the database to reflect the addition of a new assignment."""
        self.add_assignment_gui()

        # Record the creation of the new assignment in the database
        c.execute('INSERT INTO assignments (course, row) VALUES (?, ?)',
                  (self.course.code, max(self.assignments.keys())))

    def update_assignments_gui(self) -> None:
        """Update the assignments of <self.course> with the information from the
        assignment editor, and update the value of <self.average>.

        For each row of the assignment editor:
            - If there is an unfilled entry, the row is not added as an
            assignment.
            - If all entries are filled, but there is an invalid entry, a
            ValueError is raised. The value of <self.average> is not updated in
            this case.
            - Otherwise, a new Assignment object is created and added to
            <self.course>'s list of assignments.
        """
        # Clear the assignment list of <self.course> so that it can be updated
        self.course.assignments.clear()

        for i in range(1, self.editor.grid_size()[1] - 1):
            name = self.assignments[i][0].get()
            earned = self.assignments[i][1].get()
            total = self.assignments[i][2].get()
            weight = self.assignments[i][3].get()

            if earned == "" or total == "" or weight == "":
                pass
            elif (float(earned) < 0 or float(total) <= 0 or
                  float(weight) < 0):
                raise ValueError
            else:
                assignment = Assignment(name, float(earned), float(total),
                                        float(weight))
                self.course.assignments.append(assignment)

        self.average.set(self.course.calculate_average())

    def update_assignments_db(self) -> None:
        """Update the database with the information from the assignment editor.
        """
        for i in range(1, len(self.assignments) + 1):
            if self.assignments[i][0].get() != '':
                c.execute('''UPDATE assignments SET name=?
                             WHERE course=? AND row=?''',
                          (self.assignments[i][0].get(), self.course.code, i))
            if self.assignments[i][1].get() != '':
                c.execute('''UPDATE assignments SET earned=?
                             WHERE course=? AND row=?''',
                          (self.assignments[i][1].get(), self.course.code, i))
            if self.assignments[i][2].get() != '':
                c.execute('''UPDATE assignments SET total=?
                             WHERE course=? AND row=?''',
                          (self.assignments[i][2].get(), self.course.code, i))
            if self.assignments[i][3].get() != '':
                c.execute('''UPDATE assignments SET weight=?
                             WHERE course=? AND row=?''',
                          (self.assignments[i][3].get(), self.course.code, i))

    def update_assignments(self) -> None:
        """Attempt to update the assignments of <self.course> and database with
        information from the assignment editor, and hides the assignment editor.

        If a ValueError is raised, an error window is created and the assignment
        editor is not hidden.
        """
        try:
            self.update_assignments_gui()

            # The remaining two lines only execute if no ValueError is raised
            # during the previous method call
            self.editor.grab_release()
            self.editor.withdraw()
            self.update_assignments_db()

        except ValueError:
            error = Toplevel(self.editor)
            error.title("Error!")
            error.geometry("+810+225")
            error.grid_rowconfigure(0, weight=1)
            error.grid_columnconfigure(0, weight=1)
            message = "Invalid entry!\nPlease ensure that \"total\" is a " \
                      "positive number, and that \"earned\" and \"weight\" " \
                      "are non-negative numbers."
            Label(error, text=message).grid(row=0, column=0, padx=10, pady=10)

            error.grab_set()


class AddCourse:
    """A class that handles the creation of the Toplevel widget created when
    adding new courses, and its methods.
    """
    def __init__(self, master: Frame) -> None:
        """Instantiate Toplevel widget that is used to add a new course."""
        self.master = master
        self.new_course_window = new_course_window = Toplevel(master)

        new_course_window.title("New course")
        new_course_window.geometry("375x75+350+250")

        prompt = Label(new_course_window, text="Enter the course code:")
        prompt.grid(row=0, column=0, padx=10, pady=10)

        self.entry = Entry(new_course_window)
        self.entry.grid(row=0, column=1)

        confirmation = Button(new_course_window, text="OK", command=lambda:
                              self.confirm_course(self.entry.get()),
                              default=ACTIVE)
        confirmation.grid(row=1, columnspan=2, pady=5)

        new_course_window.grab_set()
        master.wait_window(new_course_window)

    def confirm_course(self, code: str) -> None:
        """Create a new instance of CourseWidget, record this new course in the
        database, and destroy the Toplevel widget <self.new_course_window> iff
        the given course <code> does not already exist.

        Otherwise, an error window is created.
        """
        matches = False

        # Loop through all existing courses recorded within the database and
        # stops once a match is found
        for code_tuple in c.execute('SELECT DISTINCT course FROM assignments'):
            if code in code_tuple:
                matches = True
                break

        # If a match was found (the course code already exists), an error window
        # is displayed
        if matches:
            error = Toplevel(self.new_course_window)
            error.title("Error!")
            error.geometry("+425+275")
            error.grid_rowconfigure(0, weight=1)
            error.grid_columnconfigure(0, weight=1)
            message = "Course with this code already exists!"
            Label(error, text=message).grid(row=0, column=0,
                                            padx=10, pady=10)

            error.grab_set()

        else:
            # Instantiate a new Course object and create its associated widgets
            # by creating an instance of CourseWidget
            course_obj = Course(code)
            CourseWidget(self.master, course_obj)
            self.new_course_window.destroy()

            # The new course is recorded in the database
            c.execute('INSERT INTO assignments (course, row) VALUES (?, ?)',
                      (code, 1))


def create_table() -> None:
    """Create the 'assignment' table using the given <cursor> iff it does not
    already exist.

    The table has the following columns and data types:
        - course (text)
        - row (integer)
        - name (text)
        - earned (real)
        - total (real)
        - weight (real)
    """
    c.execute('''SELECT name 
                 FROM sqlite_master 
                 WHERE type="table" 
                 AND name="assignments"''')

    if c.fetchone() is None:
        c.execute('''CREATE TABLE assignments(course text, row integer, 
                     name text, earned real, total real, weight real)''')


def update_gui() -> None:
    """Update the GUI of the main application with the assignments from the
    database.
    """
    c.execute('SELECT DISTINCT course FROM assignments')
    courses_list = c.fetchall()

    for course in courses_list:
        app.button.grid_forget()
        widget = CourseWidget(app.frame, Course(course[0]))
        app.button.grid(column=0, pady=10, padx=10)
        c.execute('''SELECT * FROM assignments
                     WHERE course=?
                     ORDER BY row''', (course[0],))
        for row in c.fetchall():
            if row[1] == 1:
                if row[2] is not None:
                    widget.assignments[1][0].insert(0, row[2])
                for i in range(1, 4):
                    if row[i + 2] is not None:
                        widget.assignments[1][i].insert(0, str(row[i + 2]))
            else:
                widget.add_assignment_gui()
                if row[2] is not None:
                    widget.assignments[row[1]][0].insert(0, row[2])
                for i in range(1, 4):
                    if row[i + 2] is not None:
                        widget.assignments[row[1]][i].insert(0, str(row[i + 2]))
        widget.update_assignments_gui()


if __name__ == '__main__':
    root = Tk()
    root.grid_columnconfigure(0, weight=1)
    root.title("Grade Calculator")
    root.geometry("+275+200")

    app = App(root)

    # Create a connection and cursor to the database
    conn = sqlite3.connect("grades.db")
    c = conn.cursor()

    create_table()
    update_gui()

    root.mainloop()
    conn.commit()
