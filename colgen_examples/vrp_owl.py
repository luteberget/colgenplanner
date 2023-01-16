from math import sqrt
from networkx import DiGraph
from vrpy import VehicleRoutingProblem


def dist(a, b):
    return sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


def solve(depot, goods, k, capacity):
    G = DiGraph()

    # Add edge from start location to all others
    for good_i in range(len(goods)):
        name, loc, amount = goods[good_i]

        for a in range(amount):
            G.add_edge("Source", name + str(a), cost=dist(depot, loc))
            G.add_edge(name + str(a), "Sink", cost=dist(depot, loc))
            G.nodes[name+str(a)]["demand"] = 1

        for a in range(amount):
            for b in range(1, amount):
                G.add_edge(name + str(a), name + str(b), cost=0)
                G.add_edge(name + str(b), name + str(a), cost=0)

        for good_j in range(good_i + 1, len(goods)):
            other_name, other_loc, other_amount = goods[good_j]
            cost = dist(loc, other_loc)

            for a in range(amount):
                for b in range(other_amount):
                    G.add_edge(name + str(a), other_name + str(b), cost=cost)
                    G.add_edge(other_name + str(b), name + str(a), cost=cost)

    prob = VehicleRoutingProblem(
        G,
        num_vehicles=k,
        use_all_vehicles=False,
        load_capacity=capacity,
    )

    prob.solve(time_limit=120)
    print(prob.best_routes)
    return prob.best_routes


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import random

    depot = (0.0, 0.0)
    goods = [
        ("bananas", (1.0, 1.0), 2),
        ("beer", (1.0, -1.0), 4),
    ]

    routes = solve(depot, goods, 3, 3)
    print(routes)

    plt.plot(*depot, 'o', color="red")
    plt.annotate("packing location", depot)
    nodes = {"Source": depot, "Sink": depot}
    for good_idx,(name,loc,amount) in enumerate(goods):
        for i in range(amount):
            l = (loc[0] + 0.1*i, loc[1] + 0.1*i)
            n = name + str(i)
            nodes[n] = l
            plt.plot(*l, 'o', color=f"C{good_idx}")
            plt.annotate(n,l)

    for route_id,route in routes.items():
        for i,(a,b) in enumerate(zip(route,route[1:])):
            print(a,b)
            plt.plot((nodes[a][0], nodes[b][0]), (nodes[a][1], nodes[b][1]), '-', color=f"C{route_id}")
            if i == 0:
                plt.annotate(f"split {route_id}", ( 0.5*(nodes[a][0] + nodes[b][0]), 0.5*(nodes[a][1] + nodes[b][1])))
        

    print(nodes)

    plt.savefig("x.png")




