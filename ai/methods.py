# coding=utf-8
from utils import FifoList, BoundedPriorityQueue, get_max_random_tie
from models import (SearchNode, SearchNodeHeuristicOrdered,
                    SearchNodeStarOrdered, SearchNodeCostOrdered,
                    SearchNodeValueOrdered)
import copy
import math
import random
from itertools import count


def breadth_first_search(problem, graph_search=False):
    return _search(problem,
                   FifoList(),
                   graph_search=graph_search)


def depth_first_search(problem, graph_search=False):
    return _search(problem,
                   [],
                   graph_search=graph_search)


def limited_depth_first_search(problem, depth_limit, graph_search=False):
    return _search(problem,
                   [],
                   graph_search=graph_search,
                   depth_limit=depth_limit)


def iterative_limited_depth_first_search(problem, graph_search=False):
    return _iterative_limited_search(problem,
                                     limited_depth_first_search,
                                     graph_search=graph_search)


def uniform_cost_search(problem, graph_search=False):
    return _search(problem,
                   BoundedPriorityQueue(),
                   graph_search=graph_search,
                   node_factory=SearchNodeCostOrdered)


def greedy_search(problem, graph_search=False):
    return _search(problem,
                   BoundedPriorityQueue(),
                   graph_search=graph_search,
                   node_factory=SearchNodeHeuristicOrdered)


def astar_search(problem, graph_search=False):
    return _search(problem,
                   BoundedPriorityQueue(),
                   graph_search=graph_search,
                   node_factory=SearchNodeStarOrdered)


def beam_search(problem, beamsize=100, graph_search=False):
    return _search(problem,
                   BoundedPriorityQueue(beamsize),
                   node_factory=SearchNodeValueOrdered,
                   local_search=True)


# Quite literally copied from aima
def simulated_annealing(problem, schedule=None):
    if not schedule:
        schedule = _exp_schedule()
    current = SearchNode(problem.initial_state,
                         problem=problem)
    for t in count():
        T = schedule(t)
        if T == 0:
            return current
        neighbors = current.expand()
        if not neighbors:
            return current
        succ = random.choice(neighbors)
        delta_e = problem.value(succ.state) - problem.value(current.state)
        if delta_e > 0 or random.random() < math.exp(delta_e / T):
            current = succ


def _iterative_limited_search(problem, search_method, graph_search=False):
    solution = None
    limit = 0

    while not solution:
        solution = search_method(problem, limit, graph_search)
        limit += 1

    return solution


def _search(problem, fringe, graph_search=False, depth_limit=None,
            node_factory=SearchNode, local_search=False):
    memory = set()
    fringe.append(node_factory(state=problem.initial_state,
                               problem=problem))

    while fringe:
        node = fringe.pop()
        if problem.is_goal(node.state):
            return node
        if depth_limit is None or node.depth < depth_limit:
            for n in node.expand():
                if graph_search:
                    if n.state not in memory:
                        memory.add(n.state)
                        fringe.append(n)
                else:
                    fringe.append(n)


# Math literally copied from aima-python
def _exp_schedule(k=20, lam=0.005, limit=100):
    "One possible schedule function for simulated annealing"
    def f(t):
        if t < limit:
            return k * math.exp(-lam * t)
        return 0
    return f


def _get_best_neighbor(problem, neighbors, current):
    neighbor = None
    candidate = get_max_random_tie(neighbors, lambda x: problem.value(x.state))
    if problem.value(candidate.state) <= problem.value(current.state):
        neighbor = candidate
    return neighbor


def hill_climbing_basic(problem):
    '''Basic hill climbing, where the best neighbor is chosen.'''
    return _hill_climbing(problem, _get_best_uphill_neighbor)


def _get_random_uphill_neighbor(problem, neighbors, current):
    neighbor = None
    is_uphill = lambda x: problem.value(x.state) > problem.value(current.state)
    uphill = filter(is_uphill, neighbors)
    if uphill:
        random.shuffle(uphill)
        neighbor = uphill[0]
    return neighbor


def hill_climbing_stochastic(problem):
    '''Stochastic hill climbing, where a random neighbor is chosen among
       those that have a better value'''
    return _hill_climbing(problem, _get_random_uphill_neighbor)


def _get_first_choice_random(problem, neighbors, current):
    neighbor = None
    eligible = copy.copy(neighbors)
    current_value = problem.value(current.state)
    while eligible:
        candidate = eligible.pop()
        if problem.value(candidate.state) > current_value:
            neighbor = candidate
            break
    return neighbor


def hill_climbing_first_choice(problem):
    '''First-choice hill climbing, where neighbors are randomly taken and the
       first with a better value is chosen'''
    return _hill_climbing(problem, _get_first_choice_random)


def _hill_climbing(problem, select_function):
    '''Generic hill climbing search, takes a ``select_function`` that returns
       the chosen neighbor, or None is there is not neighbor that meets the
       requirements.'''
    current = SearchNode(state=problem.initial_state, problem=problem)
    while True:
        neighbors = current.expand()
        if not neighbors:
            break
        neighbor = select_function(problem, neighbors, current)
        if neighbor is None:
            break
        current = neighbor
    return current
