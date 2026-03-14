"""
Скрипт обработки изображений для HyperCar:
- Убирает фон (делает прозрачным)
- Поворачивает стрелку ускорения вверх
- Сохраняет всё в PNG с прозрачностью
"""

import os
from PIL import Image
import numpy as np

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")


def remove_background(img: Image.Image, threshold: int = 40) -> Image.Image:
    """
    Убирает тёмный/однородный фон, делая его прозрачным.
    threshold — насколько пиксель должен быть близок к фону чтобы стать прозрачным.
    """
    img = img.convert("RGBA")
    data = np.array(img)

    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    # Определяем цвет фона по угловым пикселям (среднее)
    corners = [
        data[0, 0, :3],
        data[0, -1, :3],
        data[-1, 0, :3],
        data[-1, -1, :3],
    ]
    bg_color = np.mean(corners, axis=0).astype(int)

    # Маска: пиксели близкие к фону → прозрачные
    diff = np.abs(data[:, :, :3].astype(int) - bg_color)
    mask = np.all(diff < threshold, axis=2)

    data[:, :, 3] = np.where(mask, 0, 255)

    return Image.fromarray(data)


def process_all():
    files = {
        "Щит(Бафф).jpg":                              ("shield.png",        False, 0),
        "Доп.Жизнь(бафф).jpg":                        ("extra_life.png",    False, 0),
        "замедление(бафф).png":                        ("slow_down.png",     False, 0),
        "2х монеты(бафф).avif":                        ("double_coins.png",  False, 0),
        "Урезанные награды(0.5х монеты, дебафф).png":  ("less_coins.png",    False, 0),
        "Ускорение(дебафф).jpg":                       ("speed_up.png",      False, -90),  # поворот вверх
    }

    for src_name, (dst_name, _, rotate_angle) in files.items():
        src_path = os.path.join(IMAGES_DIR, src_name)
        dst_path = os.path.join(IMAGES_DIR, dst_name)

        if not os.path.exists(src_path):
            print(f"[ПРОПУСК] Файл не найден: {src_name}")
            continue

        print(f"[ОБРАБОТКА] {src_name} → {dst_name}")
        img = Image.open(src_path)

        # Поворот (если нужен)
        if rotate_angle != 0:
            img = img.rotate(rotate_angle, expand=True)
            print(f"  Повёрнуто на {rotate_angle}°")

        # Убираем фон
        img = remove_background(img, threshold=50)
        print(f"  Фон убран")

        img.save(dst_path, "PNG")
        print(f"  Сохранено: {dst_name}")

    print("\nГотово! Все изображения обработаны.")


if __name__ == "__main__":
    process_all()
