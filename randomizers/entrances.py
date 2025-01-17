from dataclasses import dataclass, KW_ONLY
import re
from typing import ClassVar
from collections import defaultdict

from wwlib.dzx import DZx, _2DMA, ACTR, PLYR, SCLS
from wwlib.events import EventList
from randomizers.base_randomizer import BaseRandomizer

@dataclass(frozen=True)
class ZoneEntrance:
  stage_name: str
  room_num: int
  scls_exit_index: int
  spawn_id: int
  entrance_name: str
  island_name: str = None
  warp_out_stage_name: str = None
  warp_out_room_num: int = None
  warp_out_spawn_id: int = None
  nested_in: 'ZoneExit' = None
  
  @property
  def is_nested(self):
    return self.nested_in is not None
  
  def __repr__(self):
    return f"ZoneEntrance('{self.entrance_name}')"
  
  instances_by_name: ClassVar[dict[str, 'ZoneEntrance']] = {}
  
  def __post_init__(self):
    ZoneEntrance.instances_by_name[self.entrance_name] = self
    
    # Must be an island entrance XOR must be a nested entrance.
    assert (self.island_name is None) ^ (self.nested_in is None)
  
  def __class_getitem__(cls, entrance_name):
    return ZoneEntrance.instances_by_name[entrance_name]

@dataclass(frozen=True)
class ZoneExit:
  stage_name: str
  room_num: int
  scls_exit_index: int
  spawn_id: int
  unique_name: str
  _: KW_ONLY
  boss_stage_name: str = None
  zone_name: str = None
  
  def __repr__(self):
    return f"ZoneExit('{self.unique_name}')"
  
  instances_by_name: ClassVar[dict[str, 'ZoneExit']] = {}
  
  def __post_init__(self):
    ZoneExit.instances_by_name[self.unique_name] = self
  
  def __class_getitem__(cls, exit_name):
    return ZoneExit.instances_by_name[exit_name]

DUNGEON_ENTRANCES = [
  ZoneEntrance("Adanmae", 0, 2, 2, "Dungeon Entrance on Dragon Roost Island", "Dragon Roost Island", "sea", 13, 211),
  ZoneEntrance("sea", 41, 6, 6, "Dungeon Entrance in Forest Haven Sector", "Forest Haven", "Omori", 0, 215),
  ZoneEntrance("sea", 26, 0, 2, "Dungeon Entrance in Tower of the Gods Sector", "Tower of the Gods Sector", "sea", 26, 1),
  ZoneEntrance("sea", 1, None, None, "Dungeon Entrance in Forsaken Fortress Sector", "Forsaken Fortress Sector", "sea", 1, 0),
  ZoneEntrance("Edaichi", 0, 0, 1, "Dungeon Entrance on Headstone Island", "Headstone Island", "sea", 45, 229),
  ZoneEntrance("Ekaze", 0, 0, 1, "Dungeon Entrance on Gale Isle", "Gale Isle", "sea", 4, 232),
]
DUNGEON_EXITS = [
  ZoneExit("M_NewD2", 0, 0, 0, "Dragon Roost Cavern", boss_stage_name="M_DragB", zone_name="Dragon Roost Cavern"),
  ZoneExit("kindan", 0, 0, 0, "Forbidden Woods", boss_stage_name="kinBOSS", zone_name="Forbidden Woods"),
  ZoneExit("Siren", 0, 1, 0, "Tower of the Gods", boss_stage_name="SirenB", zone_name="Tower of the Gods"),
  ZoneExit("sea", 1, None, None, "Forsaken Fortress", boss_stage_name="M2tower", zone_name="Forsaken Fortress"),
  ZoneExit("M_Dai", 0, 0, 0, "Earth Temple", boss_stage_name="M_DaiB", zone_name="Earth Temple"),
  ZoneExit("kaze", 15, 0, 15, "Wind Temple", boss_stage_name="kazeB", zone_name="Wind Temple"),
]

MINIBOSS_ENTRANCES = [
  ZoneEntrance("kindan", 9, 0, 1, "Miniboss Entrance in Forbidden Woods", nested_in=ZoneExit["Forbidden Woods"]),
  ZoneEntrance("Siren", 14, 0, 1, "Miniboss Entrance in Tower of the Gods", nested_in=ZoneExit["Tower of the Gods"]),
  ZoneEntrance("M_Dai", 7, 0, 9, "Miniboss Entrance in Earth Temple", nested_in=ZoneExit["Earth Temple"]),
  ZoneEntrance("kaze", 2, 3, 20, "Miniboss Entrance in Wind Temple", nested_in=ZoneExit["Wind Temple"]),
]
MINIBOSS_EXITS = [
  ZoneExit("kinMB", 10, 0, 0, "Forbidden Woods Miniboss Arena"),
  ZoneExit("SirenMB", 23, 0, 0, "Tower of the Gods Miniboss Arena"),
  ZoneExit("M_DaiMB", 12, 0, 0, "Earth Temple Miniboss Arena"),
  ZoneExit("kazeMB", 6, 0, 0, "Wind Temple Miniboss Arena"),
]

BOSS_ENTRANCES = [
  ZoneEntrance("M_NewD2", 10, 1, 27, "Boss Entrance in Dragon Roost Cavern", nested_in=ZoneExit["Dragon Roost Cavern"]),
  ZoneEntrance("kindan", 16, 0, 1, "Boss Entrance in Forbidden Woods", nested_in=ZoneExit["Forbidden Woods"]),
  ZoneEntrance("Siren", 18, 0, 27, "Boss Entrance in Tower of the Gods", nested_in=ZoneExit["Tower of the Gods"]),
  ZoneEntrance("sea", 1, 16, 27, "Boss Entrance in Forsaken Fortress", nested_in=ZoneExit["Forsaken Fortress"]),
  ZoneEntrance("M_Dai", 15, 0, 27, "Boss Entrance in Earth Temple", nested_in=ZoneExit["Earth Temple"]),
  ZoneEntrance("kaze", 12, 0, 27, "Boss Entrance in Wind Temple", nested_in=ZoneExit["Wind Temple"]),
]
BOSS_EXITS = [
  ZoneExit("M_DragB", 0, None, 0, "Gohma Boss Arena"),
  ZoneExit("kinBOSS", 0, None, 0, "Kalle Demos Boss Arena"),
  ZoneExit("SirenB", 0, None, 0, "Gohdan Boss Arena"),
  ZoneExit("M2tower", 0, None, 16, "Helmaroc King Boss Arena"),
  ZoneExit("M_DaiB", 0, None, 0, "Jalhalla Boss Arena"),
  ZoneExit("kazeB", 0, None, 0, "Molgera Boss Arena"),
]

SECRET_CAVE_ENTRANCES = [
  ZoneEntrance("sea", 44, 8, 10, "Secret Cave Entrance on Outset Island", "Outset Island", "sea", 44, 10),
  ZoneEntrance("sea", 13, 2, 5, "Secret Cave Entrance on Dragon Roost Island", "Dragon Roost Island", "sea", 13, 5),
  # Note: For Fire Mountain and Ice Ring Isle, the spawn ID specified is on the sea with KoRL
  # instead of being at the cave entrance, since the player would get burnt/frozen if they were put
  # at the entrance while the island is still active.
  ZoneEntrance("sea", 20, 0, 0, "Secret Cave Entrance on Fire Mountain", "Fire Mountain", "sea", 20, 0),
  ZoneEntrance("sea", 40, 0, 0, "Secret Cave Entrance on Ice Ring Isle", "Ice Ring Isle", "sea", 40, 0),
  ZoneEntrance("Abesso", 0, 1, 1, "Secret Cave Entrance on Private Oasis", "Private Oasis", "Abesso", 0, 1),
  ZoneEntrance("sea", 29, 0, 5, "Secret Cave Entrance on Needle Rock Isle", "Needle Rock Isle", "sea", 29, 5),
  ZoneEntrance("sea", 47, 1, 5, "Secret Cave Entrance on Angular Isles", "Angular Isles", "sea", 47, 5),
  ZoneEntrance("sea", 48, 0, 5, "Secret Cave Entrance on Boating Course", "Boating Course", "sea", 48, 5),
  ZoneEntrance("sea", 31, 0, 1, "Secret Cave Entrance on Stone Watcher Island", "Stone Watcher Island", "sea", 31, 1),
  ZoneEntrance("sea", 7, 0, 1, "Secret Cave Entrance on Overlook Island", "Overlook Island", "sea", 7, 1),
  ZoneEntrance("sea", 35, 0, 1, "Secret Cave Entrance on Bird's Peak Rock", "Bird's Peak Rock", "sea", 35, 1),
  ZoneEntrance("sea", 12, 0, 1, "Secret Cave Entrance on Pawprint Isle", "Pawprint Isle", "sea", 12, 1),
  ZoneEntrance("sea", 12, 1, 5, "Secret Cave Entrance on Pawprint Isle Side Isle", "Pawprint Isle", "sea", 12, 5),
  ZoneEntrance("sea", 36, 0, 1, "Secret Cave Entrance on Diamond Steppe Island", "Diamond Steppe Island", "sea", 36, 1),
  ZoneEntrance("sea", 34, 0, 1, "Secret Cave Entrance on Bomb Island", "Bomb Island", "sea", 34, 1),
  ZoneEntrance("sea", 16, 0, 1, "Secret Cave Entrance on Rock Spire Isle", "Rock Spire Isle", "sea", 16, 1),
  ZoneEntrance("sea", 38, 0, 5, "Secret Cave Entrance on Shark Island", "Shark Island", "sea", 38, 5),
  ZoneEntrance("sea", 42, 0, 2, "Secret Cave Entrance on Cliff Plateau Isles", "Cliff Plateau Isles", "sea", 42, 2),
  ZoneEntrance("sea", 43, 0, 5, "Secret Cave Entrance on Horseshoe Island", "Horseshoe Island", "sea", 43, 5),
  ZoneEntrance("sea", 2, 0, 1, "Secret Cave Entrance on Star Island", "Star Island", "sea", 2, 1),
]
SECRET_CAVE_EXITS = [
  ZoneExit("Cave09", 0, 1, 0, "Savage Labyrinth", zone_name="Outset Island"),
  ZoneExit("TF_06", 0, 0, 0, "Dragon Roost Island Secret Cave", zone_name="Dragon Roost Island"),
  ZoneExit("MiniKaz", 0, 0, 0, "Fire Mountain Secret Cave", zone_name="Fire Mountain"),
  ZoneExit("MiniHyo", 0, 0, 0, "Ice Ring Isle Secret Cave", zone_name="Ice Ring Isle"),
  ZoneExit("TF_04", 0, 0, 0, "Cabana Labyrinth", zone_name="Private Oasis"),
  ZoneExit("SubD42", 0, 0, 0, "Needle Rock Isle Secret Cave", zone_name="Needle Rock Isle"),
  ZoneExit("SubD43", 0, 0, 0, "Angular Isles Secret Cave", zone_name="Angular Isles"),
  ZoneExit("SubD71", 0, 0, 0, "Boating Course Secret Cave", zone_name="Boating Course"),
  ZoneExit("TF_01", 0, 0, 0, "Stone Watcher Island Secret Cave", zone_name="Stone Watcher Island"),
  ZoneExit("TF_02", 0, 0, 0, "Overlook Island Secret Cave", zone_name="Overlook Island"),
  ZoneExit("TF_03", 0, 0, 0, "Bird's Peak Rock Secret Cave", zone_name="Bird's Peak Rock"),
  ZoneExit("TyuTyu", 0, 0, 0, "Pawprint Isle Chuchu Cave", zone_name="Pawprint Isle"),
  ZoneExit("Cave07", 0, 0, 0, "Pawprint Isle Wizzrobe Cave"),
  ZoneExit("WarpD", 0, 0, 0, "Diamond Steppe Island Warp Maze Cave", zone_name="Diamond Steppe Island"),
  ZoneExit("Cave01", 0, 0, 0, "Bomb Island Secret Cave", zone_name="Bomb Island"),
  ZoneExit("Cave04", 0, 0, 0, "Rock Spire Isle Secret Cave", zone_name="Rock Spire Isle"),
  ZoneExit("ITest63", 0, 0, 0, "Shark Island Secret Cave", zone_name="Shark Island"),
  ZoneExit("Cave03", 0, 0, 0, "Cliff Plateau Isles Secret Cave", zone_name="Cliff Plateau Isles"),
  ZoneExit("Cave05", 0, 0, 0, "Horseshoe Island Secret Cave", zone_name="Horseshoe Island"),
  ZoneExit("Cave02", 0, 0, 0, "Star Island Secret Cave", zone_name="Star Island"),
]

SECRET_CAVE_INNER_ENTRANCES = [
  ZoneEntrance("MiniHyo", 0, 1, 0, "Inner Entrance in Ice Ring Isle Secret Cave", nested_in=ZoneExit["Ice Ring Isle Secret Cave"]),
  ZoneEntrance("Cave03", 0, 1, 1, "Inner Entrance in Cliff Plateau Isles Secret Cave", nested_in=ZoneExit["Cliff Plateau Isles Secret Cave"]),
]
SECRET_CAVE_INNER_EXITS = [
  ZoneExit("ITest62", 0, 0, 0, "Ice Ring Isle Inner Cave"),
  ZoneExit("sea", 42, 1, 1, "Cliff Plateau Isles Inner Cave"),
]


DUNGEON_ENTRANCE_NAMES_WITH_NO_REQUIREMENTS = [
  "Dungeon Entrance on Dragon Roost Island",
]
SECRET_CAVE_ENTRANCE_NAMES_WITH_NO_REQUIREMENTS = [
  "Secret Cave Entrance on Pawprint Isle",
  "Secret Cave Entrance on Cliff Plateau Isles",
]

DUNGEON_EXIT_NAMES_WITH_NO_REQUIREMENTS = [
  "Dragon Roost Cavern",
]
PUZZLE_SECRET_CAVE_EXIT_NAMES_WITH_NO_REQUIREMENTS = [
  "Pawprint Isle Chuchu Cave",
  "Ice Ring Isle Secret Cave",
  "Bird's Peak Rock Secret Cave", # Technically this has requirements, but it's just Wind Waker+Wind's Requiem.
  "Diamond Steppe Island Warp Maze Cave",
]
COMBAT_SECRET_CAVE_EXIT_NAMES_WITH_NO_REQUIREMENTS = [
  "Rock Spire Isle Secret Cave",
]

ITEM_LOCATION_NAME_TO_EXIT_OVERRIDES: dict[str, ZoneExit] = {
  "Forbidden Woods - Mothula Miniboss Room"          : ZoneExit["Forbidden Woods Miniboss Arena"],
  "Tower of the Gods - Darknut Miniboss Room"        : ZoneExit["Tower of the Gods Miniboss Arena"],
  "Earth Temple - Stalfos Miniboss Room"             : ZoneExit["Earth Temple Miniboss Arena"],
  "Wind Temple - Wizzrobe Miniboss Room"             : ZoneExit["Wind Temple Miniboss Arena"],
  
  "Dragon Roost Cavern - Gohma Heart Container"      : ZoneExit["Gohma Boss Arena"],
  "Forbidden Woods - Kalle Demos Heart Container"    : ZoneExit["Kalle Demos Boss Arena"],
  "Tower of the Gods - Gohdan Heart Container"       : ZoneExit["Gohdan Boss Arena"],
  "Forsaken Fortress - Helmaroc King Heart Container": ZoneExit["Helmaroc King Boss Arena"],
  "Earth Temple - Jalhalla Heart Container"          : ZoneExit["Jalhalla Boss Arena"],
  "Wind Temple - Molgera Heart Container"            : ZoneExit["Molgera Boss Arena"],
  
  "Pawprint Isle - Wizzrobe Cave"                    : ZoneExit["Pawprint Isle Wizzrobe Cave"],
  
  "Ice Ring Isle - Inner Cave - Chest"               : ZoneExit["Ice Ring Isle Inner Cave"],
  "Cliff Plateau Isles - Highest Isle"               : ZoneExit["Cliff Plateau Isles Inner Cave"],
}

class EntranceRandomizer(BaseRandomizer):
  def __init__(self, rando):
    super().__init__(rando)
    
    self.item_location_name_to_zone_exit: dict[str, ZoneExit] = {}
    self.zone_exit_to_item_location_names: dict[ZoneExit, list[str]] = defaultdict(list)
    for loc_name in self.logic.item_locations:
      zone_exit = self.get_zone_exit_for_item_location(loc_name)
      if zone_exit is None:
        continue
      self.item_location_name_to_zone_exit[loc_name] = zone_exit
      self.zone_exit_to_item_location_names[zone_exit].append(loc_name)
    
    # Default entrances connections to be used if the entrance randomizer is not on.
    self.entrance_connections = {
      "Dungeon Entrance on Dragon Roost Island": "Dragon Roost Cavern",
      "Dungeon Entrance in Forest Haven Sector": "Forbidden Woods",
      "Dungeon Entrance in Tower of the Gods Sector": "Tower of the Gods",
      "Dungeon Entrance in Forsaken Fortress Sector": "Forsaken Fortress",
      "Dungeon Entrance on Headstone Island": "Earth Temple",
      "Dungeon Entrance on Gale Isle": "Wind Temple",
      
      "Miniboss Entrance in Forbidden Woods": "Forbidden Woods Miniboss Arena",
      "Miniboss Entrance in Tower of the Gods": "Tower of the Gods Miniboss Arena",
      "Miniboss Entrance in Earth Temple": "Earth Temple Miniboss Arena",
      "Miniboss Entrance in Wind Temple": "Wind Temple Miniboss Arena",
      
      "Boss Entrance in Dragon Roost Cavern": "Gohma Boss Arena",
      "Boss Entrance in Forbidden Woods": "Kalle Demos Boss Arena",
      "Boss Entrance in Tower of the Gods": "Gohdan Boss Arena",
      "Boss Entrance in Forsaken Fortress": "Helmaroc King Boss Arena",
      "Boss Entrance in Earth Temple": "Jalhalla Boss Arena",
      "Boss Entrance in Wind Temple": "Molgera Boss Arena",
      
      "Secret Cave Entrance on Outset Island": "Savage Labyrinth",
      "Secret Cave Entrance on Dragon Roost Island": "Dragon Roost Island Secret Cave",
      "Secret Cave Entrance on Fire Mountain": "Fire Mountain Secret Cave",
      "Secret Cave Entrance on Ice Ring Isle": "Ice Ring Isle Secret Cave",
      "Secret Cave Entrance on Private Oasis": "Cabana Labyrinth",
      "Secret Cave Entrance on Needle Rock Isle": "Needle Rock Isle Secret Cave",
      "Secret Cave Entrance on Angular Isles": "Angular Isles Secret Cave",
      "Secret Cave Entrance on Boating Course": "Boating Course Secret Cave",
      "Secret Cave Entrance on Stone Watcher Island": "Stone Watcher Island Secret Cave",
      "Secret Cave Entrance on Overlook Island": "Overlook Island Secret Cave",
      "Secret Cave Entrance on Bird's Peak Rock": "Bird's Peak Rock Secret Cave",
      "Secret Cave Entrance on Pawprint Isle": "Pawprint Isle Chuchu Cave",
      "Secret Cave Entrance on Pawprint Isle Side Isle": "Pawprint Isle Wizzrobe Cave",
      "Secret Cave Entrance on Diamond Steppe Island": "Diamond Steppe Island Warp Maze Cave",
      "Secret Cave Entrance on Bomb Island": "Bomb Island Secret Cave",
      "Secret Cave Entrance on Rock Spire Isle": "Rock Spire Isle Secret Cave",
      "Secret Cave Entrance on Shark Island": "Shark Island Secret Cave",
      "Secret Cave Entrance on Cliff Plateau Isles": "Cliff Plateau Isles Secret Cave",
      "Secret Cave Entrance on Horseshoe Island": "Horseshoe Island Secret Cave",
      "Secret Cave Entrance on Star Island": "Star Island Secret Cave",
      
      "Inner Entrance in Ice Ring Isle Secret Cave": "Ice Ring Isle Inner Cave",
      "Inner Entrance in Cliff Plateau Isles Secret Cave": "Cliff Plateau Isles Inner Cave",
    }
    
    self.done_entrances_to_exits: dict[ZoneEntrance, ZoneExit] = {}
    self.done_exits_to_entrances: dict[ZoneExit, ZoneEntrance] = {}
    
    for entrance_name, exit_name in self.entrance_connections.items():
      zone_entrance = ZoneEntrance[entrance_name]
      zone_exit = ZoneExit[exit_name]
      self.done_entrances_to_exits[zone_entrance] = zone_exit
      self.done_exits_to_entrances[zone_exit] = zone_entrance
    
    self.entrance_names_with_no_requirements = []
    self.exit_names_with_no_requirements = []
    if self.options.get("progression_dungeons"):
      self.entrance_names_with_no_requirements += DUNGEON_ENTRANCE_NAMES_WITH_NO_REQUIREMENTS
    if self.options.get("progression_puzzle_secret_caves") \
        or self.options.get("progression_combat_secret_caves") \
        or self.options.get("progression_savage_labyrinth"):
      self.entrance_names_with_no_requirements += SECRET_CAVE_ENTRANCE_NAMES_WITH_NO_REQUIREMENTS
    
    if self.options.get("progression_dungeons"):
      self.exit_names_with_no_requirements += DUNGEON_EXIT_NAMES_WITH_NO_REQUIREMENTS
    if self.options.get("progression_puzzle_secret_caves"):
      self.exit_names_with_no_requirements += PUZZLE_SECRET_CAVE_EXIT_NAMES_WITH_NO_REQUIREMENTS
    if self.options.get("progression_combat_secret_caves"):
      self.exit_names_with_no_requirements += COMBAT_SECRET_CAVE_EXIT_NAMES_WITH_NO_REQUIREMENTS
    # No need to check progression_savage_labyrinth, since neither of the items inside Savage have no requirements.
    
    self.nested_entrance_paths: list[list[str]] = []
    self.nesting_enabled = any(
      self.options.get(option_name)
      for option_name in [
        "randomize_miniboss_entrances",
        "randomize_boss_entrances",
        "randomize_secret_cave_inner_entrances",
      ]
    )
    
    self.safety_entrance = None
    self.race_mode_banned_exits: list[ZoneExit] = []
    self.islands_with_a_banned_dungeon: list[str] = []
  
  def is_enabled(self) -> bool:
    return any(
      self.options.get(option_name)
      for option_name in [
        "randomize_dungeon_entrances",
        "randomize_secret_cave_entrances",
        "randomize_miniboss_entrances",
        "randomize_boss_entrances",
        "randomize_secret_cave_inner_entrances",
      ]
    )
  
  def _randomize(self):
    for relevant_entrances, relevant_exits in self.get_all_entrance_sets_to_be_randomized():
      self.randomize_one_set_of_entrances(relevant_entrances, relevant_exits)
    
    self.finalize_all_randomized_sets_of_entrances()
  
  def _save(self):
    self.update_all_entrance_destinations()
    self.update_all_boss_warp_out_destinations()
  
  def write_to_spoiler_log(self) -> str:
    spoiler_log = "Entrances:\n"
    for entrance_name, dungeon_or_cave_name in self.entrance_connections.items():
      spoiler_log += "  %-50s %s\n" % (entrance_name+":", dungeon_or_cave_name)
    
    def shorten_path_name(name):
      if name == "Dungeon Entrance on Dragon Roost Island":
        return "Dragon Roost Island (Main)"
      elif name == "Secret Cave Entrance on Dragon Roost Island":
        return "Dragon Roost Island (Pit)"
      elif re.search(r"^(Dungeon|Secret Cave|Inner) Entrance (on|in) ", name):
        _, short_name = re.split(r" (?:on|in) ", name, 1)
        return short_name
      elif match := re.search(r"^(Miniboss|Boss) Entrance in ", name):
        _, short_name = re.split(r" in ", name, 1)
        return f"{short_name} ({match.group(1)})"
      else:
        return name
    
    if self.nesting_enabled:
      spoiler_log += "\n"
      
      spoiler_log += "Nested entrance paths:\n"
      for path in self.nested_entrance_paths:
        if len(path) < 3:
          # Don't include non-nested short paths (e.g. DRI -> Molgera).
          continue
        shortened_path = [shorten_path_name(name) for name in path[:-1]] + [path[-1]]
        spoiler_log += "  " + " -> ".join(shortened_path) + "\n"
    
    spoiler_log += "\n\n\n"
    return spoiler_log
  
  
  #region Randomization
  def randomize_one_set_of_entrances(self, relevant_entrances: list[ZoneEntrance], relevant_exits: list[ZoneExit]):
    for zone_entrance in relevant_entrances:
      del self.done_entrances_to_exits[zone_entrance]
    for zone_exit in relevant_exits:
      del self.done_exits_to_entrances[zone_exit]
    
    doing_dungeons = False
    doing_caves = False
    if any(ex in DUNGEON_EXITS for ex in relevant_exits):
      doing_dungeons = True
    if any(ex in SECRET_CAVE_EXITS for ex in relevant_exits):
      doing_caves = True
    
    self.rng.shuffle(relevant_entrances)
    
    self.race_mode_banned_exits.clear()
    if self.options.get("race_mode"):
      for zone_exit in relevant_exits:
        if zone_exit in BOSS_EXITS:
          assert zone_exit.unique_name.endswith(" Boss Arena")
          boss_name = zone_exit.unique_name[:-len(" Boss Arena")]
          if boss_name in self.rando.boss_rewards.banned_bosses:
            self.race_mode_banned_exits.append(zone_exit)
        elif zone_exit in DUNGEON_EXITS:
          dungeon_name = zone_exit.unique_name
          if dungeon_name in self.rando.boss_rewards.banned_dungeons:
            self.race_mode_banned_exits.append(zone_exit)
        elif zone_exit in MINIBOSS_EXITS:
          assert zone_exit.unique_name.endswith(" Miniboss Arena")
          dungeon_name = zone_exit.unique_name[:-len(" Miniboss Arena")]
          if dungeon_name in self.rando.boss_rewards.banned_dungeons:
            self.race_mode_banned_exits.append(zone_exit)
    
    self.islands_with_a_banned_dungeon.clear()
    
    doing_progress_entrances_for_dungeons_and_caves_only_start = False
    if self.rando.dungeons_and_caves_only_start:
      if doing_dungeons and self.options.get("progression_dungeons"):
        doing_progress_entrances_for_dungeons_and_caves_only_start = True
      if doing_caves and (self.options.get("progression_puzzle_secret_caves") \
          or self.options.get("progression_combat_secret_caves") \
          or self.options.get("progression_savage_labyrinth")):
        doing_progress_entrances_for_dungeons_and_caves_only_start = True
    
    self.safety_entrance = None
    if doing_progress_entrances_for_dungeons_and_caves_only_start:
      # If the player can't access any locations at the start besides dungeon/cave entrances, we choose an entrance with no requirements that will be the first place the player goes.
      # We will make this entrance lead to a dungeon/cave with no requirements so the player can actually get an item at the start.
      possible_safety_entrances = [
        e for e in relevant_entrances
        if e.entrance_name in self.entrance_names_with_no_requirements
      ]
      self.safety_entrance = self.rng.choice(possible_safety_entrances)
    
    # We calculate which exits are terminal (the end of a nested chain) per-set instead of for all
    # entrances. This is so that, for example, Ice Ring Isle counts as terminal when its inner cave
    # is not being randomized.
    non_terminal_exits = []
    for en in relevant_entrances:
      if en.nested_in is not None and en.nested_in not in non_terminal_exits:
        non_terminal_exits.append(en.nested_in)
    terminal_exits = [
      ex for ex in relevant_exits
      if ex not in non_terminal_exits
    ]
    
    remaining_entrances = relevant_entrances.copy()
    remaining_exits = relevant_exits.copy()
    
    nonprogress_entrances, nonprogress_exits = self.split_nonprogress_entrances_and_exits(remaining_entrances, remaining_exits)
    if nonprogress_entrances:
      for en in nonprogress_entrances:
        remaining_entrances.remove(en)
      for ex in nonprogress_exits:
        remaining_exits.remove(ex)
      self.randomize_one_set_of_exits(nonprogress_entrances, nonprogress_exits, terminal_exits)
    
    self.randomize_one_set_of_exits(remaining_entrances, remaining_exits, terminal_exits)
  
  def split_nonprogress_entrances_and_exits(self, relevant_entrances: list[ZoneEntrance], relevant_exits: list[ZoneExit]):
    # Splits the entrance and exit lists into two pairs: ones that should be considered nonprogress
    # on this seed (will never lead to any progress items) and ones that should be considered
    # potentially required on this race mode seed.
    # This is so that we can effectively randomize these two pairs separately without any convoluted
    # logic to ensure they don't connect to each other.
    
    nonprogress_exits = []
    for ex in relevant_exits:
      locs_for_exit = self.zone_exit_to_item_location_names[ex]
      assert locs_for_exit
      # Banned race mode dungeons still technically count as progress locations, so filter them out
      # separately first.
      nonbanned_locs = [
        loc for loc in locs_for_exit
        if loc not in self.rando.boss_rewards.banned_locations
      ]
      progress_locs = self.logic.filter_locations_for_progression(nonbanned_locs)
      if not progress_locs:
        nonprogress_exits.append(ex)
    
    nonprogress_entrances = [
      en for en in relevant_entrances
      if en.nested_in is not None
      and en.nested_in in nonprogress_exits
    ]
    
    # At this point, nonprogress_entrances includes only the inner entrances nested inside of the
    # main exits, not any of the island entrances on the sea. So we need to select N random island
    # entrances to allow all of the nonprogress exits to be accessible, where N is the difference
    # between the number of entrances and exits we currently have.
    possible_island_entrances = [
      en for en in relevant_entrances
      if en.island_name is not None
    ]
    if self.safety_entrance is not None:
      # We do need to exclude the safety_entrance from being considered, as otherwise the item rando
      # would have nowhere to put items at the start of the seed.
      possible_island_entrances.remove(self.safety_entrance)
      if self.options.get("race_mode"):
        # If we're in race mode, also exclude any other entrances one the same island as the safety
        # entrance so that we don't risk getting a banned dungeon and a required dungeon on the same
        # island.
        possible_island_entrances = [
          en for en in possible_island_entrances
          if en.island_name != self.safety_entrance.island_name
        ]
    
    num_island_entrances_needed = len(nonprogress_exits) - len(nonprogress_entrances)
    for i in range(num_island_entrances_needed):
      # Note: relevant_entrances is already shuffled, so we can just take the first result from
      # possible_island_entrances and it's the same as picking one randomly.
      nonprogress_island_entrance = possible_island_entrances.pop(0)
      nonprogress_entrances.append(nonprogress_island_entrance)
    
    assert len(nonprogress_entrances) == len(nonprogress_exits)
    
    return nonprogress_entrances, nonprogress_exits
  
  def randomize_one_set_of_exits(self, relevant_entrances: list[ZoneEntrance], relevant_exits: list[ZoneExit], terminal_exits: list[ZoneExit]):
    remaining_entrances = relevant_entrances.copy()
    remaining_exits = relevant_exits.copy()
    
    doing_banned = False
    if any(ex in self.race_mode_banned_exits for ex in relevant_exits):
      doing_banned = True
    
    if not doing_banned and self.options.get("race_mode") and any(ex in SECRET_CAVE_EXITS for ex in relevant_exits):
      # Prioritize entrances that share an island with an entrance randomized to lead into a race
      # mode banned dungeon. (Potentially DRI and Pawprint.)
      # This is because we need to prevent these islands from having a required boss or anything
      # that could potentially lead to a required boss, and if we don't do this first we can get
      # backed into a corner where there is no other option left.
      entrances_not_on_unique_islands = []
      for zone_entrance in relevant_entrances:
        if zone_entrance.is_nested:
          continue
        if zone_entrance.island_name in self.islands_with_a_banned_dungeon:
          # This island was already used on a previous call to randomize_one_set_of_exits.
          entrances_not_on_unique_islands.append(zone_entrance)
          continue
        for other_zone_entrance in relevant_entrances:
          if other_zone_entrance.is_nested:
            continue
          if other_zone_entrance.island_name == zone_entrance.island_name and other_zone_entrance != zone_entrance:
            entrances_not_on_unique_islands.append(zone_entrance)
            break
      for zone_entrance in entrances_not_on_unique_islands:
        remaining_entrances.remove(zone_entrance)
      remaining_entrances = entrances_not_on_unique_islands + remaining_entrances
    
    if self.safety_entrance is not None and self.safety_entrance in remaining_entrances:
      # In order to avoid using up all dungeons/caves with no requirements, we have to do this entrance first, so move it to the start of the array.
      remaining_entrances.remove(self.safety_entrance)
      remaining_entrances.insert(0, self.safety_entrance)
    
    while remaining_entrances:
      # Filter out boss entrances that aren't yet accessible from the sea.
      # We don't want to connect these to anything yet or we risk creating an infinite loop.
      possible_remaining_entrances = [
        en for en in remaining_entrances
        if self.get_outermost_entrance_for_entrance(en) is not None
      ]
      zone_entrance = possible_remaining_entrances.pop(0)
      remaining_entrances.remove(zone_entrance)
      
      if zone_entrance == self.safety_entrance:
        possible_remaining_exits = [e for e in remaining_exits if e.unique_name in self.exit_names_with_no_requirements]
      else:
        possible_remaining_exits = remaining_exits
      
      if len(possible_remaining_entrances) == 0 and len(remaining_entrances) > 0:
        # If this is the last entrance we have left to attach exits to, then we can't place a
        # terminal exit here, as terminal exits do not create another entrance, so one would leave
        # us with no possible way to continue placing the remaining exits on future loops.
        possible_remaining_exits = [
          ex for ex in possible_remaining_exits
          if ex not in terminal_exits
        ]
      
      # The below is debugging code for testing the caves with timers.
      #if zone_entrance.entrance_name == "Secret Cave Entrance on Fire Mountain":
      #  possible_remaining_exits = [
      #    x for x in remaining_exits
      #    if x.unique_name == "Ice Ring Isle Secret Cave"
      #  ]
      #elif zone_entrance.entrance_name == "Secret Cave Entrance on Ice Ring Isle":
      #  possible_remaining_exits = [
      #    x for x in remaining_exits
      #    if x.unique_name == "Fire Mountain Secret Cave"
      #  ]
      #else:
      #  possible_remaining_exits = [
      #    x for x in remaining_exits
      #    if x.unique_name not in ["Fire Mountain Secret Cave", "Ice Ring Isle Secret Cave"]
      #  ]
      
      if self.options.get("race_mode") and zone_entrance.island_name is not None and not doing_banned:
        # Prevent required bosses (and non-terminal exits which could potentially lead to required
        # bosses) from appearing on islands where we already placed a banned boss or dungeon.
        # This can happen with DRI and Pawprint, as these islands each have two entrances.
        # This would be bad because Race Mode's dungeon markers only tell you what island the
        # required dungeons are on, not which of the two entrances to enter.
        # So e.g. if a banned dungeon gets placed on DRI's main entrance, we will then have to fill
        # DRI's pit entrance with either a miniboss or one of the caves that does not have a nested
        # entrance inside of it.
        # We allow multiple banned dungeons on a single islands, and also allow multiple required
        # dungeons on a single island.
        if zone_entrance.island_name in self.islands_with_a_banned_dungeon:
          possible_remaining_exits = [
            ex for ex in possible_remaining_exits
            if not (ex in BOSS_EXITS or ex not in terminal_exits)
          ]
      
      if not possible_remaining_exits:
        raise Exception(f"No valid exits to place for entrance: {zone_entrance.entrance_name}")
      
      # When secret caves are mixed with nested dungeons, the large number of caves can overpower
      # the small number of dungeons, resulting in boss entrances frequently leading into caves and
      # many bosses appearing directly attached to island entrances.
      # We don't want to prevent this from happening entirely, so instead we use a weighted random
      # choice to adjust the frequency a bit so that boss entrances usually lead to either a nested
      # dungeon or a boss, and island entrances usually lead to a cave or dungeon.
      if zone_entrance in BOSS_ENTRANCES:
        zone_exit = self.rando.weighted_choice(self.rng, possible_remaining_exits, [
          (7, lambda ex: ex in DUNGEON_EXITS),
          (3, lambda ex: ex in BOSS_EXITS),
        ])
      elif zone_entrance in MINIBOSS_ENTRANCES:
        zone_exit = self.rando.weighted_choice(self.rng, possible_remaining_exits, [
          (10, lambda ex: ex in DUNGEON_EXITS),
          (5, lambda ex: ex in MINIBOSS_EXITS),
        ])
      else:
        zone_exit = self.rando.weighted_choice(self.rng, possible_remaining_exits, [
          (7, lambda ex: ex in SECRET_CAVE_EXITS),
          (3, lambda ex: ex in DUNGEON_EXITS),
        ])
      remaining_exits.remove(zone_exit)
      
      self.entrance_connections[zone_entrance.entrance_name] = zone_exit.unique_name
      # print(f"{zone_entrance.entrance_name} -> {zone_exit.unique_name}")
      self.done_entrances_to_exits[zone_entrance] = zone_exit
      self.done_exits_to_entrances[zone_exit] = zone_entrance
      if zone_exit in self.race_mode_banned_exits and zone_exit in DUNGEON_EXITS + BOSS_EXITS and zone_entrance.island_name is not None:
        self.islands_with_a_banned_dungeon.append(zone_entrance.island_name)
  
  def finalize_all_randomized_sets_of_entrances(self):
    # Ensure Forsaken Fortress didn't somehow get randomized.
    assert self.entrance_connections["Dungeon Entrance in Forsaken Fortress Sector"] == "Forsaken Fortress"
    ff_dummy_entrance = ZoneEntrance["Dungeon Entrance in Forsaken Fortress Sector"]
    ff_dummy_exit = ZoneExit["Forsaken Fortress"]
    assert self.done_entrances_to_exits[ff_dummy_entrance] == ff_dummy_exit
    assert self.done_exits_to_entrances[ff_dummy_exit] == ff_dummy_entrance
    
    non_terminal_exits = []
    for en in ZoneEntrance.instances_by_name.values():
      if en.nested_in is not None and en.nested_in not in non_terminal_exits:
        non_terminal_exits.append(en.nested_in)
    
    # Prepare some data so the spoiler log can display the nesting in terms of paths.
    self.nested_entrance_paths.clear()
    for zone_exit in ZoneExit.instances_by_name.values():
      if zone_exit in non_terminal_exits:
        continue
      zone_entrance = self.done_exits_to_entrances[zone_exit]
      seen_entrances = self.get_all_entrances_on_path_to_entrance(zone_entrance)
      path = [zone_exit.unique_name]
      for entr in seen_entrances:
        path.append(entr.entrance_name)
      path.reverse()
      self.nested_entrance_paths.append(path)
    
    self.logic.update_entrance_connection_macros()
    
    if self.options.get("race_mode"):
      # Make sure we didn't accidentally place a banned boss and a required boss on the same island.
      banned_island_names = set(
        self.get_entrance_zone_for_boss(boss_name)
        for boss_name in self.rando.boss_rewards.banned_bosses
      )
      required_island_names = set(
        self.get_entrance_zone_for_boss(boss_name)
        for boss_name in self.rando.boss_rewards.required_bosses
      )
      assert not banned_island_names & required_island_names
  #endregion
  
  
  #region Saving
  def update_all_entrance_destinations(self):
    for zone_exit, zone_entrance in self.done_exits_to_entrances.items():
      if zone_exit == ZoneExit["Forsaken Fortress"]:
        continue
      outermost_entrance = self.get_outermost_entrance_for_exit(zone_exit)
      self.update_entrance_to_lead_to_exit(zone_entrance, zone_exit, outermost_entrance)
  
  def update_all_boss_warp_out_destinations(self):
    for boss_exit in BOSS_EXITS:
      outermost_entrance = self.get_outermost_entrance_for_exit(boss_exit)
      if boss_exit.unique_name == "Helmaroc King Boss Arena":
        # Special case, does not have a warp out event, just an exit.
        self.update_helmaroc_king_arena_ganon_door(boss_exit, outermost_entrance)
        continue
      self.update_boss_warp_out_destination(boss_exit.stage_name, outermost_entrance)
  
  def update_entrance_to_lead_to_exit(self, zone_entrance: ZoneEntrance, zone_exit: ZoneExit, outermost_entrance: ZoneEntrance):
    # Update the stage this entrance takes you into.
    entrance_dzr_path = "files/res/Stage/%s/Room%d.arc" % (zone_entrance.stage_name, zone_entrance.room_num)
    entrance_dzs_path = "files/res/Stage/%s/Stage.arc" % (zone_entrance.stage_name)
    entrance_dzr = self.rando.get_arc(entrance_dzr_path).get_file("room.dzr", DZx)
    entrance_dzs = self.rando.get_arc(entrance_dzs_path).get_file("stage.dzs", DZx)
    entrance_scls = entrance_dzr.entries_by_type(SCLS)[zone_entrance.scls_exit_index]
    entrance_scls.dest_stage_name = zone_exit.stage_name
    entrance_scls.room_index = zone_exit.room_num
    entrance_scls.spawn_id = zone_exit.spawn_id
    entrance_scls.save_changes()
    
    exit_dzr_path = "files/res/Stage/%s/Room%d.arc" % (zone_exit.stage_name, zone_exit.room_num)
    exit_dzs_path = "files/res/Stage/%s/Stage.arc" % zone_exit.stage_name
    
    # Update the DRI spawn to not have spawn type 5.
    # If the DRI entrance was connected to the TotG dungeon, then exiting TotG while riding KoRL would crash the game.
    if len(entrance_dzs.entries_by_type(PLYR)) > 0:
      entrance_spawns = entrance_dzs.entries_by_type(PLYR)
    else:
      entrance_spawns = entrance_dzr.entries_by_type(PLYR)
    entrance_spawn = next(spawn for spawn in entrance_spawns if spawn.spawn_id == zone_entrance.spawn_id)
    if entrance_spawn.spawn_type == 5:
      entrance_spawn.spawn_type = 1
      entrance_spawn.save_changes()
    
    if zone_exit in MINIBOSS_EXITS + BOSS_EXITS:
      # Update the spawn you're placed at when saving and reloading inside a (mini)boss room.
      exit_dzs = self.rando.get_arc(exit_dzs_path).get_file("stage.dzs", DZx)
      # For dungeons, the stage.dzs's SCLS exit at index 0 is always where to take you when saving
      # and reloading.
      exit_scls = exit_dzs.entries_by_type(SCLS)[0]
      if zone_entrance in MINIBOSS_ENTRANCES + BOSS_ENTRANCES:
        # If a dungeon's (mini)boss entrance connects to a (mini)boss, saving and reloading inside
        # the (mini)boss room should put you at the beginning of that dungeon, not the end.
        # But if multiple dungeons are nested we don't take the player all the way back to the
        # beginning of the chain, just to the beginning of the last dungeon.
        dungeon_start_exit = entrance_dzs.entries_by_type(SCLS)[0]
        exit_scls.dest_stage_name = dungeon_start_exit.dest_stage_name
        exit_scls.room_index = dungeon_start_exit.room_index
        exit_scls.spawn_id = dungeon_start_exit.spawn_id
        exit_scls.save_changes()
      else:
        # If an island entrance (or inner cave entrance) connects directly to a (mini)boss we put
        # you right outside that entrance.
        exit_scls.dest_stage_name = zone_entrance.stage_name
        exit_scls.room_index = zone_entrance.room_num
        exit_scls.spawn_id = zone_entrance.spawn_id
        exit_scls.save_changes()
    
    if zone_exit not in BOSS_EXITS:
      # Update the entrance you're put at when leaving the dungeon/secret cave/miniboss/inner cave.
      exit_dzr = self.rando.get_arc(exit_dzr_path).get_file("room.dzr", DZx)
      exit_scls = exit_dzr.entries_by_type(SCLS)[zone_exit.scls_exit_index]
      exit_scls.dest_stage_name = zone_entrance.stage_name
      exit_scls.room_index = zone_entrance.room_num
      exit_scls.spawn_id = zone_entrance.spawn_id
      exit_scls.save_changes()
    
    # Also update the extra exits when leaving Savage Labyrinth to put you on the correct entrance when leaving.
    if zone_exit.unique_name == "Savage Labyrinth":
      for stage_and_room_name in ["Cave10/Room0", "Cave10/Room20", "Cave11/Room0"]:
        savage_dzr_path = "files/res/Stage/%s.arc" % stage_and_room_name
        savage_dzr = self.rando.get_arc(savage_dzr_path).get_file("room.dzr", DZx)
        exit_sclses = [x for x in savage_dzr.entries_by_type(SCLS) if x.dest_stage_name == "sea"]
        for exit_scls in exit_sclses:
          exit_scls.dest_stage_name = zone_entrance.stage_name
          exit_scls.room_index = zone_entrance.room_num
          exit_scls.spawn_id = zone_entrance.spawn_id
          exit_scls.save_changes()
    
    if zone_exit in SECRET_CAVE_EXITS or zone_exit == ZoneExit["Ice Ring Isle Inner Cave"]:
      # Update the sector coordinates in the 2DMA chunk so that save-and-quitting in a secret cave puts you on the correct island.
      exit_dzs = self.rando.get_arc(exit_dzs_path).get_file("stage.dzs", DZx)
      _2dma = exit_dzs.entries_by_type(_2DMA)[0]
      island_number = self.rando.island_name_to_number[outermost_entrance.island_name]
      sector_x = (island_number-1) % 7
      sector_y = (island_number-1) // 7
      _2dma.sector_x = sector_x-3
      _2dma.sector_y = sector_y-3
      _2dma.save_changes()
    
    if zone_exit.unique_name == "Fire Mountain Secret Cave":
      actors = exit_dzr.entries_by_type(ACTR)
      kill_trigger = next(x for x in actors if x.name == "VolTag")
      if zone_entrance.entrance_name == "Secret Cave Entrance on Fire Mountain":
        # Unchanged from vanilla, do nothing.
        pass
      elif zone_entrance.entrance_name == "Secret Cave Entrance on Ice Ring Isle":
        # Ice Ring's entrance leads to Fire Mountain's exit.
        # Change the kill trigger on the inside of Fire Mountain to act like the one inside Ice Ring.
        kill_trigger.type = 2
        kill_trigger.save_changes()
      else:
        # An entrance without a timer leads into this cave.
        # Remove the kill trigger actor on the inside, because otherwise it would throw the player out the instant they enter.
        exit_dzr.remove_entity(kill_trigger, ACTR)
    
    if zone_exit.unique_name == "Ice Ring Isle Secret Cave":
      actors = exit_dzr.entries_by_type(ACTR)
      kill_trigger = next(x for x in actors if x.name == "VolTag")
      if zone_entrance.entrance_name == "Secret Cave Entrance on Ice Ring Isle":
        # Unchanged from vanilla, do nothing.
        pass
      elif zone_entrance.entrance_name == "Secret Cave Entrance on Fire Mountain":
        # Fire Mountain's entrance leads to Ice Ring's exit.
        # Change the kill trigger on the inside of Ice Ring to act like the one inside Fire Mountain.
        kill_trigger.type = 1
        kill_trigger.save_changes()
      else:
        # An entrance without a timer leads into this cave.
        # Remove the kill trigger actor on the inside, because otherwise it would throw the player out the instant they enter.
        exit_dzr.remove_entity(kill_trigger, ACTR)
  
  def update_boss_warp_out_destination(self, boss_stage_name, outermost_entrance: ZoneEntrance):
    # Update the wind warp out event to take you to the correct island.
    boss_stage_arc_path = "files/res/Stage/%s/Stage.arc" % boss_stage_name
    event_list = self.rando.get_arc(boss_stage_arc_path).get_file("event_list.dat", EventList)
    warp_out_event = event_list.events_by_name["WARP_WIND_AFTER"]
    director = next(actor for actor in warp_out_event.actors if actor.name == "DIRECTOR")
    stage_change_action = next(action for action in director.actions if action.name == "NEXT")
    stage_name_prop = next(prop for prop in stage_change_action.properties if prop.name == "Stage")
    stage_name_prop.value = outermost_entrance.warp_out_stage_name
    room_num_prop = next(prop for prop in stage_change_action.properties if prop.name == "RoomNo")
    room_num_prop.value = outermost_entrance.warp_out_room_num
    spawn_id_prop = next(prop for prop in stage_change_action.properties if prop.name == "StartCode")
    spawn_id_prop.value = outermost_entrance.warp_out_spawn_id
  
  def update_helmaroc_king_arena_ganon_door(self, hk_exit: ZoneExit, outermost_entrance: ZoneEntrance):
    # Update the door that originally lead into Ganondorf's room in vanilla.
    # In the randomizer, we use it in place of the WARP_WIND_AFTER warp out event.
    exit_dzr_path = "files/res/Stage/%s/Room%d.arc" % (hk_exit.stage_name, hk_exit.room_num)
    exit_dzr = self.rando.get_arc(exit_dzr_path).get_file("room.dzr", DZx)
    exit_scls = exit_dzr.entries_by_type(SCLS)[1]
    exit_scls.dest_stage_name = outermost_entrance.warp_out_stage_name
    exit_scls.room_index = outermost_entrance.warp_out_room_num
    exit_scls.spawn_id = outermost_entrance.warp_out_spawn_id
    exit_scls.save_changes()
  #endregion
  
  
  #region Convenience methods
  def get_all_entrance_sets_to_be_randomized(self):
    dungeons = self.options.get("randomize_dungeon_entrances")
    minibosses = self.options.get("randomize_miniboss_entrances")
    bosses = self.options.get("randomize_boss_entrances")
    secret_caves = self.options.get("randomize_secret_cave_entrances")
    inner_caves = self.options.get("randomize_secret_cave_inner_entrances")
    
    mix_entrances = self.options.get("mix_entrances")
    any_dungeons = dungeons or minibosses or bosses
    any_caves = secret_caves or inner_caves
    
    if mix_entrances == "Keep Separate" and any_dungeons and any_caves:
      yield self.get_one_entrance_set(dungeons=dungeons, minibosses=minibosses, bosses=bosses)
      yield self.get_one_entrance_set(caves=secret_caves, inner_caves=inner_caves)
    elif (any_dungeons or any_caves) and mix_entrances in ["Keep Separate", "Mix Together"]:
      yield self.get_one_entrance_set(
        dungeons=dungeons, minibosses=minibosses, bosses=bosses,
        caves=secret_caves, inner_caves=inner_caves,
      )
    else:
      raise Exception("An invalid combination of entrance randomizer options was selected.")
  
  def get_one_entrance_set(self, *, dungeons=False, caves=False, minibosses=False, bosses=False, inner_caves=False):
    relevant_entrances: list[ZoneEntrance] = []
    relevant_exits: list[ZoneExit] = []
    if dungeons:
      relevant_entrances += DUNGEON_ENTRANCES
      relevant_exits += DUNGEON_EXITS
      relevant_entrances.remove(ZoneEntrance["Dungeon Entrance in Forsaken Fortress Sector"])
      relevant_exits.remove(ZoneExit["Forsaken Fortress"])
    if minibosses:
      relevant_entrances += MINIBOSS_ENTRANCES
      relevant_exits += MINIBOSS_EXITS
    if bosses:
      relevant_entrances += BOSS_ENTRANCES
      relevant_exits += BOSS_EXITS
    if caves:
      relevant_entrances += SECRET_CAVE_ENTRANCES
      relevant_exits += SECRET_CAVE_EXITS
    if inner_caves:
      relevant_entrances += SECRET_CAVE_INNER_ENTRANCES
      relevant_exits += SECRET_CAVE_INNER_EXITS
    return relevant_entrances, relevant_exits
  
  def get_outermost_entrance_for_exit(self, zone_exit: ZoneExit):
    """ Unrecurses nested dungeons to determine what the outermost (island) entrance is for a given exit."""
    zone_entrance = self.done_exits_to_entrances[zone_exit]
    return self.get_outermost_entrance_for_entrance(zone_entrance)
  
  def get_outermost_entrance_for_entrance(self, zone_entrance: ZoneEntrance):
    """ Unrecurses nested dungeons to determine what the outermost (island) entrance is for a given entrance."""
    seen_entrances = self.get_all_entrances_on_path_to_entrance(zone_entrance)
    if seen_entrances is None:
      # Undecided.
      return None
    outermost_entrance = seen_entrances[-1]
    return outermost_entrance
  
  def get_all_entrances_on_path_to_entrance(self, zone_entrance: ZoneEntrance):
    """ Unrecurses nested dungeons to build a list of all entrances leading to a given entrance."""
    seen_entrances: list[ZoneEntrance] = []
    while zone_entrance.is_nested:
      if zone_entrance in seen_entrances:
        path_str = ", ".join([e.entrance_name for e in seen_entrances])
        raise Exception(f"Entrances are in an infinite loop: {path_str}")
      seen_entrances.append(zone_entrance)
      if zone_entrance.nested_in not in self.done_exits_to_entrances:
        # Undecided.
        return None
      zone_entrance = self.done_exits_to_entrances[zone_entrance.nested_in]
    seen_entrances.append(zone_entrance)
    return seen_entrances
  
  def get_entrance_zone_for_item_location(self, location_name: str) -> str:
    # Helper function to return the entrance zone name for the location.
    # For non-dungeon and non-cave locations, the entrance zone name is simply the zone/island name.
    # However, when entrances are randomized, the entrance zone name may differ from the zone name
    # for dungeons and caves.
    
    loc_zone_name, _ = self.logic.split_location_name_by_zone(location_name)
    
    if not self.logic.is_dungeon_or_cave(location_name):
      return loc_zone_name
    
    if loc_zone_name in ["Hyrule", "Ganon's Tower", "Mailbox"]:
      # Some extra locations that are considered dungeon locations by the logic but are not part of
      # entrance randomizer. Hyrule, Ganon's Tower, and the handful of Mailbox locations that depend
      # on beating dungeon bosses.
      return loc_zone_name
    
    zone_exit = self.item_location_name_to_zone_exit[location_name]
    assert zone_exit is not None, f"Could not determine entrance zone for item location: {location_name}"
    
    outermost_entrance = self.get_outermost_entrance_for_exit(zone_exit)
    return outermost_entrance.island_name
  
  def get_zone_exit_for_item_location(self, location_name: str):
    if not self.logic.is_dungeon_or_cave(location_name):
      return None
    
    loc_zone_name, _ = self.logic.split_location_name_by_zone(location_name)
    
    if loc_zone_name in ["Hyrule", "Ganon's Tower", "Mailbox"]:
      return None
    
    zone_exit = ITEM_LOCATION_NAME_TO_EXIT_OVERRIDES.get(location_name, None)
    
    if zone_exit is None:
      for possible_exit in ZoneExit.instances_by_name.values():
        if possible_exit.zone_name == loc_zone_name:
          zone_exit = possible_exit
          break
    
    return zone_exit
  
  def get_entrance_zone_for_boss(self, boss_name: str) -> str:
    boss_arena_name = f"{boss_name} Boss Arena"
    zone_exit = ZoneExit[boss_arena_name]
    outermost_entrance = self.get_outermost_entrance_for_exit(zone_exit)
    return outermost_entrance.island_name
  #endregion
