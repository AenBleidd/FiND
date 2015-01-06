#!/usr/bin/env python

import MySQLdb
import os, sys, shutil

def do_assimilate(path, uber = False):
    """
    This method scans the database for workunits that need to be 
    assimilated. It handles all processing rules passed in on the command  
    line, except for -noinsert, which must be handled in assimilate_handler.
    Calls check_stop_trigger before doing any work.
    """
    
    assimilated = 0
    checked = 0
    did_something = False
    
    listing = os.listdir(path)
    if len(listing) < 1:
        return "len(listing)"
    
    sqlList = []
    toRemove = []
    
    if uber:
        maxBatch = len(listing)
    else:
        maxBatch = self.maxBatch

    i = 0
    while checked != maxBatch:
        rfile = listing[i]

        if uber: #look for the name of the app
            if rfile.split(".")[-1] != "error": #if it's a buggy result, put it on the failed folder
                with open(path + rfile, 'r') as f:
                    experiment = rfile.split("_")[-3]
                    receptor, ligand, seed, score = f.readline().split(",")
                #idligand = "(SELECT idligands FROM {0}.ligands WHERE name='{1}')".format(db, ligand)
                #idreceptor = "(SELECT idreceptors FROM {0}.receptors WHERE name='{1}')".format(db, receptor)
                idligand = rfile.split("_")[2]
                idreceptor = rfile.split("_")[3]
                
                sqlList.append("INSERT INTO results VALUES (0, '{0}', {1}, '{2}', {3}, '{4}', {5}, {6}, {7}, {8}, '{9}')".format(experiment, idreceptor, receptor, idligand, ligand, score, 0, 0, seed, rfile))
                checked += 1
                try:
                    #os.remove(self.path + rfile)
                    toRemove.append(rfile)
                except Exception, e:
                    return "toRemove.append(rfile)"
            else:
                try:
                    shutil.move(path + rfile, "/home/boinc/findah/failed/" + rfile)
                except Exception, e:
                    return "util.move(path + rfile, \"/home/boinc/findah/failed/\" + rfile)"

                checked += 1
                
        if i ==  len(listing)-1: #something wrong
            break
        
        i += 1
        
    try:
        conn = MySQLdb.connect(host, user, passwd, db)
        conn.autocommit(True)
        cursor = conn.cursor()

        total = len(sqlList)

        for sql in sqlList:
            cursor.execute(sql)
            assimilated += 1
            print str(assimilated)+"/"+str(total)
        did_something = True
        conn.commit()
        cursor.close()
        conn.close()
    except Exception, e:
        return "conn = MySQLdb.connect(host, user, passwd, db)", e, sql
        
    # return did something result
    for dfile in toRemove:
        try:
            os.remove(path + dfile)
        except:
            print "File missing " + dfile

    return did_something

# allow the module to be executed as an application
if __name__ == '__main__':
    try:
        with open("/home/boinc/findah/bin/sql_config.conf", 'r') as sql_config:
            buff = []
            i = 0
            for line in sql_config:
                if line[0] != "#":
                    buff.append(line[:-1])
                    i += 1
    except:
        print "Error: database"
        exit(1)
    host = buff[0]
    user = buff[1]
    passwd = buff[2]
    db = buff[3]
    
    path = sys.argv[1]
    if path[-1] != "/":
        path = path+"/"
    
    print do_assimilate(path, True)
