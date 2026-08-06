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
        self.forward_speed = 0

    def move_by_keyboard(
        self,
        pressed_keys,
        front_distance_sensor,
        obstacle_car,
        road_scroll_y,
        delta_time,
    ):
        """키보드 입력에 맞춰 자동차를 움직이고 도로 스크롤 값을 돌려줍니다."""

        is_moving_forward = pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]
        is_moving_backward = pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]
        is_moving_left = pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]
        is_moving_right = pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]

        side_direction = self.get_side_direction(is_moving_left, is_moving_right)
        side_distance = side_direction * settings.CAR_SIDE_SPEED * delta_time
        next_x = self.get_limited_x(self.x + side_distance)

        front_distance_after_side_move = (
            front_distance_sensor.calculate_distance_at_position(
                next_x,
                self.y,
                obstacle_car,
                road_scroll_y,
            )
        )
        can_move_forward = not self.is_obstacle_too_close(front_distance_after_side_move)

        self.update_forward_speed(
            is_moving_forward,
            is_moving_backward,
            can_move_forward,
            delta_time,
        )

        forward_distance = self.forward_speed * delta_time

        if forward_distance != 0 and side_distance != 0:
            forward_distance *= settings.CAR_DIAGONAL_SPEED_FACTOR
            side_distance *= settings.CAR_DIAGONAL_SPEED_FACTOR
            next_x = self.get_limited_x(self.x + side_distance)

        forward_distance = self.get_safe_forward_distance(
            forward_distance,
            next_x,
            front_distance_sensor,
            obstacle_car,
            road_scroll_y,
        )

        self.x = next_x
        road_scroll_y = self.move_forward_distance(forward_distance, road_scroll_y)

        self.limit_position()
        return road_scroll_y

    def update_forward_speed(
        self,
        is_moving_forward,
        is_moving_backward,
        can_move_forward,
        delta_time,
    ):
        """전진/후진 입력에 따라 현재 속도를 가속 또는 감속합니다."""

        if is_moving_forward and is_moving_backward:
            target_speed = 0
        elif is_moving_forward and can_move_forward:
            target_speed = settings.CAR_MAX_FORWARD_SPEED
        elif is_moving_backward:
            target_speed = -settings.CAR_MAX_REVERSE_SPEED
        else:
            target_speed = 0

        if not can_move_forward and self.forward_speed > 0:
            target_speed = 0

        speed_change = settings.CAR_ACCELERATION * delta_time
        if target_speed == 0 or self.is_changing_direction(target_speed):
            speed_change = settings.CAR_DECELERATION * delta_time

        self.forward_speed = self.move_value_toward(
            self.forward_speed,
            target_speed,
            speed_change,
        )

        if abs(self.forward_speed) < settings.CAR_STOP_SPEED and target_speed == 0:
            self.forward_speed = 0

    def is_changing_direction(self, target_speed):
        """현재 진행 방향과 목표 진행 방향이 반대인지 확인합니다."""

        return self.forward_speed * target_speed < 0

    def move_value_toward(self, current_value, target_value, max_change):
        """현재 값을 목표 값 쪽으로 max_change만큼 이동합니다."""

        if current_value < target_value:
            return min(current_value + max_change, target_value)
        if current_value > target_value:
            return max(current_value - max_change, target_value)
        return current_value

    def get_side_direction(self, is_moving_left, is_moving_right):
        """좌우 입력을 -1, 0, 1 방향값으로 바꿉니다."""

        if is_moving_left and is_moving_right:
            return 0
        if is_moving_left:
            return -1
        if is_moving_right:
            return 1
        return 0

    def get_safe_forward_distance(
        self,
        forward_distance,
        next_x,
        front_distance_sensor,
        obstacle_car,
        road_scroll_y,
    ):
        """앞차와 안전거리보다 가까워지는 전진 이동을 차단합니다."""

        if forward_distance <= 0:
            return forward_distance

        front_distance = front_distance_sensor.calculate_distance_at_position(
            next_x,
            self.y,
            obstacle_car,
            road_scroll_y,
        )

        if front_distance is None:
            return forward_distance

        max_safe_forward_distance = front_distance - settings.STOP_DISTANCE
        if max_safe_forward_distance <= 0:
            self.forward_speed = 0
            return 0

        if forward_distance > max_safe_forward_distance:
            self.forward_speed = 0
            return max_safe_forward_distance

        return forward_distance

    def move_forward_distance(self, forward_distance, road_scroll_y):
        """전후 이동 거리를 차량 위치 또는 도로 스크롤에 반영합니다."""

        if forward_distance > 0:
            if self.y > settings.CAR_CAMERA_LIMIT_Y:
                self.y -= forward_distance
                self.y = max(self.y, settings.CAR_CAMERA_LIMIT_Y)
            else:
                road_scroll_y += forward_distance

        if forward_distance < 0:
            reverse_distance = abs(forward_distance)
            if road_scroll_y > 0 and self.y <= settings.CAR_CAMERA_LIMIT_Y:
                road_scroll_y -= reverse_distance
                road_scroll_y = max(0, road_scroll_y)
            else:
                self.y += reverse_distance

        return road_scroll_y

    def is_obstacle_too_close(self, front_distance):
        """앞쪽 장애물이 정지 기준 거리 안에 있는지 확인합니다."""

        return front_distance is not None and front_distance <= settings.STOP_DISTANCE

    def limit_position(self):
        """자동차가 화면 밖으로 나가지 않도록 좌표를 제한합니다."""

        self.x = self.get_limited_x(self.x)
        min_car_y = 0
        max_car_y = settings.SCREEN_HEIGHT - settings.CAR_HEIGHT

        self.y = max(min_car_y, min(self.y, max_car_y))

    def get_limited_x(self, car_x):
        """자동차가 도로 밖으로 완전히 벗어나지 않는 X좌표를 돌려줍니다."""

        min_car_x = settings.LEFT_ROAD_EDGE_X + settings.CAR_TIRE_WIDTH
        max_car_x = (
            settings.LEFT_ROAD_EDGE_X
            + settings.ROAD_WIDTH
            - settings.CAR_WIDTH
            - settings.CAR_TIRE_WIDTH
        )

        return max(min_car_x, min(car_x, max_car_x))

    def draw(self, screen):
        """빨간색 플레이어 자동차를 화면에 그립니다."""

        draw_car_shape(
            screen,
            self.x,
            self.y,
            settings.RED_CAR_BODY,
            settings.DARK_RED_CAR_DETAIL,
        )
