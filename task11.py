from graph import Graph, detect_file_format
import sys

def bellman_ford(graph: Graph, source_node: int):
    num_vertices = graph.size()

    # Инициализация
    distances = {i: float('inf') for i in range(1, num_vertices + 1)}
    predecessors = {i: None for i in range(1, num_vertices + 1)}
    distances[source_node] = 0

    # Получаем список всех рёбер
    edges = []
    for u in range(1, num_vertices + 1):
        for v in graph.adjacency_list(u):
            weight = graph.weight(u, v)
            edges.append((u, v, weight))

    # Релаксация рёбер V-1 раз
    for _ in range(num_vertices - 1):
        for u, v, weight in edges:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                predecessors[v] = u

    return distances, predecessors


def reconstruct_path(predecessors, start_node, end_node):
    path = []
    current = end_node
    while current is not None:
        path.insert(0, current)
        if current == start_node:
            return path
        current = predecessors.get(current)
    return "Путь не найден"


file = sys.argv[1]
start = int(sys.argv[2])
g = Graph(file, detect_file_format(file))

dist, pred = bellman_ford(g, start)

print(f"Кратчайшие расстояния от вершины {start}:")
print(dist)

