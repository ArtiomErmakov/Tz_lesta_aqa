import random
from queue import Queue


def generate_map(m, n, land_percentage):
    # Инициализация карты
    field = [['water' for _ in range(n)] for _ in range(m)]

    # Генерация суши
    total_cells = m * n
    land_cells = int(total_cells * land_percentage)
    land_coordinates = random.sample(range(total_cells), land_cells)

    for coord in land_coordinates:
        row = coord // n
        col = coord % n
        field[row][col] = 'land'

    return field


def print_map(field):
    for row in field:
        print(" ".join(row))


def is_valid_move(row, col, m, n):
    return 0 <= row < m and 0 <= col < n


def shortest_path(field, start, end):
    m, n = len(field), len(field[0])
    visited = [[False for _ in range(n)] for _ in range(m)]

    queue = Queue()
    queue.put(start)
    visited[start[0]][start[1]] = True

    while not queue.empty():
        current = queue.get()

        if current == end:
            break

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for d in directions:
            next_row, next_col = current[0] + d[0], current[1] + d[1]

            if is_valid_move(next_row, next_col, m, n) and not visited[next_row][next_col] \
                    and field[next_row][next_col] != 'water':
                queue.put((next_row, next_col))
                visited[next_row][next_col] = True

    return visited[end[0]][end[1]]


# Пример использования
M = int(input("Введите M: "))
N = int(input("Введите N: "))
A = tuple(map(int, input("Введите координаты точки A (через пробел): ").split()))
B = tuple(map(int, input("Введите координаты точки B (через пробел): ").split()))

# Генерация карты
land_percentage = 0.3
map_field = generate_map(M, N, land_percentage)

# Вывод сгенерированной карты
print("Сгенерированная карта:")
print_map(map_field)

# Поиск кратчайшего пути
if shortest_path(map_field, A, B):
    print(f"Можно дойти из точки A в точку B.")
else:
    print(f"Невозможно дойти из точки A в точку B.")
