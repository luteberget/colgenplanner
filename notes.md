# Classical planning using Dantzig-Wolfe goal decomposition

## Literature

 * Partial path column generation for VRP (Bjørn P
  https://backend.orbit.dtu.dk/ws/portalfiles/portal/4197236/partialpathvrptw.pdf
  https://core.ac.uk/download/pdf/13757348.pdf

 * Fragment-based planning using column generation
    https://www.aaai.org/ocs/index.php/ICAPS/ICAPS14/paper/download/7907/8015

 * A primer in column generation
  https://or.rwth-aachen.de/files/research/publications/primer.pdf


 * Planning for Mining Operations with Time and Resource Constraints: file:///home/bjornarl/Downloads/13666-Article%20Text-17184-1-2-20201228.pdf

 * Width and serialization of classical planning problem s(Lipvetzky) https://www.dtic.upf.edu/~hgeffner/width-ecai-2012.pdf

 * Other LP planning approaches
   * Linear and Integer Programming-Based Heuristics for Cost-Optimal Numeric Planning
   * Planning with Linear Continuous Numeric Change https://nms.kcl.ac.uk/andrew.coles/publications/publication2322.pdf


## Introduction


Some classical planning problems are easy -- these can often be solved by
bounded-width methods (see Lipovetzky).

Many planning problems consists of going multiple places and doing things
there. Typically, there is one or more goals per location, and the ordering of
the locations may be important, or not, depending on the specific planning
problem. In the cases where the ordering is not important, optimizing a cost
metric may be important instead. General-purpose planning systems do not
currently do a very good job optimizing in such cases. For example, planning
problems that (implicitly) have a strong resemblence to the traveling salesman
problem or the vehicle routing problem, are typically not solved well by
general-purpose planning systems.

The key to good performance on TSP- or VRP-like problems is typically either
(1) local search methods or (2) linear programming-based relaxations.  In this
note, we take a look at a linear programming methodology for vehicle routing
problems, and combine it with general-purpose a heuristic search planning
algorithm to attempt to provide both quick and high-quality solutions for
planning problems where finding a feasible plan can be done relatively easy
(such as Vehicle Routing-like domains) by serializing the goals.  When the
goals have been serialized, we produce an LP formulation of combining the
partial plans for achieving each goal (or sequence of goals), and use column
generation to search for new partial plans that may reduce the total metric
cost.

## Landmark sequencing

We want to split a plan into parts, then 


## Model

The metric SAS+ planning problem could be described as a MIP, but we will not
do so here.  Even so, we define a Dantzig-Wolfe decomposition of the full
metric SAS+ problem. 

Let `\lambda_p` be a binary variable indicating whether partial plan `p` is
used. We define the Master Problem:

```
(1)  min    \sum_{p \in P} c_p \lambda_p
(2)  s.t.   \sum_{p \in P} \alpha_g^p \lambda_p \geq 1  \forall g \in G
(3)         goal sequence continuity
(4)         resource constraints?
```


## Algorithm

 * Given a SAS+ planning problem. 
 * Solve it using Serialized Iterated Width, SIW(k), producing a concatenated
   plan `P_0 = <p_0,...,p_i>`.
 * Use the initial plan `P_0` to construct the Restricted Master Problem.
 * For each partial plan in the restricted master problem, solve the
   Cost-Modified Iterated Width problem (with the `k` value from the initial
   solve?) and add new partial plans to the Restricted Master Problem (column
   generation).
 * When no new partial plans can be added, solve the current Master Problem as
   a MIP. (This may also be done under-way, if column generation takes a lot of
   time, to get an "any-time" algorithm).

## Example

See example1.py





