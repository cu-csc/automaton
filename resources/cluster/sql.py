import sqlite3


class Sql(object):
 	def __init__(self):
		conn = sqlite3.connect('automaton.db')
		c = conn.cursor()
		
		c.execute("CREATE TABLE IF NOT EXISTS automaton(cluster text, cloud text, instance text)")
		conn.close()

	def add(self,cluster_name,cloud_name,instance_id):
		conn = sqlite3.connect('automaton.db')
		c = conn.cursor()
		c.execute("INSERT INTO automaton VALUES (?,?,?)",(cluster_name,cloud_name,instance_id))
		conn.commit()

		conn.close()
	def delete(self,instance_id):
		conn = sqlite3.connect('automaton.db')
		c = conn.cursor()
		c.execute("DELETE FROM automaton Where instance=?",[instance_id])
		conn.commit()
		conn.close()
	
	def check(self,cluster,instance_id):
		conn = sqlite3.connect('automaton.db')
		c = conn.cursor()
		c.execute('SELECT * FROM automaton WHERE instance=?', [instance_id])
		row = c.fetchone()
		if row[0]==cluster:
			conn.close()
			return True
		conn.close()
		return False

	def printsql(self):
		conn = sqlite3.connect('automaton.db')
		c = conn.cursor()
		c.execute('SELECT * FROM automaton')
		rows = c.fetchall()
		for row in rows:
			print row
		conn.close()

