from __future__ import division, print_function

import sys, os, pdb
sys.path.append(os.path.abspath('.'))
from collections import namedtuple
from matplotlib import pyplot as plt
from random import randint
import random
import tabulate
"""
This model of Next Release Problem is based on the paper
A Study of the Multi-Objective Next Release Problem by
J. J. Durillo et. al. in the
1st International Symposium on Search Based Software Engineering
"""
random.seed(1)

class Decision(object):
    def __init__(self, name, low, high, generator_fn=randint):
        assert low < high, "low > high for Decision {0}".format(name)
        self.name = name
        self.low = low
        self.high = high
        self.generator_fn = generator_fn

    def generate(self):
        return self.generator_fn(self.low, self.high)

    def __repr__(self):
        return "{0} low= {1} high= {2}".format(self.name, self.low, self.high)


def test_Decision():
    d = Decision('x', low=-1, high=0)
    for _ in range(10):
        assert d.generate() in [0,-1]


class Objective(object):
    def __init__(self, name, do_minimize=True):
        self.name = name
        self.do_minimize = do_minimize

    def __repr__(self):
        return "{0}".format(self.name)


class Requirement(object):
    cost_min = 1
    cost_max = 200

    def __init__(self, name):
        # Cost is the economical cost for satisfying a requirement
        self.name = name
        # Maximizing the negative cost
        self.cost = -1 * randint(Requirement.cost_min, Requirement.cost_max)

    def __repr__(self):
        return "{0} Cost= {1}".format(self.name,str(self.cost))


class Client(object):
    imp_min = 1
    imp_max = 10

    def __init__(self, name):
        # Each client has associated a value which reflects its degree of importance
        # as a customer for the software company
        self.name = name
        self.value = randint(Client.imp_min, Client.imp_max)

    def __repr__(self):
        return "{0} value= {1}".format(self.name, self.value)


class State(object):
    def __init__(self, decisions=None):
        self.decisions = tuple(decisions)
        self.objectives = None

    # This might be cause problems
    # Two states should be compared on based of decisions or objectives?
    def __eq__(self, other):
        return self.decisions == other.decisions

    def __hash__(self):
        return hash(self.decisions)

    def __iter__(self):
        for dec in self.decisions:
            yield dec

    def __repr__(self):
        return str(self.decisions)


def test_state():
    s = State(range(10))
    t = State(range(10))
    assert s == t
    n = State(range(1,11))
    assert s != n


class NRP(object):
    def __init__(self, n_requirements=30, n_releases=1, n_clients=20, density=0, budget=1000):

        self.n_requirements = n_requirements
        self.n_releases = n_releases
        self.n_clients = n_clients
        self.density = density  # Currently considering only independent requirements
        # Maximizing negative of cost
        self.budget = -1 * budget
        # to include a requirement or not in a release is a decision
        # If a requirement is never to be satisfied then its value will be -1
        # otherwise its value would be the release number during which it will be developed
        # For single release projects it can be either -1 (don't develop it) or 0 (ship it in current release)
        self.decisions = [Decision('d'+str(i), low=-1, high=n_releases-1) for i in range(n_requirements)]
        # Currently two objectives
        # 1) Total cost in developing the requirements
        # 2) Satisfaction of all the customers
        # Maximizing negative of cost
        self.objectives = [Objective('cost', do_minimize=False), Objective('satisfaction', do_minimize=False)]

        self.clients = None
        self.requirements = None
        self.precedence = None
        self.importance_matrix = None

        self.generate_random_data()

    def __str__(self):
        ss = "\nn_releases = {0} budget= {1}".format(self.n_releases, self.budget)
        ss += "\nRequirements : {0}\n".format(self.requirements)
        ss += "\nClients : {0}\n".format(self.clients)
        ss += "\nImportance Matrix\n"
        # for aasd in self.importance_matrix:
        #     ss += "\n" + str(aasd)
        ss += tabulate.tabulate(self.importance_matrix)
        ss += "\nDecisions: {0}\n".format(self.decisions)
        ss += "\nObjectives: {0}\n".format(self.objectives)
        return ss

    def write_to_file(self, data_file="data.txt"):
        pass

    def generate_random_data(self):
        """ Creates imaginary random clients, requirements and clients
         value for a requirement
        """
        def generate_importance():
            # TODO: Find a way to not hard-code these min and max values
            importance_min = 0
            importance_max = 100
            return [[randint(importance_min, importance_max) for _ in range(self.n_requirements)] for _ in range(self.n_clients)]

        self.clients = [Client('c' + str(i)) for i in range(self.n_clients)]
        self.requirements = [Requirement('r'+str(i)) for i in range(self.n_requirements)]
        # importance_matrix[i][j] represents the importance of requirement r_j for customer c_i
        self.importance_matrix = generate_importance()

    def calculate_cost(self, decs):
        """ Returns the cost of implementing the requirements in decs"""
        return sum([self.requirements[i].cost for i, dec in enumerate(decs) if dec != -1])

    def is_budget_ok(self, decs):
        # Checks if the requirements selected don't exceed the budget
        # TODO: For multi-release projects, this will need modification
        # Maximizing negative of cost
        return self.calculate_cost(decs) >= self.budget

    def is_dependency_ok(self, decs):
        # Checks if the dependencies among the requirements is satisfied
        # TODO: For dependent requirements, this needs to be implemented
        return True

    def any(self):
        """ Returns a State object which is a set of requirements R' """
        _n_attempts = 300
        for _ in range(_n_attempts):
            decs = [dec.generate() for dec in self.decisions]
            if self.is_budget_ok(decs) and self.is_dependency_ok(decs):
                return State(decs)
        # TODO: Decide what to do? Return None or raise an exception
        return None
        #raise Exception("Could not generate a valid decision in {0} attempts. Try again".format(_n_attempts))

    def calculate_satisfaction(self, state):
        sat_scores = 0
        for i, client in enumerate(self.clients):
             sat_scores += client.value * sum([self.importance_matrix[i][j] for j, dec in enumerate(state) if dec != -1])
        return sat_scores

    def evaluate(self, state):
        assert len(self.decisions) == len(state.decisions), "Something somewhere went terribly wrong"
        assert len(self.requirements) == len(state.decisions), "Mission Abort, report to Houston"
        if self.is_budget_ok(state) and self.is_dependency_ok(state):
            cost = self.calculate_cost(state)
            sat_score = self.calculate_satisfaction(state)
            objective = namedtuple('objectives', 'cost satisfaction')
            state.objectives = objective(cost, sat_score)
            return state.objectives
        else:
            return None


def plot_cost_and_satisfaction(objective):
    plt.title('Cost and Satisfaction graph for Next Release Problem')
    asd = (zip(*objective))

    plt.plot(asd[0], asd[1], '.')

    plt.xlabel('cost ->')
    plt.ylabel('satisfaction ->')
    plt.show()

# if __name__ == '__main__':
#     random.seed(1)
#
#     test_state()
#     test_Decision()
#
#     nrp = NRP() #n_requirements=30, budget=1000
#     print(nrp)
#     for client in nrp.clients:
#         print(client.name, end=" ")
#     print ()
#     for client in nrp.clients:
#         print(client.value, end=" ")
#     print ()
#     for req in nrp.requirements:
#         print(req.name, end=" ")
#     print ()
#     for req in nrp.requirements:
#         print(-1 * req.cost, end=" ")
#     print ()
#     pdb.set_trace()
#     dddd = []
#     for _ in range(100):
#         dddd.append(nrp.evaluate(nrp.any()))  # any might return None
#
#     for dd in sorted(dddd, key = lambda x: x[0]):
#         print dd.cost, dd.satisfaction
#     plot_cost_and_satisfaction(objective=dddd)
#
#     # two, three, four = nrp.any3()
#     # print (one, nrp.calculate_cost(one))
#     # print(two, nrp.calculate_cost(two))
#     # print(three, nrp.calculate_cost(three))
#     # print(four, nrp.calculate_cost(four))
#     # print (nrp.evaluate(one))
