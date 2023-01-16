import math
import gurobipy as gp
from gurobipy import GRB

# Order splitting as VRP with split deliveries
#
# We want to fetch the following quantity (in kg) of goods from the warehouse:
order = [ ("banana", 66), ("beer", 51) ]
#
# ... and these are located at the following places in the warehouse:
locations = { "depot": (0,0), "banana": (1,1), "beer": (1,-1) }
#
# ... and the trolleys fetching the order has a maximum capacity (in kg):
capacity = 50

# Set up a master LP for selecting routes:
master = gp.Model("vrp_master")
master.setParam(GRB.Param.OutputFlag, 0)

# Add high-cost dummy route
dummy_route = master.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1, obj=10000.0)
route_vars = [dummy_route]
route_specs = ["dummy"]

# Add constraint: we need all goods to be collected, with the specified quantities
# The dummy variable will fulfull this (at a high cost).
constraints = [ master.addConstr( qty*dummy_route >= qty ) for good,qty in order ]

# Column generation loop
colgen_iteration = 0
while True:
    colgen_iteration += 1
    print(f"Optimizing master LP iteration", colgen_iteration)
    master.optimize()
    print(f"Cost (of LP relaxation): {master.ObjVal}")

    # Calculate the prices of goods.
    shadow_price = master.getAttr(GRB.Attr.Pi)
    # We should have one price per good.
    assert(len(shadow_price) == len(order))
    print(f"Shadow prices", shadow_price)


    # Try to find a new route that has negative cost under the shadow pricing of visiting the customers.
    def generate_routes():
        stack = [[]]
        while len(stack) > 0:
            # if not full, go to next good



        for _ in range(0):
            yield ()

    best_cost,best_reduced_cost,best_route = min(generate_routes(), key=lambda x: x[1], default = (float("inf"),float("inf"),None))
    print(f"best route, cost={best_cost}, reduced_cost={best_reduced_cost}: {best_route}")

    if best_reduced_cost < 0:
        print("found improving route", best_route)
        column = gp.Column([1 if c in best_route else 0 for c in range(len(customer_angles))], constraints)
        print("adding col", column)
        new_route = master.addVar(obj=best_cost, vtype=GRB.CONTINUOUS, lb=0, column=column)
        master.update()
        print("new route constraint ", new_route)
        route_vars.append(new_route)
        route_specs.append(best_route)
    else:
        print("no improving routes")
        break

print("fractional (pricing) solution:")
print([r.X for r in route_vars])
print("price-and-branch MIP solution:")
for r in route_vars:
    r.setAttr(GRB.Attr.VType, GRB.INTEGER)

master.optimize()
print([r.X for r in route_vars])
for idx,(r,route) in enumerate(zip(route_vars,route_specs)):
    if r.X > 0.5:
        print(f"r{idx}: {route}")

print(f"value {master.ObjVal} cols={len(route_vars)}")

