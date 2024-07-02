class Assignment:
    def __init__(self, name, due_date, description):
        self.name = name
        self.due_date = due_date
        self.description = description

class StudentClass:
    def __init__(self, class_name, class_id):
        self.class_name = class_name
        self.class_id = class_id
        self.assignments = []

    def add_assignment(self, assignment):
        self.assignments.append(assignment)
