#!/usr/bin/python
import MySQLdb
import sys
import os
import fnmatch
import getopt

host = '127.0.0.1'
user = ''
passwd = ''
db = ''

# idreceptors name pdb conf_name conf status dataset window_size

def start(path, confname, dataset):
	try:
		conn = MySQLdb.connect(host, user, passwd, db);
		cursor = conn.cursor()
		
		#sql = "TRUNCATE receptors"
		#cursor.execute(sql)
		#conn.commit()

		print "Start listing"
		listing = os.listdir(path + "pdbqt")
		listconf = os.listdir(path + confname)
		print "Done listing"
		
		current = 0
		done = len(listconf)
		
		confs = []
		receptors = []
		for infile in listing:
			try:
				receptor = infile.split(".")[0]

				f = open(path + "pdbqt/" + receptor + ".pdbqt", "r")
				receptorBlob = f.read()
				f.close()
				
				for conf in listconf:
					if fnmatch.fnmatch(conf, "{0}*".format(receptor)):
						f = open(path + confname + "/" + conf, "r")
						confBlob = f.read()
						f.close()
		
						sql = "INSERT INTO receptors VALUES(0, %s, %s, %s, %s, %s, %s, %s)"
						cursor.execute(sql, (receptor, receptorBlob, conf.split(".")[0]+"_conf", confBlob, 0, dataset, 0))
						conn.commit()
						print '{0} -- {1}\r'.format(int(float(current)/float(done)*100), str(current)+"/"+str(done)),
						sys.stdout.flush()
						current += 1
				
			except Exception, e:
				print "Error: cannot import receptor"
				print e

		cursor.close()
		conn.close()
		print "Done!"

	except Exception, e:
		print e
		sys.exit(1)

def main(argv):
	path = ''
	dataset = ''
	confname = ''

	try:
		opts, args = getopt.getopt(argv,"hp:d:c:",["path=","dataset=", "confname="])
	except getopt.GetoptError:
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-p", "--path"):
			if arg[-1] == '/':
				path = arg
			else:
				path = arg+'/'
		elif opt in ("-d", "--dataset"):
			dataset = arg
		elif opt in ("-c", "--confname"):
			confname = arg

	if path=='' or dataset=='' or confname == '':
		print "-p --path -d --dataset -c --confname"
		sys.exit(2)
		
	start(path, confname, dataset)

if __name__ == "__main__":
   main(sys.argv[1:])
