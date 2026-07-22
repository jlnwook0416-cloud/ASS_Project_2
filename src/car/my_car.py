import pygame

import settings


def draw_car_shape(screen, car_x, car_y, body_color, detail_color):
    """위에서 내려다본 자동차를 원하는 색상으로 그립니다."""

    car_body = pygame.Rect(car_x, car_y, settings.CAR_WIDTH, settings.CAR_HEIGHT)
    pygame.draw.rect(screen, body_color, car_body)
    pygame.draw.rect(screen, detail_color, car_body, settings.CAR_BORDER_WIDTH)

    front_window = pygame.Rect(
        car_x + (settings.CAR_WIDTH - settings.CAR_WINDOW_WIDTH) // 2,
        car_y + 18,
        settings.CAR_WINDOW_WIDTH,
        settings.CAR_WINDOW_HEIGHT,
    )
    pygame.draw.rect(screen, settings.SKY_BLUE_WINDOW, front_window)

    rear_window = pygame.Rect(
        car_x + (settings.CAR_WIDTH - settings.CAR_WINDOW_WIDTH) // 2,
        car_y + settings.CAR_HEIGHT - settings.CAR_WINDOW_HEIGHT - 18,
        settings.CAR_WINDOW_WIDTH,
        settings.CAR_WINDOW_HEIGHT,
    )
    pygame.draw.rect(screen, settings.SKY_BLUE_WINDOW, rear_window)

    pygame.draw.line(
        screen,
        detail_color,
        (car_x + settings.CAR_WIDTH // 2, car_y + 48),
        (car_x + settings.CAR_WIDTH // 2, car_y + settings.CAR_HEIGHT - 48),
        3,
    )

    tire_rectangles = (
        pygame.Rect(
            car_x - settings.CAR_TIRE_WIDTH,
            car_y + 18,
            settings.CAR_TIRE_WIDTH,
            settings.CAR_TIRE_HEIGHT,
        ),
        pygame.Rect(
            car_x + settings.CAR_WIDTH,
            car_y + 18,
            settings.CAR_TIRE_WIDTH,
            settings.CAR_TIRE_HEIGHT,
        ),
        pygame.Rect(
            car_x - settings.CAR_TIRE_WIDTH,
            car_y + settings.CAR_HEIGHT - settings.CAR_TIRE_HEIGHT - 18,
            settings.CAR_TIRE_WIDTH,
            settings.CAR_TIRE_HEIGHT,
        ),
        pygame.Rect(
            car_x + settings.CAR_WIDTH,
            car_y + settings.CAR_HEIGHT - settings.CAR_TIRE_HEIGHT - 18,
            settings.CAR_TIRE_WIDTH,
            settings.CAR_TIRE_HEIGHT,
        ),
    )

    for tire_rectangle in tire_rectangles:
        pygame.draw.rect(screen, settings.BLACK_TIRE, tire_rectangle)


class MyCar:
    """방향키와 WASD로 조종하는 빨간 자동차입니다."""

    def __init__(self):
        self.x = settings.START_CAR_X
        self.y = settings.START_CAR_Y

    def move_by_keyboard(self, pressed_keys, front_distance, road_scroll_y):
        """키보드 입력에 맞춰 자동차를 움직이고 도로 스크롤 값을 돌려줍니다."""

        is_moving_forward = pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]
        is_moving_backward = pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]
        can_move_forward = not self.is_obstacle_too_close(front_distance)

        if is_moving_forward and can_move_forward:
            if self.y > settings.CAR_CAMERA_LIMIT_Y:
                self.y -= settings.CAR_SPEED
                self.y = max(self.y, settings.CAR_CAMERA_LIMIT_Y)
            else:
                road_scroll_y += settings.ROAD_SCROLL_SPEED

        if is_moving_backward:
            if road_scroll_y > 0 and self.y <= settings.CAR_CAMERA_LIMIT_Y:
                road_scroll_y -= settings.ROAD_SCROLL_SPEED
                road_scroll_y = max(0, road_scroll_y)
            else:
                self.y += settings.CAR_SPEED

        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            self.x -= settings.CAR_SPEED
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            self.x += settings.CAR_SPEED

        self.limit_position()
        return road_scroll_y

    def is_obstacle_too_close(self, front_distance):
        """앞쪽 장애물이 정지 기준 거리 안에 있는지 확인합니다."""

        return front_distance is not None and front_distance <= settings.STOP_DISTANCE

    def limit_position(self):
        """자동차가 화면 밖으로 나가지 않도록 좌표를 제한합니다."""

        min_car_x = settings.LEFT_ROAD_EDGE_X + settings.CAR_TIRE_WIDTH
        max_car_x = (
            settings.LEFT_ROAD_EDGE_X
            + settings.ROAD_WIDTH
            - settings.CAR_WIDTH
            - settings.CAR_TIRE_WIDTH
        )
        min_car_y = 0
        max_car_y = settings.SCREEN_HEIGHT - settings.CAR_HEIGHT

        self.x = max(min_car_x, min(self.x, max_car_x))
        self.y = max(min_car_y, min(self.y, max_car_y))

    def draw(self, screen):
        """빨간색 플레이어 자동차를 화면에 그립니다."""

        draw_car_shape(
            screen,
            self.x,
            self.y,
            settings.RED_CAR_BODY,
            settings.DARK_RED_CAR_DETAIL,
        )
