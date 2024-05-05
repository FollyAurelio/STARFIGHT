"""Fenêtre qui programme le niveau et tous les éléments qu'elle contient"""
import pygame
from Items import Item,Star
import random
from pytmx.util_pygame import load_pygame
"""On utilse Pytmx qui est un module qui permet de lire nos fichers type tmx que l'on crée avec 
Tiled, un outil pour faire les maps."""
from Enemies import Enemy,Placeholer_map
import time
pygame.init()
if Placeholer_map=="Map1":
    tmx_data=load_pygame("Maps/MAP.tmx")
if Placeholer_map=='Map2':
    tmx_data=load_pygame("Maps/MAP2.tmx")
#L'Import de la map nécessite l'initialisation de pygame.


# Caméra qui suit le joueur
class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface=pygame.display.get_surface()
        self.half_width=self.display_surface.get_size()[0]//2
        self.half_height=self.display_surface.get_size()[1]//2
        self.offset=pygame.math.Vector2()
    
    def custom_draw(self,player):
        self.offset.x=player.rect.centerx-self.half_width
        self.offset.y=player.rect.centery-self.half_height
        for sprite in self.sprites():
            offset_pos=sprite.rect.topleft-self.offset
            self.display_surface.blit(sprite.image,offset_pos)
           
    

class Tile(pygame.sprite.Sprite):
    def __init__(self,pos,surf,group):
        super().__init__(group)
        self.image=pygame.transform.scale(surf,(50,50))
        self.rect=self.image.get_rect(topleft=pos)
#Chacun des murs de notre map est un Tile, qui vont être des obstacles et rentreront en collision avec le joueur.     
class Spawner_Tile(pygame.sprite.Sprite):
    def __init__(self,pos,group,type,cooldown,id):
        super().__init__(group)
        self.image=pygame.Surface((50,50))
        self.image.fill(("darkblue"))
        self.rect=self.image.get_rect(topleft=pos)
        self.type=type
        self.cooldown=cooldown
        self.isalive=False
        self.id=id
    
    def spawn(self,effect):
        if self.type=="Enemies":
            Enemy(self.rect.center,(map.visible_sprites,map.enemy_sprites),self.id)
        if self.type=="Items":
            Item(self.rect.center,(map.visible_sprites,map.pickup_sprites),self.id,effect)
        if self.type=="Stars":
            Star(self.rect.center,(map.visible_sprites,map.pickup_sprites,map.star_sprites),"map",self.id)
        self.isalive=True

class Respwan_Tile(pygame.sprite.Sprite):
    def __init__(self,pos,group):
        super().__init__(group)
        self.image=pygame.Surface((50,50))
        self.image.set_colorkey((0,0,0))
        self.rect=self.image.get_rect(topleft=pos)       


class Map:
    def __init__(self):
        self.obsticle_sprites=pygame.sprite.Group()
        self.visible_sprites=Camera()
        self.pickup_sprites=pygame.sprite.Group()
        self.star_sprites=pygame.sprite.Group()
        self.enemy_sprites=pygame.sprite.Group()
        self.weapon_sprites=pygame.sprite.Group()
        self.bow_sprites=pygame.sprite.Group()
        self.arrow_sprites=pygame.sprite.Group()
        self.bomb_sprites=pygame.sprite.Group()
        self.flash_sprites=pygame.sprite.Group()
        self.freeze_sprites=pygame.sprite.Group()
        self.other_player_sprites=pygame.sprite.Group()
        self.spawner_sprites=pygame.sprite.Group()
        self.respawn_tile_sprites=pygame.sprite.Group()
        self.ids=4
        """Cette classe est le conteneur de chacun des types d'objets qui sont dans la map.
        Il permet de mettre les objets dans la map à jour."""
        for layer in tmx_data.layers:
            for x,y,surf in layer.tiles():
                pos =(x*50,y*50)
                Tile(pos,surf,(self.visible_sprites,self.obsticle_sprites))
        #Initialise les murs de la map
        Spawner_Tile((300,300),(self.visible_sprites,self.spawner_sprites),"Enemies",1000,self.Assign_id())
        Spawner_Tile((350,350),(self.visible_sprites,self.spawner_sprites),"Stars",1000,self.Assign_id())
        Spawner_Tile((400,400),(self.visible_sprites,self.spawner_sprites),"Items",1000,self.Assign_id())
        Respwan_Tile((500,500),(self.visible_sprites,self.respawn_tile_sprites))
            #Initialise les ennemies de la map, en prenant soin qu'il ne rentre pas dans un mur
        self.Spawners={"Enemies":{},
                         "Items":{},
                         "Stars":{}}
        for spawner in self.spawner_sprites:
            self.Spawners[spawner.type][spawner.id]={"horizontal":spawner.rect.centerx,"vertical":spawner.rect.centery,"movement":(0,0),"state":"kill","cooldown":spawner.cooldown,"last_check":pygame.time.get_ticks(),"movement_cooldown":pygame.time.get_ticks(),"Item_type":0}
    def starbounce(self):
        diagonale=0.7071067811865476
        for sprite in self.star_sprites:
            if sprite.origin=="player":
                now=time.time()
                dt=now-sprite.prev_time
                if sprite.direction.magnitude()!=0:
                    sprite.direction=sprite.direction.normalize()
                sprite.rect.x+=sprite.direction.x*dt*60
                sprite.rect.y+=sprite.direction.y*dt*60
                sprite.prev_time=now
                for Wall in self.obsticle_sprites:
                    if Wall.rect.colliderect(sprite.rect):
                        
                        if sprite.direction.x==-diagonale and sprite.direction.y==-diagonale:
                            sprite.direction=pygame.math.Vector2(1,-1)
    
                        elif sprite.direction.x==diagonale and sprite.direction.y==-diagonale:
                            sprite.direction=pygame.math.Vector2(1,1)

                        elif sprite.direction.x==diagonale and sprite.direction.y==diagonale:
                            sprite.direction=pygame.math.Vector2(-1,1)

                        elif sprite.direction.x==-diagonale and sprite.direction.y==diagonale:
                            sprite.direction=pygame.math.Vector2(-1,-1)
        """Fait que les étoiles rebondissent, si il rentre en collision avec un mur, il rebondit seulement 
        si l'étoile vient d'un joueur."""

    def allkill(self):
        for sprite in self.enemy_sprites:
            sprite.kill()
        for sprite in self.pickup_sprites:
            sprite.kill()
    def Assign_id(self):
        self.ids+=1
        return self.ids

            




    def level_draw(self,player,information,map_info,screen):
        player.update()
        for category in map_info:
            for sprite in self.spawner_sprites:
                if sprite.id in map_info[category] and map_info[category][sprite.id]["state"]=="alive" and not sprite.isalive:
                        sprite.spawn(map_info[category][sprite.id]["Item_type"])
                if sprite.id in map_info[category] and map_info[category][sprite.id]["state"]=="kill":
                    sprite.isalive=False
        for sprite in self.pickup_sprites:
            sprite.update()
            if sprite.effect=="star" and sprite.origin=="map":
                if map_info["Stars"][sprite.id]["state"]=="kill":
                    sprite.kill()
            elif sprite.effect!="star":
                if map_info["Items"][sprite.id]["state"]=="kill":
                    sprite.kill()
        for sprite in self.enemy_sprites:
            sprite.update(player,self,map_info)
            if map_info["Enemies"][sprite.id]["state"]=="kill":
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
            sprite.update(information)
        self.starbounce()     
        self.visible_sprites.custom_draw(player)
        for heart in player.healthbar:
            heart.show_hp(player,screen)
    #permet de dessiner la map
        
map=Map()     
#Instance de la map qui va être utilisé dans main et player





        


