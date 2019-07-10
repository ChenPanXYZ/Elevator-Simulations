"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any

import algorithms
from algorithms import Direction
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    stats: a dictionary of the statistics of the simulation. (key are the date
    name, values are the date)
    """
    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    stats: Dict

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.elevators = []
        for i in range(config['num_elevators']):
            self.elevators.append(Elevator([], 1, config['elevator_capacity']))
        self.arrival_generator = config['arrival_generator']
        self.moving_algorithm = config['moving_algorithm']
        self.waiting = {}
        for i in range(config['num_floors']):
            self.waiting[i+1] = []
        self.num_floors = config['num_floors']
        self.visualizer = Visualizer(self.elevators,  # should be self.elevators
                                     config['num_floors'],
                                     # should be self.num_floors
                                     config['visualize'])
        self.stats = {
            'num_iterations': 0,
            'total_people': 0,
            'people_completed': 0,
            'max_time': -1,
            'min_time': -1,
            'avg_time': -1
        }

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).

        """
        for i in range(num_rounds):

            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Pause for 1 second
            self.visualizer.wait(1)

            self._update_wait_time()

            self.stats['num_iterations'] += 1

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        new_passenger = self.arrival_generator.generate(round_num)
        for key in new_passenger:
            self.waiting[key].extend(new_passenger[key])
            self.stats['total_people'] += len(new_passenger[key])
            self.visualizer.show_arrivals(new_passenger)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""
        for elevator in self.elevators:
            for passenger in elevator.passengers:
                if passenger.target == elevator.floor:
                    self._update_stats(passenger.wait_time)
                    elevator.passengers.remove(passenger)
                    self.visualizer.show_disembarking(passenger,
                                                      elevator)

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for key in self.waiting:
            for person in self.waiting[key]:
                for the_elevator in self.elevators:
                    if person.start == the_elevator.floor and \
                            the_elevator.fullness() != 1.0:
                        the_elevator.passengers.append(person)
                        self.waiting[key].remove(person)
                        self.visualizer.show_boarding(person, the_elevator)
                        break

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.

        direction is a list (local variable) which records the move direction of
         every elevator.
        """
        direction = self.moving_algorithm.move_elevators(self.elevators,
                                                         self.waiting,
                                                         self.num_floors)
        self.visualizer.show_elevator_moves(self.elevators, direction)

        for i in range(len(self.elevators)):
            if direction[i] == Direction.UP:
                self.elevators[i].floor += 1
            elif direction[i] == Direction.DOWN:
                self.elevators[i].floor -= 1
            else:
                self.elevators[i].floor = self.elevators[i].floor

    def _update_wait_time(self) -> None:
        """After each round, update the wait_time for persons, who is still
        waiting for a place in an elevator, and who is on the elevators.
        """
        for key in self.waiting:
            for item in self.waiting[key]:
                item.wait_time += 1

        for elevator in self.elevators:
            for passenger in elevator.passengers:
                passenger.wait_time += 1

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        return {
            'num_iterations': self.stats['num_iterations'],
            'total_people': self.stats['total_people'],
            'people_completed': self.stats['people_completed'],
            'max_time': self.stats['max_time'],
            'min_time': self.stats['min_time'],
            'avg_time': self.stats['avg_time']
        }

    def _update_stats(self, finish_time: int) -> None:
        """Update stats when a person leaves. Always update people_completed and
        avg_time when calling this function, but only update max_time and
        min_time if finish_time > max_time or finish_time < min_time, or
        people_completed is 1.
        """
        self.stats['people_completed'] += 1
        if self.stats['people_completed'] == 1:
            self.stats['max_time'] = finish_time
            self.stats['min_time'] = finish_time
        else:
            if finish_time > self.stats['max_time']:
                self.stats['max_time'] = finish_time
            elif finish_time < self.stats['min_time']:
                self.stats['min_time'] = finish_time
        self.stats['avg_time'] = (self.stats['avg_time'] *
                                  (self.stats['people_completed'] - 1) +
                                  finish_time) / self.stats['people_completed']


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 6,
        'num_elevators': 6,
        'elevator_capacity': 3,
        'num_people_per_round': 2,
        # Random arrival generator with 6 max floors and 2 arrivals per round.
        'arrival_generator': algorithms.RandomArrivals(6, 2),
        'moving_algorithm': algorithms.RandomAlgorithm(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(15)
    return stats


if __name__ == '__main__':

    print(sample_run())

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'max-nested-blocks': 4
    })
