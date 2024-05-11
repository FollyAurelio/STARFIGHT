# Fenêtre qui programme les items
import pygame
import time
from Settings import *


class Item(pygame.sprite.Sprite):
    def __init__(self, pos, group, id, effect):
        super().__init__(group)
        self.id = id
        self.effect = [
            "invincible",
            "sword",
            "bow",
            "bomb",
            "freeze",
            "lightning",
            "speedup",
            "slowdown",
        ][effect]
        self.image = [
            cut_image(Useful_Item_sprites, 16, 16, 48, 36, 50, 50),
            cut_image(Useful_Item_sprites, 16, 16, 46, 35, 50, 50),
            cut_image(Useful_Item_sprites, 16, 16, 46, 37, 50, 50),
            cut_image(Useful_Item_sprites, 16, 16, 53, 35, 50, 50),
            cut_image(Ice_cream, 64, 64, 0, 0, 50, 50),
            cut_image(Lightning_icon, 64, 64, 0, 0, 50, 50),
            cut_image(Useful_Item_sprites, 16, 15, 36, 14, 50, 50),
            cut_image(Useful_Item_sprites, 16, 15, 36, 16, 50, 50),
        ][effect]

        self.rect = self.image.get_rect(center=pos)
        # Initialise le type d'item aléatoire

    def effect_apply(self, player):
        if self.effect == "speedup":
            if player.speed < 11:
                player.speed += 1
                if player.speed > 4:
                    player.bonus_item.append(Hud_Item(player.speed, "speedup"))
                else:
                    player.player.bonus_item.pop()
        if self.effect == "slowdown":
            if player.speed > 1:
                player.speed -= 1
                if player.speed <= 4:
                    player.bonus_item.append(Hud_Item(player.speed, "slowdown"))
                else:
                    player.player.bonus_item.pop()
        else:
            player.give(self.effect)
        # L'effet que l'item a quand il est ramassé

    def update(self):
        pass


class Star(pygame.sprite.Sprite):
    def __init__(self, pos, group, origin, id):
        super().__init__(group)
        self.id = id
        self.origin = origin
        self.effect = "star"
        self.prev_time = time.time()
        self.direction = pygame.math.Vector2(-1, -1)
        self.frame = 0
        self.action = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_list = create_animation(
            Useful_Item_sprites, [7], 16, 16, 4, 12, 30, 30
        ) + [create_animation(Useful_Item_sprites, [6], 16, 16, 12, 12, 30, 30)[0]]
        self.image = self.animation_list[self.action][self.frame]
        self.rect = self.image.get_rect(center=pos)

        # Crée des stars

    def effect_apply(self, player):
        player.star_count += 1

        # Augmente le nombre de stars quand on en ramasse

    def update(self):
        animation_cooldown = 100
        self.last_update, self.frame = animate(
            self.animation_list,
            animation_cooldown,
            self.last_update,
            self.action,
            self.frame,
        )
        if self.action == 0 and self.frame == 6:
            self.action = 1
            self.frame = 0
        if self.action == 1 and self.frame == 5:
            self.action = 0
            self.frame = 0
        self.image = self.animation_list[self.action][self.frame]


class Weapon(pygame.sprite.Sprite):
    def __init__(self, type, group, id):
        super().__init__(group)
        self.id = id
        self.type = type
        if self.type == "sword":
            self.image = cut_image(Useful_Item_sprites, 16, 16, 46, 35, 50, 50)
        if self.type == "bow":
            self.image = cut_image(Useful_Item_sprites, 16, 16, 46, 37, 50, 50)

        self.rect = self.image.get_rect()
        self.bow_cooldown = pygame.time.get_ticks()
        self.direction = pygame.math.Vector2(1, 0)
        if self.type == "sword":
            self.orientation = "top"
        else:
            self.orientation = "right"
        self.orignal_image = self.image

    def use_weapon(self, player):
        diagonal = 0.7071067811865476
        if player.direction == (1, 0):
            self.reorientate("right")
            self.rect.left = player.rect.right
            self.rect.centery = player.rect.centery
            self.direction = pygame.math.Vector2((1, 0))
        if player.direction == (-1, 0):
            self.reorientate("left")
            self.rect.right = player.rect.left
            self.rect.centery = player.rect.centery
            self.direction = pygame.math.Vector2((-1, 0))
        if player.direction == (0, 1):
            self.reorientate("bottom")
            self.rect.top = player.rect.bottom
            self.rect.centerx = player.rect.centerx
            self.direction = pygame.math.Vector2((0, 1))
        if player.direction == (0, -1):
            self.reorientate("top")
            self.rect.bottom = player.rect.top
            self.rect.centerx = player.rect.centerx
            self.direction = pygame.math.Vector2((0, -1))
        if player.direction == (diagonal, diagonal):  # bottomright
            self.reorientate("bottomright")
            self.rect.topleft = player.rect.bottomright
            self.direction = pygame.math.Vector2((1, 1))
        if player.direction == (-diagonal, diagonal):  # bottomleft
            self.reorientate("bottomleft")
            self.rect.topright = player.rect.bottomleft
            self.direction = pygame.math.Vector2((-1, 1))
        if player.direction == (diagonal, -diagonal):  # topright
            self.reorientate("topright")
            self.rect.bottomleft = player.rect.topright
            self.direction = pygame.math.Vector2((1, -1))
        if player.direction == (-diagonal, -diagonal):  # topleft
            self.reorientate("topleft")
            self.rect.bottomright = player.rect.topleft
            self.direction = pygame.math.Vector2((-1, -1))

    def reorientate(self, new_direction):
        if self.type == "sword":
            directions = [
                "top",
                "topleft",
                "left",
                "bottomleft",
                "bottom",
                "bottomright",
                "right",
                "topright",
            ]
        else:
            directions = [
                "right",
                "topright",
                "top",
                "topleft",
                "left",
                "bottomleft",
                "bottom",
                "bottomright",
            ]
        coef = 45 * directions.index(new_direction)
        self.orientation = new_direction
        self.image = self.orignal_image
        self.image = pygame.transform.rotate(self.image, coef)

    def shoot_arrow(self, player, map):
        cooldown = 300
        if self.type == "bow":
            current_time = pygame.time.get_ticks()
            if current_time - self.bow_cooldown >= cooldown:
                self.bow_cooldown = current_time
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    Arrow(self, (map.visible_sprites, map.arrow_sprites), player.id)
                    player.bowask = True

    def __repr__(self):
        return self.type


class Arrow(pygame.sprite.Sprite):
    def __init__(self, bow, group, id):
        super().__init__(group)
        self.id = id
        self.image = cut_image(Useful_Item_sprites, 16, 16, 47, 37, 30, 30)
        self.rect = self.image.get_rect(center=bow.rect.center)
        self.direction = bow.direction
        if self.direction.magnitude() != 0:
            self.direction.normalize()
        self.speed = 6
        self.time = pygame.time.get_ticks()
        directions = [
            "top",
            "topleft",
            "left",
            "bottomleft",
            "bottom",
            "bottomright",
            "right",
            "topright",
        ]
        coef = 45 * directions.index(bow.orientation)
        self.image = pygame.transform.rotate(self.image, coef)

    def update(self, map):
        cooldown = 10000
        current_time = pygame.time.get_ticks()
        if current_time - self.time >= cooldown:
            self.kill()
        for sprite in map.obsticle_sprites:
            if sprite.rect.colliderect(self.rect):
                self.kill()
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed


class Spell:
    def __init__(self, type):
        self.type = type

    def cast(self, player, map):
        if self.type == "bomb":
            Bomb(
                player,
                (map.visible_sprites, map.bomb_sprites),
                player.id,
            )
        if self.type == "invincible":
            player.invincibilty_power = True
        if self.type == "freeze":
            Freeze(player, (map.visible_sprites, map.freeze_sprites), player.id)
        if self.type == "lightning":
            Flash(
                player,
                (map.visible_sprites, map.flash_sprites),
                500,
                "lightning",
                player.id,
            )

    def __repr__(self):
        return self.type


class Bomb(pygame.sprite.Sprite):
    def __init__(self, player, group, id, invisible=None):
        super().__init__(group)
        self.id = id
        self.image = cut_image(Useful_Item_sprites, 16, 16, 53, 35, 50, 50)
        self.rect = self.image.get_rect(center=player.rect.center)
        if invisible:
            self.image.set_alpha(0)

    def detonate(self, map):
        for enemy in map.enemy_sprites:
            if enemy.rect.colliderect(self.rect):
                Flash(
                    self,
                    (map.visible_sprites, map.flash_sprites),
                    200,
                    "explosion",
                    self.id,
                )
                self.kill()
        for player in map.other_player_sprites:
            if player.rect.colliderect(self.rect):
                if player.id != self.id:
                    Flash(
                        self,
                        (map.visible_sprites, map.flash_sprites),
                        200,
                        "explosion",
                        self.id,
                    )
                    self.kill()


class Flash(pygame.sprite.Sprite):
    def __init__(self, pos, group, size, type, id):
        super().__init__(group)
        self.id = id
        self.type = type
        if type == "explosion":
            self.frame = 0
            self.last_update = pygame.time.get_ticks()
            self.animation_list = create_animation(
                Bomb_explosion, [8], 48, 48, 0, 0, size, size
            )
            self.image = self.animation_list[0][self.frame]
        if type == "lightning":
            self.image = pygame.Surface((size, size))
            self.image.set_alpha(0)
        self.rect = self.image.get_rect(center=pos.rect.center)
        self.timer = pygame.time.get_ticks()

    def flash(self):
        if self.type == "explosion":
            cooldown = 100
            attack_time = 800
            self.last_update, self.frame = animate(
                self.animation_list, cooldown, self.last_update, 0, self.frame
            )
            self.image = self.animation_list[0][self.frame]
        if self.type == "lightning":
            attack_time = 10
        current_time = pygame.time.get_ticks()
        if current_time - self.timer >= attack_time:
            self.kill()


class Freeze(pygame.sprite.Sprite):
    def __init__(self, player, group, id):
        super().__init__(group)
        self.id = id
        self.image = pygame.Surface((250, 250))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect(center=player.rect.center)

        self.timer = pygame.time.get_ticks()

    def freeze(self):
        attack_time = 800
        current_time = pygame.time.get_ticks()
        if current_time - self.timer >= attack_time:
            self.kill()
