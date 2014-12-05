#!/usr/bin/python
import MySQLdb
import sys
import os
import getopt
from time import sleep

host = '127.0.0.1'
user = ''
passwd = ''
db = ''

# idreceptor idligand status experiment volume

def start(name, dataset1, dataset2):
	try:
		conn = MySQLdb.connect(host, user, passwd, db)
		cursor = conn.cursor()

	except Exception, e:
		print e
		sys.exit(1)

	sql = "TRUNCATE tasks"
	cursor.execute(sql)
	conn.commit()

	try:
		sql = "INSERT INTO tasks (SELECT idreceptors, idligands, 0, '{0}', 0 FROM receptors, ligands WHERE receptors.status = 0 AND ligands.dataset = '{1}' AND receptors.dataset = '{2}')".format(name, dataset1, dataset2)
		cursor.execute(sql)
		conn.commit()
		#cursor.execute("UPDATE `fmah`.`tasks` SET `status`='0' WHERE `idreceptor`='1' and`idligand`='1' and`experiment`='plop'")
		#cursor.execute("UPDATE `fmah`.`tasks` SET `status`='0' WHERE `idreceptor`='2' and`idligand`='1' and`experiment`='plop'")
		#cursor.execute("UPDATE `fmah`.`tasks` SET `status`='0' WHERE `idreceptor`='3' and`idligand`='1' and`experiment`='plop'")
		conn.commit()
		
	except Exception, e:
		print e
		sys.exit(1)
	  
	cursor.close()
	conn.close()

	print "Done!"

def main(argv):
	name = ''
	dataset1 = ''
	dataset2 = ''

	try:
		opts, args = getopt.getopt(argv,"he:1:2:",["exp=", "dataset1=", "dataset2="])
	except getopt.GetoptError:
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-e", "--exp"):
			name = arg
		elif opt in ("-1", "--dataset1"):
			dataset1 = arg
		elif opt in ("-2", "--dataset2"):
			dataset2 = arg

	if name == '' or dataset1 == '' or dataset2 == '' :
		print "-e -1 (LIG) -2 (REC)"
		sys.exit(2)
		
	start(name, dataset1, dataset2)

if __name__ == "__main__":
   main(sys.argv[1:])
