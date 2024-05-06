"""Fenêtre qui gère le serveur, qui va permettre l'intéraction des joueurs."""

import socket
from _thread import *
import pickle
import random
import pygame

pygame.init()
clock = pygame.time.Clock()

# Création du socket, à parir duquel on va envoyer des informations.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname(socket.gethostname())
port = 12345


# Petit fonction pour vérifié si le temps est écoulé.
def time_has_gone_by(last_check, duration):
    current_time = pygame.time.get_ticks()
    if current_time - last_check >= duration:
        return True
    return False


# Donne de la nouvelle mouvement.
def new_movement():
    return (random.randint(-1, 1), random.randint(-1, 1))


# VARIABLES GLOBAUX DONT TOUS LES JOUEURS VONT UTILISER DANS LEURS THREADS.

# Dictionnaire qui contient les informations de chaque joueur.
player_information = {
    0: {
        "position": (500, 500),
        "action_frame": (0, 0),
        "facing": "right",
        "inusage": None,
        "weaponask": False,
        "bowask": False,
        "direction": (0, 0),
        "star_count": 0,
        "took_damage": False,
        "star_lost": False,
        "invincibilty": False,
        "hp": 3,
        "name": "",
    },
    1: {
        "position": (290, 290),
        "action_frame": (0, 0),
        "facing": "right",
        "inusage": None,
        "weaponask": False,
        "bowask": False,
        "direction": (0, 0),
        "star_count": 0,
        "took_damage": False,
        "star_lost": False,
        "invincibilty": False,
        "hp": 3,
        "name": "",
    },
    2: {
        "position": (230, 450),
        "action_frame": (0, 0),
        "facing": "right",
        "inusage": None,
        "weaponask": False,
        "bowask": False,
        "direction": (0, 0),
        "star_count": 0,
        "took_damage": False,
        "star_lost": False,
        "invincibilty": False,
        "hp": 3,
        "name": "",
    },
    3: {
        "position": (400, 300),
        "action_frame": (0, 0),
        "facing": "right",
        "inusage": None,
        "weaponask": False,
        "bowask": False,
        "direction": (0, 0),
        "star_count": 0,
        "took_damage": False,
        "star_lost": False,
        "invincibilty": False,
        "hp": 3,
        "name": "",
    },
}
# Contient les information des ennemies, des items, des étoiles.
Map_information = {}
# Contienne les ids des éléments tué par les autres joueurs
kill_list = []
# On vérifie si il situe dans un ménu ou pas.
inmenu = True
# Liste des joueurs connectés
Connected_list = []
# Noms des joueurs
name_list = []
# Map choisi
map_chosen = "Map1"
try:
    server.bind((host, port))
except socket.error as e:
    str(e)

server.listen()
print("Waiting for connections...")


# Le thread qui permet d'envoyer des information à des autres joueurs.
# FONCTION TRES IMPORTANT.
def threaded_client(conn, client_number):
    # Variables globals
    global player_information
    global Map_information
    global kill_list
    global inmenu
    global Connected_list
    global open_slots
    global map_chosen
    global clock
    # Ce variable permet de break si le joueur se déconnecte dans le menu.
    breakall = False
    # On envoi au client son client_number, soit l'ordre auquel il s'est connceté.
    conn.send(pickle.dumps(client_number))
    # Dans le menu
    while inmenu:
        if breakall:
            break
        try:
            # On envoi si on est dans un menu, le map chosi, et le name.
            if client_number == 0:
                inmenu, map_chosen, name = pickle.loads(conn.recv(2048))
            # On envoi le name
            else:
                name = pickle.loads(conn.recv(2048))[2]
            # On l'ajout à un name_list, qui va permettre l'affichage de tous les noms plus tard.
            if (name, client_number) not in name_list:
                name_list.append((name, client_number))
                player_information[client_number]["name"] = name
            conn.send(pickle.dumps((Connected_list, inmenu, name_list)))
        except:
            breakall = True
    # On échange les information permettant de commencé le jeu.
    if not breakall:
        p = pickle.loads(conn.recv(2048))
        conn.send(pickle.dumps((player_information, map_chosen)))
        if client_number == 0:
            info = pickle.loads(conn.recv(2048))
            Map_information = info
            start_new_thread(server_operations, ())
    # Game loop principal, on échange les infos du joueur et des maps.
    while True:
        if breakall:
            break
        try:
            data = pickle.loads(conn.recv(2048))
            if not data:
                print("Disconnected")
                break
            else:
                player_information[client_number] = data

            conn.send(pickle.dumps(player_information))
        except:
            break
        try:
            data = pickle.loads(conn.recv(2048))
            reply = data
            for i in reply:
                kill_list.append(i)
            conn.send(pickle.dumps(Map_information))

        except:
            break
        clock.tick(60)
    # Dans le cas d'une déconnection
    print("Lost connection")
    Connected_list.remove(client_number)
    for i in range(len(name_list)):
        if name_list[i][1] == client_number:
            name_list.remove(name_list[i])
    if client_number == 0:
        server.close()

    else:
        # Si tu est dans open slots, tu peut reconnecter avec ce numéro de client.
        if client_number not in open_slots and inmenu:
            open_slots = [client_number] + open_slots
    conn.close()


# Gère les opérations du serveur pour le map.
def server_operations():
    global Map_information
    global kill_list
    while True:
        # Si l'élement est dans kill_list (il s'est fait tuer par un des joueurs) alors on le tue pour tous les joueurs.
        for category in Map_information:
            for spawner in Map_information[category]:
                if spawner in kill_list:
                    Map_information[category][spawner]["state"] = "kill"
                    kill_list.remove(spawner)
                if Map_information[category][spawner]["state"] == "kill":
                    # Si l'élement est mort et le temps de respwan est écoulé, alors on le remet en vie.
                    if time_has_gone_by(
                        Map_information[category][spawner]["last_check"],
                        Map_information[category][spawner]["cooldown"],
                    ):
                        Map_information[category][spawner]["state"] = "alive"
                        Map_information[category][spawner]["Item_type"] = (
                            random.randint(2, 2)
                        )
                        Map_information[category][spawner][
                            "last_check"
                        ] = pygame.time.get_ticks()
                        Map_information[category][spawner][
                            "movement_cooldown"
                        ] = pygame.time.get_ticks()

                else:
                    Map_information[category][spawner][
                        "last_check"
                    ] = pygame.time.get_ticks()
                # On bouge tous les ennemies avec le mouvement random.
                if category == "Enemies":
                    if time_has_gone_by(
                        Map_information[category][spawner]["movement_cooldown"], 3000
                    ):
                        Map_information[category][spawner]["movement"] = new_movement()

                        Map_information[category][spawner][
                            "movement_cooldown"
                        ] = pygame.time.get_ticks()
                Map_information[category][spawner]["horizontal"] += Map_information[
                    category
                ][spawner]["movement"][0]
                Map_information[category][spawner]["vertical"] += Map_information[
                    category
                ][spawner]["movement"][1]
        clock.tick(60)


client_number = 0
open_slots = []
# Connection des nouvelles joueurs, tourne en permance.
while True:
    try:
        conn, addr = server.accept()
    except:
        break
    if client_number >= 4:
        conn.close()
        continue
    print("Connected to :", addr)
    if open_slots:
        cli = open_slots.pop()
        start_new_thread(threaded_client, (conn, cli))
        Connected_list.append(cli)
    else:
        start_new_thread(threaded_client, (conn, client_number))
        Connected_list.append(client_number)
        client_number += 1
print("Server stopped")

""" Il est important de dire que les ids sont omniprésents dans se code.
 A partir de l'id, on peut identifier un objet même dans un dictionaire où dans une liste.
 Grâce au fontion Assign_id dans Levels, on peut crée un id unique à chaque élément."""
