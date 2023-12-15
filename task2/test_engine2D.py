from engine import Engine2D
from figures import Circle, Rectangle, Triangle


def test_engine_with_shapes(capsys):
    engine = Engine2D()
    engine.add_figure(Circle(x=0, y=0, radius=10, canvas=engine.canvas, color=engine.color, draw_img=engine.draw_img))
    engine.add_figure(Triangle(x=100, y=100, canvas=engine.canvas, size=10, color=engine.color,
                               draw_img=engine.draw_img))
    engine.add_figure((Rectangle(x=200, y=200, canvas=engine.canvas, brush_size=10, color=engine.color,
                                 draw_img=engine.draw_img)))

    # Ожидаемые результаты
    expected_output = (f"Drawing Circle at (0, 0) with radius 10\n"
                       f"Drawing Triangle with vertices [(100, 100), (105, 110), (95, 110)]\n"
                       f"Drawing Rectangle at (200, 200) with width 10, height 5\n")
    engine.draw()
    captured = capsys.readouterr()
    assert captured.out == expected_output


def test_engine_without_figures(capsys):
    engine = Engine2D()

    # Тест: отрисовка без добавленных фигур
    engine.draw()
    captured = capsys.readouterr()
    assert captured.out == ''
