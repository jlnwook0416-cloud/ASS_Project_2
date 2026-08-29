from dataclasses import dataclass
from enum import Enum

import pygame

import settings


class TrafficLightState(Enum):
    """차량용 신호등의 현재 신호 상태입니다."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


@dataclass
class StopLine:
    """월드 좌표 기준의 차량 정지선입니다."""

    world_y: float
    left_x: int
    right_x: int
    width: int = settings.STOP_LINE_WIDTH
    stop_distance: int = settings.STOP_LINE_STOP_DISTANCE

    def contains_car_x(self, car_x):
        """플레이어 차량의 가로 위치가 이 정지선의 적용 범위와 겹치는지 확인합니다."""

        car_left_x = car_x
        car_right_x = car_x + settings.CAR_WIDTH
        return car_right_x >= self.left_x and car_left_x <= self.right_x

    def distance_from_car_front(self, car_y, road_scroll_y):
        """플레이어 차량 앞 범퍼에서 정지선까지 남은 월드 거리입니다."""

        car_front_world_y = car_y - road_scroll_y
        return car_front_world_y - self.world_y

    def draw(self, screen, road_scroll_y):
        """카메라 스크롤을 반영하여 정지선을 화면에 그립니다."""

        screen_y = int(self.world_y + road_scroll_y)
        stop_line_rect = pygame.Rect(
            self.left_x,
            screen_y - (self.width // 2),
            self.right_x - self.left_x,
            self.width,
        )
        pygame.draw.rect(screen, settings.WHITE_ROAD_EDGE, stop_line_rect)


class TrafficLight:
    """월드 좌표에 고정되는 차량용 신호등입니다."""

    STATE_SEQUENCE = (
        TrafficLightState.GREEN,
        TrafficLightState.YELLOW,
        TrafficLightState.RED,
    )

    STATE_DURATIONS = {
        TrafficLightState.GREEN: settings.GREEN_TIME,
        TrafficLightState.YELLOW: settings.YELLOW_TIME,
        TrafficLightState.RED: settings.RED_TIME,
    }

    def __init__(self, x, world_y, stop_line):
        self.x = x
        self.world_y = world_y
        self.stop_line = stop_line
        self.state = TrafficLightState.GREEN
        self.elapsed_time = 0.0

    def update(self, delta_time):
        """실제 경과 시간 기준으로 신호 상태를 갱신합니다."""

        self.elapsed_time += delta_time

        while self.elapsed_time >= self.get_current_duration():
            self.elapsed_time -= self.get_current_duration()
            self.state = self.get_next_state()

    def get_current_duration(self):
        """현재 신호가 유지되어야 하는 시간을 초 단위로 돌려줍니다."""

        return self.STATE_DURATIONS[self.state]

    def get_next_state(self):
        """GREEN -> YELLOW -> RED -> GREEN 순서의 다음 신호를 돌려줍니다."""

        current_index = self.STATE_SEQUENCE.index(self.state)
        next_index = (current_index + 1) % len(self.STATE_SEQUENCE)
        return self.STATE_SEQUENCE[next_index]

    def should_stop_player(self):
        """이번 단계에서는 RED와 YELLOW에서 정지합니다."""

        return self.state in (TrafficLightState.RED, TrafficLightState.YELLOW)

    def get_safe_forward_distance(self, car_x, car_y, road_scroll_y, forward_distance):
        """신호 때문에 정지해야 할 때 정지선을 넘지 않는 전진 거리로 보정합니다."""

        if forward_distance <= 0 or not self.should_stop_player():
            return forward_distance

        if not self.stop_line.contains_car_x(car_x):
            return forward_distance

        distance_to_stop_line = self.stop_line.distance_from_car_front(
            car_y,
            road_scroll_y,
        )
        if distance_to_stop_line < 0:
            return forward_distance

        max_safe_forward_distance = distance_to_stop_line - self.stop_line.stop_distance
        if max_safe_forward_distance <= 0:
            return 0

        return min(forward_distance, max_safe_forward_distance)

    def is_stopping_player_now(self, car_x, car_y, road_scroll_y):
        """정지 신호 상태에서 플레이어가 이미 정지선 앞에 도달했는지 확인합니다."""

        if not self.should_stop_player() or not self.stop_line.contains_car_x(car_x):
            return False

        distance_to_stop_line = self.stop_line.distance_from_car_front(
            car_y,
            road_scroll_y,
        )
        return 0 <= distance_to_stop_line <= self.stop_line.stop_distance

    def draw(self, screen, road_scroll_y):
        """신호등 본체와 현재 활성화된 신호를 그립니다."""

        screen_y = int(self.world_y + road_scroll_y)
        pole_x = self.x + (settings.TRAFFIC_LIGHT_WIDTH // 2)
        pole_top_y = screen_y + settings.TRAFFIC_LIGHT_HEIGHT
        pygame.draw.rect(
            screen,
            settings.TRAFFIC_LIGHT_POLE,
            pygame.Rect(
                pole_x - (settings.TRAFFIC_LIGHT_POLE_WIDTH // 2),
                pole_top_y,
                settings.TRAFFIC_LIGHT_POLE_WIDTH,
                settings.TRAFFIC_LIGHT_POLE_HEIGHT,
            ),
        )

        housing_rect = pygame.Rect(
            self.x,
            screen_y,
            settings.TRAFFIC_LIGHT_WIDTH,
            settings.TRAFFIC_LIGHT_HEIGHT,
        )
        pygame.draw.rect(screen, settings.TRAFFIC_LIGHT_HOUSING, housing_rect)

        light_definitions = (
            (
                TrafficLightState.RED,
                settings.TRAFFIC_LIGHT_RED,
                settings.TRAFFIC_LIGHT_INACTIVE_RED,
            ),
            (
                TrafficLightState.YELLOW,
                settings.TRAFFIC_LIGHT_YELLOW,
                settings.TRAFFIC_LIGHT_INACTIVE_YELLOW,
            ),
            (
                TrafficLightState.GREEN,
                settings.TRAFFIC_LIGHT_GREEN,
                settings.TRAFFIC_LIGHT_INACTIVE_GREEN,
            ),
        )
        for light_index, (state, active_color, inactive_color) in enumerate(
            light_definitions
        ):
            light_center_y = screen_y + 24 + (light_index * 35)
            color = active_color if self.state == state else inactive_color
            pygame.draw.circle(
                screen,
                color,
                (self.x + (settings.TRAFFIC_LIGHT_WIDTH // 2), light_center_y),
                settings.TRAFFIC_LIGHT_RADIUS,
            )


def create_default_traffic_lights():
    """이번 단계에서 사용할 차량용 신호등 1개를 생성합니다."""

    stop_line = StopLine(
        settings.STOP_LINE_WORLD_Y,
        settings.STOP_LINE_LEFT_X,
        settings.STOP_LINE_RIGHT_X,
    )
    return [
        TrafficLight(
            settings.TRAFFIC_LIGHT_X,
            settings.TRAFFIC_LIGHT_WORLD_Y,
            stop_line,
        )
    ]
