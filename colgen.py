import gurobipy as gp
from gurobipy import GRB
import planner2

initial,actions,goals = planner2.domain1()

# Master problem
master = gp.Model()
master.setParam(GRB.Param.OutputFlag, 0)

bigM = 1000

drop_visit_vars = [master.addVar(obj=bigM, vtype=GRB.CONTINUOUS, lb=0) for _ in enumerate(goals)]

# goals must be fulfilled
goal_constraints = [master.addConstr(v >= 1, name=f"goal{idx}") for idx,v in enumerate(drop_visit_vars)]

# flow conservation between goals-as-nodes
flow_constraints = [master.addConstr(gp.LinExpr(0) >= gp.LinExpr(0), name=f"node_g{idx}") for idx,v in enumerate(drop_visit_vars)]

# flow conservation at initial node
initial_node_flow = master.addConstr(gp.LinExpr(0) >= gp.LinExpr(-1), name=f"node_i")


while True:
    master.optimize()
    print(f"Cost (of LP relaxation): {master.ObjVal}")

    goal_price = [c.getAttr(GRB.Attr.Pi) for c in goal_constraints]
    flow_price = [c.getAttr(GRB.Attr.Pi) for c in flow_constraints] + [initial_node_flow.getAttr(GRB.Attr.Pi)]
    print(f"Goal prices: ", goal_price)
    print(f"Flow prices: ", flow_price)

    for goal,price,goal_constr in zip(goals, goal_price, goal_constraints):
        if price > 0.:
            # Try to achieve this goal from each of the nodes
            pass

    break



