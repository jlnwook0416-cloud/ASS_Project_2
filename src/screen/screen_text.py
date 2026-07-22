import settings


class ScreenText:
    """게임 화면 위에 거리와 경고 글자를 표시합니다."""

    def __init__(self, font):
        self.font = font

    def draw_distance_text(self, screen, front_distance):
        """거리 감지 결과를 화면 왼쪽 위에 표시합니다."""

        if front_distance is None:
            distance_text = "Distance: No obstacle"
        elif front_distance <= settings.STOP_DISTANCE:
            distance_text = f"Distance: {front_distance} px - STOP"
        else:
            distance_text = f"Distance: {front_distance} px"

        text_image = self.font.render(distance_text, True, settings.WHITE_TEXT)
        screen.blit(text_image, (20, 20))
