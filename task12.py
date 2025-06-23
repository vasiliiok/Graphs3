import os
import re
import heapq
import math
import numpy as np
import matplotlib.pyplot as plt


class Map:
    def __init__(self, filepath):
        self._matrix = []
        with open(filepath, 'r') as f:
            for line in f:
                row_data = line.strip().split()
                if row_data:
                    self._matrix.append([int(h) for h in row_data])

        if not self._matrix:
            self._rows, self._cols = 0, 0
        else:
            self._rows, self._cols = len(self._matrix), len(self._matrix[0])

    def __getitem__(self, coords):
        row, col = coords
        return self._matrix[row][col]

    def size(self):
        return self._rows, self._cols

    def is_valid(self, coords):
        row, col = coords
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            return False
        if self._matrix[row][col] == 0:
            return False
        return True

    def neighbors(self, coords):
        row, col = coords
        possible_neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        return [neighbor for neighbor in possible_neighbors if self.is_valid(neighbor)]


# Эвристические функции
def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def chebyshev_distance(p1, p2):
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))


def a_star_search(map_obj: Map, start, goal, heuristic):
    # Очередь с приоритетом. Хранит (f_score, node).
    # Сразу добавляем стартовую точку.
    open_set = [(heuristic(start, goal), start)]

    # Множество для уже полностью исследованных вершин.
    closed_set = set()

    # Словарь для восстановления пути.
    came_from = {}

    # Словарь для хранения реальной стоимости пути от начала до вершины.
    g_score = {start: 0}

    while open_set:
        # Извлекаем вершину с наименьшим f_score
        _, current = heapq.heappop(open_set)

        # Если мы уже обработали эту вершину (через более короткий путь), пропускаем.
        if current in closed_set:
            continue

        # Если мы достигли цели, восстанавливаем и возвращаем путь.
        if current == goal:
            path = []
            temp_current = current
            while temp_current in came_from:
                path.append(temp_current)
                temp_current = came_from[temp_current]
            path.append(start)
            return path[::-1], g_score[goal]

        # Помечаем текущую вершину как полностью исследованную.
        closed_set.add(current)

        for neighbor in map_obj.neighbors(current):
            # Пропускаем соседа, если он уже полностью исследован.
            if neighbor in closed_set:
                continue

            # Рассчитываем стоимость пути до соседа через текущую вершину.
            cost = 1 + abs(map_obj[neighbor] - map_obj[current])
            tentative_g_score = g_score.get(current, float('inf')) + cost

            # Если этот путь короче, чем ранее известный обновляем всю информацию о нём и добавляем в очередь.
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return None, float('inf')


def visualize_path(map_matrix, path, start, goal):
    """Создает и отображает визуализацию карты с путем."""
    data = np.array(map_matrix)

    masked_data = np.ma.masked_where(data == 0, data)

    fig, ax = plt.subplots(figsize=(10, 10))

    cmap = plt.cm.gray
    cmap.set_bad(color='black')
    ax.imshow(masked_data, cmap=cmap, interpolation='none')

    if path:
        # path содержит кортежи (row, col)
        # matplotlib.plot ожидает (x, y), что соответствует (col, row)
        rows, cols = zip(*path)
        ax.plot(cols, rows, marker='.', color='yellow', linewidth=2, markersize=8)

        # Отмечаем начало и конец
        # start и goal имеют формат (row, col), поэтому для plot нужно (col, row)
        ax.plot(start[1], start[0], 'go', markersize=12, label='Start')  # Зеленый круг
        ax.plot(goal[1], goal[0], 'rx', markersize=12, mew=3, label='Goal')  # Красный крест

    # Настройка сетки и осей для наглядности
    rows, cols = data.shape
    ax.set_xticks(np.arange(cols))
    ax.set_yticks(np.arange(rows))
    ax.set_xticks(np.arange(-.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-.5, rows, 1), minor=True)
    ax.grid(which='minor', color='w', linestyle='-', linewidth=1, alpha=0.3)
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    ax.legend()

    plt.show()


def run_a_star_tester():
    tests_dir = os.path.join('tests', 'task12')
    if not os.path.isdir(tests_dir):
        print(f"Ошибка: Директория для тестов не найдена: '{tests_dir}'")
        return

    ans_pattern = re.compile(r'map_00[1-8]_ans_00\d+\.txt')
    try:
        test_files = sorted([f for f in os.listdir(tests_dir) if ans_pattern.match(f)])
    except FileNotFoundError:
        print(f"Ошибка: Не удалось прочитать файлы из директории '{tests_dir}'.")
        return

    if not test_files:
        print(f"В директории '{tests_dir}' не найдено файлов с ответами.")
        return

    print("Доступные тесты:")
    for i, filename in enumerate(test_files):
        print(f"  {i + 1}. {filename}")

    choice = -1
    while not (1 <= choice <= len(test_files)):
        try:
            choice = int(input(f"Выберите тест (1-{len(test_files)}): "))
        except ValueError:
            print("Пожалуйста, введите число.")

    # Парсинг имен файлов и координат
    selected_ans_file = test_files[choice - 1]
    base_name = re.match(r"(map_00\d+)", selected_ans_file).group(1)
    map_filename = base_name + '.txt'

    ans_filepath = os.path.join(tests_dir, selected_ans_file)
    map_filepath = os.path.join(tests_dir, map_filename)

    with open(ans_filepath, 'r') as f:
        ans_content = f.read()
        match = re.search(r'between \((\d+), (\d+)\) and \((\d+), (\d+)\)', ans_content)
        r1, c1, r2, c2 = map(int, match.groups())
        start_point = (r1, c1)
        goal_point = (r2, c2)

    # Загрузка карты
    print(f"\nЗагрузка карты из '{map_filepath}'...")
    map_obj = Map(map_filepath)

    # Выбор эвристики
    heuristics = {
        1: ("Манхэттенская", manhattan_distance),
        2: ("Евклидова", euclidean_distance),
        3: ("Чебышева", chebyshev_distance)
    }
    print("\nВыберите эвристику:")
    for i, (name, _) in heuristics.items():
        print(f"  {i}. {name}")

    h_choice = -1
    while h_choice not in heuristics:
        try:
            h_choice = int(input(f"Ваш выбор (1-3): "))
        except ValueError:
            print("Пожалуйста, введите число.")

    h_name, h_func = heuristics[h_choice]
    print(f"\nЗапуск A* с эвристикой '{h_name}' от {start_point} до {goal_point}...")

    # Запуск алгоритма
    found_path, found_cost = a_star_search(map_obj, start_point, goal_point, h_func)

    # Вывод результатов
    print("\n--- Результат алгоритма ---")
    if found_path:
        print(f"{int(found_cost)} - length of path between {start_point} and {goal_point} points.")
        print(f"Path:\n{found_path}")
    else:
        print("Путь не найден.")

    print("\n--- Правильный ответ ---")
    print(ans_content.strip())

    # Визуализация
    print("\nОтображение визуализации...")
    visualize_path(map_obj._matrix, found_path, start_point, goal_point)


if __name__ == '__main__':
    run_a_star_tester()