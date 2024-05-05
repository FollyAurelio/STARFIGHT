"""Fenêtre qui programme le joueur"""

import pygame
import Items
import Levels
import random
import time
from Settings import *

pygame.init()
Text = pygame.font.SysFont("Arial", 20)

# Spritesheet des dinosaurs.
Dinos = [
    "Sprites/DinoSprites - doux.png",
    "Sprites/DinoSprites - mort.png",
    "Sprites/DinoSprites - tard.png",
    "Sprites/DinoSprites - vita.png",
]


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, id, name):
        super().__init__(group)
        self.id = id
        self.name = name
        # self.nametag = Nametag(self)

        self.star_lost = False
        self.star_count = 0

        self.hp = 3
        self.healthbar = (Heart(0), Heart(1), Heart(2))
        self.heartframe = 0
        self.heartspin = [pygame.time.get_ticks(), pygame.time.get_ticks()]

        self.death_timer = pygame.time.get_ticks()
        self.appear = False

        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 4
        self.facing = "right"
        self.prev_time = time.time()

        self.flyback_mesure = pygame.time.get_ticks()
        self.taking_knockback = False
        self.knockback_direction = pygame.math.Vector2()

        self.took_damage = False
        self.invincibilty = False
        self.invincibilty_power = False
        self.invincibilty_power_mesure = pygame.time.get_ticks()
        self.invincibilty_mesure = pygame.time.get_ticks()

        self.frozen = False
        self.frozen_mesure = pygame.time.get_ticks()

        self.items_list = [
            Items.Weapon("sword", (Levels.map.weapon_sprites), self.id),
            Items.Weapon("sword", (Levels.map.weapon_sprites), self.id),
            Items.Weapon("sword", (Levels.map.weapon_sprites), self.id),
        ]
        self.using_item = False
        self.item_timer = pygame.time.get_ticks()
        self.inusage = None
        self.weaponask = False
        self.bowask = False

        self.spritesheet = pygame.image.load(Dinos[self.id]).convert_alpha()
        self.frame = 0
        self.action = 0
        self.last_update = pygame.time.get_ticks()

        animation_length = [4, 6, 3, 4]
        self.animation_list = create_animation(
            self.spritesheet, animation_length, 24, 24, 0, 0, 45
        )

        self.kill_list = []
        self.image = self.animation_list[self.action][self.frame]
        self.rect = self.image.get_rect(center=pos)

    # Réuni tous les methodes du joueurs ainsi que gérer ses animations
    def update(self):
        animation_cooldown = 100
        heart_cooldown = 100
        spin_cooldown = 2000
        current_time = pygame.time.get_ticks()
        self.last_update, self.frame = animate(
            self.animation_list,
            animation_cooldown,
            self.last_update,
            self.action,
            self.frame,
        )
        if current_time - self.heartspin[1] >= spin_cooldown:
            self.heartspin[0], self.heartframe = animate(
                [["1", "2", "3", "4", "5", "6"]],
                heart_cooldown,
                self.heartspin[0],
                0,
                self.heartframe,
            )
            if self.heartframe == 0:
                self.heartspin[1] = current_time
        if self.hp > 0:
            self.Damage_Check()
            self.knockback()
            self.invincible_tick()
            self.freeze_tick()
            self.invincibilty_powerup()
            self.use_item()
            self.show_item()
            self.pickup()
            self.mouvement()
            self.flicker()
            self.image = self.animation_list[self.action][self.frame]
            # self.nametag.rect.topleft = self.rect.bottomright
        self.dead()

    # On applique une animation de dégat quand le joueur est invincible.
    def flicker(self):
        if self.invincibilty:
            self.action = 3

    # Gère le mouvement et l'état de ses animations en fonction du mouvement.
    # Le joueur peut bouger dans les 8 huits directions.
    # On applique un animation de marche quand il bouge.
    def mouvement(self):
        keys = pygame.key.get_pressed()
        if not self.frozen and not self.taking_knockback:
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.action = 1
                if self.facing == "left":
                    self.turn()
                    self.facing = "right"
            elif keys[pygame.K_q]:
                self.direction.x = -1
                self.action = 1
                if self.facing == "right":
                    self.turn()
                    self.facing = "left"
            else:
                self.direction.x = 0
            if keys[pygame.K_z]:
                self.direction.y = -1
                self.action = 1
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.action = 1
            else:
                self.direction.y = 0
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()
            now = time.time()
            dt = now - self.prev_time
            self.rect.x += self.direction.x * self.speed * dt * 60
            self.check_collision("horizontal")
            self.rect.y += self.direction.y * self.speed * dt * 60
            self.prev_time = now
            self.check_collision("vertical")

    # Gère les collisions avec les murs, le joueur ne peut pas franchir un mur.
    def check_collision(self, direction):
        if direction == "horizontal":
            for sprite in Levels.map.obsticle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right

        if direction == "vertical":
            for sprite in Levels.map.obsticle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top

    # Gère le ramassement des items et des étoiles.
    # On le tue l'item et on le met dans kill list pour qu'il puisse être tuer pour les autres joueurs.
    # On applique aussi son effet
    def pickup(self):
        if not self.invincibilty:
            for sprite in Levels.map.pickup_sprites:
                if sprite.rect.colliderect(self.rect):
                    sprite.effect_apply(self)
                    if sprite.effect == "star":
                        self.kill_list.append(sprite.id)
                    else:
                        self.kill_list.append(sprite.id)
                    sprite.kill()

    # met l'item dans item_list
    # Le nombre d'item ne peut pas dépasser 3
    # Si le list est remplie, les items déjà dans le list ne sont pas remplacés.
    def give(self, effect):
        for item in range(len(self.items_list)):
            if not self.items_list[item]:
                if effect == "sword" or effect == "spear" or effect == "axe":
                    self.items_list[item] = Items.Weapon(
                        effect, (Levels.map.weapon_sprites), self.id
                    )
                    break
                if effect == "bow":
                    self.items_list[item] = Items.Weapon(
                        effect, (Levels.map.bow_sprites), self.id
                    )
                    break
                if (
                    effect == "bomb"
                    or effect == "invincible"
                    or effect == "freeze"
                    or effect == "lightning"
                ):
                    self.items_list[item] = Items.Spell(effect)
                    break

    # Applique les changement correspondants lorsque le joueur prend des dégats:
    # On perd un hp, on devient invincible et on perd un étoile si on à un.
    # On prend aussi de la knockback, la direction de ceci étant en fonction de la source des dégats.
    def Ouch(self, dealer=None):
        if not self.invincibilty and not self.invincibilty_power:
            self.invincibilty = True
            self.took_damage = True
            self.hp -= 1
            if dealer:
                if dealer in Levels.map.enemy_sprites:
                    self.taking_knockback = True
                    if self.direction == (0, 0):
                        self.knockback_direction = dealer.direction
                    else:
                        self.knockback_direction = -self.direction
                if (
                    dealer in Levels.map.weapon_sprites
                    or dealer in Levels.map.arrow_sprites
                ):
                    self.taking_knockback, self.knockback_direction = (
                        True,
                        dealer.direction,
                    )
            if self.star_count > 0:
                self.star_count -= 1
                self.star_lost = True
                Levels.Star(
                    self.rect.center,
                    (
                        Levels.map.visible_sprites,
                        Levels.map.pickup_sprites,
                        Levels.map.star_sprites,
                    ),
                    "player",
                    0,
                )
            if not self.invincibilty_power:
                if self.frame > 3:
                    self.frame = 0
                self.action = 3

    # Vérifie si on à rentré en collision avec un source de dégats.
    # Si c'est un gèle, on devient gelé.
    def Damage_Check(self):
        for sprite in Levels.map.enemy_sprites:
            if sprite.rect.colliderect(self.rect):
                self.Ouch(sprite)
        for sprite in Levels.map.weapon_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id != self.id:
                    self.Ouch(sprite)
        for sprite in Levels.map.arrow_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id != self.id:
                    self.Ouch(sprite)
        for sprite in Levels.map.flash_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id != self.id:
                    self.Ouch()
        for sprite in Levels.map.bomb_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id != self.id:
                    Items.Flash(
                        sprite,
                        (Levels.map.visible_sprites, Levels.map.flash_sprites),
                        200,
                        sprite.id,
                    )
                    sprite.kill()
        for sprite in Levels.map.freeze_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id != self.id:
                    self.frozen = True

    # On prend de la knockback quand il est appelé pendant un certain temps.
    # On ne peut pas bouger quand on prend de la knockback.
    def knockback(self):
        current_time = pygame.time.get_ticks()
        duration = 50
        if self.taking_knockback:
            self.speed = 10
            self.direction = self.knockback_direction
            now = time.time()
            dt = now - self.prev_time
            self.rect.x += self.direction.x * self.speed * dt * 60
            self.check_collision("horizontal")
            self.rect.y += self.direction.y * self.speed * dt * 60
            self.prev_time = now
            self.check_collision("vertical")
            if current_time - self.flyback_mesure >= duration:
                self.taking_knockback = False
        else:
            self.flyback_mesure = pygame.time.get_ticks()
            self.speed = 4

    # Compte le temps pendant lequel on est invincible
    def invincible_tick(self):
        if self.invincibilty:
            invincibilty_frames = 1000
            current_time = pygame.time.get_ticks()
            if current_time - self.invincibilty_mesure >= invincibilty_frames:
                self.invincibilty = False
                self.invincibilty_mesure = current_time
                self.action = 0
                self.frame = 0
        else:
            self.invincibilty_mesure = pygame.time.get_ticks()

    # Compte le temps pendant lequel on est gelé
    def freeze_tick(self):
        if self.frozen:
            frozen_frames = 10000
            current_time = pygame.time.get_ticks()
            if current_time - self.frozen_mesure >= frozen_frames:
                self.frozen = False
                self.frozen_mesure = current_time
        else:
            self.frozen_mesure = pygame.time.get_ticks()

    # Permet d'utiliser les items, quand le bouton correspondant est appuié.
    def use_item(self):
        keys = pygame.key.get_pressed()
        keyboard = [keys[pygame.K_j], keys[pygame.K_k], keys[pygame.K_l]]
        if not self.using_item:
            for i in range(len(keyboard)):
                if keyboard[i]:
                    if self.items_list[i]:
                        if (
                            self.items_list[i].type == "sword"
                            or self.items_list[i].type == "spear"
                            or self.items_list[i].type == "axe"
                            or self.items_list[i].type == "bow"
                        ):
                            self.items_list[i].add(Levels.map.visible_sprites)
                            self.weaponask = self.items_list[i].type
                            self.inusage = self.items_list[i].type
                            self.using_item = i + 1
                        else:
                            self.items_list[i].cast(self, Levels.map)
                            self.weaponask = self.items_list[i].type
                            self.inusage = self.items_list[i].type
                            self.items_list[i] = ""

    # Montre l'item quand il est utilisé.
    # Si il s'agit d'un bow, on peut envoyer des arrows avec la touche espace.
    # Les items permettent de faire des dégats aux autres joueurs.
    def show_item(self):
        cooldown = 3000
        if self.using_item:
            current_time = pygame.time.get_ticks()
            self.items_list[self.using_item - 1].use_weapon(self)
            if self.items_list[self.using_item - 1].type == "sword":
                self.speed = 7
            self.items_list[self.using_item - 1].shoot_arrow(self, Levels.map)
            if current_time - self.item_timer >= cooldown:
                self.items_list[self.using_item - 1].kill()
                self.items_list[self.using_item - 1] = ""
                self.using_item = False
                self.inusage = None
                self.speed = 4
                self.item_timer = current_time

        else:
            self.item_timer = pygame.time.get_ticks()

    # Donne de l'invincibilité quand l'item invincible est utilisé
    def invincibilty_powerup(self):
        duration = 6000
        if self.invincibilty_power:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincibilty_power_mesure >= duration:
                self.invincibilty_power = False
                self.invincibilty_power_mesure = current_time
        else:
            self.invincibilty_power_mesure = pygame.time.get_ticks()

    # Change l'animation du joueur quand il se retourne.
    def turn(self):
        for animation in self.animation_list:
            for frame in range(len(animation)):
                animation[frame] = pygame.transform.flip(animation[frame], True, False)

    # Gère la mort. Si l'hp du joueur est<=0 il meurt pendant un temps.
    # Il ne peut pas accèdé aux autres méthodes, et il n'apparait plus sur l'écran.
    # Après que le temps est écoulé, il réaparait à un position random.
    def dead(self):
        death_time = 10000
        death_time_post_tp = 4000
        self.prev_time = time.time()
        current_time = pygame.time.get_ticks()
        if self.hp <= 0:
            self.image.set_alpha(0)
            if self.using_item:
                self.items_list[self.using_item - 1].kill()
                self.using_item = False
                self.speed = 4
                self.item_timer = pygame.time.get_ticks()
            self.inusage = None
            self.items_list = ["", "", ""]
            if current_time - self.death_timer >= death_time:
                if not self.appear:
                    self.rect.center = random.choice(
                        list(Levels.map.respawn_tile_sprites)
                    ).rect.topleft
                    self.appear = True
                if current_time - self.death_timer >= death_time + death_time_post_tp:
                    self.hp = 3
                    self.death_timer = current_time
        else:
            self.death_timer = pygame.time.get_ticks()
            self.appear = False
            self.image.set_alpha(255)


class otherPlayer(pygame.sprite.Sprite):
    def __init__(self, pos, group, id, name):
        super().__init__(group)
        self.id = id
        self.name = name

        self.spritesheet = pygame.image.load(Dinos[self.id]).convert_alpha()
        self.facing = "right"
        self.action = 0
        self.frame = 0
        self.weapon = None
        self.direction = pygame.math.Vector2()

        self.animation_list = []
        animation_length = [4, 6, 3, 4]
        self.animation_list = create_animation(
            self.spritesheet, animation_length, 24, 24, 0, 0, 45
        )

        self.image = self.animation_list[self.action][self.frame]
        self.rect = self.image.get_rect(center=pos)

    def turn(self):
        for animation in self.animation_list:
            for frame in range(len(animation)):
                animation[frame] = pygame.transform.flip(animation[frame], True, False)

    # Fonction qui met à jour l'état des autres joueurs en fonction de l'information reçu par le serveur.
    def update(self, player_information):
        # Le position est mise à jour
        self.rect.center = player_information[self.id]["position"]
        self.direction = player_information[self.id]["direction"]
        # L'animation effectué est donné.
        self.action, self.frame = (
            player_information[self.id]["action_frame"][0],
            player_information[self.id]["action_frame"][1],
        )
        if self.facing != player_information[self.id]["facing"]:
            self.turn()
            self.facing = player_information[self.id]["facing"]
        # Si il demande d'utilisé un arme on lui donne
        if (
            player_information[self.id]["weaponask"] == "sword"
            or player_information[self.id]["weaponask"] == "spear"
            or player_information[self.id]["weaponask"] == "axe"
        ) and not self.weapon:
            self.weapon = Items.Weapon(
                player_information[self.id]["weaponask"],
                (Levels.map.weapon_sprites),
                self.id,
            )
        if (player_information[self.id]["weaponask"] == "bow") and not self.weapon:
            self.weapon = Items.Weapon(
                player_information[self.id]["weaponask"],
                (Levels.map.bow_sprites),
                self.id,
            )
        if player_information[self.id]["weaponask"] == "bomb":
            Items.Bomb(
                self,
                (Levels.map.visible_sprites, Levels.map.bomb_sprites),
                self.id,
                "Invisible",
            )
        if player_information[self.id]["weaponask"] == "freeze":
            Items.Freeze(
                self, (Levels.map.visible_sprites, Levels.map.freeze_sprites), self.id
            )
        if player_information[self.id]["weaponask"] == "lightning":
            Items.Flash(
                self,
                (Levels.map.visible_sprites, Levels.map.flash_sprites),
                500,
                self.id,
            )
        # Si il utilse un arme on lui donne l'arme.
        if player_information[self.id]["inusage"] and self.weapon:
            if self.weapon not in Levels.map.visible_sprites:
                self.weapon.add(Levels.map.visible_sprites)
            self.weapon.use_weapon(self)
            if player_information[self.id]["bowask"]:
                Items.Arrow(
                    self.weapon,
                    (Levels.map.visible_sprites, Levels.map.arrow_sprites),
                    self.id,
                )
        else:
            if self.weapon:
                self.weapon.kill()
                self.weapon = None
        # Pris des dégats
        if (
            player_information[self.id]["took_damage"]
            and player_information[self.id]["invincibilty"]
        ):
            if player_information[self.id]["star_lost"]:
                print("i")
                Items.Star(
                    self.rect.center,
                    (
                        Levels.map.visible_sprites,
                        Levels.map.pickup_sprites,
                        Levels.map.star_sprites,
                    ),
                    "player",
                    0,
                )
        # Si il récupère un étoile on le tue
        for sprite in Levels.map.star_sprites:
            if (
                sprite.origin == "player"
                and sprite.rect.colliderect(self.rect)
                and not player_information[self.id]["invincibilty"]
            ):
                sprite.kill()

        self.image = self.animation_list[self.action][self.frame]
        # Il disparait quand il meurt
        if player_information[self.id]["hp"] <= 0:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)


class Nametag(pygame.sprite.Sprite):
    def __init__(self, player):
        self.image = pygame.Surface((50, 50))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(topleft=player.rect.bottomright)
        l = Text.render(f"{player.name}", False, (0, 0, 0))
        self.image.blit(l, self.rect.center)

    def update(self, player, screen):
        screen.blit(
            Text.render(f"{player.name}", False, (0, 0, 0)), player.nametag.rect.center
        )


class Heart(pygame.sprite.Sprite):
    def __init__(self, heart_id):
        self.animation_list = create_animation(
            Useful_Item_sprites, [6], 16, 16, 25, 14, 30
        )
        self.image = self.animation_list[0][0]
        self.id = heart_id
        self.rect = self.image.get_rect(center=[(0, 30), (30, 30), (60, 30)][heart_id])

    def show_hp(self, player, screen):
        if player.hp >= self.id + 1:
            screen.blit(self.image, self.rect.center)
        self.image = self.animation_list[0][player.heartframe]


# 14,25,6 long
