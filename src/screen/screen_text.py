import settings


class ScreenText:
    """게임 화면 위에 거리와 경고 글자를 표시합니다."""

    def __init__(self, font):
        self.font = font

    def draw_distance_text(self, screen, front_distance):
        """거리 감지 결과를 화면 왼쪽 위에 표시합니다."""

        if isinstance(front_distance, dict):
            self.draw_sensor_distance_text(screen, front_distance)
            return

        if front_distance is None:
            distance_text = "Distance: No obstacle"
        elif front_distance <= settings.STOP_DISTANCE:
            distance_text = f"Distance: {front_distance} px - STOP"
        else:
            distance_text = f"Distance: {front_distance} px"

        text_image = self.font.render(distance_text, True, settings.WHITE_TEXT)
        screen.blit(text_image, (20, 20))

    def draw_sensor_distance_text(self, screen, sensor_states):
        """4방향 센서 감지 결과를 줄 단위로 표시합니다."""

        direction_labels = (
            ("front", "FRONT"),
            ("left", "LEFT"),
            ("right", "RIGHT"),
            ("rear", "REAR"),
        )
        line_y = 20

        for direction, label in direction_labels:
            sensor_state = sensor_states[direction]
            if sensor_state.nearest_distance is None:
                distance_text = f"{label}: No obstacle"
            elif direction == "front" and sensor_state.nearest_distance <= settings.STOP_DISTANCE:
                distance_text = f"{label}: {sensor_state.nearest_distance} px - STOP"
            else:
                distance_text = f"{label}: {sensor_state.nearest_distance} px"

            text_image = self.font.render(distance_text, True, settings.WHITE_TEXT)
            screen.blit(text_image, (20, line_y))
            line_y += text_image.get_height() + 4
