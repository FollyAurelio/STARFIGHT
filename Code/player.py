#Fenêtre qui programme le joueur
import pygame
import Items
import Levels
import random
import time
from Settings import *
pygame.init()
Text=pygame.font.SysFont("Arial",20)

#On coup le spritesheet qui contient les animations du joueur


Dinos=["Sprites/DinoSprites - doux.png","Sprites/DinoSprites - mort.png","Sprites/DinoSprites - tard.png","Sprites/DinoSprites - vita.png"]

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,group,id,name): 
        super().__init__(group)
        self.id=id
        self.star_count=0
        self.hp=3
        self.healthbar=(Heart(0),Heart(1),Heart(2))
        self.heartframe=0
        self.heartspin=[pygame.time.get_ticks(),pygame.time.get_ticks()]
        self.name=name
        self.death_timer=pygame.time.get_ticks()
        self.appear=False
        self.spritesheet=pygame.image.load(Dinos[self.id]).convert_alpha()
        self.frame=0
        self.action=0
        self.direction=pygame.math.Vector2(0,0)
        self.speed=4
        self.facing="right"
        self.last_update=pygame.time.get_ticks()
        self.invincibilty_mesure=pygame.time.get_ticks()
        self.flyback_mesure=pygame.time.get_ticks()
        self.taking_knockback=False
        self.knockback_direction=pygame.math.Vector2()
        self.invincibilty=False
        self.invincibilty_power=False
        self.invincibilty_power_mesure=pygame.time.get_ticks()
        self.frozen=False
        self.frozen_mesure=pygame.time.get_ticks()
        self.items_list=[Items.Weapon("sword",(Levels.map.weapon_sprites),self.id),Items.Weapon("sword",(Levels.map.weapon_sprites),self.id),Items.Weapon("sword",(Levels.map.weapon_sprites),self.id)]
        self.using_item=False
        self.inusage=None
        self.weaponask=False
        self.bowask=False
        self.took_damage=False
        self.star_lost=False
        self.prev_time=time.time()
        self.item_timer=pygame.time.get_ticks()
        animation_length=[4,6,3,4]
        self.animation_list=create_animation(self.spritesheet,animation_length,24,24,0,0,45)
        self.kill_list=[]
        self.image=self.animation_list[self.action][self.frame]
        self.rect=self.image.get_rect(center=pos)
        self.nametag=Nametag(self)
    """ Initialise les attributs du joueurs. Dans ceci on retrouve dans l'ordre : Le nombre d'étoiles
    son spritesheet, le parti de l'animation auquel il est en cours, l'animation qu'il effectue, son direction
    modélisé par une vecteur, sa vitesse, son sens d'orientation, le temps du dernier mise a jour de son animation,
    le temps depuis qu'il est devenu invincible, la duration d'une animation, si il est invinvible, une liste qui contient tous ses animations
    la longeur de chaque animation, son image, et son rectangle.
    """
    def update(self):
        animation_cooldown=100
        heart_cooldown=100
        spin_cooldown=2000
        current_time=pygame.time.get_ticks()
        self.last_update,self.frame=animate(self.animation_list,animation_cooldown,self.last_update,self.action,self.frame)
        if current_time-self.heartspin[1]>=spin_cooldown:
            self.heartspin[0],self.heartframe=animate([["1","2","3","4","5","6"]],heart_cooldown,self.heartspin[0],0,self.heartframe)
            if self.heartframe==0: 
                self.heartspin[1]=current_time
        if self.hp>0:
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
            self.image=self.animation_list[self.action][self.frame]
            self.nametag.rect.topleft=self.rect.bottomright
        self.dead()
    # Met a jour tous les attributs du joueur

    def flicker(self):
        if self.invincibilty:
            self.action=3
    # Change l'animation a celui indiquant qu'il prend des dégâts si il est invincible

        

    def mouvement(self):
        keys=pygame.key.get_pressed()
        if not self.frozen and not self.taking_knockback:
            if keys[pygame.K_d]:
                self.direction.x=1
                self.action=1
                if self.facing=="left":
                    self.turn()
                    self.facing="right"
            elif keys[pygame.K_q]:
                self.direction.x=-1
                self.action=1
                if self.facing=="right":
                    self.turn()
                    self.facing="left"
            else:
                self.direction.x=0   
            if keys[pygame.K_z]:
                self.direction.y=-1
                self.action=1    
            elif keys[pygame.K_s]:
                self.direction.y=1
                self.action=1        
            else:
                self.direction.y=0
            if self.direction.magnitude()!=0:
                self.direction=self.direction.normalize()
            now=time.time()
            dt=now-self.prev_time
            self.rect.x+=self.direction.x*self.speed*dt*60
            self.check_collision("horizontal")
            self.rect.y+=self.direction.y*self.speed*dt*60
            self.prev_time=now
            self.check_collision("vertical")
        """Le mouvement. Une normalisation des vecteurs est effectuer pour éviter un bug avec les diagonales
        Sa direction de mouvement est multiplié par sa vitesse, puis on vérifie si il rentre en collision avec un mur."""
        
        
    def check_collision(self,direction):
        if direction=="horizontal":
            for sprite in Levels.map.obsticle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x>0:
                       self.rect.right=sprite.rect.left
                    if self.direction.x<0:
                       self.rect.left=sprite.rect.right
                       
        if direction=="vertical":
            for sprite in Levels.map.obsticle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y<0:
                        self.rect.top=sprite.rect.bottom
                    if self.direction.y>0:
                       self.rect.bottom=sprite.rect.top
        """Collision. Si il est en collision avec un mur, alors ses coordonnés sont égals aux côtés qu'il parcourt"""
    def pickup(self):
        if not self.invincibilty:   
            for sprite in Levels.map.pickup_sprites:
                if sprite.rect.colliderect(self.rect):
                    sprite.effect_apply(self)
                    if sprite.effect=="star":
                        self.kill_list.append(sprite.id)
                    else:
                        self.kill_list.append(sprite.id)
                    sprite.kill()
                    
    # Ramassement des items. Si il rentre en contact avec un item, on applique son effet et on le supprime.
    
    def give(self,effect):
        for item in range(len(self.items_list)):
            if not self.items_list[item]:
                if effect=="sword" or effect=="spear" or effect=="axe":
                    self.items_list[item]=Items.Weapon(effect,(Levels.map.weapon_sprites),self.id)
                    break
                if effect=="bow":
                    self.items_list[item]=Items.Weapon(effect,(Levels.map.bow_sprites),self.id)
                    break
                if effect=="bomb" or effect=="invincible" or effect=="freeze" or effect=="lightning":
                    self.items_list[item]=Items.Spell(effect)
                    break
                
                    
    def Ouch(self,dealer=None):
        if not self.invincibilty and not self.invincibilty_power:
            self.invincibilty=True
            self.took_damage=True
            self.hp-=1
            if dealer:
                if dealer in Levels.map.enemy_sprites:
                    self.taking_knockback=True
                    if self.direction==(0,0):
                        self.knockback_direction=dealer.direction
                    else:
                        self.knockback_direction=-self.direction
                if dealer in Levels.map.weapon_sprites or dealer in Levels.map.arrow_sprites:
                    self.taking_knockback,self.knockback_direction=True,dealer.direction
            if self.star_count>0:
                self.star_count-=1
                self.star_lost=True
                Levels.Star(self.rect.center,(Levels.map.visible_sprites,Levels.map.pickup_sprites,Levels.map.star_sprites),"player",0)
            if not self.invincibilty_power:
                if self.frame>3:
                    self.frame=0
                self.action=3

    def Damage_Check(self):
        for sprite in Levels.map.enemy_sprites:
            if sprite.rect.colliderect(self.rect):
                self.Ouch(sprite)
        for sprite in Levels.map.weapon_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id!=self.id:
                    #self.taking_knockback,self.knockback_direction=True,sprite.direction
                    self.Ouch(sprite)
        for sprite in Levels.map.arrow_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id!=self.id:
                    #self.taking_knockback,self.knockback_direction=True,sprite.direction
                    self.Ouch(sprite)
        for sprite in Levels.map.flash_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id!=self.id:
                    self.Ouch()
        for sprite in Levels.map.bomb_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id!=self.id:
                    Items.Flash(sprite,(Levels.map.visible_sprites,Levels.map.flash_sprites),200,sprite.id)
                    sprite.kill()
        for sprite in Levels.map.freeze_sprites:
            if sprite.rect.colliderect(self.rect):
                if sprite.id!=self.id:
                    self.frozen=True
    
    def knockback(self):
        current_time=pygame.time.get_ticks()
        duration=50
        if self.taking_knockback:
            self.speed=10
            self.direction=self.knockback_direction
            now=time.time()
            dt=now-self.prev_time
            self.rect.x+=self.direction.x*self.speed*dt*60
            self.check_collision("horizontal")
            self.rect.y+=self.direction.y*self.speed*dt*60
            self.prev_time=now
            self.check_collision("vertical")
            if current_time-self.flyback_mesure>=duration:
                self.taking_knockback=False
        else:
            self.flyback_mesure=pygame.time.get_ticks()
            self.speed=4
        
        
        
        
                
    """Prise de dégats. Si on rente en contact avec un enemies, 
    on devient invincible et on perd une étoile qu'on a qui va rebondir. On change a l'animation de dégât"""
                   
                   


    def invincible_tick(self):
        if self.invincibilty:
            invincibilty_frames=1000
            current_time=pygame.time.get_ticks()
            if current_time-self.invincibilty_mesure>=invincibilty_frames:
                self.invincibilty=False
                self.invincibilty_mesure=current_time
                self.action=0
                self.frame=0
        else:
            self.invincibilty_mesure=pygame.time.get_ticks()
    def freeze_tick(self):
        if self.frozen:
            frozen_frames=10000
            current_time=pygame.time.get_ticks()
            if current_time-self.frozen_mesure>=frozen_frames:
                self.frozen=False
                self.frozen_mesure=current_time
        else:
            self.frozen_mesure=pygame.time.get_ticks()
    

        # Compteur d'invincibilité.
    
    def use_item(self):
        keys=pygame.key.get_pressed()
        keyboard=[keys[pygame.K_j],keys[pygame.K_k],keys[pygame.K_l]]
        if not self.using_item:
            for i in range(len(keyboard)):
                if keyboard[i]:
                    if self.items_list[i]:
                        if self.items_list[i].type=="sword" or self.items_list[i].type=="spear" or self.items_list[i].type=="axe" or self.items_list[i].type=="bow": 
                            self.items_list[i].add(Levels.map.visible_sprites)
                            self.weaponask=self.items_list[i].type
                            self.inusage=self.items_list[i].type
                            self.using_item=i+1
                        else:
                            self.items_list[i].cast(self,Levels.map)
                            self.weaponask=self.items_list[i].type
                            self.inusage=self.items_list[i].type
                            self.items_list[i]=""
                            
    
    def show_item(self):
        cooldown=3000
        if self.using_item:
            current_time=pygame.time.get_ticks()
            self.items_list[self.using_item-1].use_weapon(self)
            if self.items_list[self.using_item-1].type=='sword':
                self.speed=7
            self.items_list[self.using_item-1].shoot_arrow(self,Levels.map)
            if current_time-self.item_timer>=cooldown:
                self.items_list[self.using_item-1].kill()
                self.items_list[self.using_item-1]=""
                self.using_item=False
                self.inusage=None
                self.speed=4
                self.item_timer=current_time
                
        else:
            self.item_timer=pygame.time.get_ticks()
                        
    def invincibilty_powerup(self):
        duration=6000
        if self.invincibilty_power:
            current_time=pygame.time.get_ticks()
            if current_time-self.invincibilty_power_mesure>=duration:
                self.invincibilty_power=False
                self.invincibilty_power_mesure=current_time
        else:
            self.invincibilty_power_mesure=pygame.time.get_ticks()

    def turn(self):
        for animation in self.animation_list:
            for frame in range(len(animation)):
                animation[frame]=pygame.transform.flip(animation[frame],True,False)

    def dead(self):
        death_time=10000
        death_time_post_tp=4000
        self.prev_time=time.time()
        current_time=pygame.time.get_ticks()
        if self.hp<=0:
            self.image.set_alpha(0)
            if self.using_item:
                self.items_list[self.using_item-1].kill()
                self.using_item=False
                self.speed=4
                self.item_timer=pygame.time.get_ticks()
            self.inusage=None
            self.items_list=["","",""]
            if current_time-self.death_timer>=death_time:
                if not self.appear:
                    self.rect.center=random.choice(list(Levels.map.respawn_tile_sprites)).rect.topleft
                    self.appear=True
                if current_time-self.death_timer>=death_time+death_time_post_tp:
                    self.hp=3
                    self.death_timer=current_time
        else:
            self.death_timer=pygame.time.get_ticks()
            self.appear=False
            self.image.set_alpha(255)
        


class otherPlayer(pygame.sprite.Sprite):
    def __init__(self,pos,group,id,name):
        super().__init__(group)
        self.id=id
        self.name=name
        self.spritesheet=pygame.image.load(Dinos[self.id]).convert_alpha()
        self.facing="right"
        self.action=0
        self.frame=0
        self.weapon=None
        self.direction=pygame.math.Vector2()
        self.animation_list=[]
        animation_length=[4,6,3,4]
        steps=0
        for ani in animation_length:
           temp=[]
           for i in range(ani):
               cut=cut_image(self.spritesheet,24,24,steps,0,45)
               temp.append(cut)
               steps+=1
           self.animation_list.append(temp)
        self.image=self.animation_list[self.action][self.frame]
        self.rect=self.image.get_rect(center=pos)
    
    def turn(self):
        for animation in self.animation_list:
            for frame in range(len(animation)):
                animation[frame]=pygame.transform.flip(animation[frame],True,False)
        
    def update(self,information):
        self.rect.center=information[self.id]["position"]
        self.direction=information[self.id]["direction"]
        self.action,self.frame=information[self.id]["action_frame"][0],information[self.id]["action_frame"][1]
        if self.facing!=information[self.id]["facing"]:
            self.turn()
            self.facing=information[self.id]["facing"]
        if (information[self.id]["weaponask"]=="sword" or information[self.id]["weaponask"]=="spear" or information[self.id]["weaponask"]=="axe") and not self.weapon:
            self.weapon=Items.Weapon(information[self.id]["weaponask"],(Levels.map.weapon_sprites),self.id)
        if (information[self.id]["weaponask"]=="bow") and not self.weapon:
            self.weapon=Items.Weapon(information[self.id]["weaponask"],(Levels.map.bow_sprites),self.id)
        if information[self.id]["weaponask"]=="bomb":
            Items.Bomb(self,(Levels.map.visible_sprites,Levels.map.bomb_sprites),self.id,"Invisible")
        if information[self.id]["weaponask"]=="freeze":
            Items.Freeze(self,(Levels.map.visible_sprites,Levels.map.freeze_sprites),self.id)
        if information[self.id]["weaponask"]=="lightning":
            Items.Flash(self,(Levels.map.visible_sprites,Levels.map.flash_sprites),500,self.id)
        if information[self.id]["inusage"] and self.weapon:
            if self.weapon not in Levels.map.visible_sprites:
                self.weapon.add(Levels.map.visible_sprites)
            self.weapon.use_weapon(self)
            if information[self.id]["bowask"]:
                Items.Arrow(self.weapon,(Levels.map.visible_sprites,Levels.map.arrow_sprites),self.id)
        else:
            if self.weapon:
                self.weapon.kill()
                self.weapon=None
        if information[self.id]["took_damage"] and information[self.id]["invincibilty"]:
            if information[self.id]["star_lost"]:
                print("i")
                Items.Star(self.rect.center,(Levels.map.visible_sprites,Levels.map.pickup_sprites,Levels.map.star_sprites),"player",0)
        for sprite in Levels.map.star_sprites:
            if sprite.origin=="player" and sprite.rect.colliderect(self.rect) and not information[self.id]["invincibilty"]:
                sprite.kill()
        self.image=self.animation_list[self.action][self.frame]
        if information[self.id]["hp"]<=0:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

class Nametag(pygame.sprite.Sprite):
    def __init__(self,player):
        self.image=pygame.Surface((50,50))
        self.image.set_colorkey((0,0,0))
        self.rect=self.image.get_rect(topleft=player.rect.bottomright)
        l=Text.render(f"{player.name}",False,(0,0,0))
        self.image.blit(l,self.rect.center)
    def update(self,player,screen):
        screen.blit(Text.render(f"{player.name}",False,(0,0,0)),player.nametag.rect.center)


class Heart(pygame.sprite.Sprite):
    def __init__(self,heart_id):
        self.animation_list=create_animation(Useful_Item_sprites,[6],16,16,25,14,30)
        self.image=self.animation_list[0][0]
        self.id=heart_id 
        self.rect=self.image.get_rect(center=[(0,30),(30,30),(60,30)][heart_id])
    def show_hp(self,player,screen):
        if player.hp>=self.id+1:
            screen.blit(self.image,self.rect.center)
        self.image=self.animation_list[0][player.heartframe]


#14,25,6 long
        


    
    






