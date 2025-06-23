import random
from graph import Graph, detect_file_format
import sys


class AntColonyOptimization:

    def __init__(self, graph, num_ants, num_iterations, alpha, beta, rho):
        """
        Инициализатор алгоритма.

        :param graph: Объект класса Graph.
        :param num_ants: Количество муравьёв в колонии.
        :param num_iterations: Количество итераций алгоритма.
        :param alpha: Коэффициент важности феромона.
        :param beta: Коэффициент важности эвристической информации.
        :param rho: Коэффициент испарения феромона.
        """
        self.graph = graph
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.rho = rho

        self.num_vertices = self.graph.size()  # Исправлено
        # Инициализация феромонов на всех рёбрах
        self.pheromones = [[1.0 / (self.num_vertices * self.num_vertices)] * (self.num_vertices + 1)
                           for _ in range(self.num_vertices + 1)]
        self.best_path = None
        self.best_path_length = float('inf')

    def run(self):
        """Запускает основной цикл алгоритма муравьиной колонии."""
        for _ in range(self.num_iterations):
            all_paths = []
            for _ in range(self.num_ants):
                path = self._construct_tour()
                path_length = self._calculate_path_length(path)

                all_paths.append((path, path_length))

                if path_length < self.best_path_length:
                    self.best_path = path
                    self.best_path_length = path_length

            self._update_pheromones(all_paths)

        return self.best_path, self.best_path_length

    def _update_pheromones(self, all_paths):
        """Обновляет феромоны: испарение и отложение."""
        # Испарение
        for i in range(1, self.num_vertices + 1):
            for j in range(1, self.num_vertices + 1):
                self.pheromones[i][j] *= (1.0 - self.rho)

        # Отложение
        for path, length in all_paths:
            pheromone_to_add = 1.0 / length
            for i in range(self.num_vertices):
                u, v = path[i], path[i + 1]
                self.pheromones[u][v] += pheromone_to_add
                self.pheromones[v][u] += pheromone_to_add  # Для неориентированного графа

    def _construct_tour(self):
        """Строит один полный маршрут для одного муравья."""
        start_vertex = random.randint(1, self.num_vertices)
        tour = [start_vertex]
        visited = {start_vertex}

        while len(tour) < self.num_vertices:
            current_vertex = tour[-1]
            next_vertex = self._select_next_vertex(current_vertex, visited)
            tour.append(next_vertex)
            visited.add(next_vertex)

        # Добавляем начальную вершину в конец, чтобы замкнуть цикл
        tour.append(start_vertex)
        return tour

    def _select_next_vertex(self, current_vertex, visited):
        """Выбирает следующую вершину для посещения."""
        probabilities = {}
        total_prob = 0.0

        # Рассчитываем вероятности перехода в каждую из непосещённых вершин
        for vertex in range(1, self.num_vertices + 1):
            if vertex not in visited:
                pheromone = self.pheromones[current_vertex][vertex] ** self.alpha
                # Эвристика: обратный вес ребра
                heuristic = (1.0 / self.graph.weight(current_vertex, vertex)) ** self.beta

                probabilities[vertex] = pheromone * heuristic
                total_prob += probabilities[vertex]

        # Если муравей застрял
        if total_prob == 0.0:
            unvisited = [v for v in range(1, self.num_vertices + 1) if v not in visited]
            return random.choice(unvisited)

        # Метод рулетки для выбора следующей вершины
        r = random.uniform(0, total_prob)
        cumulative_prob = 0.0
        for vertex, prob in probabilities.items():
            cumulative_prob += prob
            if cumulative_prob >= r:
                return vertex

        return max(probabilities, key=probabilities.get)

    def _calculate_path_length(self, path):
        """Вычисляет общую длину заданного пути."""
        length = 0.0
        for i in range(len(path) - 1):
            length += self.graph.weight(path[i], path[i + 1])  # Исправлено
        return length


if __name__ == '__main__':
    filename = sys.argv[1]
    filetype = detect_file_format(filename)
    g = Graph(filename, filetype)

    params = {
        'num_ants': 10,  # Количество муравьёв
        'num_iterations': 150,  # Количество итераций
        'alpha': 1.0,  # Влияние феромона
        'beta': 5.0,  # Влияние эвристики (длины ребра)
        'rho': 0.5  # Коэффициент испарения феромона
    }

    aco = AntColonyOptimization(graph=g, **params)
    best_path, best_length = aco.run()

    print(f"Length of shortest traveling salesman path is: {round(best_length, 2)}.")
    print("Path:")
    for i in range(len(best_path) - 1):
        u, v = best_path[i], best_path[i + 1]
        w = g.weight(u, v)
        print(f"{u}-{v} : {w}")