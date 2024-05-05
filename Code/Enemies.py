# Crée des ennemies
import pygame
import random
import time

Placeholer_map = "Map1"


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, group, id):
        super().__init__(group)
        self.id = id
        self.image = pygame.Surface((50, 50))
        self.image.fill("red")
        self.g = group
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.last_movement = pygame.time.get_ticks()
        self.prev_time = time.time()
        self.frozen = False
        self.frozen_timer = pygame.time.get_ticks()

    def move(self, player, map, map_info):
        self.direction.x = map_info["Enemies"][self.id]["movement"][0]
        self.direction.y = map_info["Enemies"][self.id]["movement"][1]
        if not self.frozen:
            now = time.time()
            dt = now - self.prev_time
            self.rect.x += self.direction.x * dt * 60
            self.check_collision(player, "horizontal", map)
            self.rect.y += self.direction.y * dt * 60
            self.check_collision(player, "vertical", map)
            self.prev_time = now

    def check_collision(self, player, direction, map):
        if direction == "horizontal":
            for sprite in map.obsticle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right
        if direction == "vertical":
            for sprite in map.obsticle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
        for sprite in map.weapon_sprites:
            if sprite.rect.colliderect(self.rect):
                player.kill_list.append(self.id)
                self.kill()
        for sprite in map.arrow_sprites:
            if sprite.rect.colliderect(self.rect):
                player.kill_list.append(self.id)
                self.kill()
        for sprite in map.flash_sprites:
            if sprite.rect.colliderect(self.rect):
                player.kill_list.append(self.id)
                self.kill()
        for sprite in map.freeze_sprites:
            if sprite.rect.colliderect(self.rect):
                self.frozen = True

    def freezetime(self):
        duration = 10000
        if self.frozen:
            current_time = pygame.time.get_ticks()
            if current_time - self.frozen_timer >= duration:
                self.frozen = False
                self.frozen_timer = current_time
        else:
            self.frozen_timer = pygame.time.get_ticks()

    # def project(self,player,map):
    #     if not self.frozen:
    #         current_time=pygame.time.get_ticks()
    #         cooldown=1000
    #         if current_time-self.projectile_cooldown>=cooldown:
    #             self.projectile_cooldown=current_time
    #             temp=map.Assign_id()
    #             Projectile(player,self,self.g,temp)
    #             map.Enemy_list[temp]=(self.rect.center,True)
    def update(self, player, map, map_info):
        self.freezetime()
        self.move(player, map, map_info)


# class Range(pygame.sprite.Sprite):
#     def __init__(self,enemy,group):
#         super().__init__(group)
#         self.image=pygame.Surface((250,250))
#         self.image.set_colorkey((0,0,0))

#         self.image.fill("black")
#         self.rect=self.image.get_rect(center=enemy.rect.center)


# class Projectile(pygame.sprite.Sprite):
#     def __init__(self,player,enemy,group,id):
#         self.id=id
#         super().__init__(group)
#         self.image=pygame.Surface((25,25))
#         self.image.fill("brown")
#         self.rect=self.image.get_rect(center=enemy.rect.center)
#         self.time=pygame.time.get_ticks()
#         # angle=math.atan2(player.rect.y-self.rect.y,player.rect.x-self.rect.x)
#         # de_angle=int(angle/math.pi)
#         self.direction=pygame.math.Vector2((player.rect.x-self.rect.x)*0.01,(player.rect.y-self.rect.y)*0.01)
#         if self.direction.magnitude()!=0:
#             self.direction.normalize()


#         #     angle=self.direction.angle_to((1,0))
#         #     pygame.transform.rotate(self.image,angle)
#             # print(angle)
#         self.isproject=True
#         self.duration=3000


#     def update(self,player,map):
#         if player.id==0:
#             k=False
#             current_time=pygame.time.get_ticks()
#             for sprite in map.obsticle_sprites:
#                 if sprite.rect.colliderect(self.rect):
#                     k=True
#                     self.kill()
#             if current_time-self.time>=self.duration:
#                 k=True
#                 self.kill()
#             self.rect.x+=self.direction.x
#             self.rect.y+=self.direction.y
#             if k:
#                 del map.Enemy_list[self.id]
# map.Enemy_list[self.id]=(self.rect.center,True)
