from collections import deque
import sys
from graph import Graph, detect_file_format

def path_exists(start_node, end_node, adj_list):
    """
    Проверяет наличие пути между start_node и end_node с помощью BFS.
    :param adj_list: Список смежности графа, по которому ищем путь.
    """
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
    """
    Находит MST с помощью алгоритма Краскала.
    Проверка на циклы выполняется через BFS вместо DSU.
    """

    # Получаем и сортируем все рёбра
    edges = graph.list_of_edges()
    sorted_edges = sorted(edges, key=lambda item: item[2])

    # Инициализация
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


file = sys.argv[1]
g = Graph(file, detect_file_format(file))

mst = kruskal(g)

print("Minimal spanning tree:")
# Сортируем
for u, v, weight in sorted(mst, key=lambda item: item[2]):
    print(f"{u}-{v}: {weight}")