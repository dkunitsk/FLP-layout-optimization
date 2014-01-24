#! /Frameworks/Python.framework/Versions/2.7/lib/python2.7/
from __future__ import division
import math
import random
from random import choice
from random import shuffle
import time
from graphics import *

dataset_name = "FOM12"
##############/parameter setup
FLOOR_X = 14.7
FLOOR_Y = 13.0
AREA_MINS = [float(i) for i in [16, 16, 16, 16, 36, 36, 9, 9, 9, 9, 9, 9]]
N_DEPTS = len(AREA_MINS)
DEPTS = [i+1 for i in range(N_DEPTS)]
L_BND_ALL = {i+1: [2, 2, 2, 2, 3, 3, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5][i] for i in range(N_DEPTS)} 
U_BND_ALL = {i+1: [8, 8, 8, 8, 12, 12, 6, 6, 6, 6, 6, 6][i] for i in range(N_DEPTS)} 
_param_f = """0	1	0	0	0	0	0	0	0	0	0	0
1	0	1	0	0	0	0	0	0	0	0	0
0	1	0	1	0	0	0	0	0	0	0	0
0	0	1	0	1	0	0	0	0	0	0	0
0	0	0	1	0	1	0	0	0	0	0	0
0	0	0	0	1	0	1	0	0	0	0	0
0	0	0	0	0	1	0	1	0	0	0	0
0	0	0	0	0	0	1	0	1	0	0	0
0	0	0	0	0	0	0	1	0	1	0	0
0	0	0	0	0	0	0	0	1	0	1	0
0	0	0	0	0	0	0	0	0	1	0	1
0	0	0	0	0	0	0	0	0	0	1	0""" 
def _parse_freq():
	arr = []
	for i in _param_f.splitlines():
		arr.append(map(float, i.replace('t', ' ').rsplit()))
	return arr
class _FlowFreqs(object):
	freq_arr = _parse_freq()
	
	def __init__(self): 
		pass
		
	@classmethod
	def getFlowBetween(cls, i, j):
		return cls.freq_arr[i-1][j-1]

	@classmethod
	def getRow(cls, i):
		return cls.freq_arr[i-1]
FLOW_FREQ = _FlowFreqs() 
##############\


##############/start graphics window
vis_scale = 75
vis_offset = 0.005*vis_scale
win = GraphWin(dataset_name + ' (BEST)', FLOOR_X*vis_scale, FLOOR_Y*vis_scale)
win.setCoords(-vis_offset, -vis_offset, 
			  FLOOR_X+vis_offset, FLOOR_Y+vis_offset)
floor_vis = Rectangle(Point(0,0), Point(FLOOR_X, FLOOR_Y))
floor_vis.setWidth(3) 
floor_vis.setOutline(color_rgb(125, 125, 125))
floor_vis.draw(win)

win2 = GraphWin(dataset_name + ' (WORST)', FLOOR_X*vis_scale, FLOOR_Y*vis_scale)
win2.setCoords(-vis_offset, -vis_offset, 
			  FLOOR_X+vis_offset, FLOOR_Y+vis_offset)
floor_vis2 = Rectangle(Point(0,0), Point(FLOOR_X, FLOOR_Y))
floor_vis2.setWidth(3) 
floor_vis2.setOutline(color_rgb(125, 125, 125))
floor_vis2.draw(win2)
###############\

def createAmortizedAreaDictionary():
	excess = FLOOR_X * FLOOR_Y - sum(AREA_MINS)
	return {i+1 : (AREA_MINS[i] + (AREA_MINS[i]/sum(AREA_MINS)*excess)) for i in range(N_DEPTS)}
areas_w_excess_dict = createAmortizedAreaDictionary()
class SpaceNode(object):
	def __init__(self, name, Lx, Ly, LL_corner_x, LL_corner_y, remaining_depts_list, left_child, right_child):
		self.name = name
		self.Lx = Lx
		self.Ly = Ly
		self.LL_corner_x = LL_corner_x
		self.LL_corner_y = LL_corner_y
		self.area = Lx * Ly
		self.remaining_depts_list = remaining_depts_list
		self.left_child = left_child
		self.right_child = right_child
		self.isLeaf = False
	def getCentroidX(self): return self.LL_corner_x + (self.Lx / 2)
	def getCentroidY(self): return self.LL_corner_y + (self.Ly / 2)
layout_dictionary = {i+1 : None for i in range(N_DEPTS)}
class TreeNode(object):
	def __init__(self, left, right, arr):
		self.left = left
		self.right = right
		self.arr = arr
		self.isLeaf = False
		self.cut = None
		self.bounding_curve = None
	def isLeaf(self): return self.isLeaf;


def generateBoundingCurves(step_size):
	bounding_curve_dict = {}
	for i in range(N_DEPTS):
		dept = i+1
		bounding_curve = []
		x_coord = 0
		 
		while (x_coord <= FLOOR_X):
			if ((x_coord < L_BND_ALL.get(dept)) or (x_coord > U_BND_ALL.get(dept))):
				bounding_curve.append(None);
			else:
				height = AREA_MINS[i]/x_coord
				if ((height < L_BND_ALL.get(dept)) or (height > U_BND_ALL.get(dept))): 
					bounding_curve.append(None);
				else:
					bounding_curve.append(round(height, 2));
			x_coord += step_size

		bounding_curve_dict[dept] = bounding_curve
		bounding_curve = []
	return bounding_curve_dict;

def generateSlicingTree(parent_tree_node):
	arr = parent_tree_node.arr
	if len(arr) == 1:
		parent_tree_node.isLeaf = True
		return parent_tree_node
	else:
		split = random.randint(1, len(arr)-1);
		cut = choice(['V', 'H'])
		groupA = arr[:split]
		groupB = arr[split:]

		if cut == 'H':
			parent_tree_node.cut = 'H'
		else:
			parent_tree_node.cut = 'V'

		parent_tree_node.left = generateSlicingTree(TreeNode(None, None, groupA))
		parent_tree_node.right = generateSlicingTree(TreeNode(None, None, groupB))
	return parent_tree_node;


bounding_curve_dict = generateBoundingCurves(0.1);
def calculateBoundingCurves(tree_node):
	# This is done bottom-to-top
	if tree_node.isLeaf:
		tree_node.bounding_curve = bounding_curve_dict[tree_node.arr[0]]
		return tree_node.bounding_curve
	else:
		# Initialize sum_bounding_curve w/ None values
		sum_bounding_curve = [None]*len(bounding_curve_dict[1]);
		left_curve = calculateBoundingCurves(tree_node.left)
		right_curve = calculateBoundingCurves(tree_node.right)

		if tree_node.cut == 'H':
			for i in range(len(left_curve)):
				if left_curve[i] is not None and right_curve[i] is not None:
					sum_bounding_curve[i] = left_curve[i] + right_curve[i]
		else:
			for i in range(len(left_curve)):
				if left_curve[i] is not None:
					try:
						j = 0
						for k in range(len(right_curve)):
							if right_curve[k] is not None:
								if abs(right_curve[k]- left_curve[i]) < 0.01:
									j = k;
									break;
						if j != 0:
							sum_bounding_curve[i+j] = left_curve[i]
					except:
						pass
		
		tree_node.bounding_curve = sum_bounding_curve
		return tree_node.bounding_curve;






def generateSimpleLayout(parent_space_node):
	def add(x, y): return x + y; 
	remaining_depts = parent_space_node.remaining_depts_list
	if len(remaining_depts) == 1:
		parent_space_node.isLeaf = True
		layout_dictionary[remaining_depts[0]] = parent_space_node
	
	else:
		split = random.randint(1, len(remaining_depts)-1);
		cut = choice(['V', 'H'])
		groupA = remaining_depts[:split]
		groupB = remaining_depts[split:]
		
		if cut == 'V':
			total_area_groupA = reduce(add, [areas_w_excess_dict[i] for i in groupA])
			total_area_groupB = parent_space_node.area - total_area_groupA
			Lx_groupA = total_area_groupA / parent_space_node.Ly
			Lx_groupB = parent_space_node.Lx - Lx_groupA

			node_groupA = SpaceNode(str(groupA), Lx_groupA, parent_space_node.Ly, parent_space_node.LL_corner_x, parent_space_node.LL_corner_y, groupA, None, None) 
			node_groupB = SpaceNode(str(groupB), Lx_groupB, parent_space_node.Ly, (parent_space_node.LL_corner_x + Lx_groupA), parent_space_node.LL_corner_y, groupB, None, None)

			parent_space_node.left_child = node_groupA
			parent_space_node.right_child = node_groupB

			generateSimpleLayout(node_groupA)
			generateSimpleLayout(node_groupB)
		if cut == 'H': 
			total_area_groupA = reduce(add, [areas_w_excess_dict[i] for i in groupA])
			total_area_groupB = parent_space_node.area - total_area_groupA
			Ly_groupA = total_area_groupA / parent_space_node.Lx
			Ly_groupB = parent_space_node.Ly - Ly_groupA

			node_groupA = SpaceNode(str(groupA), parent_space_node.Lx, Ly_groupA, parent_space_node.LL_corner_x, parent_space_node.LL_corner_y, groupA, None, None) 
			node_groupB = SpaceNode(str(groupB), parent_space_node.Lx, Ly_groupB, parent_space_node.LL_corner_x, (parent_space_node.LL_corner_y + Ly_groupA), groupB, None, None)

			parent_space_node.left_child = node_groupA
			parent_space_node.right_child = node_groupB

			generateSimpleLayout(node_groupA)
			generateSimpleLayout(node_groupB)

	return layout_dictionary




def calculateOFV(layout_dictionary):
	cost = 0
	for thisdept in layout_dictionary: 
		dept_centroid_x = layout_dictionary[thisdept].getCentroidX()
		dept_centroid_y = layout_dictionary[thisdept].getCentroidY()

		for otherdept in layout_dictionary:
			dist = abs(dept_centroid_x - layout_dictionary[otherdept].getCentroidX()) + abs(dept_centroid_y - layout_dictionary[otherdept].getCentroidY())
			cost = cost + dist * (FLOW_FREQ.getFlowBetween(thisdept, otherdept))

	return cost
def layoutAcceptable(layout_dictionary):
	for thisdept in layout_dictionary: 
		if layout_dictionary[thisdept].Lx < L_BND_ALL[thisdept] or layout_dictionary[thisdept].Lx > U_BND_ALL[thisdept] or layout_dictionary[thisdept].Ly < L_BND_ALL[thisdept] or layout_dictionary[thisdept].Ly > U_BND_ALL[thisdept]:
			return False
	return True

def main():

	print calculateBoundingCurves(generateSlicingTree(TreeNode(None, None, DEPTS)))
	


	min_cost = None
	best_layout = None
	max_cost = None
	worst_layout = None
	
	firstAcceptableRun = True
	generated_count = 0
	acceptable_count = 0 

	###
	for i in range(1000):
		full_dept_list = [x+1 for x in range(N_DEPTS)]
		shuffle(full_dept_list)
		originalNode = SpaceNode(str(full_dept_list), FLOOR_X, FLOOR_Y, 0, 0, full_dept_list, None, None)
		layout = generateSimpleLayout(originalNode)
		generated_count += 1
		
		if not layoutAcceptable(layout):
			continue
		
		cost = calculateOFV(layout)
		acceptable_count += 1
		
		if firstAcceptableRun:
			best_layout = layout.copy()
			worst_layout = layout.copy()
			min_cost = cost
			max_cost = cost
			firstAcceptableRun = False

		else:
			if cost < min_cost:
				min_cost = cost
				best_layout = layout.copy()
			if cost > max_cost:
				max_cost = cost
				worst_layout = layout.copy()	
	

	print '\n---------'
	if firstAcceptableRun:
		print '***FAILED***\n'
		return
	print 'min cost: ', min_cost, '\nmax cost: ', max_cost
	print '\ntotal layouts generated: ', generated_count
	print 'acceptable layouts:      ', acceptable_count
	print '% acceptable:            ', str(round((acceptable_count/generated_count)*100, 3)) + '%', '\n'


	for i in range(N_DEPTS):
		a = best_layout[i+1]
		a_rect = Rectangle(Point(a.LL_corner_x, a.LL_corner_y),
								  Point(a.LL_corner_x + a.Lx, a.LL_corner_y + a.Ly))
		a_rect.draw(win)
		a_text = Text(Point(a.LL_corner_x + a.Lx/2, a.LL_corner_y + a.Ly/2), a.name.strip('[]') + '  area=' + str(round(a.area, 3)))
		a_text.draw(win)

	for i in range(N_DEPTS):
		a = worst_layout[i+1]
		a_rect = Rectangle(Point(a.LL_corner_x, a.LL_corner_y),
								  Point(a.LL_corner_x + a.Lx, a.LL_corner_y + a.Ly))
		a_rect.draw(win2)
		a_text = Text(Point(a.LL_corner_x + a.Lx/2, a.LL_corner_y + a.Ly/2), a.name.strip('[]') + '  area=' + str(round(a.area, 3)))
		a_text.draw(win2)


	time.sleep(2)
	###





if __name__ == "__main__":
    main()