import sys
from graph import Graph, detect_file_format
from collections import deque


class FlowNetwork:
    def __init__(self, graph):
        self.graph = graph
        self.n = graph.size()
        # Инициализируем потоки нулями
        self.flow = {}
        for u in range(1, self.n + 1):
            self.flow[u] = {}
            for v in range(1, self.n + 1):
                self.flow[u][v] = 0

    def get_capacity(self, u, v):
        """Получить пропускную способность ребра (u, v)"""
        return self.graph.weight(u, v) if self.graph.is_edge(u, v) else 0

    def get_residual_capacity(self, u, v):
        """Получить остаточную пропускную способность ребра (u, v)"""
        # Прямое ребро: capacity - flow
        if self.graph.is_edge(u, v):
            return self.get_capacity(u, v) - self.flow[u][v]
        # Обратное ребро: flow в обратном направлении
        elif self.graph.is_edge(v, u):
            return self.flow[v][u]
        else:
            return 0

    def find_augmenting_path_bfs(self, source, sink):
        """
        Найти увеличивающий путь от source к sink используя BFS
        Возвращает (путь, минимальная_пропускная_способность) или (None, 0)
        """
        parent = {source: None}
        visited = {source}
        queue = deque([source])

        while queue:
            u = queue.popleft()

            if u == sink:
                # Восстанавливаем путь
                path = []
                current = sink
                while parent[current] is not None:
                    path.append((parent[current], current))
                    current = parent[current]
                path.reverse()

                # Находим минимальную остаточную пропускную способность на пути
                min_capacity = float('inf')
                for u, v in path:
                    min_capacity = min(min_capacity, self.get_residual_capacity(u, v))

                return path, min_capacity

            # Проверяем все возможные ребра
            for v in range(1, self.n + 1):
                if v not in visited:
                    residual = self.get_residual_capacity(u, v)
                    if residual > 0:
                        visited.add(v)
                        parent[v] = u
                        queue.append(v)

        return None, 0

    def update_flow(self, path, flow_value):
        """Обновить поток вдоль пути на величину flow_value"""
        for u, v in path:
            if self.graph.is_edge(u, v):
                # Увеличиваем поток по прямому ребру
                self.flow[u][v] += flow_value
            else:
                # Уменьшаем поток по обратному ребру
                self.flow[v][u] -= flow_value

    def get_max_flow_value(self, source):
        """Получить суммарный поток из источника"""
        total_flow = 0
        for v in range(1, self.n + 1):
            total_flow += self.flow[source][v]
        return total_flow

    def get_flow_edges(self):
        """Получить список рёбер с ненулевым потоком"""
        edges = []
        for u in range(1, self.n + 1):
            for v in range(1, self.n + 1):
                if self.flow[u][v] > 0:
                    edges.append((u, v, self.flow[u][v]))
        return edges


def ford_fulkerson(graph, source, sink):
    """
    Алгоритм Форда-Фалкерсона для поиска максимального потока
    """
    # Создаем сеть потоков
    network = FlowNetwork(graph)

    # Пока существует увеличивающий путь
    while True:
        path, min_capacity = network.find_augmenting_path_bfs(source, sink)

        if path is None:
            break

        # Обновляем поток вдоль пути
        network.update_flow(path, min_capacity)

    # Возвращаем максимальный поток и рёбра с потоками
    max_flow = network.get_max_flow_value(source)
    flow_edges = network.get_flow_edges()

    return max_flow, flow_edges


def find_source_and_sink(graph):

    n = graph.size()
    in_degree = [0] * (n + 1)
    out_degree = [0] * (n + 1)

    # Подсчитываем степени
    for u in range(1, n + 1):
        for v in graph.adjacency_list(u):
            out_degree[u] += 1
            in_degree[v] += 1

    # Ищем вершины без входящих/исходящих рёбер
    sources = [v for v in range(1, n + 1) if in_degree[v] == 0]
    sinks = [v for v in range(1, n + 1) if out_degree[v] == 0]

    # Если нет явных источников/стоков, выбираем по степеням
    if not sources:
        max_out = max(out_degree[1:])
        sources = [v for v in range(1, n + 1) if out_degree[v] == max_out]

    if not sinks:
        max_in = max(in_degree[1:])
        sinks = [v for v in range(1, n + 1) if in_degree[v] == max_in]

    return sources[0] if sources else 1, sinks[0] if sinks else n


def main():

    filename = sys.argv[1]
    filetype = detect_file_format(filename)
    graph = Graph(filename, filetype)

    # Определяем источник и сток
    if len(sys.argv) >= 4:
        source = int(sys.argv[2])
        sink = int(sys.argv[3])
    else:
        source, sink = find_source_and_sink(graph)

    # Находим максимальный поток
    max_flow, flow_edges = ford_fulkerson(graph, source, sink)

    # Выводим результат
    print(f"Maximum flow value: {int(max_flow)}.")
    print(f"Source: {source}, sink: {sink}.")
    print("Flow:")

    # Сортируем ребра
    flow_edges.sort()
    for u, v, flow in flow_edges:
        print(f"{u}-{v} : {int(flow)}")


if __name__ == "__main__":
    main()