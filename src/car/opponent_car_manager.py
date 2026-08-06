import random

import settings
from car.opponent_car import OpponentCar


class OpponentCarManager:
    """상대 차량 목록의 생성, 이동, 그리기를 관리합니다."""

    def __init__(self):
        self.opponent_cars = self.create_default_opponent_cars()
        self.farthest_player_world_y = settings.START_CAR_Y
        self.last_spawn_player_world_y = settings.START_CAR_Y
        self.next_spawn_interval_distance = self.get_next_spawn_interval_distance()

    def create_default_opponent_cars(self):
        """게임 시작 시 겹치지 않도록 충분한 간격을 두고 상대 차량을 배치합니다."""

        opponent_cars = []
        same_direction_lanes = settings.RIGHT_DIRECTION_LANE_INDICES
        opposite_direction_lanes = settings.LEFT_DIRECTION_LANE_INDICES

        for car_index in range(settings.OPPONENT_CAR_COUNT):
            if car_index % 2 == 0:
                same_direction_index = car_index // 2
                lane_index = same_direction_lanes[
                    same_direction_index % len(same_direction_lanes)
                ]
                world_y = (
                    settings.START_CAR_Y
                    - settings.OPPONENT_CAR_START_DISTANCE_AHEAD
                    - (same_direction_index * settings.OPPONENT_CAR_MIN_START_GAP)
                )
                move_direction = settings.OPPONENT_CAR_FORWARD_DIRECTION
                speed = settings.OPPONENT_CAR_SAME_DIRECTION_SPEED
            else:
                opposite_direction_index = car_index // 2
                lane_index = opposite_direction_lanes[
                    opposite_direction_index % len(opposite_direction_lanes)
                ]
                world_y = (
                    settings.START_CAR_Y
                    - settings.OPPONENT_CAR_START_DISTANCE_AHEAD
                    - (opposite_direction_index * settings.OPPONENT_CAR_MIN_START_GAP)
                )
                move_direction = settings.OPPONENT_CAR_REVERSE_DIRECTION
                speed = settings.OPPONENT_CAR_OPPOSITE_DIRECTION_SPEED

            opponent_cars.append(
                OpponentCar(lane_index, world_y, move_direction, speed)
            )

        return opponent_cars

    def update(self, delta_time):
        """모든 상대 차량을 한 프레임만큼 이동합니다."""

        for opponent_car in self.opponent_cars:
            opponent_car.update(delta_time)

    def maintain_traffic(self, my_car, road_scroll_y):
        """플레이어 주변의 상대 차량 생성과 삭제를 관리합니다."""

        player_world_y = self.get_player_world_y(my_car, road_scroll_y)
        self.farthest_player_world_y = min(
            self.farthest_player_world_y,
            player_world_y,
        )
        self.remove_far_cars(player_world_y)
        self.try_spawn_car(player_world_y)

    def try_spawn_car(self, player_world_y):
        """플레이어가 충분히 전진했을 때 새 상대 차량 생성을 시도합니다."""

        if len(self.opponent_cars) >= settings.OPPONENT_CAR_MAX_COUNT:
            return

        driven_distance = self.last_spawn_player_world_y - self.farthest_player_world_y
        if driven_distance < self.next_spawn_interval_distance:
            return

        self.spawn_car_ahead(player_world_y)
        self.last_spawn_player_world_y = self.farthest_player_world_y
        self.next_spawn_interval_distance = self.get_next_spawn_interval_distance()

    def spawn_car_ahead(self, player_world_y):
        """플레이어가 볼 수 없는 앞쪽 위치에 새 상대 차량을 생성합니다."""

        for _ in range(settings.OPPONENT_CAR_SPAWN_MAX_ATTEMPTS):
            lane_index = random.randrange(settings.TOTAL_LANE_COUNT)
            spawn_distance = random.randint(
                settings.OPPONENT_CAR_MIN_SPAWN_AHEAD_DISTANCE,
                settings.OPPONENT_CAR_MAX_SPAWN_AHEAD_DISTANCE,
            )
            world_y = player_world_y - spawn_distance

            if not self.is_safe_spawn_position(lane_index, world_y, player_world_y):
                continue

            move_direction, speed = self.get_lane_movement(lane_index)
            self.opponent_cars.append(
                OpponentCar(lane_index, world_y, move_direction, speed)
            )
            return

    def is_safe_spawn_position(self, lane_index, world_y, player_world_y):
        """새 차량이 기존 차량과 플레이어 주변을 침범하지 않는지 확인합니다."""

        if abs(world_y - player_world_y) < settings.OPPONENT_CAR_PLAYER_SAFE_SPAWN_GAP:
            return False

        for opponent_car in self.opponent_cars:
            if opponent_car.lane_index != lane_index:
                continue
            if abs(opponent_car.world_y - world_y) < settings.OPPONENT_CAR_SAFE_SPAWN_GAP:
                return False

        return True

    def remove_far_cars(self, player_world_y):
        """플레이어 기준으로 충분히 멀어진 상대 차량을 목록에서 제거합니다."""

        self.opponent_cars = [
            opponent_car
            for opponent_car in self.opponent_cars
            if abs(opponent_car.world_y - player_world_y)
            <= settings.OPPONENT_CAR_DELETE_DISTANCE
        ]

    def get_lane_movement(self, lane_index):
        """차선 방향에 맞는 이동 방향과 속도를 돌려줍니다."""

        if lane_index in settings.RIGHT_DIRECTION_LANE_INDICES:
            return (
                settings.OPPONENT_CAR_FORWARD_DIRECTION,
                settings.OPPONENT_CAR_SAME_DIRECTION_SPEED,
            )

        return (
            settings.OPPONENT_CAR_REVERSE_DIRECTION,
            settings.OPPONENT_CAR_OPPOSITE_DIRECTION_SPEED,
        )

    def get_next_spawn_interval_distance(self):
        """다음 생성 시도까지 필요한 전진 거리를 무작위로 정합니다."""

        return random.randint(
            settings.OPPONENT_CAR_MIN_SPAWN_INTERVAL_DISTANCE,
            settings.OPPONENT_CAR_MAX_SPAWN_INTERVAL_DISTANCE,
        )

    def get_player_world_y(self, my_car, road_scroll_y):
        """플레이어 차량의 화면 Y좌표를 월드 Y좌표로 변환합니다."""

        return my_car.y - road_scroll_y

    def draw(self, screen, road_scroll_y):
        """모든 상대 차량을 현재 카메라 스크롤에 맞춰 그립니다."""

        for opponent_car in self.opponent_cars:
            opponent_car.draw(screen, road_scroll_y)

    def get_cars(self):
        """센서와 충돌 방지 로직에서 사용할 상대 차량 목록을 돌려줍니다."""

        return self.opponent_cars
