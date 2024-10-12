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
    """This bot's name"""

    RACE: Race = Race.Terran
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    async def on_start(self):
        """
        This code runs once at the start of the game
        Do things here before the game starts
        """
        print("Game started")

    async def on_step(self, iteration: int):
        """
        This code runs continually throughout the game
        Populate this function with whatever your bot should do!
        """
        await self.distribute_workers()
        await self.build_workers()
        await self.build_supply()
        await self.build_rax()
        await self.build_gas()
        await self.build_marines()
        await self.attack()
        pass

    async def build_workers(self):
            bases=self.townhalls.ready
            for base in bases:
                if (self.can_afford(UnitTypeId.SCV) 
                    and base.is_idle
                    and self.workers.amount < self.townhalls.amount * 22):
                    base.train(UnitTypeId.SCV)

    async def build_supply(self):
         base = self.townhalls.ready.random
         pos = base.position.towards(self.enemy_start_locations[0], 10)
         if (self.supply_left < 3 
             and self.already_pending(UnitTypeId.SUPPLYDEPOT)==0
             and self.can_afford(UnitTypeId.SUPPLYDEPOT) ):
              await self.build(UnitTypeId.SUPPLYDEPOT, near=pos)
    
    async def build_rax(self):
         if (self.structures(UnitTypeId.SUPPLYDEPOT).ready
             and self.can_afford(UnitTypeId.BARRACKS)
             and len(self.structures(UnitTypeId.BARRACKS))<3):
              base = self.townhalls.ready.random
              pos = base.position.towards(self.enemy_start_locations[0], 20)
              await self.build(UnitTypeId.BARRACKS, near=pos)

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
            raxes=self.structures(UnitTypeId.BARRACKS)
            for rax in raxes:
                if (self.can_afford(UnitTypeId.MARINE) 
                    and rax.is_idle):
                    rax.train(UnitTypeId.MARINE)
            
    async def attack(self):
         armycount=self.units(UnitTypeId.MARINE).amount
         marines = self.units(UnitTypeId.MARINE).ready.idle
         for marine in marines:
              if armycount>20:
                   marine.attack(self.enemy_start_locations[0])
              

    async def on_end(self, result: Result):
        """
        This code runs once at the end of the game
        Do things here after the game ends
        """
        print("Game ended.")

    