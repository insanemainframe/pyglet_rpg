#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
import random
import pdb

location_WIDTH_TILES = 100
location_HEIGHT_TILES = 100

TILE_SEA = 0
TILE_LAND = 1

NUMBER_OF_GENERATIONS = 3000

class locationPoint:
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

def setlocationTile(map_row, map_col):
  # If map coordinates are out-of-bounds then
  # location-wrap them
  if map_row < 0:
    map_row = location_HEIGHT_TILES + map_row
  elif map_row >= location_HEIGHT_TILES:
    map_row = map_row - location_HEIGHT_TILES

  if map_col < 0: 
    map_col = location_WIDTH_TILES + map_col
  elif map_col >= location_WIDTH_TILES:
    map_col = map_col - location_WIDTH_TILES

  if (location_map[map_row][map_col] == TILE_SEA):
    rand_tile = weighted_rand.getRandomValue()
    location_map[map_row][map_col] = rand_tile
    return location_map[map_row][map_col]

  # DIRTY HACK DOESN"T ADDRESS THE MAIN ISSUE
  return TILE_SEA#location_map[map_row][map_col]
 
# Takes a location point as input and
# looks at the surrounding 8 points
def grow_location_seed(curr_pt):
  new_land_pts = []
  
  if (setlocationTile(curr_pt.row-1,curr_pt.col-1) == TILE_LAND):
    new_land_pts.append(locationPoint(curr_pt.row-1,curr_pt.col-1));

  if (setlocationTile(curr_pt.row-1,curr_pt.col) == TILE_LAND):
    new_land_pts.append(locationPoint(curr_pt.row-1,curr_pt.col));

  if (setlocationTile(curr_pt.row-1,curr_pt.col+1) == TILE_LAND):
    new_land_pts.append(locationPoint(curr_pt.row-1,curr_pt.col+1));

  if (setlocationTile(curr_pt.row,curr_pt.col-1) == TILE_LAND):
    new_land_pts.append(locationPoint(curr_pt.row,curr_pt.col-1));

  if (setlocationTile(curr_pt.row,curr_pt.col+1) == TILE_LAND):
    new_land_pts.append(locationPoint(curr_pt.row,curr_pt.col+1));

  if (setlocationTile(curr_pt.row+1,curr_pt.col-1) == TILE_LAND):
    new_land_pts.append(locationPoint(curr_pt.row+1,curr_pt.col-1));

  if (setlocationTile(curr_pt.row+1,curr_pt.col) == TILE_LAND):
    new_land_pts.append(locationPoint(curr_pt.row+1,curr_pt.col));

  if (setlocationTile(curr_pt.row+1,curr_pt.col+1) == TILE_LAND):
    new_land_pts.append(locationPoint(curr_pt.row+1,curr_pt.col+1));

  return new_land_pts

# Initialize all location map tiles to sea
location_map = []
for iLatitude in range(0,location_HEIGHT_TILES):
  location_map.append([TILE_SEA]*location_WIDTH_TILES)

# Initialize with seed points
land_pts = deque([locationPoint(52,12), locationPoint(61,13)]);
generation_count = 2
while land_pts and generation_count<NUMBER_OF_GENERATIONS:
  curr_pt = land_pts.popleft()
  location_map[curr_pt.row][curr_pt.col] = TILE_LAND
  #pdb.set_trace()
  land_pts.extend(grow_location_seed(curr_pt))
  
  generation_count += 1
#pdb.set_trace()
#for landPt in land_pts:
#  location_map

# Now that the landmass has been generated lets output it to 
# a file so it can be analyzed

# Open locationmap.txt for writing as buffered
fileHandle = open('locationmap.txt', 'w', 1);

for iRow in range(0,location_HEIGHT_TILES):
  latitudeStr = ",".join(map(str,location_map[iRow]))
  fileHandle.write(latitudeStr)
  fileHandle.write("\n")
  
fileHandle.close();