import csv
import math
import os.path
import sys
from os import path


class City:
    def __init__(self, cId, x, y):
        self.cId = cId
        self.x = x
        self.y = y


class Graph:
    def __init__(self, vertices):
        self.graph = None
        self.V = vertices
        self.adjList = {}

    # From and to is the index of the city
    def get_cost(self, city_a, city_b):
        return round(math.sqrt((city_b.x - city_a.x) ** 2 + (city_b.y - city_a.y) ** 2))

    def build_graph(self, data):
        for this in range(len(data)):
            for another_point in range(len(data)):
                if this != another_point:
                    if this not in self.adjList:
                        self.adjList[this] = {}

                    self.adjList[this][another_point] = self.get_cost(data[this], data[another_point])

    def get_list(self):
        return self.adjList


# Union find data structure for quick kruskal algorithm
class UnionFind:
    def __init__(self):
        self.weights = {}
        self.parents = {}

    def __getitem__(self, object):
        if object not in self.parents:
            self.parents[object] = object
            self.weights[object] = 1
            return object

        # find path of objects leading to the root
        path = [object]
        root = self.parents[object]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def __iter__(self):
        return iter(self.parents)

    def union(self, *objects):
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest


def minimum_spanning_tree(G):
    tree = []
    subtrees = UnionFind()
    graph = G.get_list()
    for W, u, v in sorted((graph[u][v], u, v) for u in graph for v in graph[u]):
        if subtrees[u] != subtrees[v]:
            tree.append((u, v, W))
            subtrees.union(u, v)

    return tree


def find_odd_vertexes(MST):
    vertexes = []
    # Create a list to hold degrees of vertecies
    arr = [0] * (
            len(MST) + 1)

    for i in range(len(MST)):
        arr[MST[i][0]] += 1
        arr[MST[i][1]] += 1

    for vertex in range(len(arr)):
        if arr[vertex] % 2 == 1:
            vertexes.append(vertex)

    return vertexes


def add_min_weight(MST, G, odd_vert):
    # Shuffle the array so we might get a better result
    import random
    random.shuffle(odd_vert)

    # find closest pair
    while odd_vert:
        v = odd_vert.pop()
        length = float("inf")
        u = 1
        closest = 0
        for u in odd_vert:
            if v != u and G.adjList[v][u] < length:
                length = G.adjList[v][u]
                closest = u

        MST.append((v, closest))
        odd_vert.remove(closest)


def find_eulerian_tour(MatchedMSTree, G):
    # find neigbours
    neighbours = {}
    for edge in MatchedMSTree:
        if edge[0] not in neighbours:
            neighbours[edge[0]] = []

        if edge[1] not in neighbours:
            neighbours[edge[1]] = []

        neighbours[edge[0]].append(edge[1])
        neighbours[edge[1]].append(edge[0])

    # print("Neighbours: ", neighbours)

    # finds the hamiltonian circuit
    start_vertex = MatchedMSTree[0][0]
    EP = [neighbours[start_vertex][0]]

    while len(MatchedMSTree) > 0:
        for i, v in enumerate(EP):
            if len(neighbours[v]) > 0:
                break

        while len(neighbours[v]) > 0:
            w = neighbours[v][0]

            remove_edge_from_matchedMST(MatchedMSTree, v, w)

            del neighbours[v][(neighbours[v].index(w))]
            del neighbours[w][(neighbours[w].index(v))]

            i += 1
            EP.insert(i, w)

            v = w

    return EP


def remove_edge_from_matchedMST(MatchedMST, v1, v2):
    for i, item in enumerate(MatchedMST):
        if (item[0] == v2 and item[1] == v1) or (item[0] == v1 and item[1] == v2):
            del MatchedMST[i]

    return MatchedMST


def main():
    # Usage: write input and output files names in open function and path.exists function
    if not path.exists("test-input-1.txt"):
        print("File doesn't exist.")
        return
    # Open the file read the lines and create graph of cities
    input_file = open("test-input-1.txt", "r")
    output_file = open("test-output-1.txt", "w")
    lines = input_file.readlines()
    data = []

    for line in lines:
        x = line.split()
        data.append(City(int(x[0]), int(x[1]), int(x[2])))

    length = len(data)
    g = Graph(length)
    g.build_graph(data)
    graph_repr = g.get_list()
    # for j in range(length):
        # print(graph_repr[j])

    # Create MST with kruskal's algorithm
    MST = minimum_spanning_tree(g)
    # for p in range(len(MST)):
        # print("Kruskal MST: ", MST[p], graph_repr[MST[p][0]][MST[p][1]])

    # Find odd vertexes
    odd_vertexes = find_odd_vertexes(MST)
    print("Odd vertexes: ", odd_vertexes)   

    # Find minimum edges and add it to MST
    add_min_weight(MST, g, odd_vertexes)
    print("Minimum weight matching: ", MST)

    # Find eulerian tour
    eulerian_tour = find_eulerian_tour(MST, g)
    print("Eulerian tour: ", eulerian_tour)

    # Delete duplicates from eulerian tour
    total_weight = 0
    current = eulerian_tour[0]
    res = []
    added = [False for i in range(len(eulerian_tour))]
    for e in eulerian_tour[1:]:
        if not added[e]:
            res.append(e)
            added[e] = True

            total_weight += graph_repr[current][e]
            current = e

    res.append(res[0])
    #res_len = len(res)
    # total_weight += graph_repr[res_len-2][res[0]]

    print("Result path: ", res)
    print("Result length of the path: ", total_weight)

    print(total_weight, file=output_file)
    for s in range(len(res)):
        print(res[s], file=output_file)

    input_file.close()
    output_file.close()


if __name__ == "__main__":
    main()
