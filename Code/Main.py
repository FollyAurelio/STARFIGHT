"""Fenetre qui rassemble tous les autres fonctions du 
jeu et doit être lancé pour faire marche le jeu"""

import pygame
import time

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
running = True
Game_time = 10000
# Imports de base en pygame et import les autres modules nécessaires.
Text = pygame.font.SysFont("Arial", 20)
setup = False
from Client import *
from MainMenu import *

while running:
    if Main_menu.inmenu:
        for event in pygame.event.get():
            for box in Main_menu.inputboxes:
                box.insert(Main_menu, event)
            if event.type == pygame.QUIT:
                running = False
        screen.fill("darkgreen")
        if Main_menu.state == 6:
            endscreen(player_information, screen)
        Main_menu.show_menu(screen)
        if Main_menu.serverstarted:
            Main_menu.Connected_list, Main_menu.inmenu, Main_menu.name_list = (
                Main_menu.network.send(
                    (Main_menu.inmenu, Main_menu.map_chosen, Main_menu.name)
                )
            )
    else:
        if not setup:
            player_information, map_chosen = Main_menu.network.send("")
            from Debugger import *
            import Items
            import Enemies

            Enemies.Placeholer_map = map_chosen
            from player import *
            import Levels

            player = Player(
                player_information[Main_menu.network.id]["position"],
                Levels.map.visible_sprites,
                Main_menu.network.id,
                player_information[Main_menu.network.id]["name"],
            )
            for id in player_information:
                if id != Main_menu.network.id:
                    otherPlayer(
                        player_information[id]["position"],
                        (Levels.map.visible_sprites, Levels.map.other_player_sprites),
                        id,
                        player_information[id]["name"],
                    )
            if player.id == 0:
                Main_menu.network.send_sol(Levels.map.Spawners)
            setup = True
            Timer = time.time()
        if time.time() - Timer <= Game_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Permet de quiter le jeu
                if event.type == pygame.KEYUP:
                    player.action = 0
                    player.frame = 0
                    # Pour bien changer l'animation du joueur

            screen.fill("white")

            player_information = Main_menu.network.send(
                {
                    "position": player.rect.center,
                    "action_frame": (player.action, player.frame),
                    "facing": player.facing,
                    "inusage": player.inusage,
                    "weaponask": player.weaponask,
                    "bowask": player.bowask,
                    "direction": player.direction,
                    "star_count": player.star_count,
                    "took_damage": player.took_damage,
                    "star_lost": player.star_lost,
                    "invincibilty": player.invincibilty,
                    "hp": player.hp,
                    "name": player.name,
                }
            )
            map_info = Main_menu.network.send(player.kill_list)
            if not map_info:
                print("Unable to connect to server")
                break
            if player.star_lost:
                print("a")
            player.kill_list = []
            player.weaponask = False
            player.bowask = False
            player.took_damage = False
            player.star_lost = False

            # for sprite in Levels.map.other_player_sprites:
            #     screen.blit(Text.render(f"{sprite.name}",False,(0,0,0)),sprite.rect.center)
            Levels.map.level_draw(player, player_information, map_info, screen)
            # On met a jour le joueur et le map
            debug_position(
                [
                    (player.rect.center, (0, 0)),
                    (player.star_count, (450, 450)),
                    (player.hp, (450, 400)),
                    (player.items_list, (0, 450)),
                    (round(Game_time - (time.time() - Timer)), (400, 0)),
                ],
                screen,
            )
        else:
            Main_menu.network.client.close()
            Main_menu.state = 6
            Main_menu.inmenu = True
            Main_menu.serverstarted = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
