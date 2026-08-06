import pygame

import settings


class FrontDistanceSensor:
    """내 차와 앞 장애물 사이의 거리를 감지합니다."""

    def calculate_distance(self, my_car, obstacle_car, road_scroll_y):
        """내 차 앞쪽과 장애물 자동차 뒤쪽 사이의 빈 공간을 계산합니다."""

        return self.calculate_distance_at_position(
            my_car.x,
            my_car.y,
            obstacle_car,
            road_scroll_y,
        )

    def calculate_distance_at_position(self, car_x, car_y, obstacle_car, road_scroll_y):
        """지정한 자동차 위치에서 앞 장애물까지의 빈 공간을 계산합니다."""

        player_world_y = car_y - road_scroll_y

        player_left_x = car_x
        player_right_x = car_x + settings.CAR_WIDTH
        obstacle_left_x = obstacle_car.x
        obstacle_right_x = obstacle_car.x + settings.CAR_WIDTH

        is_x_overlapping = (
            player_left_x < obstacle_right_x
            and player_right_x > obstacle_left_x
        )
        if not is_x_overlapping:
            return None

        player_front_world_y = player_world_y
        obstacle_rear_world_y = obstacle_car.world_y + settings.CAR_HEIGHT
        empty_space_distance = player_front_world_y - obstacle_rear_world_y

        if empty_space_distance < 0:
            return None

        return int(empty_space_distance)

    def has_front_obstacle(self, front_distance):
        """앞에 장애물이 감지되었는지 확인합니다."""

        return front_distance is not None

    def is_safe_distance(self, front_distance):
        """현재 거리가 안전거리보다 먼지 확인합니다."""

        return front_distance is None or front_distance > settings.STOP_DISTANCE

    def draw_sensor_line(self, screen, my_car, obstacle_car, road_scroll_y):
        """감지 중일 때 내 차 앞쪽 중앙에서 장애물 뒤쪽 중앙까지 선을 그립니다."""

        player_front_center = (
            my_car.x + (settings.CAR_WIDTH // 2),
            my_car.y,
        )
        obstacle_rear_center = (
            obstacle_car.x + (settings.CAR_WIDTH // 2),
            obstacle_car.get_screen_y(road_scroll_y) + settings.CAR_HEIGHT,
        )

        pygame.draw.line(
            screen,
            settings.SENSOR_LINE_COLOR,
            player_front_center,
            obstacle_rear_center,
            2,
        )
