from abc import ABC, abstractmethod
from constants import Settings


class Figure(ABC):
    def __init__(self, x, y, canvas, color, draw_img) -> None:
        self.x = x
        self.y = y
        self.canvas = canvas
        self.color = color
        self.draw_img = draw_img

    @abstractmethod
    def draw(self) -> None:
        pass


class Circle(Figure):

    def __init__(self, x, y, canvas, radius, color, draw_img) -> None:
        super().__init__(x, y, canvas, color, draw_img)
        self.radius = radius

    def draw(self) -> None:
        self.canvas.create_oval(self.x, self.y, self.x + self.radius, self.y + self.radius,
                                fill=self.color,
                                width=Settings.WIDTH_ZERO)
        self.draw_img.ellipse((self.x, self.y, self.x + self.radius, self.y + self.radius), fill=self.color)
        print(f'Drawing Circle at ({self.x}, {self.y}) with radius {self.radius}')


class Rectangle(Figure):
    def __init__(self, x, y, canvas, brush_size, color, draw_img) -> None:
        super().__init__(x, y, canvas, color, draw_img)
        self.height = int(brush_size / 2)
        self.width = brush_size

    def draw(self) -> None:
        self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height,
                                     fill=self.color,
                                     width=Settings.WIDTH_ZERO)
        self.draw_img.polygon((self.x, self.y, self.x + self.width, self.y, self.x + self.width,
                               self.y + self.height, self.x, self.y + self.height),
                              fill=self.color)
        print(f'Drawing Rectangle at ({self.x}, {self.y}) with width {self.width}, height {self.height}')


class Triangle(Figure):

    def __init__(self, x, y, canvas, size, color, draw_img) -> None:
        super().__init__(x, y, canvas, color, draw_img)
        self.size = size

    def draw(self) -> None:
        self.canvas.create_polygon([self.x, self.y],
                                   [self.x + self.size / 2, self.y + self.size],
                                   [self.x - self.size / 2, self.y + self.size],
                                   fill=self.color)
        self.draw_img.polygon([(self.x, self.y),
                               (self.x + self.size / 2, self.y + self.size),
                               (self.x - self.size / 2, self.y + self.size)],
                              fill=self.color)
        print(f'Drawing Triangle with vertices [({self.x}, {self.y}), ({int(self.x + self.size / 2)}, '
              f'{self.y + self.size}), ({int(self.x - self.size / 2)}, {self.y + self.size})]')
