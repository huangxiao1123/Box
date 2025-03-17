from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.label import Label
from kivy.core.window import Window
import random
import os

# 配置窗口大小（适配手机竖屏）
Config.set('graphics', 'resizable', '0')
Window.size = (360, 640)  # 常见手机竖屏尺寸

# 游戏常量
GRID_SIZE = 20
CELL_SIZE = 25
INITIAL_SPEED = 0.15
DIRECTIONS = ['up', 'right', 'down', 'left']


class SnakeSegment:
    def __init__(self, pos):
        self.pos = pos


class Snake:
    def __init__(self):
        self.body = [SnakeSegment((GRID_SIZE // 2, GRID_SIZE // 2))]
        self.direction = 'right'
        self.growing = False

    @property
    def head(self):
        return self.body[0]

    def move(self):
        x, y = self.head.pos
        if self.direction == 'up':
            new_head = (x, y + 1)
        elif self.direction == 'down':
            new_head = (x, y - 1)
        elif self.direction == 'left':
            new_head = (x - 1, y)
        else:  # right
            new_head = (x + 1, y)

        self.body.insert(0, SnakeSegment(new_head))
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False

    def grow(self):
        self.growing = True


class Food:
    def __init__(self):
        self.pos = (0, 0)
        self.spawn()

    def spawn(self, snake_body=None):
        while True:
            self.pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if snake_body is None or all(self.pos != seg.pos for seg in snake_body):
                break


class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.paused = False

        # 加载食物图片
        self.food_texture = None
        if os.path.exists("images/apple.png"):
            self.food_texture = CoreImage("images/apple.png").texture

        # 游戏计时器
        Clock.schedule_interval(self.update, INITIAL_SPEED)

        # 得分标签
        self.score_label = Label(
            text=f"Score: {self.score}",
            pos=(20, Window.height - 60),
            font_size='20sp'
        )
        self.add_widget(self.score_label)

    def on_touch_down(self, touch):
        if self.game_over:
            return
        # 触摸左半屏逆时针转，右半屏顺时针转
        if touch.x < self.width / 2:
            new_dir_index = (DIRECTIONS.index(self.snake.direction) - 1) % 4
        else:
            new_dir_index = (DIRECTIONS.index(self.snake.direction) + 1) % 4
        self.snake.direction = DIRECTIONS[new_dir_index]

    def update(self, dt):
        if self.game_over or self.paused:
            return

        self.snake.move()

        # 检测食物碰撞
        if self.snake.head.pos == self.food.pos:
            self.score += 1
            self.score_label.text = f"Score: {self.score}"
            self.snake.grow()
            self.food.spawn([seg.pos for seg in self.snake.body])

        # 检测碰撞
        if self.check_collision():
            self.game_over = True
            self.show_game_over()

        self.draw()

    def check_collision(self):
        head = self.snake.head.pos
        # 边界检测
        if not (0 <= head[0] < GRID_SIZE and 0 <= head[1] < GRID_SIZE):
            return True
        # 自碰检测
        for seg in self.snake.body[1:]:
            if head == seg.pos:
                return True
        return False

    def show_game_over(self):
        self.add_widget(Label(
            text=f"Game Over!\nScore: {self.score}",
            pos=(self.center_x - 100, self.center_y),
            font_size='30sp',
            color=(1, 0, 0, 1),
            bold=True
        ))

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            # 绘制背景
            Color(0.2, 0.2, 0.2)
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))

            # 绘制食物
            if self.food_texture:
                Rectangle(
                    texture=self.food_texture,
                    pos=(
                        self.food.pos[0] * CELL_SIZE + (Window.width - GRID_SIZE * CELL_SIZE) / 2,
                        self.food.pos[1] * CELL_SIZE + 50
                    ),
                    size=(CELL_SIZE, CELL_SIZE)
                )
            else:
                Color(1, 0, 0)
                Rectangle(
                    pos=(
                        self.food.pos[0] * CELL_SIZE + (Window.width - GRID_SIZE * CELL_SIZE) / 2,
                        self.food.pos[1] * CELL_SIZE + 50
                    ),
                    size=(CELL_SIZE, CELL_SIZE)
                )

            # 绘制蛇
            Color(0, 1, 0)
            for seg in self.snake.body:
                Rectangle(
                    pos=(
                        seg.pos[0] * CELL_SIZE + (Window.width - GRID_SIZE * CELL_SIZE) / 2,
                        seg.pos[1] * CELL_SIZE + 50
                    ),
                    size=(CELL_SIZE - 1, CELL_SIZE - 1)
                )


class SnakeApp(App):
    def build(self):
        game = SnakeGame()
        # 游戏区域居中显示
        game.pos = (0, 50)
        return game


if __name__ == '__main__':
    SnakeApp().run()