from collections import deque
import sys
from graph import Graph, detect_file_format


def find_connected_components(graph: Graph):
    """Находит все компоненты связности в графе с помощью BFS."""
    num_vertices = graph.size()
    visited = set()
    components = []
    for i in range(1, num_vertices + 1):
        if i not in visited:
            component = []
            q = deque([i])
            visited.add(i)
            while q:
                u = q.popleft()
                component.append(u)
                for v in graph.adjacency_list(u):
                    if v not in visited:
                        visited.add(v)
                        q.append(v)
            components.append(component)
    return components


def floyd_warshall_for_component(graph: Graph, component_nodes: list):
    v_comp = len(component_nodes)
    inf = float('inf')

    # Создаем отображение номера вершины в индекс матрицы (0..v_comp-1)
    node_to_idx = {node: i for i, node in enumerate(component_nodes)}

    dist = [[inf] * v_comp for _ in range(v_comp)]
    next_v = [[None] * v_comp for _ in range(v_comp)]

    for i in range(v_comp):
        dist[i][i] = 0

    for u_node in component_nodes:
        u_idx = node_to_idx[u_node]
        for start_node, v_node, weight in graph.list_of_edges(u_node):
            if v_node in node_to_idx:
                v_idx = node_to_idx[v_node]
                dist[u_idx][v_idx] = weight
                next_v[u_idx][v_idx] = v_node

    # Основной алгоритм
    for k_idx in range(v_comp):
        for i_idx in range(v_comp):
            for j_idx in range(v_comp):
                if dist[i_idx][j_idx] > dist[i_idx][k_idx] + dist[k_idx][j_idx]:
                    dist[i_idx][j_idx] = dist[i_idx][k_idx] + dist[k_idx][j_idx]
                    # Восстановление пути использует оригинальные номера вершин
                    k_node = component_nodes[k_idx]
                    next_v[i_idx][j_idx] = next_v[i_idx][node_to_idx[k_node]]

    return dist, next_v, node_to_idx


def reconstruct_path(start_node, end_node, next_v, node_to_idx, component_nodes):
    """Восстанавливает кратчайший путь между двумя вершинами."""
    if start_node not in node_to_idx or end_node not in node_to_idx:
        return None  # Вершины не в одной компоненте

    start_idx = node_to_idx[start_node]
    end_idx = node_to_idx[end_node]

    if next_v[start_idx][end_idx] is None:
        # Проверяем, есть ли путь
        if start_node == end_node:
            return [start_node]
        else:
            return None  # Нет пути между вершинами

    path = [start_node]
    current = start_node

    while current != end_node:
        current_idx = node_to_idx[current]
        next_node = next_v[current_idx][end_idx]
        if next_node is None:
            return None  # Путь не существует
        path.append(next_node)
        current = next_node

    return path


def calculate_characteristics_for_component(graph, component_nodes, dist_matrix):
    """Вычисляет характеристики для одной компоненты связности."""
    v_comp = len(component_nodes)
    characteristics = {}

    degrees = [len(graph.adjacency_list(node)) for node in component_nodes]
    characteristics['degrees'] = degrees

    eccentricities = [0.0] * v_comp
    for i in range(v_comp):
        max_dist = max(dist_matrix[i])
        eccentricities[i] = max_dist if max_dist != float('inf') else 0  # Для изолированных вершин
    characteristics['eccentricities'] = eccentricities

    radius = min(eccentricities)
    diameter = max(eccentricities)
    characteristics['radius'] = radius
    characteristics['diameter'] = diameter

    # Отображаем результаты обратно на оригинальные номера вершин
    node_to_ecc = {component_nodes[i]: e for i, e in enumerate(eccentricities)}
    central = [node for node, e in node_to_ecc.items() if e == radius]
    peripheral = [node for node, e in node_to_ecc.items() if e == diameter]
    characteristics['central_vertices'] = sorted(central)
    characteristics['peripheral_vertices'] = sorted(peripheral)

    return characteristics


file = sys.argv[1]
g = Graph(file, detect_file_format(file))
components = find_connected_components(g)

path_requested = False
start_vertex = None
end_vertex = None

if len(sys.argv) == 4:
    start_vertex = int(sys.argv[2])
    end_vertex = int(sys.argv[3])
    path_requested = True

# Для хранения результатов Флойда-Уоршелла для всех компонент
all_results = []

# Обрабатываем каждую компоненту по очереди
for component in sorted(components, key=len, reverse=True):
    print("Vertices list in component:")
    print(sorted(component))

    # Для компоненты из одной вершины характеристики тривиальны
    if len(component) <= 1:
        print("Vertices degrees:\n[0]")
        print("Eccentricity:\n[0]")
        print("R = 0")
        print("Central vertices:\n", component)
        print("D = 0")
        print("Peripherial vertices:\n", component)

        # Сохраняем результаты для возможного восстановления пути
        all_results.append((component, None, None, None))
        print("\n\n")
        continue

    # Запускаем Флойда-Уоршелла для текущей компоненты
    dist_submatrix, next_v, node_to_idx = floyd_warshall_for_component(g, component)

    # Сохраняем результаты для возможного восстановления пути
    all_results.append((component, dist_submatrix, next_v, node_to_idx))

    # Вычисляем и выводим характеристики для этой компоненты
    chars = calculate_characteristics_for_component(g, component, dist_submatrix)

    print("Vertices degrees:")
    print(chars['degrees'])
    print("Eccentricity:")
    print(chars['eccentricities'])
    print(f"R = {chars['radius']}")
    print("Central vertices:")
    print(chars['central_vertices'])
    print(f"D = {chars['diameter']}")
    print("Peripherial vertices:")
    print(chars['peripheral_vertices'])
    print("\n\n")


if path_requested:
    for component, dist_matrix, next_v, node_to_idx in all_results:
        if start_vertex in component and end_vertex in component:
            if len(component) == 1:
                # Особый случай: компонента из одной вершины
                if start_vertex == end_vertex:
                    print(f"Path: {start_vertex}")
                    print("Distance: 0")
            else:
                # Восстанавливаем путь
                path = reconstruct_path(start_vertex, end_vertex, next_v, node_to_idx, component)
                if path:
                    print(f"Path: {' -> '.join(map(str, path))}")
                    start_idx = node_to_idx[start_vertex]
                    end_idx = node_to_idx[end_vertex]
                    print(f"Distance: {dist_matrix[start_idx][end_idx]}")