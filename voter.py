import syslog
from flask import Flask, request, render_template, send_from_directory, Response, jsonify
from flask.ext.bootstrap import Bootstrap
import json
import re, os

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

def getSStoreResults():
    proc = 'Results'
    baseDir = '../h-store'
    os.chdir(baseDir)
    cmd = 'ant hstore-invoke -Dproject=voterdemosstorecorrect -Dproc=Results > tmp'
    os.system(cmd)
    f = open('tmp', 'r')
    lines = f.readlines()
    f.close()
    os.chdir('../voter-demo')
    return parseFile(lines)


def getHStoreResults():
    proc = 'Results'
    baseDir = '../h-store'
    os.chdir(baseDir)
    cmd = 'ssh istc3 "cd insertinto/h-store; ant hstore-invoke -Dproject=voterdemosstorecorrect -Dproc=Results > tmp"'
    os.system(cmd)
    cmd = 'scp istc3:~/insertinto/h-store/tmp tmp_hstore'
    os.system(cmd)
    f = open('tmp_hstore', 'r')
    lines = f.readlines()
    f.close()
    os.chdir('../voter-demo')
    return parseFile(lines)


def parseFile(lines):
    retVal = []
    startLine = 0
    for line in lines:
        line = line.strip()
        if line.startswith('[java] Results: '):
            break
        startLine += 1

#    if len(lines) < 24:  # no results yet
#        for i in range(27):
#            retVal.append(' ')
#        return retVal

    totalVotes = lines[startLine+24].replace('[java]', ' ').strip().split(', ')[0][:-1]
    trendingVotes = lines[startLine+29].replace('[java]', ' ').strip().split(', ')[0][:-1]

    retVal.append(lines[startLine+3].replace('[java]', ' ').strip().split(', ')[0])
    votes = lines[startLine+3].replace('[java]', ' ').strip().split(', ')[1][:-1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[startLine+4].replace('[java]', ' ').strip().split(', ')[0])
    votes = lines[startLine+4].replace('[java]', ' ').strip().split(', ')[1][:-1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[startLine+5].replace('[java]', ' ').strip().split(', ')[0])
    votes = lines[startLine+5].replace('[java]', ' ').strip().split(', ')[1][:-1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
        
    retVal.append(lines[startLine+10].replace('[java]', ' ').strip().split(', ')[0])
    votes = lines[startLine+10].replace('[java]', ' ').strip().split(', ')[1][:-1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[startLine+11].replace('[java]', ' ').strip().split(', ')[0])
    votes = lines[startLine+11].replace('[java]', ' ').strip().split(', ')[1][:-1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))
    retVal.append(lines[startLine+12].replace('[java]', ' ').strip().split(', ')[0])
    votes = lines[startLine+12].replace('[java]', ' ').strip().split(', ')[1][:-1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(totalVotes)))

    retVal.append(lines[startLine+17].replace('[java]', ' ').strip().split(', ')[0])
    votes = lines[startLine+17].replace('[java]', ' ').strip().split(', ')[1][:-1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(trendingVotes)))
    retVal.append(lines[startLine+18].replace('[java]', ' ').strip().split(', ')[0])
    votes = lines[startLine+18].replace('[java]', ' ').strip().split(', ')[1][:-1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(trendingVotes)))
    retVal.append(lines[startLine+19].replace('[java]', ' ').strip().split(', ')[0])
    votes = lines[startLine+19].replace('[java]', ' ').strip().split(', ')[1][:-1]
    retVal.append(votes)
    retVal.append('%2.1f%%' % (int(votes)*100.0/int(trendingVotes)))

    return retVal



@app.route('/_start_voting')
def start_voting():
    # reset_results()
    baseDir = '../h-store'
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
        cmd = 'ant hstore-benchmark -Dproject=voterdemosstorecorrect -Dclient.threads_per_host=1 -Dclient.txnrate=50'
        os.system(cmd)
        os.chdir('../voter-demo')
        os._exit(0)
    else:
        hstorepid = os.fork()
        if hstorepid == 0: # Running H-Store benchmark on the remote
            cmd = 'ssh istc3 "cd insertinto/h-store; ant hstore-benchmark -Dproject=voterdemohstorecorrect -Dclient.threads_per_host=1 -Dclient.txnrate=50"'
            os.system(cmd)
            os._exit(0)
        else:
            return



@app.route('/_get_removal_votes')
def get_removal_votes():
    return jsonify(removal_votes = 3428)



@app.route('/_reset_results')
def reset_results():
    get_results(reset=True)



@app.route('/_get_results')
def get_results(reset=False):
    if reset == False:
        retVal = getSStoreResults()
        retVal.extend(getHStoreResults())
        retVal.extend([3428])
    else:
        for i in range(55):
            retVal.append('')
#    print(retVal)
        
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

        sstore_bottom3_1_name = retVal[9], 
        sstore_bottom3_1_votes = retVal[10], 
        sstore_bottom3_1_percentage = retVal[11], 
        sstore_bottom3_2_name = retVal[12], 
        sstore_bottom3_2_votes = retVal[13], 
        sstore_bottom3_2_percentage = retVal[14], 
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

        hstore_top3_1_name = retVal[27], 
        hstore_top3_1_votes = retVal[28], 
        hstore_top3_1_percentage = retVal[29],  
        hstore_top3_2_name = retVal[30], 
        hstore_top3_2_votes = retVal[31], 
        hstore_top3_2_percentage = retVal[32], 
        hstore_top3_3_name = retVal[33], 
        hstore_top3_3_votes = retVal[34], 
        hstore_top3_3_percentage = retVal[35], 

        hstore_bottom3_1_name = retVal[36], 
        hstore_bottom3_1_votes = retVal[37], 
        hstore_bottom3_1_percentage = retVal[38], 
        hstore_bottom3_2_name = retVal[39], 
        hstore_bottom3_2_votes = retVal[40], 
        hstore_bottom3_2_percentage = retVal[41],
        hstore_bottom3_3_name = retVal[42], 
        hstore_bottom3_3_votes = retVal[43], 
        hstore_bottom3_3_percentage = retVal[44], 

        hstore_trending3_1_name = retVal[45], 
        hstore_trending3_1_votes = retVal[46], 
        hstore_trending3_1_percentage = retVal[47],
        hstore_trending3_2_name = retVal[48], 
        hstore_trending3_2_votes = retVal[49], 
        hstore_trending3_2_percentage = retVal[50], 
        hstore_trending3_3_name = retVal[51], 
        hstore_trending3_3_votes = retVal[52], 
        hstore_trending3_3_percentage = retVal[53],
        removal_votes = retVal[54]
    )
    
        
    

# This is a GET route to display the landing page of bikeshare
@app.route('/')
def home():
    return render_template('index.html')
    


if __name__ == '__main__':
    if debug:
        app.run(host='127.0.0.1', port=8081, debug=True)
    else:
        app.run(host='0.0.0.0', port=8081, debug=True)


