"""Fenêtre qui programme le niveau et tous les éléments qu'elle contient"""

import pygame
from Items import Item, Star

# On utilse Pytmx qui est un module qui permet de lire nos fichers type tmx que l'on crée avec Tiled, un outil pour faire les maps.
from pytmx.util_pygame import load_pygame
from Settings import *


from Enemies import Enemy
import time

# L'Import de la map nécessite l'initialisation de pygame.
pygame.init()

tmx_data = load_pygame(Maps[Placeholder_map])


# Caméra qui permet de placer tous les éléments du map en fonction de la position du joueur.
# Class TRES IMPORTANT car pygame n'a pas de caméra codé dans ses fonctionalités.
class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # On prend d'abord la différence de la position du joueur et du centre de l'écran et on le met dans un vecteur
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height
        for sprite in self.sprites():  # Pour chaque élément du map
            # On calcule la position de chaque élément en faisant la différence de la position réel et l'offset.
            # Cela marche car quand la position du joueur évolue le offset évolue aussi
            # Exemple : Quand player.x augmente=joueur bouge à droite, l'offset.x augmente aussi.
            # Comme on le soustrait, tous les éléments de l'écran seront donc bougé à gauche.
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)


# Un mur dont on rentre en collision avec.
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, group):
        super().__init__(group)
        self.image = pygame.transform.scale(surf, (50, 50))
        self.rect = self.image.get_rect(topleft=pos)


# Les espaces où vont apparitres les items, les étoiles, et les énemies.
class Spawner_Tile(pygame.sprite.Sprite):
    def __init__(self, pos, group, type, cooldown, id):
        super().__init__(group)
        self.image = pygame.Surface((50, 50))
        self.image.fill(("darkblue"))
        self.rect = self.image.get_rect(topleft=pos)
        self.type = type
        self.cooldown = cooldown
        self.isalive = False
        # Ceci va permettre de différencier chaque spawner
        self.id = id

    # Quand cet fonction est appelé, l'élément dans self.type est spawn.
    def spawn(self, effect):
        if self.type == "Enemies":
            Enemy(self.rect.center, (map.visible_sprites, map.enemy_sprites), self.id)
        if self.type == "Items":
            Item(
                self.rect.center,
                (map.visible_sprites, map.pickup_sprites),
                self.id,
                effect,
            )
        if self.type == "Stars":
            Star(
                self.rect.center,
                (map.visible_sprites, map.pickup_sprites, map.star_sprites),
                "map",
                self.id,
            )
        self.isalive = True


# Des espaces où les joueurs vont réaparaitre quand ils respawn.
class Respwan_Tile(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.Surface((50, 50))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(topleft=pos)


# Conteneur de tous les groups, et donc tous les éléments du map.
class Map:
    def __init__(self):
        self.obsticle_sprites = pygame.sprite.Group()
        self.visible_sprites = Camera()
        self.pickup_sprites = pygame.sprite.Group()
        self.star_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.weapon_sprites = pygame.sprite.Group()
        self.bow_sprites = pygame.sprite.Group()
        self.arrow_sprites = pygame.sprite.Group()
        self.bomb_sprites = pygame.sprite.Group()
        self.flash_sprites = pygame.sprite.Group()
        self.freeze_sprites = pygame.sprite.Group()
        self.other_player_sprites = pygame.sprite.Group()
        self.spawner_sprites = pygame.sprite.Group()
        self.respawn_tile_sprites = pygame.sprite.Group()
        self.particle_sprites = pygame.sprite.Group()
        self.ids = 4

        # Génère le map
        for layer in tmx_data.layers:
            for x, y, surf in layer.tiles():
                pos = (x * 50, y * 50)
                if layer.name == "Walls":
                    Tile(pos, surf, (self.visible_sprites, self.obsticle_sprites))
                else:
                    Tile(pos, surf, (self.visible_sprites))
        # Génère les spawners
        Spawner_Tile(
            (300, 300),
            (self.visible_sprites, self.spawner_sprites),
            "Enemies",
            1000,
            self.Assign_id(),
        )
        Spawner_Tile(
            (350, 350),
            (self.visible_sprites, self.spawner_sprites),
            "Stars",
            1000,
            self.Assign_id(),
        )
        Spawner_Tile(
            (400, 400),
            (self.visible_sprites, self.spawner_sprites),
            "Items",
            1000,
            self.Assign_id(),
        )
        # Génère les respawn_tiles
        Respwan_Tile((500, 500), (self.visible_sprites, self.respawn_tile_sprites))
        # Prépare l'envoi des spawners au serveur.
        self.Spawners = {"Enemies": {}, "Items": {}, "Stars": {}}
        for spawner in self.spawner_sprites:
            self.Spawners[spawner.type][spawner.id] = {
                "horizontal": spawner.rect.centerx,
                "vertical": spawner.rect.centery,
                "movement": (0, 0),
                "state": "kill",
                "cooldown": spawner.cooldown,
                "last_check": pygame.time.get_ticks(),
                "movement_cooldown": pygame.time.get_ticks(),
                "Item_type": 0,
            }

    # Gère le rebonssement des étoiles,
    # Les étoiles rebondissent que si il viennent d'un joueur.
    # Si il rentre en collision avec un mur, il rebondit comme le DVD screensaver.
    def starbounce(self):
        diagonale = 0.7071067811865476
        for sprite in self.star_sprites:
            if sprite.origin == "player":
                now = time.time()
                dt = now - sprite.prev_time
                if sprite.direction.magnitude() != 0:
                    sprite.direction = sprite.direction.normalize()
                sprite.rect.x += sprite.direction.x * dt * 60
                sprite.rect.y += sprite.direction.y * dt * 60
                sprite.prev_time = now
                for Wall in self.obsticle_sprites:
                    if Wall.rect.colliderect(sprite.rect):

                        if (
                            sprite.direction.x == -diagonale
                            and sprite.direction.y == -diagonale
                        ):
                            sprite.direction = pygame.math.Vector2(1, -1)

                        elif (
                            sprite.direction.x == diagonale
                            and sprite.direction.y == -diagonale
                        ):
                            sprite.direction = pygame.math.Vector2(1, 1)

                        elif (
                            sprite.direction.x == diagonale
                            and sprite.direction.y == diagonale
                        ):
                            sprite.direction = pygame.math.Vector2(-1, 1)

                        elif (
                            sprite.direction.x == -diagonale
                            and sprite.direction.y == diagonale
                        ):
                            sprite.direction = pygame.math.Vector2(-1, -1)

    # Tue tous les éléments non murs du map.
    def allkill(self):
        for sprite in self.enemy_sprites:
            sprite.kill()
        for sprite in self.pickup_sprites:
            sprite.kill()

    # Permet de donner un id à un spawner.
    def Assign_id(self):
        self.ids += 1
        return self.ids

    # Dessine le niveau et met à jour tous les éléments d'un coup.
    # Method TRES IMPORTANT.
    def level_draw(self, player, player_information, map_info, screen):
        player.update()
        # Tue ou respawn les items, ennemies et étoiles en fonction de son état envoié par le serveur.
        for category in map_info:
            for sprite in self.spawner_sprites:
                if (
                    sprite.id in map_info[category]
                    and map_info[category][sprite.id]["state"] == "alive"
                    and not sprite.isalive
                ):
                    sprite.spawn(map_info[category][sprite.id]["Item_type"])
                if (
                    sprite.id in map_info[category]
                    and map_info[category][sprite.id]["state"] == "kill"
                ):
                    sprite.isalive = False
        for sprite in self.pickup_sprites:
            sprite.update()
            if sprite.effect == "star" and sprite.origin == "map":
                if map_info["Stars"][sprite.id]["state"] == "kill":
                    sprite.kill()
            elif sprite.effect != "star":
                if map_info["Items"][sprite.id]["state"] == "kill":
                    sprite.kill()
        for sprite in self.enemy_sprites:
            sprite.update(player, self, map_info)
            if map_info["Enemies"][sprite.id]["state"] == "kill":
                sprite.kill()
        for bomb in self.bomb_sprites:
            bomb.detonate(self)
        for sprite in self.arrow_sprites:
            sprite.update(self)
        for sprite in self.flash_sprites:
            sprite.flash()
        for sprite in self.freeze_sprites:
            sprite.freeze()
        for sprite in self.other_player_sprites:
            sprite.update(player_information)
        for sprite in self.particle_sprites:
            sprite.update()
        self.starbounce()
        self.visible_sprites.custom_draw(player)
        for heart in player.healthbar:
            heart.show(player, screen)
        for star in player.star_list:
            star.show(player, screen)
        for item in player.item_hud:
            item.show(player, screen)


# Instance de la map qui va être utilisé
map = Map()
