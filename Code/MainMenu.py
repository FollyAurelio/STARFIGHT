import pygame
from Client import *
from _thread import *

pygame.init()
Starfight=pygame.font.SysFont("Arial",40)
Text=pygame.font.SysFont("Arial",20)

def server_start():
    import server1
class menu:
    def __init__(self):
        self.state=0
        self.title_screen=pygame.sprite.Group()
        self.host_join=pygame.sprite.Group()
        self.hosting=pygame.sprite.Group()
        self.chosing_map=pygame.sprite.Group()
        self.joining=pygame.sprite.Group()
        self.joining_join=pygame.sprite.Group()
        self.end_screen=pygame.sprite.Group()
        self.menus=[self.title_screen,self.host_join,self.hosting,self.joining,self.chosing_map,self.joining_join,self.end_screen]
        Button((250,250),100,100,self.title_screen,"Play")
        Button((100,250),100,100,self.host_join,"Host")
        Button((400,250),100,100,self.host_join,"Join")
        Button((150,475),100,50,self.hosting,"Maps")
        Button((100,100),200,100,self.chosing_map,"Map1")
        Button((100,200),200,100,self.chosing_map,"Map2")
        Button((250,475),100,50,self.hosting,"Start Game")
        self.flashcards=[FlashCard((20,50),(self.hosting,self.joining_join),0),FlashCard((140,50),(self.hosting,self.joining_join),1),FlashCard((260,50),(self.hosting,self.joining_join),2),FlashCard((380,50),(self.hosting,self.joining_join),3)]
        self.inputboxes=[inputbox((100,350),self.title_screen,"Name"),inputbox((100,250),self.joining,"Join")]
        self.serverstarted=False
        self.inmenu=True
        self.Connected_list=[]
        self.network=""
        self.map_chosen="Map1"
        self.name=""
        self.name_list=[]
    def show_menu(self,screen):
        self.menus[self.state].draw(screen)
        if self.state==0 or self.state==1:
            screen.blit(Starfight.render(f"STARFIGHT",False,(0,0,0)),(165,0))
        if self.state==2:
            screen.blit(Starfight.render(f"HOST",False,(0,0,0)),(205,0))
        if self.state==3:
            screen.blit(Starfight.render(f"JOIN",False,(0,0,0)),(205,0))
        if self.name:
            screen.blit(Text.render(f"Name : {self.name}",False,(0,0,0)),(0,0))
        for button in self.menus[self.state]:
            button.update(self,screen)
            
class Button(pygame.sprite.Sprite):
    def __init__(self,pos,width,height,group,function):
        super().__init__(group)
        self.image=pygame.Surface((width,height))
        self.image.fill("white")
        self.rect=self.image.get_rect(center=pos)
        self.function=function
        self.Functions=["Play","Host","Join","Maps"]
        self.map_list=["Map1","Map2"]
    

    def update(self,menu,screen):
        screen.blit(Text.render(f"{self.function}",False,(0,0,0)),(self.rect.centerx-20,self.rect.centery-10))
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()) and self.function in self.Functions and menu.name:
            menu.state=self.Functions.index(self.function)+1
        elif pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()) and self.function=="Start Game":
            menu.inmenu=False
        elif pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()) and self.function in self.map_list:
            menu.map_chosen=self.function
            menu.state=2
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()) and self.function=="Host":
            start_new_thread(server_start,())
            menu.network=Network()
            menu.serverstarted=True
        
        
            
            



class FlashCard(pygame.sprite.Sprite):
    def __init__(self,pos,group,id):
        super().__init__(group)
        self.id=id
        self.image=pygame.Surface((100,400))
        self.image.fill("white")
        self.image.fill(["blue","red","yellow","green",][id],(0,200,100,300))
        self.rect=self.image.get_rect(topleft=pos)
        self.name=f"Player {id+1}"
        self.connected="Connected"
    
    def update(self,menu,screen):
        if self.id in menu.Connected_list:
            self.connected="Connected"
        else:
            self.connected=""
        screen.blit(Text.render(f"{self.connected}",False,(0,0,0)),(self.rect.centerx-30,self.rect.centery-130))
        screen.blit(Text.render(f"{self.name}",False,(0,0,0)),(self.rect.centerx-30,self.rect.centery-100))
        for name,id in menu.name_list:
            if id==self.id and self.id in menu.Connected_list:
                screen.blit(Text.render(f"{name}",False,(0,0,0)),(self.rect.centerx-30,self.rect.centery-60))
class inputbox(pygame.sprite.Sprite):
    def __init__(self,pos,group,function):
        super().__init__(group)
        self.image=pygame.Surface((300,50))
        self.image.fill("white")
        self.rect=self.image.get_rect(topleft=pos)
        self.text="192.168.2.164"
        self.error=False
        self.exist=False
        self.function=function
    def insert(self,menu,event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_RETURN and self.exist:
                if self.function=="Join":
                    menu.network=Network(self.text)
                    if menu.network.id:
                        menu.serverstarted=True
                        menu.state=5
                    else:
                        self.error=True
                if self.function=="Name":
                    menu.name=self.text
                    self.text=""
                    if not menu.name:
                        self.error=True
                        
            elif event.key==pygame.K_BACKSPACE:
                self.text=self.text[:-1]
            elif self.exist:
                self.text += event.unicode
    def update(self,menu,screen):
        if (menu.state==0 and self.function=="Name") or (menu.state==3 and self.function=="Join"):
            self.exist=True
        else:
            self.exist=False
            self.text=""
        screen.blit(Text.render(f"{self.text}",False,(0,0,0)),(self.rect.topleft))
        if self.error and self.function=="Join":
            screen.blit(Text.render(f"Check your ip",False,(0,0,0)),(self.rect.centerx-10,self.rect.centery+10))
        if self.error and self.function=="Name":
            screen.blit(Text.render(f"Enter a name",False,(0,0,0)),(self.rect.centerx-10,self.rect.centery+10))


Main_menu=menu()


def endscreen(information,screen):
    screen.blit(Starfight.render(f"RESULTS",False,(0,0,0)),(205,0))
    screen.blit(Text.render(f"Player 1 : {information[0]['star_count']} stars",False,(0,0,0)),(0,100))
    screen.blit(Text.render(f"Player 2 : {information[1]['star_count']} stars",False,(0,0,0)),(0,200))
    screen.blit(Text.render(f"Player 3 : {information[2]['star_count']} stars",False,(0,0,0)),(0,300))
    screen.blit(Text.render(f"Player 4 : {information[3]['star_count']} stars",False,(0,0,0)),(0,400))
    screen.blit(Text.render(f"Close the game to play again",False,(0,0,0)),(0,450))
    
# while running:
#     for event in pygame.event.get():
#         for box in Main_menu.inputboxes:
#             box.insert(Main_menu,event)
#         if event.type==pygame.QUIT:
#             running=False
    

#     screen.fill("darkgreen")
#     if serverstarted: 
#         network.send_sol(inmenu)
#         Connected_list=network.recv_sol()
#     Main_menu.show_menu(screen)
    
        
    
    

#     pygame.display.update()
#     clock.tick(60)

# pygame.quit()