from collections import deque
import sys
from graph import Graph, detect_file_format

def is_connected(graph: Graph):
    adj_list = graph.adjacency_list

    if not adj_list:
        return True

    all_vertices = set()
    for u in adj_list:
        all_vertices.add(u)
        for v, _ in adj_list[u]:
            all_vertices.add(v)

    if not all_vertices:
        return True

    # Запускаем BFS из первой вершины
    start = next(iter(all_vertices))
    visited = set()
    queue = deque([start])
    visited.add(start)

    while queue:
        current = queue.popleft()

        # Проверяем всех соседей
        if current in adj_list:
            for neighbor, _ in adj_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

    return len(visited) == len(all_vertices)

def path_exists(start_node, end_node, adj_list):

    if start_node not in adj_list:
        return False

    queue = deque([start_node])
    visited = {start_node}

    while queue:
        current_node = queue.popleft()
        if current_node == end_node:
            return True

        for neighbor in adj_list.get(current_node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False


def kruskal(graph: Graph):

    # Получаем и сортируем все рёбра
    edges = graph.list_of_edges()
    sorted_edges = sorted(edges, key=lambda item: item[2])

    mst_edges = []
    # Список смежности для графа, состоящего только из рёбер остова
    mst_adj_list = {}

    # Итерация по рёбрам
    for u, v, weight in sorted_edges:
        # Проверка на цикл
        if not path_exists(u, v, mst_adj_list):
            # Добавление ребра
            mst_edges.append((u, v, weight))

            # Обновляем список смежности остова
            mst_adj_list.setdefault(u, []).append(v)
            mst_adj_list.setdefault(v, []).append(u)

    return mst_edges

def main():
    file = sys.argv[1]
    g = Graph(file, detect_file_format(file))

    if not is_connected(g):
        print("Graph is not connected")
        return

    mst = kruskal(g)

    print("Minimal spanning tree:")
    for u, v, weight in sorted(mst, key=lambda item: item[2]):
        print(f"{u}-{v}: {weight}")

if __name__ == '__main__':
    main()