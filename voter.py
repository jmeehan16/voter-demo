#!/usr/bin/python
import syslog
from flask import Flask, request, render_template, send_from_directory, Response, jsonify
from flask.ext.bootstrap import Bootstrap
import json
import re, os, sys

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import time

app = Flask(__name__)

bootstrap = Bootstrap(app)

# Set debug mode.
debug = False

# ================
# REST API function definitions
# ================

# default values
remoteserver = 'istc3'
hstorelogfile = '/home/jdu/insertinto/h-store/logs/demohstorecurrent.txt'
sstorelogfile = '/home/jdu/insertinto/h-store/logs/demosstorecurrent.txt'
contestants_number = 25

try:
    remoteremove = 'rm ' + hstorelogfile
    os.system('rm ' + hstorelogfile)
    os.system('ssh ' + remoteserver + ' "' + remoteremove + '"')
    remoteremove = 'rm ' + sstorelogfile
    os.system('rm ' + sstorelogfile)
    os.system('ssh ' + remoteserver + ' "' + remoteremove + '"')
except (OSError, IOError) as e:
    pass

top3_1_same_flag = True
top3_2_same_flag = True
top3_3_same_flag = True
bottom3_1_same_flag = True
bottom3_2_same_flag = True
bottom3_3_same_flag = True
trending3_1_same_flag = True
trending3_2_same_flag = True
trending3_3_same_flag = True

def getSStoreResults():
    try:
        f = open(sstorelogfile, 'r')
        lines = f.readlines()
        f.close()
        return parseFile(lines)
    except (OSError, IOError) as e:
        retVal = []
        for i in range(27):
            retVal.append('')
        return retVal


def getHStoreResults():
    try:
        cmd = 'scp ' + remoteserver + ':' +hstorelogfile + ' ' + hstorelogfile
	print(cmd)
        os.system(cmd)
        f = open(hstorelogfile, 'r')
        lines = f.readlines()
        f.close()
        return parseFile(lines)
    except (OSError, IOError) as e:
        retVal = []
        for i in range(27):
            retVal.append('')
        return retVal


def parseFile(lines):
    retVal = []

    totalVotes = lines[17].strip()
    trendingVotes = lines[20].strip()
    candidatesRemaining = lines[23].strip()

    retVal.append(lines[2].strip().split(',')[0])
    votes = lines[2].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[3].strip().split(',')[0])
    votes = lines[3].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[4].strip().split(',')[0])
    votes = lines[4].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
        
    retVal.append(lines[7].strip().split(',')[0])
    votes = lines[7].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[8].strip().split(',')[0])
    votes = lines[8].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[9].strip().split(',')[0])
    votes = lines[9].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
        
    retVal.append(lines[12].strip().split(',')[0])
    votes = lines[12].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[13].strip().split(',')[0])
    votes = lines[13].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[14].strip().split(',')[0])
    votes = lines[14].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(candidatesRemaining)
        
    return retVal



@app.route('/_start_voting')
def start_voting():
#    for logfile in (sstorelogfile, hstorelogfile):
#    	cmd = 'rm ' + logfile
#        try:
#    	    os.system(cmd)
#        except (OSError, IOError) as e:
#            pass
    reset_results()
    baseDir = '/'.join(sstorelogfile.split('/')[:-2])
#    controllerpid = os.fork()
#    if controllerpid == 0: # Running the controller
#        os.chdir(baseDir+'/tools')
#        cmd = 'python voterdemoserver.py'
#        os.system(cmd)
#        os._exit(0)
#    else:
    sstorepid = os.fork()
    if sstorepid == 0:  # Running S-Store benchmark on the local
        os.chdir(baseDir)
        cmd = 'ant hstore-benchmark -Dproject=voterdemosstorecorrect -Dclient.threads_per_host=10 -Dclient.txnrate=10 -Dglobal.sstore=true -Dglobal.sstore_scheduler=true -Dclient.duration=1000000'
        os.system(cmd)
#        os.chdir('../voter-demo')
        os._exit(0)
    else:
        hstorepid = os.fork()
        if hstorepid == 0: # Running H-Store benchmark on the remote
            baseDir = '/'.join(hstorelogfile.split('/')[:-2])
            cmd = '"cd ' + baseDir + '; ant hstore-benchmark -Dproject=voterdemohstorecorrect -Dclient.threads_per_host=10 -Dclient.txnrate=10 -Dglobal.sstore=false -Dglobal.sstore_scheduler=false -Dclient.duration=1000000"'
            cmd = 'ssh ' + remoteserver + ' ' + cmd
            print(cmd)
            os.system(cmd)
            os._exit(0)
        else:
            return



@app.route('/_get_removal_votes')
def get_removal_votes():
    return jsonify(removal_votes = 3428)



@app.route('/_reset_results')
def reset_results():
    try:
        cmd = 'rm ' + sstorelogfile
        os.system(cmd)
        os.system('ssh ' + remoteserver + ' "' + cmd + '"')
        cmd = 'rm ' + hstorelogfile
        os.system(cmd)
        os.system('ssh ' + remoteserver + ' "' + cmd + '"')
    except (OSError, IOError) as e:
        pass
    get_results(reset=True)



@app.route('/_get_results')
def get_results(reset=False):
    retVal = ['']
    if reset == False:
        retVal = getSStoreResults()
        retVal.extend(getHStoreResults())
#        retVal.extend([3428])
        if retVal[27] == '':
            retVal[27] = contestants_number
        if len(retVal) > 55 and retVal[55] == '':
            retVal[55] = contestants_number
    else:
        for i in range(56):
            retVal.append('')
        # Hack
        global contestants_number
        retVal[27] = contestants_number
        retVal[55] = contestants_number

    if retVal[0] == '' or retVal[0] == retVal[28]:
        top3_1_same_flag = True
    else:
        top3_1_same_flag = False

    if retVal[0] == '' or retVal[3] == retVal[31]:
        top3_2_same_flag = True
    else:
        top3_2_same_flag = False

    if  retVal[0] == '' or retVal[6] == retVal[34]:
        top3_3_same_flag = True
    else:
        top3_3_same_flag = False

    if retVal[0] == '' or retVal[9] == retVal[37]:
        bottom3_1_same_flag = True
    else:
        bottom3_1_same_flag = False

    if retVal[0] == '' or retVal[12] == retVal[40]:
        bottom3_2_same_flag = True
    else:
        bottom3_2_same_flag = False

    if retVal[0] == '' or retVal[15] == retVal[43]:
        bottom3_3_same_flag = True
    else:
        bottom3_3_same_flag = False

    if retVal[0] == '' or retVal[18] == retVal[46]:
        trending3_1_same_flag = True
    else:
        trending3_1_same_flag = False

    if retVal[0] == '' or retVal[21] == retVal[49]:
        trending3_2_same_flag = True
    else:
        trending3_2_same_flag = False

    if retVal[0] == '' or retVal[24] == retVal[52]:
        trending3_3_same_flag = True
    else:
        trending3_3_same_flag = False

    return jsonify(
        sstore_top3_1_name = retVal[0], 
        sstore_top3_1_votes = retVal[1], 
        sstore_top3_1_percentage = retVal[2],
        sstore_top3_2_name = retVal[3], 
        sstore_top3_2_votes = retVal[4], 
        sstore_top3_2_percentage = retVal[5], 
        sstore_top3_3_name = retVal[6],
        sstore_top3_3_votes = retVal[7], 
        sstore_top3_3_percentage = retVal[8], 

        sstore_bottom3_1_number = str(int(retVal[27])),
        sstore_bottom3_1_name = retVal[9], 
        sstore_bottom3_1_votes = retVal[10], 
        sstore_bottom3_1_percentage = retVal[11], 
        sstore_bottom3_2_number = str(int(retVal[27])-1),
        sstore_bottom3_2_name = retVal[12], 
        sstore_bottom3_2_votes = retVal[13], 
        sstore_bottom3_2_percentage = retVal[14], 
        sstore_bottom3_3_number = str(int(retVal[27])-1),
        sstore_bottom3_3_name = retVal[15], 
        sstore_bottom3_3_votes = retVal[16], 
        sstore_bottom3_3_percentage = retVal[17],

        sstore_trending3_1_name = retVal[18], 
        sstore_trending3_1_votes = retVal[19], 
        sstore_trending3_1_percentage = retVal[20], 
        sstore_trending3_2_name = retVal[21], 
        sstore_trending3_2_votes = retVal[22], 
        sstore_trending3_2_percentage = retVal[23], 
        sstore_trending3_3_name = retVal[24], 
        sstore_trending3_3_votes = retVal[25], 
        sstore_trending3_3_percentage = retVal[26],
        sstore_candidates_remaining = retVal[27],

        hstore_top3_1_name = retVal[28], 
        hstore_top3_1_votes = retVal[29], 
        hstore_top3_1_percentage = retVal[30],  
        hstore_top3_2_name = retVal[31], 
        hstore_top3_2_votes = retVal[32], 
        hstore_top3_2_percentage = retVal[33], 
        hstore_top3_3_name = retVal[34], 
        hstore_top3_3_votes = retVal[35], 
        hstore_top3_3_percentage = retVal[36], 

        hstore_bottom3_1_number = str(int(retVal[55])),
        hstore_bottom3_1_name = retVal[37], 
        hstore_bottom3_1_votes = retVal[38], 
        hstore_bottom3_1_percentage = retVal[39], 
        hstore_bottom3_2_number = str(int(retVal[55])-1),
        hstore_bottom3_2_name = retVal[40], 
        hstore_bottom3_2_votes = retVal[41], 
        hstore_bottom3_2_percentage = retVal[42],
        hstore_bottom3_3_number = str(int(retVal[55])-2),
        hstore_bottom3_3_name = retVal[43], 
        hstore_bottom3_3_votes = retVal[44], 
        hstore_bottom3_3_percentage = retVal[45], 

        hstore_trending3_1_name = retVal[46], 
        hstore_trending3_1_votes = retVal[47], 
        hstore_trending3_1_percentage = retVal[48],
        hstore_trending3_2_name = retVal[49], 
        hstore_trending3_2_votes = retVal[50], 
        hstore_trending3_2_percentage = retVal[51], 
        hstore_trending3_3_name = retVal[52], 
        hstore_trending3_3_votes = retVal[53], 
        hstore_trending3_3_percentage = retVal[54],
        hstore_candidates_remaining = retVal[55],

        top3_1_same = top3_1_same_flag,
        top3_2_same = top3_2_same_flag,
        top3_3_same = top3_3_same_flag,
        bottom3_1_same = bottom3_1_same_flag,
        bottom3_2_same = bottom3_2_same_flag,
        bottom3_3_same = bottom3_3_same_flag,
        trending3_1_same = trending3_1_same_flag,
        trending3_2_same = trending3_2_same_flag,
        trending3_3_same = trending3_3_same_flag
    )
    
        
    

# This is a GET route to display the landing page of bikeshare
@app.route('/')
def home():
    return render_template('index.html')
    


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('python ' + sys.argv[0] + ' <remote server> <S-Store log file> <H-Store log file> <Number of contestants>')
        sys.exit(2)

    global remoteserver
    remoteserver = sys.argv[1]
    global sstorelogfile
    sstorelogfile = sys.argv[2]
    global hstorelogfile
    hstorelogfile = sys.argv[3]
    global contestants_number
    contestants_number = int(sys.argv[4])

    if debug:
        app.run(host='127.0.0.1', port=8081, debug=True)
    else:
        app.run(host='0.0.0.0', port=8081, debug=True)

