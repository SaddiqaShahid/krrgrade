# grading_logic.py
import numpy as np

def load_grading_rules(file_path="grading_rules.pl"):
    rules = []
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line or not line.startswith("grade"): continue
            grade_part = line.split(":-")[0]
            conditions = line.split(":-")[1].replace(".", "").strip()
            grade = grade_part.split(",")[1].strip().replace("'", "").replace(")", "")
            rules.append((grade, conditions))
    return rules

def evaluate_condition(condition_str, marks):
    conditions = condition_str.split(",")
    for cond in conditions:
        cond = cond.strip()
        if ">=" in cond:
            val = int(cond.split(">=")[1])
            if not marks >= val:
                return False
        elif "<=" in cond:
            val = int(cond.split("<=")[1])
            if not marks <= val:
                return False
        elif ">" in cond:
            val = int(cond.split(">")[1])
            if not marks > val:
                return False
        elif "<" in cond:
            val = int(cond.split("<")[1])
            if not marks < val:
                return False
    return True

def absolute_grade_from_file(marks, rules):
    for grade, condition in rules:
        if evaluate_condition(condition, marks):
            return grade
    return "N/A"

def relative_grades(marks):
    marks_arr = np.array(marks)
    mean = np.mean(marks_arr)
    std = np.std(marks_arr)

    grades = []
    for m in marks:
        z = (m - mean) / std if std != 0 else 0

        if z >= 1.5:
            grades.append("A+")
        elif z >= 1.0:
            grades.append("A-")
        elif z >= 0.5:
            grades.append("B+")
        elif z >= 0.0:
            grades.append("B-")
        elif z >= -0.5:
            grades.append("C+")
        elif z >= -1.0:
            grades.append("C-")
        elif z >= -1.5:
            grades.append("D+")
        else:
            grades.append("F")
    return grades
