import settings
from car.my_car import draw_car_shape


class OpponentCar:
    """차선을 따라 일정한 속도로 자동 이동하는 상대 차량입니다."""

    def __init__(self, lane_index, world_y, move_direction, speed):
        self.lane_index = lane_index
        self.width = settings.CAR_WIDTH
        self.height = settings.CAR_HEIGHT
        self.x = settings.LANE_CENTER_X_LIST[lane_index] - (self.width // 2)
        self.world_y = world_y
        self.move_direction = move_direction
        self.speed = speed

    def update(self, delta_time):
        """월드 좌표 기준으로 차선을 따라 이동합니다."""

        self.world_y += self.move_direction * self.speed * delta_time

    def get_screen_y(self, road_scroll_y):
        """도로 스크롤 값을 반영하여 화면에 그릴 Y좌표를 계산합니다."""

        return self.world_y + road_scroll_y

    def draw(self, screen, road_scroll_y):
        """플레이어 차량과 구분되는 색상으로 상대 차량을 그립니다."""

        screen_y = self.get_screen_y(road_scroll_y)
        draw_car_shape(
            screen,
            self.x,
            screen_y,
            settings.OPPONENT_CAR_BODY,
            settings.OPPONENT_CAR_DETAIL,
        )
