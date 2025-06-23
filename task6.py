import os
import re
from collections import deque


def load_maze(filepath):
    """
    Загружает лабиринт из файла
    Первая строка с размерами игнорируется
    """
    if not os.path.exists(filepath):
        print(f"Ошибка: Файл лабиринта не найден по пути {filepath}")
        return None
    with open(filepath, 'r') as f:
        lines = f.readlines()[1:]
        maze_lines = [line.strip().split() for line in lines]

        return [[int(cell) for cell in row] for row in maze_lines]


def solve_maze(maze, start, end):
    """
    Находит кратчайший путь в лабиринте с помощью BFS
    Возвращает список кортежей с координатами пути или None, если пути нет
    """
    if not maze:
        return None

    rows, cols = len(maze), len(maze[0])

    queue = deque([start])
    visited = {start}
    parent = {start: None}

    while queue:
        current_pos = queue.popleft()

        if current_pos == end:
            path = []
            while current_pos is not None:
                path.append(current_pos)
                current_pos = parent.get(current_pos)
            return path[::-1]

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_row, next_col = current_pos[0] + dr, current_pos[1] + dc

            if 0 <= next_row < rows and 0 <= next_col < cols and \
                    maze[next_row][next_col] == 1 and \
                    (next_row, next_col) not in visited:
                next_pos = (next_row, next_col)
                visited.add(next_pos)
                parent[next_pos] = current_pos
                queue.append(next_pos)
    return None


# -----------------------
# ТЕСТИРОВАНИЕ
# -----------------------


def run_maze_tester():
    tests_dir = os.path.join('tests', 'task6')

    try:
        ans_pattern = re.compile(r'ans_maze_t6_00[1-7]_ans_[1-4]\.txt')
        test_files = sorted([f for f in os.listdir(tests_dir) if ans_pattern.match(f)])
    except FileNotFoundError:
        print(f"Ошибка: Не удалось прочитать файлы из директории '{tests_dir}'.")
        return

    if not test_files:
        print(f"В директории '{tests_dir}' не найдено файлов с ответами, соответствующих шаблону.")
        return

    # Показать список и получить выбор пользователя
    print("Доступные тесты:")
    for i, filename in enumerate(test_files):
        print(f"  {i + 1}. {filename}")

    choice = -1
    while choice < 1 or choice > len(test_files):
        try:
            choice = int(input(f"Выберите тест (1-{len(test_files)}): "))
        except ValueError:
            print("Пожалуйста, введите число.")

    selected_ans_file = test_files[choice - 1]

    # Извлечь информацию из имени файла и его содержимого
    base_name = selected_ans_file.split('_ans_')[0]  # 'ans_maze_t6_001'
    maze_filename = base_name.replace('ans_', '') + '.txt'  # 'maze_t6_001.txt'

    ans_filepath = os.path.join(tests_dir, selected_ans_file)
    maze_filepath = os.path.join(tests_dir, maze_filename)

    start_point, end_point = None, None
    correct_answer_content = ""

    try:
        with open(ans_filepath, 'r', encoding='utf-8') as f:
            correct_answer_content = f.read()
            # Поиск координат в первой строке файла
            match = re.search(r'from \((\d+), (\d+)\) to \((\d+), (\d+)\)', correct_answer_content)
            if match:
                r1, c1, r2, c2 = map(int, match.groups())
                start_point = (r1, c1)
                end_point = (r2, c2)
    except FileNotFoundError:
        print(f"Ошибка: Не удалось открыть файл с ответом: {ans_filepath}")
        return
    except Exception as e:
        print(f"Произошла ошибка при чтении файла ответа: {e}")
        return

    if start_point is None:
        print("Не удалось извлечь начальную и конечную точки из файла ответа.")
        return

    # Загрузить матрицу лабиринта
    maze = load_maze(maze_filepath)
    if maze is None:
        return

    print("\n" + "=" * 40)
    print(f"Запуск теста: {selected_ans_file}")
    print(f"Лабиринт: {maze_filename}")
    print(f"Путь от {start_point} до {end_point}")
    print("=" * 40 + "\n")

    # Выполнить алгоритм и напечатать результат
    found_path = solve_maze(maze, start_point, end_point)

    print("--- Ваш результат ---")
    if found_path:
        print(f"Length of path from {start_point} to {end_point}: {len(found_path) - 1}")
        # print("Path:")
        # print(f"{found_path}")
    else:
        print(f"Путь от {start_point} до {end_point} не найден.")
    print("-" * 21 + "\n")

    # Напечатать правильный ответ
    print("--- Правильный ответ ---")
    print(correct_answer_content.splitlines()[0])
    print("-" * 24 + "\n")


if __name__ == '__main__':
    run_maze_tester()