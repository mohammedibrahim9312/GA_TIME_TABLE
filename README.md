
---

## GA_TIME_TABLE

```md
# GA Timetable Scheduling System

A university timetable scheduling system built using a Genetic Algorithm (GA) to automatically generate optimized schedules while minimizing conflicts between courses, lecturers, rooms, and time slots.

## Features

- Automatic timetable generation
- Conflict detection and minimization
- Genetic Algorithm optimization
- Lecturer and room assignment
- Fitness score evaluation
- GUI for displaying schedules

## Problem Solved

Manual timetable scheduling is difficult and time-consuming because of:

- Lecturer conflicts
- Room conflicts
- Overlapping courses
- Limited available time slots

This project solves these issues using Genetic Algorithms to generate optimized schedules automatically.

## Technologies Used

- Python
- Tkinter GUI
- Genetic Algorithm
- Object-Oriented Programming

## Genetic Algorithm Components

### Population
A set of possible timetable solutions.

### Fitness Function
Evaluates schedules based on the number of conflicts.

### Selection
Chooses the best schedules for reproduction.

### Crossover
Combines two schedules to create better offspring.

### Mutation
Randomly modifies schedules to maintain diversity.

## Fitness Evaluation

The algorithm minimizes:

- Room conflicts
- Lecturer conflicts
- Duplicate course scheduling

Higher fitness means fewer conflicts and a better timetable.

## Example Output

```text
Fitness: 90
Conflicts: 1
