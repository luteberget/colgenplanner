import math
import numbers

def dist(loc_a,loc_b):
    return math.sqrt((loc_a[0]-loc_b[0])**2 + (loc_a[1]-loc_b[1])**2)

def testdomain():
    initial = {"location": (0,0), "battery": 1.0}
    locations = [(0,0),(1,2),(-2,1)]

    def transition(state):
        if state["location"] == (0,0):
            yield (1.0, state | {"camera": True})
            yield (1.0, state | {"battery": 1.0})
        else:
            if state.get("camera", False):
                yield (1.0,state | {"pictures": state.get("pictures",set()) | set([state["location"]]) })
        for loc in locations: 
            if state["location"] != loc and (loc == (0,0) or state["battery"] >= 0.6):
                yield (dist(state["location"], loc), state | {"location": loc, "battery": state["battery"]-0.6})

    return initial,transition

def state_is_subset(small, large):
    for k,v in small.items():
        if not k in large:
            return False
        v2 = large[k]
        if isinstance(v, set):
            if not (set(v) <= set(v2)):
                return False
        if isinstance(v, numbers.Number):
            if not (v <= v2):
                return False
        else:
            if v != v2:
                return False

    return True


def plan_bfs(initial, transition, goal):
    queue = [(0.0, initial, None)]
    it = 0
    while len(queue) > 0:
        it += 1
        cost,state,parent = queue.pop(0)
        if state_is_subset(goal, state):
            print(f"Search succeeded after {it} steps.")
            return (cost, state,parent)
        else:
            for new_cost,new_state in transition(state):
                queue.append((cost+new_cost, new_state,(state,parent)))

def get_plan(state,parent):
    states = [state]
    while parent is not None:
        state,parent = parent
        states.insert(0, state)
    return states


if __name__ == "__main__":
    initial,transition = testdomain()
    cost,state,parent = plan_bfs(initial, transition, {"pictures": set([(-2,1),(1,2)]), "location": (0,0), "battery": 1.0 })
    print(initial)
    print(cost)
    print(get_plan(state,parent))

