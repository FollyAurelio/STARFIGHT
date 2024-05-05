import pygame


def cut_image(image, width, height, index_x, index_y, size):
    coupure = pygame.Surface((width, height))
    coupure.set_colorkey((0, 0, 0))
    coupure.blit(image, (0, 0), (width * index_x, height * index_y, width, height))
    coupure = pygame.transform.scale(coupure, (size, size))
    return coupure


def animate(animation_list, animation_cooldown, last_update, action, frame):
    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
        frame += 1
        last_update = current_time
        if frame >= len(animation_list[action]):
            frame = 0
    return last_update, frame


def create_animation(
    spritesheet, animation_length, width, height, index_x, index_y, size
):
    animation_list = []
    steps = index_x
    for ani in animation_length:
        temp = []
        for i in range(ani):
            cut = cut_image(spritesheet, width, height, steps, index_y, size)
            temp.append(cut)
            steps += 1
        animation_list.append(temp)
    return animation_list


Useful_Item_sprites = pygame.image.load(
    "Sprites/coins-chests-etc-2-0.png"
).convert_alpha()
Weapons_sprites = pygame.image.load(
    "Sprites/Medieval weapons pack v1.2/Medieval weapons pack/steel/outline x4.png"
).convert_alpha()
