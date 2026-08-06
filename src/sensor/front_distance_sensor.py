from dataclasses import dataclass

import pygame

import settings


@dataclass
class SensorState:
    """한 방향 센서의 이번 프레임 감지 상태입니다."""

    direction: str
    length: int
    width: int
    detection_rect: pygame.Rect
    nearest_vehicle: object | None = None
    nearest_distance: int | None = None
    is_detecting: bool = False
    default_sensor_color: tuple[int, int, int] = settings.SENSOR_LINE_COLOR
    detected_sensor_color: tuple[int, int, int] = settings.DETECTED_SENSOR_LINE_COLOR


class FrontDistanceSensor:
    """내 차 주변 4방향에서 가장 가까운 자동차와의 거리를 감지합니다."""

    DIRECTIONS = ("front", "left", "right", "rear")

    def calculate_distance(self, my_car, obstacle_car, road_scroll_y):
        """기존 전방 자동 정지 로직을 위한 전방 거리 계산입니다."""

        return self.calculate_distance_at_position(
            my_car.x,
            my_car.y,
            obstacle_car,
            road_scroll_y,
        )

    def calculate_distance_at_position(self, car_x, car_y, obstacle_car, road_scroll_y):
        """지정한 자동차 위치에서 앞 장애물까지의 빈 공간을 계산합니다."""

        front_state = self.calculate_sensor_state_at_position(
            "front",
            car_x,
            car_y,
            obstacle_car,
            road_scroll_y,
        )
        return front_state.nearest_distance

    def calculate_all(self, my_car, obstacle_cars, road_scroll_y):
        """플레이어 자동차 기준 4방향 센서 상태를 계산합니다."""

        return {
            direction: self.calculate_sensor_state_at_position(
                direction,
                my_car.x,
                my_car.y,
                obstacle_cars,
                road_scroll_y,
            )
            for direction in self.DIRECTIONS
        }

    def calculate_sensor_state_at_position(
        self,
        direction,
        car_x,
        car_y,
        obstacle_cars,
        road_scroll_y,
    ):
        """지정한 방향 센서의 감지 영역과 가장 가까운 자동차를 계산합니다."""

        detection_rect = self.get_detection_rect(direction, car_x, car_y, road_scroll_y)
        length, width = self.get_sensor_size(direction)
        nearest_vehicle = None
        nearest_distance = None

        for obstacle_car in self.get_obstacle_cars(obstacle_cars):
            obstacle_rect = self.get_obstacle_world_rect(obstacle_car)
            if not detection_rect.colliderect(obstacle_rect):
                continue

            distance = self.calculate_direction_distance(
                direction,
                car_x,
                car_y,
                obstacle_car,
                road_scroll_y,
            )
            if distance is None or distance > length:
                continue

            if nearest_distance is None or distance < nearest_distance:
                nearest_vehicle = obstacle_car
                nearest_distance = distance

        return SensorState(
            direction=direction,
            length=length,
            width=width,
            detection_rect=detection_rect,
            nearest_vehicle=nearest_vehicle,
            nearest_distance=nearest_distance,
            is_detecting=nearest_vehicle is not None,
        )

    def get_obstacle_cars(self, obstacle_cars):
        """단일 장애물 또는 장애물 목록을 같은 방식으로 순회합니다."""

        if isinstance(obstacle_cars, (list, tuple)):
            return obstacle_cars
        return (obstacle_cars,)

    def get_sensor_size(self, direction):
        """방향별 센서 길이와 폭을 돌려줍니다."""

        if direction in ("front", "rear"):
            length = settings.FRONT_SENSOR_LENGTH
            if direction == "rear":
                length = settings.REAR_SENSOR_LENGTH
            return length, settings.FRONT_REAR_SENSOR_WIDTH

        return settings.SIDE_SENSOR_LENGTH, settings.SIDE_SENSOR_WIDTH

    def get_detection_rect(self, direction, car_x, car_y, road_scroll_y):
        """화면 좌표 차량 위치를 기준으로 월드 좌표 감지 영역을 만듭니다."""

        player_world_y = car_y - road_scroll_y
        length, width = self.get_sensor_size(direction)

        if direction == "front":
            return pygame.Rect(car_x, player_world_y - length, width, length)

        if direction == "rear":
            return pygame.Rect(
                car_x,
                player_world_y + settings.CAR_HEIGHT,
                width,
                length,
            )

        side_y = player_world_y + ((settings.CAR_HEIGHT - width) // 2)
        if direction == "left":
            return pygame.Rect(car_x - length, side_y, length, width)

        if direction == "right":
            return pygame.Rect(car_x + settings.CAR_WIDTH, side_y, length, width)

        raise ValueError(f"Unknown sensor direction: {direction}")

    def get_obstacle_world_rect(self, obstacle_car):
        """장애물 자동차의 월드 좌표 사각형을 만듭니다."""

        return pygame.Rect(
            obstacle_car.x,
            obstacle_car.world_y,
            settings.CAR_WIDTH,
            settings.CAR_HEIGHT,
        )

    def calculate_direction_distance(
        self,
        direction,
        car_x,
        car_y,
        obstacle_car,
        road_scroll_y,
    ):
        """방향별로 내 차와 장애물 자동차 사이의 빈 공간을 계산합니다."""

        player_world_y = car_y - road_scroll_y
        player_left_x = car_x
        player_right_x = car_x + settings.CAR_WIDTH
        player_front_world_y = player_world_y
        player_rear_world_y = player_world_y + settings.CAR_HEIGHT

        obstacle_left_x = obstacle_car.x
        obstacle_right_x = obstacle_car.x + settings.CAR_WIDTH
        obstacle_front_world_y = obstacle_car.world_y
        obstacle_rear_world_y = obstacle_car.world_y + settings.CAR_HEIGHT

        if direction == "front":
            distance = player_front_world_y - obstacle_rear_world_y
        elif direction == "rear":
            distance = obstacle_front_world_y - player_rear_world_y
        elif direction == "left":
            distance = player_left_x - obstacle_right_x
        elif direction == "right":
            distance = obstacle_left_x - player_right_x
        else:
            raise ValueError(f"Unknown sensor direction: {direction}")

        if distance < 0:
            return None
        return int(distance)

    def has_front_obstacle(self, front_distance):
        """앞에 장애물이 감지되었는지 확인합니다."""

        return front_distance is not None

    def is_safe_distance(self, front_distance):
        """현재 거리가 안전거리보다 먼지 확인합니다."""

        return front_distance is None or front_distance > settings.STOP_DISTANCE

    def draw_all_sensor_lines(self, screen, my_car, sensor_states, road_scroll_y):
        """4방향 센서선을 현재 감지 상태 색상으로 그립니다."""

        for direction in self.DIRECTIONS:
            self.draw_sensor_line(screen, my_car, sensor_states[direction], road_scroll_y)

    def draw_sensor_line(self, screen, my_car, sensor_state, road_scroll_y=None):
        """센서 감지 영역의 중심축과 같은 위치에 얇은 선을 그립니다."""

        start_position, end_position = self.get_sensor_line_points(
            my_car,
            sensor_state,
            road_scroll_y,
        )
        color = sensor_state.default_sensor_color
        if sensor_state.is_detecting:
            color = sensor_state.detected_sensor_color

        pygame.draw.line(
            screen,
            color,
            start_position,
            end_position,
            settings.SENSOR_LINE_WIDTH,
        )

    def get_sensor_line_points(self, my_car, sensor_state, road_scroll_y):
        """월드 좌표 감지 영역을 화면 좌표 센서선 시작/끝점으로 변환합니다."""

        rect = sensor_state.detection_rect
        scroll_y = 0 if road_scroll_y is None else road_scroll_y

        if sensor_state.direction == "front":
            x = rect.centerx
            return (x, my_car.y), (x, rect.top + scroll_y)

        if sensor_state.direction == "rear":
            x = rect.centerx
            return (x, my_car.y + settings.CAR_HEIGHT), (x, rect.bottom + scroll_y)

        if sensor_state.direction == "left":
            y = rect.centery + scroll_y
            return (my_car.x, y), (rect.left, y)

        if sensor_state.direction == "right":
            y = rect.centery + scroll_y
            return (my_car.x + settings.CAR_WIDTH, y), (rect.right, y)

        raise ValueError(f"Unknown sensor direction: {sensor_state.direction}")
