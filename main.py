"""Student Performance Analysis System demonstrating core Python OOP principles."""

import csv
from abc import ABC, abstractmethod
from pathlib import Path

DATA_FILE = Path(__file__).with_name("students.csv")
REPORT_FILE = Path(__file__).with_name("performance_report.txt")


class Student(ABC):
    """Abstract student class. Scores are encapsulated and validated."""

    def __init__(self, student_id, name, scores):
        self.student_id = student_id
        self.name = name
        self.__scores = []  # Private attribute: encapsulation
        for score in scores:
            self.add_score(score)

    @property
    def scores(self):
        """Return a copy to prevent external modification of the private list."""
        return self.__scores.copy()

    def add_score(self, score):
        """Validate marks before storing them."""
        score = float(score)
        if not 0 <= score <= 100:
            raise ValueError(f"Score must be between 0 and 100: {score}")
        self.__scores.append(score)

    def average(self, *extra_scores):
        """Flexible arguments demonstrate Python's alternative to overloading.

        With no arguments, average existing scores; with extra scores, include
        those values without changing the student's saved marks.
        """
        additional = [float(score) for score in extra_scores]
        if any(not 0 <= score <= 100 for score in additional):
            raise ValueError("Additional scores must be between 0 and 100")
        all_scores = self.__scores + additional
        return sum(all_scores) / len(all_scores) if all_scores else 0.0

    def grade(self):
        average = self.average()
        if average >= 80:
            return "A"
        if average >= 70:
            return "B"
        if average >= 60:
            return "C"
        if average >= 50:
            return "D"
        return "F"

    @abstractmethod
    def scholarship_eligible(self):
        """Each student type defines its own scholarship eligibility rule."""

    @abstractmethod
    def student_type(self):
        """Identify the type of student."""


class RegularStudent(Student):
    """Regular students qualify with an average of at least 85%."""

    def scholarship_eligible(self):
        return self.average() >= 85

    def student_type(self):
        return "Regular"


class ScholarshipStudent(Student):
    """Scholarship-track students retain eligibility with at least 80%."""

    def scholarship_eligible(self):  # Method overriding / polymorphism
        return self.average() >= 80 and min(self.scores) >= 70

    def student_type(self):
        return "Scholarship"


class PerformanceAnalyzer:
    """Calculate student and whole-class performance statistics."""

    def __init__(self, students):
        if not students:
            raise ValueError("At least one student is required for analysis")
        self.students = students

    def highest_average(self):
        return max(self.students, key=lambda student: student.average())

    def lowest_average(self):
        return min(self.students, key=lambda student: student.average())

    def overall_class_average(self):
        return sum(student.average() for student in self.students) / len(self.students)

    def generate_report(self):
        lines = [
            "STUDENT PERFORMANCE ANALYSIS REPORT",
            "=" * 84,
            f"{'ID':<7}{'Name':<20}{'Type':<14}{'Average':>9}  {'Grade':<7}{'Scholarship'}",
            "-" * 84,
        ]
        for student in self.students:  # Polymorphic calls for both student types
            eligible = "Yes" if student.scholarship_eligible() else "No"
            lines.append(
                f"{student.student_id:<7}{student.name:<20}"
                f"{student.student_type():<14}{student.average():>8.2f}%  "
                f"{student.grade():<7}{eligible}"
            )
        best = self.highest_average()
        lowest = self.lowest_average()
        lines.extend([
            "-" * 84,
            "CLASS SUMMARY",
            f"Number of students: {len(self.students)}",
            f"Highest average: {best.name} ({best.average():.2f}%)",
            f"Lowest average: {lowest.name} ({lowest.average():.2f}%)",
            f"Overall class average: {self.overall_class_average():.2f}%",
            f"Scholarship eligible: {sum(s.scholarship_eligible() for s in self.students)}",
            "",
            "Scholarship rules (illustrative project rules):",
            "Regular: average >= 85%; Scholarship-track: average >= 80% and every mark >= 70%.",
        ])
        return "\n".join(lines)


def load_students(csv_file):
    """Create different student subclasses from CSV records."""
    students = []
    with open(csv_file, newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            student_type = row["student_type"].strip().lower()
            classes = {"regular": RegularStudent, "scholarship": ScholarshipStudent}
            if student_type not in classes:
                raise ValueError(f"Unknown student type: {student_type}")
            scores = [row[subject] for subject in ("math", "english", "science")]
            students.append(classes[student_type](row["student_id"], row["name"], scores))
    return students


def main():
    students = load_students(DATA_FILE)
    analyzer = PerformanceAnalyzer(students)
    report = analyzer.generate_report()
    print(report)
    REPORT_FILE.write_text(report + "\n", encoding="utf-8")
    print(f"\nReport saved to: {REPORT_FILE.name}")
    # Overloading alternative: same method supports additional optional scores.
    print(f"\nOverloading example: {students[0].name}'s average with an extra 90 = "
          f"{students[0].average(90):.2f}%")


if __name__ == "__main__":
    main()
