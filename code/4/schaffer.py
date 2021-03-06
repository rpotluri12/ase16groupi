from __future__ import print_function
import argparse
import math
import random

# ---------------------------------------------------------------
# command to run: $ python schaffer.py --n 1000 --m 50 --seed 20
# n, m and seed are optional arguments
parser = argparse.ArgumentParser()
parser.add_argument("--n", help="Number of cycles. Default is 30", type=int)
parser.add_argument("--m", help="Number of trials per cycle. Default is 25", type=int)
parser.add_argument("--seed", help="A seed for random generator. Default is a random int between 1 and 100", type=int)
# ---------------------------------------------------------------


def find_max_f1_f2(x):
    return pow(x,2) + pow(x-2, 2)


def find_schaffer_max_min():
    """Calculate the maximum and minimum of (F1 + F2)
    
    A baseline study where you run the Schaffer 10000 times to find the min 
    and max values for (f1 + f2). This is needed to normalize the shaffer 
    objective function value in 0..1.
    """
    _max = -float("inf")
    _min = +float("inf")
    for i in range(10000):
        e = find_max_f1_f2(random.randint(-100000, 100000))
        _max = e if e > _max else _max
        _min = e if e < _min else _min
    return _max, _min

#print(find_schaffer_max_min())
    
SC_MAX, SC_MIN = find_schaffer_max_min()
K_MAX = 1000.0


def schaffer(x):
    "The schaffer objective function"
    return (pow(x,2) + pow((x-2), 2) - SC_MIN) / float(SC_MAX - SC_MIN)


def probability(old, new, k):
    return math.exp((old - new)/float(k))


def simulated_annealing(n, m, seed):
    """ Simulated Annealing (SA) tries to find the decision which optimizes the objectives. 
    How? 
    It Starts off at a random state and calculates the energy at that state. say this state 'sn'
    If sn is the best yet, saves this state as sb and jumps to that state. So sn becomes 's'
    If sn is not the best yet, but somewhat better than the previous state (s), jump to it.
    If sn is not even better than the previous state, then at a random probability, take it. (this step makes GA to avoid local minima/maxima)
    Repeat this a large number of times. 
    """
    # n is Number of cycles
    # m is number of trials per cycle
    
    print("\nNote: ")
    print("Each line represents a cycle of {0} trials. \nEach trial is represented by a full stop i.e. '.'".format(m))
    print("Additionally: \n'?' means we picked a state that was not as good as the present state. i.e 'A drunken decision'")
    print("'+' means we picked a state that was better than the current one.")
    print("'!' means we picked a state that is the best among the states encounterd yet.")
    print("For larger n and m, the number of ? printed should decrease.")
    
    random.seed(seed)
    s = random.randint(-100000, 100000)  # initial state, it is like the previous state.
    e = schaffer(s)  # Initial energy or the previous energy
    print("Initial State: {0}\nInitial Energy: {1} \n".format(s, e))
    sb = s  # best solution
    eb = e  # lowest energy
    k = 1
    for i in range(n):  # We could have done it in one loop itself, but breaking it into two loops helps us with output formatting.
        print()
        print(', {0}, :{1:.2f},\t'.format(m * i, e), end="")
        for j in range(m):
            sn = random.randint(-100000, 100000)
            en = schaffer(sn)
            if en < eb:  # We got the best yet
                sb, eb = sn, en
                print ("!", end="")
                
            if en < e:  # we got someone better, take it :) 
                s, e = sn, en
                print("+", end="")
            elif probability(e, en, k/K_MAX) < random.random(): # We are making a crazy decision
                s = sn
                e = en 
                print("?", end="")
            k += 1
            print(".", end="")
    return sb, eb 

    
if __name__ == "__main__":
    args = parser.parse_args()
    seed = args.seed if args.seed else random.randint(0,100)
    n = 30 if args.n is None else args.n
    m = args.m if args.m else 25

    sb, e = simulated_annealing(n, m, seed)
    print("\nseed = {0}, sb= {4}, e={1}, \nnumber of cycles = {2}, number of trials per cycle = {3}".format(seed, e, n, m, sb))
