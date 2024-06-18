class Assignment:
    def __init__(self, name, due_date):
        self.name = name
        self.due_date = due_date

class StudentClass:
    def __init__(self, class_name):
        self.class_name = class_name
        self.assignments = []

    def add_assignment(self, assignment):
        self.assignments.append(assignment)
