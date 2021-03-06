import requests
import json
import sqlite3
import traceback

class NetworkStateService(object):
	Link = "Link";
	LinkUtilization = "LinkUtilization"
	LinkStatus = "LinkStatus"
	LinkLspCount = "LinkLspCount"
	LinkLspList = "LinkLspList"
	Router = "Router"
	Lsp = "Lsp"
	LspRoute = "LspRoute"
	LspLatency = "LspLatency"
	LspRealLatency = "LspRealLatency"
	LspFreeUtilization = "LspFreeUtilization"
	LspStatus = "LspStatus"
	LspLinkList = "LspLinkList"
	Interface = "Interface"
	InterfaceInBps = "InterfaceInBps"
	InterfaceOutBps = "InterfaceOutBps"
	Topology = "Topology"
	UtilizationSum = "UtilizationSum"

	def snapshot(self, name):
		return name + "_"

	def create(self, name):
		print "create table: " + name
		c = self.connection.cursor();
		c.execute("CREATE TABLE " + name + " (name text, key text, time real, value text, PRIMARY KEY(name, key, time))");
		c.execute("CREATE TABLE " + self.snapshot(name) + " (name text, key text, time real, value text, PRIMARY KEY(name, key))");
		self.connection.commit()
		self.tables.append(name)

	def __init__(self, database):
		self.connection = sqlite3.connect(database, check_same_thread=False);
		print "adding UDFs"
		#self.connection.create_function("link_to_lsp", 1, link_to_lsp)
		print "loading database"
		c = self.connection.cursor();
		rows = c.execute("SELECT name FROM sqlite_master WHERE type = 'table'");
		self.tables = [];
		for row in rows:
			print "loading table: " + row[0]
			self.tables.append(row[0])

	def close(self):
		self.connection.close()

	def save(self, name, key, time, value):
		name = str(name);
		key = str(key);
		time = int(time);
		time -= time % 10;
		time = str(time);
		value = str(value);
		c = self.connection.cursor();

		# Create table
		if name not in self.tables:
			self.create(name);
			time = time[:-1] + "0";
			for table in [name, self.snapshot(name)]:
				c.execute("INSERT OR REPLACE INTO " + table + " VALUES ('" + name + "','" + key + "','" + time + "','" + value + "')");
		else :
			for table in [name, self.snapshot(name)]:
				c.execute("SELECT time, value FROM " + table + " WHERE key = '" + key + "' AND time = (SELECT max(time) FROM " + name + ")");
			row = c.fetchone();
			if row is None:
				for table in [name, self.snapshot(name)]:
					c.execute("INSERT OR REPLACE INTO " + table + " VALUES ('" + name + "','" + key + "','" + time + "','" + value + "')");
			else :
				if row[0] + 10 <= int(time):
					sec = row[0] + 10;
					while sec <= int(time):
						if sec - row[0] < int(time) - sec:
							for table in [name, self.snapshot(name)]:
								c.execute("INSERT OR REPLACE INTO " + table + " VALUES ('" + name + "','" + key + "','" + str(sec) + "','" + str(row[1]) + "')");
						else:
							for table in [name, self.snapshot(name)]:
								c.execute("INSERT OR REPLACE INTO " + table + " VALUES ('" + name + "','" + key + "','" + str(sec) + "','" + value + "')");
						sec += 10;

		if (name != self.Topology):
			print "commit to database: %s, %s, %s, %s" % (name, key, time, value)

		# Save (commit) the changes
		self.connection.commit()

	def query(self, query_string, query_type):
		c = self.connection.cursor();
		print "executing query with type %s: %s" % (query_type, query_string)
		if (query_string == "..."):
			return [];
		try:
			jsons = [];
			rows = c.execute(query_string);
			if (query_type == 'stream'):
				for row in rows:
					json = {}
					json['name'] = row[0];
					json['key'] = row[1];
					json['time'] = row[2];
					json['value'] = row[3];
					jsons.append(json);			
			else:
				for row in rows:
					json = {}
					for key in range(0,len(row)):
						json['key' + str(key)] = row[key];
						jsons.append(json);
					jsons.append(json);	
			#print "returning: " + str(jsons)
			return jsons;
		except Exception, e:
			traceback.print_exc()
			raise e
			return [];

	def clear(self):
		c = self.connection.cursor();
		rows = c.execute("SELECT name FROM sqlite_master WHERE type = 'table'");
		for row in rows:
			print "deleting table: " + row[0];
			c.execute("DROP TABLE " + row[0]);
		self.connection.commit()


'''
nss = NetworkStateService("database/states.db");
print nss.query("SELECT link_to_lsp(1), link_to_lsp(1), link_to_lsp(1), link_to_lsp(1) FROM Link_");
'''

'''
nss.save("LinkStatus", "10.0.0.1_10.0.0.2", "1456451402", "Up");
print nss.query("SELECT * FROM LinkStatus");
nss.save("LinkUtilization", "10.0.0.1_10.0.0.2", "1456451402", "0.04");
print nss.query("SELECT * FROM LinkUtilization");
nss.save("LinkUtilization", "10.0.0.1_10.0.0.2", "1456451409", "0.04");
print nss.query("SELECT * FROM LinkUtilization");
nss.save("LinkUtilization", "10.0.0.1_10.0.0.2", "1456451412", "0.04");
print nss.query("SELECT * FROM LinkUtilization");
nss.save("LinkUtilization", "10.0.0.1_10.0.0.2", "1456451452", "0.04");
print nss.query("SELECT * FROM LinkUtilization");
'''
#nss.clear();
