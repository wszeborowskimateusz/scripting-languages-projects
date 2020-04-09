from simple_graphs import *
from graphs import Graph

x = AdjacencyList(text="@")
x.addVertex()
x.addEdge(0, 1)
print(x.order())
x.deleteEdge(0, 1)
print(x.order())