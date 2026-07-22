import pygame

import settings


class RoadDrawer:
    """도로 배경, 중앙선, 차선 표시를 그립니다."""

    def draw(self, screen, road_scroll_y):
        """화면 중앙에 세로 도로와 차선을 그립니다."""

        road_rectangle = pygame.Rect(
            settings.LEFT_ROAD_EDGE_X,
            0,
            settings.ROAD_WIDTH,
            settings.SCREEN_HEIGHT,
        )
        pygame.draw.rect(screen, settings.GRAY_ROAD, road_rectangle)

        pygame.draw.line(
            screen,
            settings.WHITE_ROAD_EDGE,
            (settings.LEFT_ROAD_EDGE_X, 0),
            (settings.LEFT_ROAD_EDGE_X, settings.SCREEN_HEIGHT),
            settings.ROAD_EDGE_LINE_WIDTH,
        )
        pygame.draw.line(
            screen,
            settings.WHITE_ROAD_EDGE,
            (settings.RIGHT_ROAD_EDGE_X, 0),
            (settings.RIGHT_ROAD_EDGE_X, settings.SCREEN_HEIGHT),
            settings.ROAD_EDGE_LINE_WIDTH,
        )

        for separator_index in range(1, settings.TOTAL_LANE_COUNT):
            separator_line_x = settings.LEFT_ROAD_EDGE_X + (
                settings.LANE_WIDTH * separator_index
            )

            if separator_line_x == settings.CENTER_DIVIDER_LINE_X:
                self.draw_dashed_vertical_line(
                    screen,
                    settings.YELLOW_CENTER_LINE,
                    separator_line_x,
                    road_scroll_y,
                    settings.CENTER_LINE_WIDTH,
                )
            else:
                self.draw_dashed_vertical_line(
                    screen,
                    settings.WHITE_ROAD_EDGE,
                    separator_line_x,
                    road_scroll_y,
                    settings.LANE_SEPARATOR_LINE_WIDTH,
                )

    def draw_dashed_vertical_line(self, screen, color, line_x, road_scroll_y, line_width):
        """카메라 스크롤에 맞춰 세로 점선을 자연스럽게 이어 그립니다."""

        lane_cycle = settings.LANE_DASH_LENGTH + settings.LANE_DASH_GAP
        lane_start_y = (road_scroll_y % lane_cycle) - lane_cycle

        while lane_start_y < settings.SCREEN_HEIGHT:
            lane_end_y = lane_start_y + settings.LANE_DASH_LENGTH
            pygame.draw.line(
                screen,
                color,
                (line_x, lane_start_y),
                (line_x, lane_end_y),
                line_width,
            )
            lane_start_y += lane_cycle
