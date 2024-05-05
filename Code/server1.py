import socket 
from _thread import *
import pickle
import random
import pygame
pygame.init()
clock=pygame.time.Clock()

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host=socket.gethostbyname(socket.gethostname())
port=12345
def time_has_gone_by(last_check,duration):
    current_time=pygame.time.get_ticks()
    if current_time-last_check>=duration:
        return True
    return False
def new_movement():
    return (random.randint(-1,1),random.randint(-1,1))

player_information={0:{"position":(500,500),"action_frame":(0,0),"facing":"right","inusage":None,"weaponask":False,"bowask":False,"direction":(0,0),"star_count":0,"took_damage":False,"star_lost":False,"invincibilty":False,"hp":3,"name":""},
                    1:{"position":(290,290),"action_frame":(0,0),"facing":"right","inusage":None,"weaponask":False,"bowask":False,"direction":(0,0),"star_count":0,"took_damage":False,"star_lost":False,"invincibilty":False,"hp":3,"name":""},
                    2:{"position":(230,450),"action_frame":(0,0),"facing":"right","inusage":None,"weaponask":False,"bowask":False,"direction":(0,0),"star_count":0,"took_damage":False,"star_lost":False,"invincibilty":False,"hp":3,"name":""},
                    3:{"position":(400,300),"action_frame":(0,0),"facing":"right","inusage":None,"weaponask":False,"bowask":False,"direction":(0,0),"star_count":0,"took_damage":False,"star_lost":False,"invincibilty":False,"hp":3,"name":""},             
                    }
Map_information={}
kill_list=[]
inmenu=True
Connected_list=[]
name_list=[]
map_chosen="Map1"
try:
    server.bind((host,port))
except socket.error as e:
    str(e)

server.listen()
print("Waiting for connections...")

def threaded_client(conn,client_number):
    global player_information
    global Map_information
    global kill_list
    global inmenu
    global Connected_list
    global open_slots
    global map_chosen
    global clock
    breakall=False
    conn.send(pickle.dumps(client_number))
    while inmenu:
        if breakall:
            break
        try:
            if client_number==0:
                inmenu,map_chosen,name=pickle.loads(conn.recv(2048))
            else:
                name=pickle.loads(conn.recv(2048))[2]
            if (name,client_number) not in name_list:
                name_list.append((name,client_number))
                player_information[client_number]["name"]=name
            conn.send(pickle.dumps((Connected_list,inmenu,name_list)))
        except:
            breakall=True
    if not breakall:
        p=pickle.loads(conn.recv(2048))
        conn.send(pickle.dumps((player_information,map_chosen)))
        if client_number==0:
            info=pickle.loads(conn.recv(2048))
            Map_information=info
            start_new_thread(server_operations,())
    
    while True:
        if breakall:
            break
        try:
            data=pickle.loads(conn.recv(2048))
            if not data:
                print("Disconnected")
                break
            else:
                #print(f"Received {data} from player {client_number}")
                player_information[client_number]=data 
                #print(f"sending data to {client_number}")
                if player_information[client_number]["weaponask"]:
                    print(player_information[client_number]["weaponask"])
                
            conn.send(pickle.dumps(player_information))
        except:
            break
        try:
            data=pickle.loads(conn.recv(2048))            
            reply=data
            for i in reply:
                kill_list.append(i)
            conn.send(pickle.dumps(Map_information))
                
        
            
        except:
            break
        clock.tick(60)
    print("Lost connection")
    Connected_list.remove(client_number)
    for i in range(len(name_list)):
        if name_list[i][1]==client_number:
            name_list.remove(name_list[i])
    if client_number==0:
        server.close()
    
    else:
        if client_number not in open_slots and inmenu:
            open_slots=[client_number]+open_slots
    conn.close()


def server_operations():
    global Map_information
    global kill_list
    # global clock
    while True:
        for category in Map_information:
            for spawner in Map_information[category]:
                if spawner in kill_list:
                    Map_information[category][spawner]["state"]="kill"
                    kill_list.remove(spawner)
                if Map_information[category][spawner]["state"]=="kill":
                    if time_has_gone_by(Map_information[category][spawner]["last_check"],Map_information[category][spawner]["cooldown"]):
                        Map_information[category][spawner]["state"]="alive"
                        Map_information[category][spawner]["Item_type"]=random.randint(0,7)
                        Map_information[category][spawner]["last_check"]=pygame.time.get_ticks()
                        Map_information[category][spawner]["movement_cooldown"]=pygame.time.get_ticks()

                else:
                    Map_information[category][spawner]["last_check"]=pygame.time.get_ticks()
                if category=="Enemies":
                    if time_has_gone_by(Map_information[category][spawner]["movement_cooldown"],3000):
                        Map_information[category][spawner]["movement"]=new_movement()
                        

                        Map_information[category][spawner]["movement_cooldown"]=pygame.time.get_ticks()
                Map_information[category][spawner]["horizontal"]+=Map_information[category][spawner]["movement"][0]
                Map_information[category][spawner]["vertical"]+=Map_information[category][spawner]["movement"][1]
        clock.tick(60)
client_number=0
open_slots=[]
while True:
    try:
        conn,addr=server.accept()
    except:
        break
    if client_number>=4:
        conn.close()
        continue
    print("Connected to :",addr)
    if open_slots:
        cli=open_slots.pop()
        start_new_thread(threaded_client,(conn,cli))
        Connected_list.append(cli)
    else:
        start_new_thread(threaded_client,(conn,client_number))
        Connected_list.append(client_number)
        client_number+=1
print("Server stopped")
    
