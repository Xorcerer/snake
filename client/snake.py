from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout


class SquareWidget(Widget):
    pass

class BoardWidget(GridLayout):
    def __init__(self, rows, cols):
        super(self.__class__, self).__init__()

        self.rows = rows
        self.cols = cols

        for x in xrange(self.rows * self.cols):
            self.add_widget(SquareWidget())

class SnakeApp(App):

    def build(self):
        board = BoardWidget(10, 10)

        return board


if __name__ == '__main__':
    SnakeApp().run()
