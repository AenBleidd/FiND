#!/usr/bin/python
import MySQLdb
import sys
import os
from time import sleep

host = '127.0.0.1'
user = 'boinc'
passwd = 'boinc'
db = 'fmah'

try:
    conn = MySQLdb.connect(host, user, passwd, db)
    cursor = conn.cursor()

except Exception, e:
    print e
    sys.exit(1)

try:
    sql = "TRUNCATE tasks"
    cursor.execute(sql)
    conn.commit()
    
except Exception, e:
    print e
    sys.exit(1)

try:
    sql = "INSERT INTO tasks (SELECT idreceptors, idligands, 0, 'plop', 0 from receptors, ligands where receptors.status = 0)"
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