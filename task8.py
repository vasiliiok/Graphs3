import sys
from graph import Graph, detect_file_format

def find_bridges_and_cut_vertices(graph: Graph):
    """
    Находит мосты и шарниры в графе за O(V+E).
    :param graph: Объект класса Graph. Граф должен быть неорнитированным.
    :return: Кортеж (список мостов, список шарниров).
    """
    num_vertices = graph.size()
    # Нумерация с 1, поэтому используем массивы размером N+1
    visited = [False] * (num_vertices + 1)
    discovery_time = [-1] * (num_vertices + 1)
    low_link = [-1] * (num_vertices + 1)
    parent = [-1] * (num_vertices + 1)

    bridges = []
    cut_vertices = set()  # Используем set для автоматического удаления дубликатов

    time = 0

    def dfs(u):
        nonlocal time

        visited[u] = True
        discovery_time[u] = low_link[u] = time
        time += 1

        children_count = 0  # Счётчик детей в DFS-дереве для корневой вершины

        for v in graph.adjacency_list(u):
            if v == parent[u]:
                continue  # Игнорируем ребро к родителю

            if visited[v]:
                # Это обратное ребро (back edge)
                low_link[u] = min(low_link[u], discovery_time[v])
            else:
                # Это прямое ребро (tree edge)
                children_count += 1
                parent[v] = u
                dfs(v)

                # После рекурсии обновляем low_link для u
                low_link[u] = min(low_link[u], low_link[v])

                # --- Проверка на мост ---
                if low_link[v] > discovery_time[u]:
                    # Сортируем для канонического вида
                    bridges.append(tuple(sorted((u, v))))

                # --- Проверка на шарнир ---
                # Случай 1: u - не корень DFS-дерева и low_link потомка >= времени входа u
                if parent[u] != -1 and low_link[v] >= discovery_time[u]:
                    cut_vertices.add(u)

        # Случай 2: u - корень DFS-дерева и у него больше одного ребенка
        if parent[u] == -1 and children_count > 1:
            cut_vertices.add(u)

    # Запускаем DFS для всех компонент связности (если их несколько)
    for i in range(1, num_vertices + 1):
        if not visited[i]:
            dfs(i)

    return sorted(list(bridges)), sorted(list(cut_vertices))


# --- Пример Запуска ---

file = sys.argv[1]
g = Graph(file, detect_file_format(file))

if g.is_directed():
    print("Внимание: Алгоритм предназначен для неориентированных графов.")

found_bridges, found_cuts = find_bridges_and_cut_vertices(g)

print("Bridges:")
print(found_bridges)
print("Cut vertices:")
print(found_cuts)