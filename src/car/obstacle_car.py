import settings
from car.my_car import draw_car_shape


class ObstacleCar:
    """도로 위에 고정되어 있는 파란색 장애물 자동차입니다."""

    def __init__(self, lane_index, world_y):
        self.lane_index = lane_index
        self.x = settings.LANE_CENTER_X_LIST[lane_index] - (settings.CAR_WIDTH // 2)
        self.world_y = world_y

    def get_screen_y(self, road_scroll_y):
        """도로 스크롤 값을 반영하여 화면에 그릴 Y좌표를 계산합니다."""

        return self.world_y + road_scroll_y

    def draw(self, screen, road_scroll_y):
        """파란색 장애물 자동차를 화면에 그립니다."""

        screen_y = self.get_screen_y(road_scroll_y)
        draw_car_shape(
            screen,
            self.x,
            screen_y,
            settings.BLUE_CAR_BODY,
            settings.DARK_BLUE_CAR_DETAIL,
        )
