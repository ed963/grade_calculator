from __future__ import annotations
from typing import List


class Assignment:
    """An assignment for an university course.

    ===Attributes===
        name: the name of this assignment
        total: the total possible marks for this assignment
        earned: the number of marks earned for this assignment
        weight: the weight of this assignment (as a percentage)
    """
    name: str
    earned: float
    total: float
    weight: float

    def __init__(self, name: str, earned: float, total: float, weight: float
                 ) -> None:
        """Initialize a new assignment with given <name>, <total> possible
        marks, and a weight of <weight>."""
        self.name = name
        self.earned = earned
        self.total = total
        self.weight = weight

    def percentage(self) -> float:
        """Return the percentage grade of this assignment."""
        return self.earned / self.total


class Course:
    """A university course with assignments.

    ===Attributes===
        code: the course code of this course
        assignments: a list of assignments for this course
    """
    code: str
    assignments: List[Assignment]

    def __init__(self, code: str) -> None:
        """Initialize a new course with the given <code>."""
        self.code = code
        self.assignments = []
        self.average = 0.0

    def calculate_average(self) -> float:
        """Return the average of this course to two decimal places."""
        total_weight = 0.0
        total_earned = 0.0

        for assignment in self.assignments:
            total_weight += assignment.weight
            total_earned += assignment.percentage() * assignment.weight

        if total_weight == 0.0:
            return 0.0
        else:
            return round((total_earned / total_weight) * 100, 2)
