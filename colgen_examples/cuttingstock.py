import gurobipy as gp
from gurobipy import GRB

item_sizes = [20, 45, 50, 55, 75]
item_demands = [48, 35, 24, 10, 8]
roll_width = 110

# Enumerate all possible (maximal) cuts.

def all_cuts():
    cuts = set()
    stack = [[]]
    while len(stack) > 0:
        cut = stack.pop()
        current_sum = sum(item_sizes[idx] for idx in cut)

        is_leaf = True
        for idx,size in enumerate(item_sizes):
            if current_sum + size <= roll_width:
                stack.append(cut + [idx])
                is_leaf = False

        if is_leaf:
            cuts.add("".join(map(str,sorted(cut))))
    return [ list(map(int, (x for x in cut))) for cut in cuts]


print("All possible cuts")
cuts = all_cuts()
print(cuts)

def solve_cuttingstock(cuts):
    m = gp.Model("cuttingstock")
    m.setParam(GRB.Param.OutputFlag, 0)
    # make integers for selecting 
    z = [m.addVar(vtype=GRB.CONTINUOUS, name=f"z{i}") for i in range(len(cuts))]
    m.update()

    # Set objective
    m.setObjective(sum(z))

    # Constraint: achieve the demands
    # One constraint per demand
    lhss = [ 0.0 for _ in item_demands ]
    for var,cut in zip(z, cuts):
        for item in cut:
            lhss[item] += var
    for demand,lhs in zip(item_demands, lhss):
        print(lhs >= demand)
        m.addConstr(lhs >= demand)

    # Solve
    m.optimize()
    for idx,v in enumerate(z):
        print(f"{idx} {int(round(v.X))} pcs of {cuts[idx]} ")

solve_cuttingstock(cuts)

def solve_cuttingstock_colgen():

    master = gp.Model("cuttingstock")
    master.setParam(GRB.Param.OutputFlag, 0)
    #master.setParam(GRB.Param.Presolve,0)

    # make integers for selecting the one-cut stocks
    zs = [master.addVar(obj=1.0, vtype=GRB.CONTINUOUS, lb=0, name=f"z{i}") for
            i in range(len(item_sizes))]

    # Achieve the demands
    constraints = []
    for var,demand in zip(zs, item_demands):
        c = master.addConstr(var >= demand)
        constraints.append(c)

    iteration = 0
    while True:
        iteration += 1
        print(f"Optimizing iteration {iteration}")
        master.optimize()
        #for idx,v in enumerate(zs):
        #    print(f"{idx} {v.X} pcs of cut{idx} ")

        # Detect missing columns
        shadow_price = master.getAttr(GRB.Attr.Pi)
        #print(shadow_price)
        assert(len(shadow_price) == len(item_sizes))
        #for idx,(price,size,demand,c) in enumerate(zip(shadow_price,item_sizes,item_demands,constraints)):
        #    print(f"idx {idx} item size {size} demand {demand} price {price} {c.Pi}")

        # with these shadow prices, can we find a new cutting?
        pricing = gp.Model("pricing")
        pricing.setParam(GRB.Param.OutputFlag, 0)

        # variables: the variables are how many pieces
        pieces = [pricing.addVar(vtype=GRB.INTEGER, name=f"size{size}") for
                size in item_sizes]

        # objective: want to maximise the shadow prices
        pricing.setObjective(1 - sum( price*piece for price,piece in zip(shadow_price, pieces)))

        # constraints: pieces need to fit in stock
        pricing.addConstr(sum(size*piece for size,piece in zip(item_sizes, pieces)) <= roll_width)

        pricing.optimize()

        if pricing.ObjVal < 0:
            print("Found an improving column")

            idx = len(zs)
            column = gp.Column([p.X for p in pieces], constraints)
            print("adding col", column)
            zs.append(master.addVar(obj=1.0, vtype=GRB.CONTINUOUS, lb=0,
                column=column))
        else:
            print("No improving columns. Finsihed.")
            break

    print("fractional (pricing) solution:")
    print([z.X for z in zs])
    print("price-and-branch MIP solution:")
    for z in zs:
        z.setAttr(GRB.Attr.VType, GRB.INTEGER)

    master.optimize()
    print([z.X for z in zs])
    #for idx,v in enumerate(zs):
    #    print(f"{idx} {v.X} pcs of cut{idx} ")

    print(f"value {master.ObjVal} cols={len(zs)} cols_added={len(zs)-len(item_sizes)}")

solve_cuttingstock_colgen()
