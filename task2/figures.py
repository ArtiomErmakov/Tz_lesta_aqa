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
