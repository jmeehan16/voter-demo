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
# remoteserver = 'istc3'
# hstorelogfile = '/home/jdu/insertinto/h-store/logs/demohstorecurrent.txt'
# sstorelogfile = '/home/jdu/insertinto/h-store/logs/demosstorecurrent.txt'
# contestants_number = 25

# try:
#     remoteremove = 'rm ' + hstorelogfile
#     os.system('rm ' + hstorelogfile)
#     os.system('ssh ' + remoteserver + ' "' + remoteremove + '"')
#     remoteremove = 'rm ' + sstorelogfile
#     os.system('rm ' + sstorelogfile)
#     os.system('ssh ' + remoteserver + ' "' + remoteremove + '"')
# except (OSError, IOError) as e:
#     pass

contestantFile = 'contestants'
contestantLines = open(contestantFile, 'r').readlines()
contestantList = [contestant[:-1] for contestant in contestantLines]
sstorecontestants = {}
hstorecontestants = {}
for contestant in contestantList:
    # key: name; value: flag for alive
    sstorecontestants[contestant] = True
    hstorecontestants[contestant] = True
#contestants.sort(key=lambda s: s.split()[1])
sortedSStoreContestants = sorted(sstorecontestants.items())
sortedHStoreContestants = sorted(hstorecontestants.items())

top3_1_same_flag = True
top3_2_same_flag = True
top3_3_same_flag = True
bottom3_1_same_flag = True
bottom3_2_same_flag = True
bottom3_3_same_flag = True
trending3_1_same_flag = True
trending3_2_same_flag = True
trending3_3_same_flag = True

def getSStoreContestants():
    global contestantList
    global sstorecontestants
    global sortedSStoreContestants
    sstorecontestantfile = '/'.join(sstorelogfile.split('/')[:-1])+'/sstorecontestants.txt'
    try:
        f = open(sstorecontestantfile, 'r')
        buf = f.read()
        f.close()
        parseContestants(buf, True)
    except (OSError, IOError) as e:
        for contestant in contestantList:
            # key: name; value: flag for alive
            sstorecontestants[contestant] = True
        sortedSStoreContestants = sorted(sstorecontestants.items())


def getHStoreContestants():
    global contestantList
    global hstorecontestants
    global sortedHStoreContestants
    hstorecontestantfile = '/'.join(hstorelogfile.split('/')[:-1])+'/hstorecontestants.txt'
    try:
        if remoteserver != "localhost":
            cmd = 'scp ' + remoteserver + ':' +hstorecontestantfile + ' ' + hstorecontestantfile
            print(cmd)
            os.system(cmd)
        f = open(hstorecontestantfile, 'r')
        buf = f.read()
        f.close()
        parseContestants(buf, False)
    except (OSError, IOError) as e:
        for contestant in contestantList:
            # key: name; value: flag for alive
            hstorecontestants[contestant] = True
        sortedHStoreContestants = sorted(hstorecontestants.items())


def parseContestants(buf, sstoreflag):
    global sstorecontestants
    global hstorecontestants
    global contestantList
    bufs = re.compile('--*\n').split(buf)

    deletedBuf = bufs[1]
    deletedStr = deletedBuf.split('**RemovedContestants**\n')
    if len(deletedStr) > 1:
        deletedList = deletedStr[1].split('\n')
        deletedNames = [d.split(',')[1] for d in deletedList[:-1]]
        for deletedName in deletedNames:
            if sstoreflag == True:
                sstorecontestants[deletedName] = False
            else:
                hstorecontestants[deletedName] = False


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
        if remoteserver != "localhost":
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
    votesTilNextDelete = lines[26].strip()

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
    retVal.append('%2.1f%%' % (int(votes)))#*100.0/int(totalVotes)))
    retVal.append(lines[13].strip().split(',')[0])
    votes = lines[13].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)))#*100.0/int(totalVotes)))
    retVal.append(lines[14].strip().split(',')[0])
    votes = lines[14].strip().split(',')[1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)))#*100.0/int(totalVotes)))
    retVal.append(candidatesRemaining)
    retVal.append(votesTilNextDelete)
        
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
        cmd = 'ant hstore-benchmark -Dproject=voterdemosstorecorrect -Dclient.threads_per_host=5 -Dclient.txnrate=20 -Dglobal.sstore=true -Dglobal.sstore_scheduler=true -Dclient.duration=150000 -Dnoshutdown=false'
        os.system(cmd)
#        os.chdir('../voter-demo')
        os._exit(0)
    else:
        hstorepid = os.fork()
        if hstorepid == 0: # Running H-Store benchmark on the remote
            if remoteserver == "localhost":
                os.chdir(baseDir + "/demo")
                cmd = 'python simulatehstore.py'
                print(cmd)
                os.system(cmd)
                os._exit(0)
            else:
                baseDir = '/'.join(hstorelogfile.split('/')[:-2])
                print ("BASE DIR: " + baseDir)
                cmd = '"cd ' + baseDir + '; ant hstore-benchmark -Dproject=voterdemohstorecorrect -Dclient.threads_per_host=5 -Dclient.txnrate=20 -Dglobal.sstore=false -Dglobal.sstore_scheduler=false -Dclient.duration=150000 -Dnoshutdown=false"'
                cmd = 'ssh ' + remoteserver + ' ' + cmd
                print(cmd)
                os.system(cmd)
                os._exit(0)
        else:
            return



@app.route('/_reset_results')
def reset_results():
    global sstorelogfile
    global hstorelogfile
    global remoteserver
    try:
        sstorecontestantfile = '/'.join(sstorelogfile.split('/')[:-1])+'/sstorecontestants.txt'
        os.system('rm ' + sstorecontestantfile)
        os.system('ssh ' + remoteserver + ' "rm ' + sstorecontestantfile + '"')
        hstorecontestantfile = '/'.join(hstorelogfile.split('/')[:-1])+'/hstorecontestants.txt'
        os.system('rm ' + hstorecontestantfile)
        os.system('ssh ' + remoteserver + ' "rm ' + hstorecontestantfile + '"')

        cmd = 'rm ' + sstorelogfile
        os.system(cmd)
        os.system('ssh ' + remoteserver + ' "' + cmd + '"')
        cmd = 'rm ' + hstorelogfile
        os.system(cmd)
        os.system('ssh ' + remoteserver + ' "' + cmd + '"')

    except (OSError, IOError) as e:
        print "ERROR: COULD NOT RESET RESULTS"
        pass
    get_results(reset=True)



@app.route('/_get_results')
def get_results(reset=False):
    global contestants_number
    global contestantList
    global sstorecontestants
    global hstorecontestants
    global sortedSStoreContestants
    global sortedHStoreContestants
    retVal = ['']
    if reset == False:
        getSStoreContestants()
        getHStoreContestants()
        sortedSStoreContestants = sorted(sstorecontestants.items())
        sortedHStoreContestants = sorted(hstorecontestants.items())

        retVal = getSStoreResults()
        retVal.extend(getHStoreResults())
        if len(retVal) < 58:
            retVal = []
            for i in range(58):
                retVal.append('')
        if retVal[27] == '':
            retVal[27] = contestants_number
        if retVal[56] == '':
            retVal[56] = contestants_number
    else:
        for i in range(58):
            retVal.append('')
        # Hack
        global contestants_number
        retVal[27] = contestants_number
        retVal[56] = contestants_number

        for contestant in contestantList:
            # key: name; value: flag for alive
            sstorecontestants[contestant] = True
            hstorecontestants[contestant] = True
        sortedSStoreContestants = sorted(sstorecontestants.items())
        sortedHStoreContestants = sorted(hstorecontestants.items())


    if retVal[0] == '' or retVal[0] == retVal[29]:
        top3_1_same_flag = True
    else:
        top3_1_same_flag = False

    if retVal[0] == '' or retVal[3] == retVal[32]:
        top3_2_same_flag = True
    else:
        top3_2_same_flag = False

    if  retVal[0] == '' or retVal[6] == retVal[35]:
        top3_3_same_flag = True
    else:
        top3_3_same_flag = False

    if retVal[0] == '' or retVal[9] == retVal[38]:
        bottom3_3_same_flag = True
    else:
        bottom3_3_same_flag = False

    if retVal[0] == '' or retVal[12] == retVal[41]:
        bottom3_2_same_flag = True
    else:
        bottom3_2_same_flag = False

    if retVal[0] == '' or retVal[15] == retVal[44]:
        bottom3_1_same_flag = True
    else:
        bottom3_1_same_flag = False

    if retVal[0] == '' or retVal[18] == retVal[47]:
        trending3_1_same_flag = True
    else:
        trending3_1_same_flag = False

    if retVal[0] == '' or retVal[21] == retVal[50]:
        trending3_2_same_flag = True
    else:
        trending3_2_same_flag = False

    if retVal[0] == '' or retVal[24] == retVal[53]:
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

        sstore_bottom3_3_number = str(int(retVal[27])),
        sstore_bottom3_3_name = retVal[9], 
        sstore_bottom3_3_votes = retVal[10], 
        sstore_bottom3_3_percentage = retVal[11], 
        sstore_bottom3_2_number = str(int(retVal[27])-1) if int(retVal[27])-1 > 0 else '-',
        sstore_bottom3_2_name = retVal[12], 
        sstore_bottom3_2_votes = retVal[13], 
        sstore_bottom3_2_percentage = retVal[14], 
        sstore_bottom3_1_number = str(int(retVal[27])-2) if int(retVal[27])-2 > 0 else '-',
        sstore_bottom3_1_name = retVal[15], 
        sstore_bottom3_1_votes = retVal[16], 
        sstore_bottom3_1_percentage = retVal[17],

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
        sstore_votes_til_next_delete = retVal[28],

        hstore_top3_1_name = retVal[29], 
        hstore_top3_1_votes = retVal[30], 
        hstore_top3_1_percentage = retVal[31],  
        hstore_top3_2_name = retVal[32], 
        hstore_top3_2_votes = retVal[33], 
        hstore_top3_2_percentage = retVal[34], 
        hstore_top3_3_name = retVal[35], 
        hstore_top3_3_votes = retVal[36], 
        hstore_top3_3_percentage = retVal[37], 

        hstore_bottom3_3_number = str(int(retVal[56])),
        hstore_bottom3_3_name = retVal[38], 
        hstore_bottom3_3_votes = retVal[39], 
        hstore_bottom3_3_percentage = retVal[40], 
        hstore_bottom3_2_number = str(int(retVal[56])-1) if int(retVal[56])-1 > 0 else '-',
        hstore_bottom3_2_name = retVal[41], 
        hstore_bottom3_2_votes = retVal[42], 
        hstore_bottom3_2_percentage = retVal[43],
        hstore_bottom3_1_number = str(int(retVal[56])-2) if int(retVal[56])-2 > 0 else '-',
        hstore_bottom3_1_name = retVal[44], 
        hstore_bottom3_1_votes = retVal[45], 
        hstore_bottom3_1_percentage = retVal[46], 

        hstore_trending3_1_name = retVal[47], 
        hstore_trending3_1_votes = retVal[48], 
        hstore_trending3_1_percentage = retVal[49],
        hstore_trending3_2_name = retVal[50], 
        hstore_trending3_2_votes = retVal[51], 
        hstore_trending3_2_percentage = retVal[52], 
        hstore_trending3_3_name = retVal[53], 
        hstore_trending3_3_votes = retVal[54], 
        hstore_trending3_3_percentage = retVal[55],
        hstore_candidates_remaining = retVal[56],
        hstore_votes_til_next_delete = retVal[57],

        top3_1_same = top3_1_same_flag,
        top3_2_same = top3_2_same_flag,
        top3_3_same = top3_3_same_flag,
        bottom3_1_same = bottom3_1_same_flag,
        bottom3_2_same = bottom3_2_same_flag,
        bottom3_3_same = bottom3_3_same_flag,
        trending3_1_same = trending3_1_same_flag,
        trending3_2_same = trending3_2_same_flag,
        trending3_3_same = trending3_3_same_flag,

        sstore_contestants_1_name = sortedSStoreContestants[0][0],
        sstore_contestants_1_alive = sortedSStoreContestants[0][1],
        sstore_contestants_2_name = sortedSStoreContestants[1][0],
        sstore_contestants_2_alive = sortedSStoreContestants[1][1],
        sstore_contestants_3_name = sortedSStoreContestants[2][0],
        sstore_contestants_3_alive = sortedSStoreContestants[2][1],
        sstore_contestants_4_name = sortedSStoreContestants[3][0],
        sstore_contestants_4_alive = sortedSStoreContestants[3][1],
        sstore_contestants_5_name = sortedSStoreContestants[4][0],
        sstore_contestants_5_alive = sortedSStoreContestants[4][1],
        sstore_contestants_6_name = sortedSStoreContestants[5][0],
        sstore_contestants_6_alive = sortedSStoreContestants[5][1],
        sstore_contestants_7_name = sortedSStoreContestants[6][0],
        sstore_contestants_7_alive = sortedSStoreContestants[6][1],
        sstore_contestants_8_name = sortedSStoreContestants[7][0],
        sstore_contestants_8_alive = sortedSStoreContestants[7][1],
        sstore_contestants_9_name = sortedSStoreContestants[8][0],
        sstore_contestants_9_alive = sortedSStoreContestants[8][1],
        sstore_contestants_10_name = sortedSStoreContestants[9][0],
        sstore_contestants_10_alive = sortedSStoreContestants[9][1],
        sstore_contestants_11_name = sortedSStoreContestants[10][0],
        sstore_contestants_11_alive = sortedSStoreContestants[10][1],
        sstore_contestants_12_name = sortedSStoreContestants[11][0],
        sstore_contestants_12_alive = sortedSStoreContestants[11][1],

        hstore_contestants_1_name = sortedHStoreContestants[0][0],
        hstore_contestants_1_alive = sortedHStoreContestants[0][1],
        hstore_contestants_2_name = sortedHStoreContestants[1][0],
        hstore_contestants_2_alive = sortedHStoreContestants[1][1],
        hstore_contestants_3_name = sortedHStoreContestants[2][0],
        hstore_contestants_3_alive = sortedHStoreContestants[2][1],
        hstore_contestants_4_name = sortedHStoreContestants[3][0],
        hstore_contestants_4_alive = sortedHStoreContestants[3][1],
        hstore_contestants_5_name = sortedHStoreContestants[4][0],
        hstore_contestants_5_alive = sortedHStoreContestants[4][1],
        hstore_contestants_6_name = sortedHStoreContestants[5][0],
        hstore_contestants_6_alive = sortedHStoreContestants[5][1],
        hstore_contestants_7_name = sortedHStoreContestants[6][0],
        hstore_contestants_7_alive = sortedHStoreContestants[6][1],
        hstore_contestants_8_name = sortedHStoreContestants[7][0],
        hstore_contestants_8_alive = sortedHStoreContestants[7][1],
        hstore_contestants_9_name = sortedHStoreContestants[8][0],
        hstore_contestants_9_alive = sortedHStoreContestants[8][1],
        hstore_contestants_10_name = sortedHStoreContestants[9][0],
        hstore_contestants_10_alive = sortedHStoreContestants[9][1],
        hstore_contestants_11_name = sortedHStoreContestants[10][0],
        hstore_contestants_11_alive = sortedHStoreContestants[10][1],
        hstore_contestants_12_name = sortedHStoreContestants[11][0],
        hstore_contestants_12_alive = sortedHStoreContestants[11][1]

    )
    
        
    

# This is a GET route to display the landing page of bikeshare
@app.route('/')
def home():
    return render_template('index.html')
    


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('python ' + sys.argv[0] + ' <remote server> <S-Store log file> <H-Store log file> <Number of contestants>')
        sys.exit(2)

    print('starting server!')
    global remoteserver
    remoteserver = sys.argv[1]
    global sstorelogfile
    sstorelogfile = sys.argv[2]
    global hstorelogfile
    hstorelogfile = sys.argv[3]
    global contestants_number
    contestants_number = int(sys.argv[4])

    print remoteserver

    os.system('rm ' + sstorelogfile)
    os.system('rm ' + hstorelogfile)
    
    sstorecontestantfile = '/'.join(sstorelogfile.split('/')[:-1])+'/sstorecontestants.txt'
    os.system('rm ' + sstorecontestantfile)
    hstorecontestantfile = '/'.join(hstorelogfile.split('/')[:-1])+'/hstorecontestants.txt'
    os.system('rm ' + hstorecontestantfile)

    if debug:
        app.run(host='127.0.0.1', port=8081, debug=True)
    else:
        app.run(host='0.0.0.0', port=8081, debug=True)

