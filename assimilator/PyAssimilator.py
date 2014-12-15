#!/usr/bin/env python

import MySQLdb
from threading import Thread
import thread
import boinc_path_config
from assimilator import *
import os, sys, shutil
from Crypto.Random.random import randint

class PyAssimilator(Assimilator):
    """
    PyMW Assimilator. Copies workunit results to a predefined output directory. 
    """
    
    def __init__(self):
        Assimilator.__init__(self)
        self.assimilated_count = 0
        self.randNum = randint(0,55000)
        self.maxBatch = 100

    def _copy_to_output(self, result, error_mask=0):
        # validate that the destination path still exists
        if not os.path.exists(self.path):
            self.logCritical("PyMW path does not exist or is inaccessible: %s\n", \
                            self.path)
            return
        
        resultFullPath = self.get_file_path(result)
        resultName = re.search('<name>(.*)</name>',result.xml_doc_in).group(1)

        # validate that the source path is accessible
        if not error_mask and not os.path.exists(resultFullPath):
            self.logCritical("Result path does not exist or is inaccessible: %s\n", \
                            resultFullPath)
            return
        
        # copy the file to the output directory where it
        # will be processed by PyMW
        try:
            dest = os.path.join(self.path, str(self.randNum) + "_" + resultName) #generate a unique batch name
            if error_mask:
                dest += ".error"
                f = open(dest, "w")
                try:
                    f.writelines("BOINC error: " + str(error_mask) + "\n")
                    if result.stderr_out:
                        f.writelines("STD ERR: " + result.stderr_out + "\n")
                finally: f.close()
                self.assimilated_count += 1 #+one assimilated result
                self.logNormal("Error flag created [%s]\n", resultName)
            else:
                shutil.copy2(resultFullPath, dest)
                self.assimilated_count += 1 #+one assimilated result
                self.logNormal("Result copied [%s]\n", resultName)
        except Exception,msg:
            self.logCritical("Error copying output\n" + \
                             "  - Source: %s\n" + \
                             "  - Dest: %s\n" + 
                             "  - Error: %s",
                             resultFullPath, dest, msg)

        if(self.assimilated_count == self.maxBatch):
            thread.start_new_thread(self.do_assimilate,(self.randNum,))
            self.randNum = randint(0,55000)
            self.assimilated_count = 0
                
    def assimilate_handler(self, wu, results, canonical_result):
        """
        Assimilates a canonical result by copying the result file
        to the PyMW pickup directory, self.path
        """
        
        # check for valid wu.canonical_result
        if wu.canonical_result:
            self.logNormal("[%s] Found canonical result\n", wu.name)
            self._copy_to_output(canonical_result, wu.error_mask)
        elif wu.error_mask != 0:
            # this is an error
            self.logNormal("[%s] Workunit failed, sending arbitrary result\n", wu.name)
            self._copy_to_output(results[0], wu.error_mask)
            self.logNormal("[%s] No canonical result\n", wu.name)
        else:
            self.logNormal("[%s] No canonical result\n", wu.name)

        # report errors with the workunit
        if self.report_errors(wu):
            pass

    def do_assimilate(self, randNum, uber = False):
        """
        This method scans the database for workunits that need to be 
        assimilated. It handles all processing rules passed in on the command  
        line, except for -noinsert, which must be handled in assimilate_handler.
        Calls check_stop_trigger before doing any work.
        """
        self.num_thread += 1
        time.sleep(1)
        self.logNormal("Current %s, Assimilate %s, Thread %s\n", self.randNum, randNum, self.num_thread)
        
        did_something = False
    
        assimilated = 0
        checked = 0
        
        listing = os.listdir(self.path)
        if len(listing) < 1:
            self.num_thread -= 1
            return did_something
        
        sqlList = []
        toRemove = []
        
        if uber:
            maxBatch = len(listing)
        else:
            maxBatch = self.maxBatch

        i = 0
        while checked != maxBatch:
            rfile = listing[i]

            if rfile.split("_")[0] == str(randNum) or uber: #look for the name of the app
                if rfile.split(".")[-1] != "error": #if it's a buggy result, put it on the failed folder
                    with open(self.path + rfile, 'r') as f:
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
                        shutil.move(self.path + rfile, self.pendingPath + rfile)
                        toRemove.append(rfile)
                    except Exception, e:
                        self.logCritical("Error: %s", e)
                        self.num_thread -= 1
                        return did_something
                else:
                    try:
                        shutil.move(self.path + rfile, self.failedPath + rfile)
                    except Exception, e:
                        self.logCritical("Error: %s", e)
                        self.num_thread -= 1
                        return did_something

                    checked += 1
                    
            if i ==  len(listing)-1: #something wrong
                break
            
            i += 1
            
        try:
            while self.num_thread > 50:
                time.sleep(3)
            
            self.conn.ping(True)
            cursor = self.conn.cursor()
            
            for sql in sqlList:
                cursor.execute(sql)
                assimilated += 1
            did_something = True
            self.logDebug("%d results inserted into database, %d errors\n", assimilated, checked-assimilated)
            self.conn.commit()
            cursor.close()
        except Exception, e:
            self.logCritical("Error: %s", e)
            self.num_thread -= 1
            return did_something
            
        # return did something result
        for dfile in toRemove:
            try:
                os.remove(self.pendingPath + dfile)
            except:
                self.logCritical("File missing: %s", e)

        self.num_thread -= 1
        return did_something

# allow the module to be executed as an application
if __name__ == '__main__':

    asm = PyAssimilator()
    asm.run()
