import os

def detect_file_format(filepath):
    """Определяет формат файла с графом на основе имени файла"""
    filename = os.path.basename(filepath)

    if 'edges' in filename:
        return 'edges'
    elif 'adjacency' in filename:
        return 'adjacency'
    elif 'matrix' in filename:
        return 'matrix'
    else:
        return 'unknown'

class Graph:
    def __init__(self, filepath, filetype):
        """
        Конструктор класса
        filepath: путь к файлу с графом
        filetype: тип файла ('edges', 'adjacency_list', 'adjacency_matrix')
        """
        self._adjacency_list = {}
        self._is_directed = False
        self._num_vertices = 0

        if filetype == 'edges':
            self._load_from_edges(filepath)
        elif filetype == 'adjacency':
            self._load_from_adjacency_list(filepath)
        elif filetype == 'matrix':
            self._load_from_adjacency_matrix(filepath)
        else:
            raise ValueError(f"Unknown filetype: {filetype}")

    def _load_from_edges(self, filepath):
        """Загрузка графа из списка рёбер"""
        with open(filepath, 'r') as f:
            lines = f.readlines()
            self._num_vertices = int(lines[0].strip())

            # Инициализация пустых списков смежности
            for i in range(1, self._num_vertices + 1):
                self._adjacency_list[i] = []

            # Чтение рёбер
            for line in lines[1:]:
                if line.strip():
                    parts = line.strip().split()
                    u, v, w = int(parts[0]), int(parts[1]), float(parts[2])

                    # Добавляем ребро в список смежности
                    self._adjacency_list[u].append((v, w))

                    # Проверяем, является ли граф ориентированным
                    if not self._check_reverse_edge(v, u, w):
                        self._is_directed = True
                    else:
                        # Если граф неориентированный, добавляем обратное ребро
                        if not any(neighbor == u and weight == w for neighbor, weight in self._adjacency_list[v]):
                            self._adjacency_list[v].append((u, w))

    # Вставьте этот код в класс Graph в файле graph.py, заменив старый метод
    def _load_from_adjacency_list(self, filepath):
        """Загрузка графа из списков смежности (с поддержкой невзвешенных графов)"""
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if not lines:
                self._num_vertices = 0
                return

            self._num_vertices = int(lines[0].strip())

            # Инициализация пустых списков смежности
            for i in range(1, self._num_vertices + 1):
                self._adjacency_list[i] = []

            # Чтение списков смежности
            for i, line in enumerate(lines[1:], 1):
                if i > self._num_vertices:
                    break

                if line.strip():
                    neighbors = line.strip().split()
                    for neighbor_data in neighbors:
                        # Если есть вес, указанный через ':', парсим его
                        if ':' in neighbor_data:
                            neighbor, weight = neighbor_data.split(':')
                            self._adjacency_list[i].append((int(neighbor), float(weight)))
                        # ИНАЧЕ (для невзвешенного графа) считаем вес равным 1.0
                        else:
                            self._adjacency_list[i].append((int(neighbor_data), 1.0))

        # Проверка на ориентированность
        self._check_if_directed()

    def _load_from_adjacency_matrix(self, filepath):
        """Загрузка графа из матрицы смежности"""
        with open(filepath, 'r') as f:
            lines = f.readlines()
            self._num_vertices = int(lines[0].strip())

            # Инициализация пустых списков смежности
            for i in range(1, self._num_vertices + 1):
                self._adjacency_list[i] = []

            # Чтение матрицы смежности
            matrix = []
            for line in lines[1:self._num_vertices + 1]:
                row = list(map(float, line.strip().split()))
                matrix.append(row)

            # Преобразование матрицы в списки смежности
            for i in range(self._num_vertices):
                for j in range(self._num_vertices):
                    if matrix[i][j] != 0:
                        self._adjacency_list[i + 1].append((j + 1, matrix[i][j]))

            # Проверка на симметричность матрицы
            self._is_directed = False
            for i in range(self._num_vertices):
                for j in range(self._num_vertices):
                    if matrix[i][j] != matrix[j][i]:
                        self._is_directed = True
                        break
                if self._is_directed:
                    break

    def _check_reverse_edge(self, u, v, w):
        """Проверка наличия обратного ребра с тем же весом"""
        return any(neighbor == v and weight == w for neighbor, weight in self._adjacency_list[u])

    def _check_if_directed(self):
        """Проверка, является ли граф ориентированным"""
        self._is_directed = False
        for u in self._adjacency_list:
            for v, w in self._adjacency_list[u]:
                if not self._check_reverse_edge(v, u, w):
                    self._is_directed = True
                    return

    def size(self):
        """Возвращает количество вершин в графе"""
        return self._num_vertices

    def weight(self, u, v):
        """Возвращает вес ребра между вершинами u и v"""
        for neighbor, w in self._adjacency_list.get(u, []):
            if neighbor == v:
                return w
        return float('inf')  # Если ребра нет, возвращаем бесконечность

    def is_edge(self, u, v):
        """Проверяет наличие ребра между вершинами u и v"""
        return any(neighbor == v for neighbor, _ in self._adjacency_list.get(u, []))

    def adjacency_matrix(self):
        """Возвращает матрицу смежности графа"""
        matrix = [[0 for _ in range(self._num_vertices)] for _ in range(self._num_vertices)]

        for u in range(1, self._num_vertices + 1):
            for v, w in self._adjacency_list.get(u, []):
                matrix[u - 1][v - 1] = w

        return matrix

    def adjacency_list(self, vertex):
        """Возвращает список вершин, смежных данной вершине"""
        return [v for v, _ in self._adjacency_list.get(vertex, [])]

    def list_of_edges(self, vertex=None):
        """
        Возвращает список рёбер графа
        Если указана вершина, возвращает только рёбра, инцидентные/исходящие из неё
        """
        edges = []

        if vertex is None:
            # Возвращаем все рёбра
            visited = set()
            for u in self._adjacency_list:
                for v, w in self._adjacency_list[u]:
                    if self._is_directed:
                        edges.append((u, v, w))
                    else:
                        # Для неориентированного графа избегаем дублирования
                        edge = tuple(sorted([u, v]) + [w])
                        if edge not in visited:
                            visited.add(edge)
                            edges.append((u, v, w))
        else:
            # Возвращаем рёбра для конкретной вершины
            for v, w in self._adjacency_list.get(vertex, []):
                edges.append((vertex, v, w))

        return edges

    def is_directed(self):
        """Возвращает True, если граф ориентированный"""
        return self._is_directed