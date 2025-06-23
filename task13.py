import sys
from graph import Graph, detect_file_format


def is_bipartite(graph):
    n = graph.size()
    colors = {}

    # Обходим все компоненты связности
    for start in range(1, n + 1):
        if start not in colors:
            # BFS для раскраски
            queue = [start]
            colors[start] = 0

            while queue:
                u = queue.pop(0)
                current_color = colors[u]

                # Проверяем всех соседей
                for v in graph.adjacency_list(u):
                    if v not in colors:
                        colors[v] = 1 - current_color
                        queue.append(v)
                    elif colors[v] == current_color:
                        # Найдено ребро между вершинами одного цвета
                        return False, None

    return True, colors


def find_augmenting_path_dfs(graph, u, match, visited, left_part):
    """
    Ищет увеличивающий путь из вершины u используя DFS.
    match - текущее паросочетание (словарь)
    visited - посещенные вершины в текущем поиске
    left_part - множество вершин левой доли
    """
    for v in graph.adjacency_list(u):
        if v in left_part:  # Пропускаем вершины из той же доли
            continue

        if v not in visited:
            visited.add(v)

            # Если v не сопоставлена или можно найти увеличивающий путь из match[v]
            if v not in match or find_augmenting_path_dfs(graph, match[v], match, visited, left_part):
                match[v] = u
                match[u] = v
                return True

    return False


def kuhn_algorithm(graph, left_part, right_part):
    """
    Алгоритм Куна для поиска максимального паросочетания.
    left_part, right_part - множества вершин левой и правой долей
    """
    match = {}  # Словарь паросочетания: match[v] = u означает, что v сопоставлена с u

    # Для каждой вершины левой доли пытаемся найти увеличивающий путь
    for u in left_part:
        visited = set()
        find_augmenting_path_dfs(graph, u, match, visited, left_part)

    # Формируем результат - список рёбер паросочетания
    matching_edges = []
    processed = set()

    for v in match:
        if v not in processed:
            u = match[v]
            processed.add(v)
            processed.add(u)
            # Добавляем ребро (меньший_номер, больший_номер, None)
            if u < v:
                matching_edges.append((u, v, None))
            else:
                matching_edges.append((v, u, None))

    return matching_edges


def find_maximum_matching(graph):
    """
    Находит максимальное паросочетание в двудольном графе.
    Возвращает список рёбер паросочетания.
    """
    # Проверяем, является ли граф двудольным
    is_bip, colors = is_bipartite(graph)

    if not is_bip:
        raise ValueError("Граф не является двудольным!")

    # Разделяем вершины на две доли
    left_part = set()
    right_part = set()

    for vertex, color in colors.items():
        if color == 0:
            left_part.add(vertex)
        else:
            right_part.add(vertex)

    # Применяем алгоритм Куна
    matching = kuhn_algorithm(graph, left_part, right_part)

    return matching


def main():
    file = sys.argv[1]

    filetype = detect_file_format(file)
    graph = Graph(file, filetype)
    matching = find_maximum_matching(graph)

    # Выводим результат
    print(f"Size of maximum matching: {len(matching)}.")
    print("Maximum matching:")
    print(matching)


if __name__ == "__main__":
    main()