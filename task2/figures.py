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
