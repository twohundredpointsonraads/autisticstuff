"""Model with basic utils for building progress bars"""

from math import atan2, pi

def draw_circle(
    size: int = 10,
    percentage: int = 50,
    filled_char: str = "█",
    empty_char: str = "░",
    title: str = None,
):
    """
    Draw a circle with given size and percentage.
    :param size: Size of circle.
    :param percentage: Percentage of circle.
    :param filled_char: Character used to fill circle.
    :param empty_char: Character used to fill circle.
    :param title: Text displays under circle or on it
    """
    result = []
    center = size // 2
    radius = size // 2 - 1

    # Подготовка текста для центрирования
    title_lines = []
    if title:
        # Разбиваем текст на строки, каждая строка помещается в центр
        text_width = max(1, int(radius))
        words = title.split()
        current_line = ""

        for word in words:
            if len(current_line + " " + word) <= text_width:
                current_line += ("  " if current_line else "") + word
            else:
                if current_line:
                    title_lines.append(current_line)
                current_line = word
        if current_line:
            title_lines.append(current_line)

    # Вычисляем начальную y-позицию для центрирования текста по вертикали
    text_start_y = center - len(title_lines) // 2

    for y in range(int(size)):
        line = ""
        for x in range(size):
            distance = ((x - center) ** 2 + (y - center) ** 2) ** 0.5
            angle = ((180 / pi) * (pi + atan2(y - center, x - center))) % 360

            # Проверяем, находимся ли мы в центральной области
            is_text_area = distance < radius / 1.3

            # Определяем, какой символ должен быть в этой позиции
            char_to_add = " "

            if is_text_area and title:
                # Вычисляем индекс строки текста для текущей y-позиции
                text_line_index = y - text_start_y

                if 0 <= text_line_index < len(title_lines):
                    current_text_line = title_lines[text_line_index]
                    # Центрируем текст по горизонтали с более точным расчетом
                    text_start_x = center - (len(current_text_line) + 1) // 2
                    char_index = x - text_start_x

                    if 0 <= char_index < len(current_text_line):
                        char_to_add = current_text_line[char_index]
            if is_text_area:
                # Для текста добавляем символ один раз и пробел для растяжения
                line +=  char_to_add + " "
            else:
                # Для графики добавляем символ дважды для растяжения
                for _ in range(2):
                    if distance <= radius:
                        fill_angle = (percentage / 100) * 360
                        if angle <= fill_angle:
                            line += filled_char
                        else:
                            line += empty_char
                    else:
                        line += " "

        result.append(line)

    return "\n".join(result)
