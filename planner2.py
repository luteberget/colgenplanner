from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
import math


def dist(loc_a,loc_b):
    return math.sqrt((loc_a[0]-loc_b[0])**2 + (loc_a[1]-loc_b[1])**2)



State = Dict[str, float]

@dataclass
class Action:
    name :str
    preconditions :State
    effect_abs :State
    effect_rel :State
    cost :float = 0.0


def domain1() -> Tuple[State, List[Action], List[State]]:
    locations = [(0,0),(1,2),(-2,1),(-3,1),(-4,-2)]
    initial :State = {"loc0":1, "battery":1.0}
    actions :List[Action]= [
        Action("get_camera", {"loc0":1}, {"camera":1}, {}, 0.0),
        Action("charge", {"loc0":1}, {"battery":1.0}, {}, 0.0),
    ]

    # travel actions
    for i in range(len(locations)):
        for j in range(len(locations)):
            if i != j:
                actions.append(Action(
                    name=f"go_{i}_{j}", 
                    preconditions= {f"loc{i}":1, "battery": 0.6 if j > 0 else 0.3,}, 
                    effect_abs= {f"loc{i}":0, f"loc{j}":1}, 
                    effect_rel={"battery": -0.3}, 
                    cost=dist(locations[i], locations[j])))
    
    # inspect actions
    for i in range(1, len(locations)):
        actions.append(Action(f"inspect{i}", {f"loc{i}":1, "camera":1}, {f"inspected{i}":1}, {}, 0.0))

    goals = [{f"inspected{i}":1} for i in range(1,len(locations))]

    return initial, actions, goals

substate = lambda a,b: all( b.get(k,0.0) >= v for k,v in a.items())

def apply(state :State, action :Action) -> State:
    new_state :State= {**state}
    for k,v in action.effect_abs.items():
        new_state[k] = v
    for k,v in action.effect_rel.items():
        new_state[k] = new_state.get(k,0.0) + v
    return new_state

def plan_w2(state, actions, goal):
    visited :Dict[Tuple[str,str], Set[float,float]]= defaultdict(set)
    queue = [(state, None, None)]
    it = 0
    while len(queue) > 0:
        it += 1
        parent = queue.pop(0)
        state = parent[0]
        #print(f"state {state}")
        for action in (a for a in actions if substate(a.preconditions,state)):
            succ = apply(state, action)
            if substate(goal, succ):
                print(f"Found after {it} states")
                return succ,action,parent
            #print(f"  succ {succ}")
            keys = list(succ.keys())
            append = False
            for k1,k2 in ((keys[i], keys[j]) for i in range(len(keys)) for j in range(i+1, len(keys))):
                if succ[k1] <= 0.0 or succ[k2] <= 0.0:
                    continue
                if not any( v1 >= succ[k1] and v2 >= succ[k2] for v1,v2 in visited[(k1,k2)] ):
                    #print(f"    new state because of {k1,k2}")
                    visited[(k1,k2)].add((succ[k1],succ[k2]))
                    append = True

            if append:
                queue.append((succ,action,parent))
            #else:
                #print("    pruned")
    # print(f"it  {it}")
    return None

def plan_actions(_,action,parent):
    actions = []
    while action is not None:
        actions.insert(0, action)
        _, action, parent = parent
    return actions

def combined_action(name :str, actions :List[Action]) -> Action:
    internal_state = {}
    external_state = {}
    effects_abs = {}
    effects_rel = {}
    cost =0.0
    for action in actions:
        for k,v in action.preconditions.items():
            if internal_state.get(k, 0.0) < v:
                external_state[k] = external_state.get(k, 0.0) + (v - internal_state.get(k, 0.0))
                internal_state[k] = v
        internal_state = apply(internal_state, action)
        cost += action.cost
        for k,v in action.effect_abs.items():
            effects_abs[k] = v
        for k,v in action.effect_rel.items():
            if k in effects_abs:
                effects_rel.pop(k,None)
                effects_abs[k] += v
            else:
                effects_rel[k] = effects_rel.get(k,0.0) + v

    return Action(
        name=name,
        preconditions=external_state,
        effect_abs= effects_abs,
        effect_rel= effects_rel,
        cost=cost
    )

def landmarks(state :State, actions :List[Action], goals :List[State]):
    action_labels = {a.name :set() for a in actions}
    state_labels = { k : [(v, set([(k,v)]))]  for k,v in state.items() }
    while True:
        print("lm it")
        changed = False
        for action in actions:
            for pre_k, pre_v in action.preconditions.items():
                ls = next(( ls for v,ls in state_labels.get(pre_k, []) if v >= pre_v ), [])
                for (k,v) in ls:
                    if not (k,pre_v) in action_labels[action.name]:
                        changed = True
                        action_labels[action.name].add(label)

        for k in state_labels.keys():
            for v,ls in state_labels[k]:
                pass


        if not changed:
            break

    for a,ls in action_labels.items():
        print(f"A {a} -- {ls}")

    for k,ls in state_labels.items():
        for v,ls in ls:
            print(f"V {k}:{v} -- {ls}")





if __name__ == "__main__":
    initial,actions,goals = domain1()

    print("LANDMARKS")
    landmarks(initial, actions, goals)

    state = initial
    for goal in goals:
        x = plan_w2(state, actions, goal)
        state, action, parent = x
        combined = combined_action(f"g{next(iter(goal.keys()))}", plan_actions(*x))
        print(combined)
        print(state,action,parent)
                
