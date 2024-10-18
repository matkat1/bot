from sc2.bot_ai import BotAI, Race
from sc2.data import Result
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.player import Bot, Computer



class CompetitiveBot(BotAI):
    NAME: str = "MacroPolo"
    RACE: Race = Race.Terran

    building_slots: []

    async def on_start(self):
        
        base = self.townhalls.ready.random
        main_position = base.position.towards(self.enemy_start_locations[0], 15)
        main_ramp = await self.find_main_ramp(main_position)
        self.building_slots = await self.find_building_slots(main_ramp)
        print("Game started")
        


    async def on_step(self, iteration: int):
        
        await self.distribute_workers()
        await self.build_workers()
        await self.build_supply()
        await self.build_rax()
        await self.build_gas()
        await self.build_marines()
        await self.attack()
        pass
    
    async def find_building_slots(self, main_ramp):
        base = self.townhalls.ready.random
        main_position = base.position.towards(self.enemy_start_locations[0], 15)
        start = []
        start.append(base.position[0])
        start.append(base.position[1])
        xd=main_ramp.barracks_correct_placement
        tmp2=[2,2]
        tmp2[0]=xd[0]
        tmp2[1]=xd[1]
        slots=[main_ramp.barracks_correct_placement]
        add=1
        point = Point2((tmp2[0], (tmp2[1] + (add * 3)) ))
        while(await self.check_build_spot(point)):
             slots.append(Point2((tmp2[0],(tmp2[1]+(add*3)))))
             add=add+1
             point = Point2((tmp2[0], (tmp2[1] + (add * 3)) ))
        add=1
        point = Point2((tmp2[0], (tmp2[1] - (add * 3)) ))
        while(await self.check_build_spot(point)):
             slots.append(Point2((tmp2[0],(tmp2[1]-(add*3)))))
             add=add+1
             point = Point2((tmp2[0], (tmp2[1] - (add * 3)) ))
        add=0
        tmp2[0]-=7
        point = Point2((tmp2[0], (tmp2[1] + (add * 3)) ))
        if(start[1]>main_position[1]):
          for i in range(4):
              if (await self.check_build_spot(point)):
                 slots.append(Point2((tmp2[0],(tmp2[1]+(add*3)))))
              add=add+1
              point = Point2((tmp2[0], (tmp2[1] + (add * 3)) ))
        add=0
        point = Point2((tmp2[0], (tmp2[1] - (add * 3)) ))
        if(start[1]<main_position[1]):
          for i in range(4):
               if (await self.check_build_spot(point)):
                 slots.append(Point2((tmp2[0],(tmp2[1]-(add*3)))))
               add=add+1
               point = Point2((tmp2[0], (tmp2[1] - (add * 3)) ))
        add=0
        tmp2[0]+=14
        if(start[1]>main_position[1]):
          for i in range(4):
               if (await self.check_build_spot(point)):
                 slots.append(Point2((tmp2[0],(tmp2[1]+(add*3)))))
               add=add+1
               point = Point2((tmp2[0], (tmp2[1] + (add * 3)) ))
        add=0
        if(start[1]<main_position[1]):
          point = Point2((tmp2[0], (tmp2[1] - (add * 3)) ))
          for i in range(4):
               if (await self.check_build_spot(point)):
                 slots.append(Point2((tmp2[0],(tmp2[1]-(add*3)))))
               add=add+1
               point = Point2((tmp2[0], (tmp2[1] - (add * 3)) ))
        return slots    

    async def draw_main_asci(self):
     
        x1=int(self.start_location[0])
        y1=int(self.start_location[1])
        base=self.start_location
        pos = base.position.towards(self.enemy_start_locations[0], 15)
        pos=(int(pos[0]),int(pos[1]))
        x2=int(pos[0])
        y2=int(pos[1])
        for x in range (60):
            for y in range (60):
                 if (x==30 or y==30):
                      print("?", end="")
                 elif (x1+30-x==x2 or y1+30-y==y2):
                      print("!", end="")
                 elif self.game_info.placement_grid.is_set((x1+30-x,y1+30-y)):
                      print("#", end="")
                 else:
                      print(" ", end="")
            print("")

    async def find_main_ramp(self, main):
        ramps=self.game_info._find_ramps_and_vision_blockers()
        ramps=ramps[0]
        min=99999
        main_ramp=ramps[0]
        for ramp in ramps:
             dist=main.distance_to(ramp.top_center)
             if (dist<min):
                  min = dist
                  main_ramp = ramp
        return main_ramp
         
    async def check_build_spot(self, pos: Point2):
         grid=self.game_info.placement_grid
         x1=pos[0]
         y1=pos[1]
         check=True
         for x in range (7):
              for y in range(3):
                   if(not grid.is_set((int(x1-3+x), int(y1-1+y)))):
                        check=False
                        break
         if (check):
              return True
         else: 
              return False

    async def build_workers(self):
            bases=self.townhalls.ready
            for base in bases:
                if (self.can_afford(UnitTypeId.SCV) 
                    and base.is_idle
                    and self.workers.amount < self.townhalls.amount * 22):
                    base.train(UnitTypeId.SCV)

    async def build_supply(self):
         base=self.start_location
         pos = base.position.towards(self.enemy_start_locations[0], -15)
         if (self.supply_left < 3 
             and self.already_pending(UnitTypeId.SUPPLYDEPOT)==0
             and self.can_afford(UnitTypeId.SUPPLYDEPOT) ):
              await self.build(UnitTypeId.SUPPLYDEPOT, near=pos)
    
    async def build_rax(self):
        if (self.structures(UnitTypeId.SUPPLYDEPOT).ready
            and self.can_afford(UnitTypeId.BARRACKS)
            and len(self.structures(UnitTypeId.BARRACKS))<24):
                for i in range(len(self.building_slots)):
                    pos=self.building_slots[i]
                    worker = self.select_build_worker(pos)
                    if worker is None:
                         pass
                    if (await self.can_place_single(UnitTypeId.BARRACKS, pos)):
                        worker.build(UnitTypeId.BARRACKS, pos)
                        worker.stop(queue=True)
                        pass
                    else:
                         continue

    async def build_gas(self):
         if (self.structures(UnitTypeId.BARRACKS)
             and self.can_afford(UnitTypeId.REFINERY)):
              for base in self.townhalls.ready:
                   geysers=self.vespene_geyser.closer_than(10,base)
                   for geyser in geysers:
                        if (not self.can_afford(UnitTypeId.REFINERY)):
                             break
                        worker = self.select_build_worker(geyser.position)
                        if worker is None:
                             break
                        if (not self.gas_buildings or not self.gas_buildings.closer_than(1, geyser)):
                             worker.build(UnitTypeId.REFINERY, geyser)
                             worker.stop(queue=True)
              
    async def build_marines(self):
            slots=self.structures(UnitTypeId.BARRACKS)
            for rax in slots:
                if (self.can_afford(UnitTypeId.MARINE) 
                    and rax.is_idle):
                    rax.train(UnitTypeId.MARINE)
            
    async def attack(self):
         armycount=self.units(UnitTypeId.MARINE).amount
         marines = self.units(UnitTypeId.MARINE).ready.idle
         for marine in marines:
              if armycount>100:
                   marine.attack(self.enemy_start_locations[0])
              
    async def on_end(self, result: Result):
        print("Game ended.")

    