import sqlite3


class Database(object):
 	def __init__(self):
		conn = sqlite3.connect('self.db')
		c = conn.cursor()		
		c.execute("CREATE TABLE IF NOT EXISTS self(cluster text, cloud text, instance text, launch integer)")
		conn.close()

	def add(self,cluster_name,cloud_name,instance_id):
		conn = sqlite3.connect('self.db')
		c = conn.cursor()
		c.execute("INSERT INTO self VALUES (?,?,?,?)",(cluster_name,cloud_name,instance_id,1))
		conn.commit()

		conn.close()
	def terminate(self,instance_id):
		conn = sqlite3.connect('self.db')
		c = conn.cursor()
		c.execute('UPDATE self SET launch = 0 WHERE instance=?',[instance_id])
		conn.commit()
		conn.close()
	
	def check(self,cluster,instance_id):
		conn = sqlite3.connect('self.db')
		c = conn.cursor()
		c.execute('SELECT * FROM self WHERE instance=?', [instance_id])
		row = c.fetchone()
		if row[0]==cluster:
			conn.close()
			return True
		conn.close()
		return False

	def printdata(self):
		conn = sqlite3.connect('self.db')
		c = conn.cursor()
		c.execute('SELECT * FROM self')
		rows = c.fetchall()
		clusters = list()
		a = 0
		b = 0
		clouds=list()
		for row in rows:
			for cluster in clusters:
				if cluster[0][0][0]==row[0]:
					a=1
					for cloud in cluster:
						if cloud[0][1]==row[1]:
							cloud.append(row)
							b=1
					if b == 0:
						clouds = list()
						clouds.append(row)
						cluster.append(clouds)
					b=0
			if a == 0:
				cluster = list()
				clouds = list()
				clouds.append(row)
				cluster.append(clouds)
				clusters.append(cluster)
			a = 0
		for cluster in clusters:
			print ""
			print "Cluster: "+cluster[0][0][0]
			for cloud in cluster:
				print cloud[0][1]+":"
				for instance in cloud:
					if instance[3]==1:
						print instance[2]+" (running)"
					else:
						print instance[2]+" (terminated)"
		conn.close()

