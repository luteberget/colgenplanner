import math
import gurobipy as gp
from gurobipy import GRB

customer_angles = [
        90*quadrant+local_angle
        for quadrant in [0,1,2,3]
        for local_angle in [43, 47]]

initial_routes = [[7,0],[1,2],[3,4],[5,6]]
route_specs = [r for r in initial_routes]

def route_cost(route):
    return 2 + math.pi*( abs(customer_angles[route[0]] - customer_angles[route[1]]) / 180.0 )

for route in initial_routes:
    print(f"route {route} length {route_cost(route)}")
    print(f"  route angles {[customer_angles[r] for r in route]}")

#print(f" a better route could be ", 2 + math.pi*(abs(customer_angles[1] - customer_angles[0]))/180.0)


master = gp.Model("vrp_master")
master.setParam(GRB.Param.OutputFlag, 0)

# Add routes (and objective)
routes = [master.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1,
    obj=route_cost(route)) for route in initial_routes]

# Add constraint: we need all customers to be visited
constraints = []
for customer_idx in range(len(customer_angles)):
    routes_visiting_customer = [routes[idx] for idx,r in enumerate(initial_routes) if customer_idx in r]
    print(f"routes visiting customer {customer_idx}: {routes_visiting_customer}")
    constraints.append(master.addConstr(sum(routes_visiting_customer) >= 1))

# Column generation loop
iteration = 0
while True:
    iteration += 1
    print(f"Optimizing master LP iteration", iteration)
    master.optimize()
    print(f"Cost (of LP relaxation): {master.ObjVal}")

    shadow_price = master.getAttr(GRB.Attr.Pi)
    print(f"Shadow prices", shadow_price)

    # Try to find a new route that has negative cost under the shadow pricing of visiting the customers.
    def generate_routes():
        for c1 in range(len(customer_angles)):
            for c2 in range(len(customer_angles)):
                if c1 == c2:
                    continue

                route = [c1,c2]
                cost = route_cost(route)
                reduced_cost = cost - shadow_price[c1] - shadow_price[c2]
                yield (cost,reduced_cost,route)

    best_cost,best_reduced_cost,best_route = min(generate_routes(), key=lambda x: x[1])
    print(f"best route, cost={best_cost}, reduced_cost={best_reduced_cost}: {best_route}")

    if best_reduced_cost < 0:
        print("found improving route", best_route)
        column = gp.Column([1 if c in best_route else 0 for c in range(len(customer_angles))], constraints)
        print("adding col", column)
        new_route = master.addVar(obj=best_cost, vtype=GRB.CONTINUOUS, lb=0, column=column)
        master.update()
        print("new route constraint ", new_route)
        routes.append(new_route)
        route_specs.append(best_route)
    else:
        print("no improving routes")
        break

print("fractional (pricing) solution:")
print([r.X for r in routes])
print("price-and-branch MIP solution:")
for r in routes:
    r.setAttr(GRB.Attr.VType, GRB.INTEGER)

master.optimize()
print([r.X for r in routes])
for idx,(r,route) in enumerate(zip(routes,route_specs)):
    if r.X > 0.5:
        print(f"r{idx}: {route}")

print(f"value {master.ObjVal} cols={len(routes)} cols_added={len(routes)-len(initial_routes)}")

