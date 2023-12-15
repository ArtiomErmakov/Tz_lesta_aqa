from tkinter import *
from PIL import Image, ImageDraw
from random import randint
from tkinter import colorchooser, messagebox
from figures import Circle, Rectangle, Triangle
from constants import Settings, Title, Color


class Engine2D:
    x: int = Settings.POINT_ZERO
    y: int = Settings.POINT_ZERO
    root: Tk = Tk()
    brush_size: int = Settings.SIZE_TEN
    color: str = Color.BLACK
    canvas: Canvas = Canvas(root, bg=Color.WHITE)
    menu: Menu = Menu(tearoff=0)
    image1: Image = Image.new('RGB', (Settings.POINT_1280, Settings.POINT_640), Color.WHITE)
    draw_img: ImageDraw = ImageDraw.Draw(image1)
    color_lab: Label = Label(root, bg=color, width=Settings.WIDTH_TEN)
    start_value: IntVar = IntVar(value=Settings.TEN_VALUE)
    figures = []

    def __init__(self) -> None:
        self._post_init()
        self.root.mainloop()

    def _post_init(self) -> None:
        self._init_root()
        self._init_canvas()
        self._create_menu()
        self._create_interface()

    def _init_root(self) -> None:
        self.root.title(Title.ENGINE2D)
        self.root.geometry(Settings.SIZE_1280x720)
        self.root.resizable(Settings.FALSE_VALUE,
                            Settings.FALSE_VALUE)
        self.root.columnconfigure(Settings.SIX_COLUMN,
                                  weight=Settings.WEIGHT_ONE)
        self.root.rowconfigure(Settings.TWO_ROW,
                               weight=Settings.WEIGHT_ONE)

    def _init_canvas(self) -> None:
        self.canvas.grid(row=Settings.TWO_ROW,
                         column=Settings.ZERO_COLUMN,
                         columnspan=Settings.SEVEN_COLUMN,
                         padx=Settings.FIVE_PIXELS,
                         pady=Settings.FIVE_PIXELS,
                         sticky=E + W + S + N)
        self.canvas.bind(Settings.BUTTON_B1, self.draw_pen)
        self.canvas.bind(Settings.BUTTON_3, self.popup)

    def _create_menu(self) -> None:
        self.menu.add_command(label=Title.RECTANGLE, command=self.draw_rectangle)
        self.menu.add_command(label=Title.CIRCLE, command=self.draw_circle)
        self.menu.add_command(label=Title.TRIANGLE, command=self.draw_triangle)

    def _create_interface(self) -> None:
        Label(self.root,
              text=Title.OPTIONS + Settings.COLON).grid(row=Settings.ZERO_ROW,
                                                        column=Settings.ZERO_COLUMN,
                                                        padx=Settings.SIX_PIXELS)
        Button(self.root,
               text=Title.CHOOSE_COLOR,
               width=Settings.WEIGHT_ELEVEN,
               command=self.choose_color).grid(row=Settings.ZERO_ROW,
                                               column=Settings.ONE_COLUMN,
                                               padx=Settings.SIX_PIXELS)

        self.color_lab.grid(row=Settings.ZERO_ROW,
                            column=Settings.TWO_COLUMN,
                            padx=Settings.SIX_PIXELS)

        Scale(self.root,
              variable=self.start_value,
              from_=Settings.VALUE_ONE,
              to=Settings.VALUE_ONE_HUNDRED,
              orient=HORIZONTAL,
              command=self.select).grid(row=Settings.ZERO_ROW,
                                        column=Settings.THREE_COLUMN,
                                        padx=Settings.SIX_PIXELS)

        Label(self.root,
              text=Title.ACTIONS + Settings.COLON).grid(row=Settings.ONE_ROW,
                                                        column=Settings.ONE_COLUMN)

        Button(self.root,
               text=Title.FILL,
               width=Settings.WEIGHT_TEN,
               command=self.pour).grid(row=Settings.ONE_ROW,
                                       column=Settings.ONE_COLUMN)

        Button(self.root,
               text=Title.CLEAR,
               width=Settings.WEIGHT_TEN,
               command=self.clear_canvas).grid(row=Settings.ONE_ROW,
                                               column=Settings.TWO_COLUMN)

        Button(self.root,
               text=Title.SAVE,
               width=Settings.WEIGHT_TEN,
               command=self.save_img).grid(row=Settings.ONE_ROW,
                                           column=Settings.SIX_COLUMN)

    def popup(self, event) -> None:
        self.x = event.x
        self.y = event.y
        self.menu.post(event.x_root, event.y_root)

    def draw_pen(self, event) -> None:
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        self.canvas.create_oval(x1, y1, x2, y2, fill=self.color, width=Settings.WIDTH_ZERO)
        self.draw_img.ellipse((x1, y1, x2, y2), fill=self.color)

    def draw_rectangle(self) -> None:
        rectangle = Rectangle(self.x, self.y, self.canvas, self.brush_size, self.color, self.draw_img)
        rectangle.draw()

    def draw_circle(self) -> None:
        circle = Circle(self.x, self.y, self.canvas, self.brush_size, self.color, self.draw_img)
        circle.draw()

    def draw_triangle(self) -> None:
        triangle = Triangle(self.x, self.y, self.canvas, self.brush_size, self.color, self.draw_img)
        triangle.draw()

    def choose_color(self) -> None:
        (rqb, hx) = colorchooser.askcolor()
        self.color = hx
        self.color_lab[Settings.COLUMN_BG] = hx

    def select(self, value) -> None:
        self.brush_size = int(value)

    def pour(self) -> None:
        self.canvas.delete(Settings.ALL)
        self.canvas[Settings.COLUMN_BG] = self.color
        self.draw_img.rectangle((Settings.POINT_ZERO, Settings.POINT_ZERO, Settings.POINT_1280, Settings.POINT_720),
                                width=Settings.WIDTH_ZERO,
                                fill=self.color)
        self.draw_img.rectangle((Settings.POINT_ZERO, Settings.POINT_ZERO, Settings.POINT_1280, Settings.POINT_720),
                                width=Settings.WIDTH_ZERO,
                                fill=self.color)

    def clear_canvas(self) -> None:
        self.canvas.delete(Settings.ALL)
        self.canvas[Settings.COLUMN_BG] = Color.WHITE
        self.draw_img.rectangle((Settings.POINT_ZERO, Settings.POINT_ZERO, Settings.POINT_1280, Settings.POINT_720),
                                width=Settings.WIDTH_ZERO,
                                fill=Color.WHITE)

    def save_img(self) -> None:
        filename = f'image_{randint(0, 10000)}.png'
        self.image1.save(filename)
        messagebox.showinfo(Title.SAVE, 'Saved under name %s' % filename)

    def draw(self) -> None:
        for figure in self.figures:
            figure.draw()
        self.clear_canvas()

    def add_figure(self, figure) -> None:
        self.figures.append(figure)

    def start(self) -> None:
        self.root.mainloop()
