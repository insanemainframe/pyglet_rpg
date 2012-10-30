#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
import random
import pdb

WORLD_WIDTH_TILES = 100
WORLD_HEIGHT_TILES = 100

TILE_SEA = 0
TILE_LAND = 1

NUMBER_OF_GENERATIONS = 3000

class WorldPoint:
  def __init__(self, newRow, newCol):
    self.row = newRow
    self.col = newCol

# This class returns one of two values based on
# a weighted probability that was specified.
# This instance definition:
#      WeightedRandom(2, 0.45, 10, 0.55)
#      The value of 2 will have a 45% chance of being returned
#      THe value of 10 will have a 55% chance of being returned  
# weighted selection algorithm is a variant of the Roulette Wheel selection algorithm
class WeightedRandom:
  """ valueOne -> any integer 
      valueOneProb -> must
  """
  def __init__(self, valueOne, valueOneProb, valueTwo, valueTwoProb):
    probHundredOne = int(valueOneProb*100)    
    probHundredTwo = int(valueTwoProb*100)    
  
    self.prob_array = []

    # If given invalid probabilities then abort
    if (probHundredOne+probHundredTwo != 100):
      return;

    self.prob_array.extend([valueOne]*probHundredOne)
    self.prob_array.extend([valueTwo]*probHundredTwo)

  def getRandomValue(self):
    if (self.prob_array):
      rand_value = random.randrange(0,len(self.prob_array))
      return self.prob_array[rand_value]
    else:
      return;

weighted_rand = WeightedRandom(TILE_SEA, 0.75, TILE_LAND, 0.25)

def setWorldTile(map_row, map_col):
  # If map coordinates are out-of-bounds then
  # world-wrap them
  if map_row < 0:
    map_row = WORLD_HEIGHT_TILES + map_row
  elif map_row >= WORLD_HEIGHT_TILES:
    map_row = map_row - WORLD_HEIGHT_TILES

  if map_col < 0: 
    map_col = WORLD_WIDTH_TILES + map_col
  elif map_col >= WORLD_WIDTH_TILES:
    map_col = map_col - WORLD_WIDTH_TILES

  if (world_map[map_row][map_col] == TILE_SEA):
    rand_tile = weighted_rand.getRandomValue()
    world_map[map_row][map_col] = rand_tile
    return world_map[map_row][map_col]

  # DIRTY HACK DOESN"T ADDRESS THE MAIN ISSUE
  return TILE_SEA#world_map[map_row][map_col]
 
# Takes a world point as input and
# looks at the surrounding 8 points
def grow_world_seed(curr_pt):
  new_land_pts = []
  
  if (setWorldTile(curr_pt.row-1,curr_pt.col-1) == TILE_LAND):
    new_land_pts.append(WorldPoint(curr_pt.row-1,curr_pt.col-1));

  if (setWorldTile(curr_pt.row-1,curr_pt.col) == TILE_LAND):
    new_land_pts.append(WorldPoint(curr_pt.row-1,curr_pt.col));

  if (setWorldTile(curr_pt.row-1,curr_pt.col+1) == TILE_LAND):
    new_land_pts.append(WorldPoint(curr_pt.row-1,curr_pt.col+1));

  if (setWorldTile(curr_pt.row,curr_pt.col-1) == TILE_LAND):
    new_land_pts.append(WorldPoint(curr_pt.row,curr_pt.col-1));

  if (setWorldTile(curr_pt.row,curr_pt.col+1) == TILE_LAND):
    new_land_pts.append(WorldPoint(curr_pt.row,curr_pt.col+1));

  if (setWorldTile(curr_pt.row+1,curr_pt.col-1) == TILE_LAND):
    new_land_pts.append(WorldPoint(curr_pt.row+1,curr_pt.col-1));

  if (setWorldTile(curr_pt.row+1,curr_pt.col) == TILE_LAND):
    new_land_pts.append(WorldPoint(curr_pt.row+1,curr_pt.col));

  if (setWorldTile(curr_pt.row+1,curr_pt.col+1) == TILE_LAND):
    new_land_pts.append(WorldPoint(curr_pt.row+1,curr_pt.col+1));

  return new_land_pts

# Initialize all world map tiles to sea
world_map = []
for iLatitude in range(0,WORLD_HEIGHT_TILES):
  world_map.append([TILE_SEA]*WORLD_WIDTH_TILES)

# Initialize with seed points
land_pts = deque([WorldPoint(52,12), WorldPoint(61,13)]);
generation_count = 2
while land_pts and generation_count<NUMBER_OF_GENERATIONS:
  curr_pt = land_pts.popleft()
  world_map[curr_pt.row][curr_pt.col] = TILE_LAND
  #pdb.set_trace()
  land_pts.extend(grow_world_seed(curr_pt))
  
  generation_count += 1
#pdb.set_trace()
#for landPt in land_pts:
#  world_map

# Now that the landmass has been generated lets output it to 
# a file so it can be analyzed

# Open worldmap.txt for writing as buffered
fileHandle = open('worldmap.txt', 'w', 1);

for iRow in range(0,WORLD_HEIGHT_TILES):
  latitudeStr = ",".join(map(str,world_map[iRow]))
  fileHandle.write(latitudeStr)
  fileHandle.write("\n")
  
fileHandle.close();