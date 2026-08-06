import pygame

import settings
from car.my_car import MyCar
from car.opponent_car_manager import OpponentCarManager
from road.road_drawer import RoadDrawer
from screen.screen_text import ScreenText
from sensor.front_distance_sensor import FrontDistanceSensor


class GameManager:
    """pygame 실행 흐름과 게임에 필요한 객체들을 관리합니다."""

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("ASS V1.0 - Road")

        self.clock = pygame.time.Clock()
        self.distance_font = pygame.font.SysFont(None, settings.DISTANCE_TEXT_SIZE)

        self.my_car = MyCar()
        self.opponent_car_manager = OpponentCarManager()
        self.road_drawer = RoadDrawer()
        self.front_distance_sensor = FrontDistanceSensor()
        self.screen_text = ScreenText(self.distance_font)

        self.road_scroll_y = 0
        self.is_running = True

    def run(self):
        """창이 닫힐 때까지 게임 루프를 실행합니다."""

        while self.is_running:
            delta_time = self.clock.tick(settings.FPS) / 1000
            delta_time = min(delta_time, settings.MAX_DELTA_TIME)

            self.handle_events()
            self.opponent_car_manager.update(delta_time)
            self.handle_keyboard_input(delta_time)
            self.opponent_car_manager.maintain_traffic(
                self.my_car,
                self.road_scroll_y,
            )
            self.update_screen()

        pygame.quit()

    def handle_events(self):
        """창 닫기와 ESC 키 입력 같은 pygame 이벤트를 처리합니다."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_running = False

    def handle_keyboard_input(self, delta_time):
        """현재 누르고 있는 키를 확인하고 내 차를 움직입니다."""

        pressed_keys = pygame.key.get_pressed()

        self.road_scroll_y = self.my_car.move_by_keyboard(
            pressed_keys,
            self.front_distance_sensor,
            self.opponent_car_manager.get_cars(),
            self.road_scroll_y,
            delta_time,
        )

    def update_screen(self):
        """도로, 자동차, 센서, 글자를 순서대로 그리고 화면을 갱신합니다."""

        sensor_states = self.front_distance_sensor.calculate_all(
            self.my_car,
            self.opponent_car_manager.get_cars(),
            self.road_scroll_y,
        )

        self.screen.fill(settings.GREEN_BACKGROUND)
        self.road_drawer.draw(self.screen, self.road_scroll_y)
        self.opponent_car_manager.draw(self.screen, self.road_scroll_y)
        self.my_car.draw(self.screen)
        self.front_distance_sensor.draw_all_sensor_lines(
            self.screen,
            self.my_car,
            sensor_states,
            self.road_scroll_y,
        )
        self.screen_text.draw_distance_text(self.screen, sensor_states)
        pygame.display.flip()
