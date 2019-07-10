"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithsm'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    And this function should return a Dict
    """

    def __init__(self, max_floor: int, num_people: int) -> None:
        ArrivalGenerator.__init__(self, max_floor, num_people)

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """
        This function returns a dictionary (new_person).

        And the key of new_person will be an integer, which should be floor
        number here. And the value is a list whose item is Person. The length of
        the list is equal to the num_people.
        """
        new_person = {}
        for i in range(1, (self.max_floor + 1)):
            new_person[i] = []

        for i in range(self.num_people):
            start_floor = random.randint(1, self.max_floor)
            target_floor = random.randint(1, self.max_floor)
            while start_floor == target_floor:
                start_floor = random.randint(1, self.max_floor)
                target_floor = random.randint(1, self.max_floor)

            new_person[start_floor].append(Person(start_floor, target_floor))

        return new_person


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.
    === Attributes ===
    arrival_list: a list that records every line of a csvfile
    """
    arrival_list: List

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor, None)

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.
        self.arrival_list = []
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                self.arrival_list.append(list(map(int, line)))
                # to one line of the original file.
                # You'll need to convert the strings to ints and then process
                # and store them.

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """
        This function returns a dictionary (new_person), which records the
        person that should appear in this round and the floor s/he appears.
        """
        new_person = {}
        for i in range(1, (self.max_floor + 1)):
            new_person[i] = []

        i = 1
        for every_round in self.arrival_list:
            if round_num == every_round[0]:
                while i <= (len(every_round) - 1):
                    if every_round[i] <= self.max_floor:
                        new_person[every_round[i]].\
                            append(Person(every_round[i], every_round[i+1]))
                    i += 2
                break

        return new_person


###############################################################################
# Elevator moving algorithms
###############################################################################


class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """
        This function returns a list (direction_list). And the length of
        direction_list is equal to the length of elevators after this function.

        The function will create a random direction, from Direction.UP,
        Direction.STAY and Direction.DOWN for every elevator.

        And since it is possible that a elevator is on the top floor but the
        direction for it is UP, or a elevator is on the lowest floor but the
        direction for it is DOWN. So, after creating the direction for each
        floor, the function enter a while loop which runs at list one time to
        avoid such situation.
        """
        direction_list = []
        direction_choice = [Direction.UP, Direction.STAY, Direction.DOWN]
        for index, elevator in enumerate(elevators):
            direction_list.append(random.choice(direction_choice))
            while True:
                if direction_list[index] == Direction.UP and \
                        elevator.floor == max_floor:
                    direction_list[index] = random.choice(direction_choice)
                elif direction_list[index] == Direction.DOWN and \
                        elevator.floor == 1:
                    direction_list[index] = random.choice(direction_choice)
                else:
                    break

        return direction_list


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        direction_list = []
        for i, elevator in enumerate(elevators):
            if elevator.fullness() != 0.0:
                if elevator.passengers[0].target > elevator.floor:
                    direction_list.append(Direction.UP)
                elif elevator.passengers[0].target < elevator.floor:
                    direction_list.append(Direction.DOWN)
                else:
                    direction_list.append(Direction.STAY)
            else:
                direction_list.append(Direction.STAY)
                for key in waiting:
                    if len(waiting[key]) != 0 and key > elevator.floor:
                        direction_list[i] = Direction.UP
                        break
                    elif len(waiting[key]) != 0 and key < elevator.floor:
                        direction_list[i] = Direction.DOWN
                        break
                    elif len(waiting[key]) != 0 and key == elevator.floor:
                        direction_list[i] = Direction.STAY
                        break

        return direction_list


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        direction_list = []
        for elevator in elevators:
            interval = max_floor
            target = elevator.floor
            if elevator.fullness() == 0.0:
                for floor in waiting:
                    if len(waiting[floor]) != 0 and \
                            abs(floor - elevator.floor) < interval:
                        target = floor
                    else:
                        target = target
            else:
                for passenger in elevator.passengers:
                    if abs(passenger.target - elevator.floor) < interval:
                        target = passenger.target
                    else:
                        target = target
                    break
            if target > elevator.floor:
                direction_list.append(Direction.UP)
            elif target < elevator.floor:
                direction_list.append(Direction.DOWN)
            else:
                direction_list.append(Direction.STAY)

        return direction_list


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'max-attributes': 12,
        'disable': ['R0201']
    })
