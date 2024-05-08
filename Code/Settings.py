import pygame

pygame.init()
pygame.font.init()

Placeholder_map = "Map1"


def cut_image(image, width, height, index_x, index_y, sizex, sizey):
    coupure = pygame.Surface((width, height))
    coupure.set_colorkey((0, 0, 0))
    coupure.blit(image, (0, 0), (width * index_x, height * index_y, width, height))
    coupure = pygame.transform.scale(coupure, (sizex, sizey))
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
    spritesheet, animation_length, width, height, index_x, index_y, sizex, sizey
):
    animation_list = []
    steps = index_x
    for ani in animation_length:
        temp = []
        for i in range(ani):
            cut = cut_image(spritesheet, width, height, steps, index_y, sizex, sizey)
            temp.append(cut)
            steps += 1
        animation_list.append(temp)
    return animation_list


Star_background = pygame.image.load("Sprites/Enjl-Starry Space Background/preview.png")
Useful_Item_sprites = pygame.image.load(
    "Sprites/coins-chests-etc-2-0.png"
).convert_alpha()
Weapons_sprites = pygame.image.load(
    "Sprites/Medieval weapons pack v1.2/Medieval weapons pack/steel/outline x4.png"
).convert_alpha()
Ice = pygame.image.load(
    "Sprites/Ice Effect 01/Ice Effect 01/Ice VFX 2/Ice VFX 2 Active.png"
).convert_alpha()
Light = pygame.image.load(
    "Sprites/Thunder Effect 02/Thunder Effect 02/Thunder Strike/Thunderstrike wo blur.png"
).convert_alpha()
Lightning_icon = pygame.image.load(
    "Sprites/download-icon-lightning-131982518827228370_64.png"
)
Ice_animation = create_animation(Ice, [8], 32, 32, 0, 0, 50, 50)
Lightning_animation = create_animation(Light, [12], 75, 64, 0, 0, 100, 100)
Ice_cream = pygame.image.load("Sprites/download-icon-cream-131982518805283723_64.png")
Bomb_explosion = pygame.image.load(
    "Sprites/explosions-pack-web/explosions-pack-web/spritesheets/explosion-6.png"
)
Block_text = pygame.font.Font("Sprites/kenney_kenney-fonts/Fonts/Kenney Blocks.ttf", 60)


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, group, type):
        super().__init__(group)
        self.frame = 0
        self.type = type
        self.last_update = pygame.time.get_ticks()
        if type == "freeze":
            self.animation_list = Ice_animation
        if type == "lightning":
            self.animation_list = Lightning_animation
        self.image = self.animation_list[0][self.frame]
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        cooldown = 100
        self.last_update, self.frame = animate(
            self.animation_list, cooldown, self.last_update, 0, self.frame
        )
        self.image = self.animation_list[0][self.frame]
        if (self.frame == 7 and self.type == "freeze") or (
            self.frame == 11 and self.type == "lightning"
        ):
            self.kill()
