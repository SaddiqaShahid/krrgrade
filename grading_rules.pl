grade(Marks, 'A+') :- Marks >= 90.
grade(Marks, 'A-') :- Marks >= 85, Marks < 90.
grade(Marks, 'B+') :- Marks >= 80, Marks < 85.
grade(Marks, 'B-') :- Marks >= 75, Marks < 80.
grade(Marks, 'C+') :- Marks >= 65, Marks < 75.
grade(Marks, 'C-') :- Marks >= 55, Marks < 65.
grade(Marks, 'D')  :- Marks >= 40, Marks < 55.
grade(Marks, 'F')  :- Marks < 40.
