from graph import Graph, detect_file_format
import sys
sys.setrecursionlimit(2000)

def find_scc(graph: Graph):
    """
    Находит компоненты сильной связности в орграфе с помощью алгоритма Косарайю.
    :param graph: Объект класса Graph, который должен быть ориентированным.
    :return: Список списков, где каждый внутренний список - это компонента сильной связности.
    """

    # --- Шаг 1: Первый DFS для получения порядка выхода ---

    visited = set()
    order = []  # Используем как стек

    def dfs1(u):
        visited.add(u)
        for v in graph.adjacency_list(u):
            if v not in visited:
                dfs1(v)
        order.append(u)

    for i in range(1, graph.size() + 1):
        if i not in visited:
            dfs1(i)

    # --- Шаг 2: Транспонирование графа ---

    adj_list_T = {i: [] for i in range(1, graph.size() + 1)}
    for u, v, w in graph.list_of_edges():
        adj_list_T[v].append(u)

    # --- Шаг 3: Второй DFS на транспонированном графе ---

    visited.clear()
    components = []

    def dfs2(u):
        visited.add(u)
        current_component.append(u)
        for v in adj_list_T[u]:
            if v not in visited:
                dfs2(v)

    while order:
        u = order.pop()  # Берем вершины в порядке убывания времени выхода
        if u not in visited:
            current_component = []
            dfs2(u)
            components.append(sorted(current_component))

    # Проверяем, связный ли граф
    is_strongly_connected = len(components) == 1 and len(components[0]) == graph.size()

    return is_strongly_connected, components

#-----------------------------
file = sys.argv[1]
g = Graph(file, detect_file_format(file))

# Находим компоненты
is_connected, scc = find_scc(g)

# Выводим результат в формате, как в примере
if is_connected:
    print("Digraph is strongly connected")
else:
    print("Digraph is not strongly connected")

print("\nStrongly connected components:")
for component in scc:
    print(component)