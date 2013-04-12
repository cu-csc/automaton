import os
import sys
import random
from lib.util import read_path

class Tree(object):
	def __init__(self):
		self.name = None
		self.attributes = list()

class Parser(object):
	def __init__(self,config):
		self.data = list()
		self.config = config
		self.local_path = self.config.globals.log_local_path
		self.instance_types = list()
		type_list(self.local_path,self.instance_types)

	
	def read_dir(self,root_dir):
		for line in os.listdir(root_dir):
			path = os.path.join(root_dir, line)
			if os.path.isdir(path):
				self.read_dir(path)
			elif os.path.basename(path)=='.DS_Store':
				continue
			else:
				inputs = self.insert_data(path)

	def insert_data(self,path):
		filelist=list()
		pathlist=list()
		#read_file(path)
		pathlist = splitpath(path, 20)
		filename =  os.path.basename(path)
		filelist = filename.split('_')
		if len(self.data) != 0:
			for item in self.data:
				if item.name==pathlist[3]:
					for n in range(len(self.instance_types)):
						if filelist[2]==self.instance_types[n]:
							item.attributes[n].append(read_file(path))
					return
				else:
					continue
		tree = Tree()
		for n in range(len(self.instance_types)):
			tree.attributes.append(list())
			if filelist[2]==self.instance_types[n]:
				tree.attributes[n].append(read_file(path))
		tree.name = pathlist[3]
		self.data.append(tree)

	def get_mean(self):
		self.read_dir(self.local_path)
		li = list()
		for item in self.data:
			l = list()
			l.append(item.name)
			for attribute in item.attributes:
				s = 0
				if len(attribute)==0:
					s=0
				else:
					for n in attribute:
						s+=n
					s = s/float(len(attribute))
				l.append(s)
			li.append(l)
		return li
	
	def print_tree(self):
		for item in self.data:
			print item.name
			for n in self.attributes:
				print n

def splitpath(path, maxdepth=20):
     ( head, tail ) = os.path.split(path)
     return splitpath(head, maxdepth - 1) + [ tail ] \
         if maxdepth and head and head != path \
         else [ head or tail ]

def read_file(filename):
	lnlist = list()
	with open(filename, 'r') as handle:
		for ln in handle:
			if 'Total time for running BioPerf is' in ln:
				lnlist=ln.split(' ')
				return int(lnlist[6])
		return 0

def type_list(root_dir,instance_type):
	for line in os.listdir(root_dir):
		path = os.path.join(root_dir, line)
		if os.path.isdir(path):
			type_list(path,instance_type)
		elif os.path.basename(path)=='.DS_Store':
			continue
		else:
			filelist=list()
			filename = os.path.basename(path)
			filelist = filename.split('_')
			if filelist[2] in instance_type:
				continue
			else:
				instance_type.append(filelist[2])

