# Examples of metric-cost

## Plain TSP robot

```
table cost_matrix(a,b)
fluent robot_location = { home, a, b, c, d } := home
fluent visited_a, visited_b, visited_c, visited_d = { true, false } := false
goal visited_a, visited_b, visited_c, visited_d
action go(a,b):
  pre: robot_location=a
  post: robot_location=b
  cost: cost_matrix(a,b)

action: visit_a:
  pre: robot_location=a
  post: visited_a=true
action: visit_b:
  pre: robot_location=b
  post: visited_b=true
action: visit_c:
  pre: robot_location=c
  post: visited_c=true
action: visit_c:
  pre: robot_location=c
  post: visited_c=true
```


## Robot with equipment

## Robot with battery constraint

## Two-phase TSP (need to close all emergencies before doing normal jobs)



