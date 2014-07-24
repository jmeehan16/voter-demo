import syslog
from flask import Flask, request, render_template, send_from_directory, Response, jsonify
from flask.ext.bootstrap import Bootstrap
import json
import re, os

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import sstoreclient

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import time

app = Flask(__name__)

bootstrap = Bootstrap(app)

# Set debug mode.
debug = False

# Create S-Store client object instance
db = sstoreclient.sstoreclient()

# ================
# REST API function definitions
# ================

def getResults():
    proc = 'Results'
    baseDir = '../h-store'
    os.chdir(baseDir)
    cmd = 'ant hstore-invoke -Dproject=voterdemosstorecorrect -Dproc=Results > tmp'
    os.system(cmd)
    f = open('tmp', 'r')
    lines = f.readlines()

    retVal = []
    startLine = 0
    for line in lines:
        line = line.strip()
        if line.startswith('[java] Results: '):
            break
        startLine += 1

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

    f.close()
    os.chdir('../voter-demo')

    return retVal



# Get top 3 from S-Store
# ========
def getSStoreTop3():
    proc = 'getTop3'
    baseDir = '../h-store'
    os.chdir(baseDir)
    cmd = 'ant hstore-invoke -Dproject=voterdemosstorewinsp1dist -Dproc=getTop3 -Ddataonly=true > tmp'
    os.system(cmd)
    f = open('tmp', 'r')
    lines = f.readlines()
    
    resultLines = [line for line in lines if '[java]' in line ]
    results = [' '.join(line.strip().split(' ')[1:]) for line in resultLines]
    results = results[:-1]  # remove the last empty line
    print(results)
    f.close()
    os.chdir('../voter-demo')
#    try:
#        data = db.call_proc(proc)
#        print(data)
#    except Exception as e:
#        syslog.log_procerr(proc,str(e))
#        return '{}', 500
#	pass
    
    if len(results) > 0:
        sstore_top3_1_name = results[0].split(' ')[0][:-1]
        sstore_top3_1_votes = results[0].split(' ')[1][:-1]
        sstore_top3_1_percentage = '14.9%'
    else:
        sstore_top3_1_name = ''
        sstore_top3_1_votes = ''
        sstore_top3_1_percentage = ''
    if len(results) > 1:
        sstore_top3_2_name = results[1].split(' ')[0][:-1]
        sstore_top3_2_votes = results[1].split(' ')[1][:-1]
        sstore_top3_2_percentage = '14.1%'
    else:
        sstore_top3_2_name = ''
        sstore_top3_2_votes = ''
        sstore_top3_2_percentage = ''
    if len(results) > 2:
        sstore_top3_3_name = results[2].split(' ')[0][:-1]
        sstore_top3_3_votes = results[2].split(' ')[1][:-1]
        sstore_top3_3_percentage = '12.6%'
    else:
        sstore_top3_3_name = ''
        sstore_top3_3_votes = ''
        sstore_top3_3_percentage = ''
        
    return sstore_top3_1_name, sstore_top3_1_votes, sstore_top3_1_percentage,  \
            sstore_top3_2_name, sstore_top3_2_votes, sstore_top3_2_percentage, \
            sstore_top3_3_name, sstore_top3_3_votes, sstore_top3_3_percentage

# Get top 3 from H-Store
# ========
def getHStoreTop3():
    hstore_top3_1_name = 'Louise Burns'
    hstore_top3_1_votes = 3961
    hstore_top3_1_percentage = '14.9%'
    hstore_top3_2_name = 'Stephen Fearing'
    hstore_top3_2_votes = 3746
    hstore_top3_2_percentage = '14.1%'
    hstore_top3_3_name = 'Celine Dion'
    hstore_top3_3_votes = 3340
    hstore_top3_3_percentage = '12.6%'
    return hstore_top3_1_name, hstore_top3_1_votes, hstore_top3_1_percentage,  \
            hstore_top3_2_name, hstore_top3_2_votes, hstore_top3_2_percentage, \
            hstore_top3_3_name, hstore_top3_3_votes, hstore_top3_3_percentage

# Get bottom 3 from S-Store
# ========
def getSStoreBottom3():
    sstore_bottom3_1_name = 'Ruth Moody'
    sstore_bottom3_1_votes = 1564
    sstore_bottom3_1_percentage = '5.9%'
    sstore_bottom3_2_name = 'Justin Bieber'
    sstore_bottom3_2_votes = 1341
    sstore_bottom3_2_percentage = '5.0%'
    sstore_bottom3_3_name = 'Daniel Romano'
    sstore_bottom3_3_votes = 1340
    sstore_bottom3_3_percentage = '5.0%'
    return sstore_bottom3_1_name, sstore_bottom3_1_votes, sstore_bottom3_1_percentage,  \
            sstore_bottom3_2_name, sstore_bottom3_2_votes, sstore_bottom3_2_percentage, \
            sstore_bottom3_3_name, sstore_bottom3_3_votes, sstore_bottom3_3_percentage

# Get bottom 3 from H-Store
# ========
def getHStoreBottom3():
    hstore_bottom3_1_name = 'Ruth Moody'
    hstore_bottom3_1_votes = 1564
    hstore_bottom3_1_percentage = '5.9%'
    hstore_bottom3_2_name = 'Daniel Romano'
    hstore_bottom3_2_votes = 1346
    hstore_bottom3_2_percentage = '5.0%'
    hstore_bottom3_3_name = 'Justin Bieber'
    hstore_bottom3_3_votes = 1340
    hstore_bottom3_3_percentage = '5.0%'
    return hstore_bottom3_1_name, hstore_bottom3_1_votes, hstore_bottom3_1_percentage,  \
            hstore_bottom3_2_name, hstore_bottom3_2_votes, hstore_bottom3_2_percentage, \
            hstore_bottom3_3_name, hstore_bottom3_3_votes, hstore_bottom3_3_percentage

# Get trending 3 from S-Store
# ========
def getSStoreTrending3():
    sstore_trending3_1_name = 'Louise Burns'
    sstore_trending3_1_votes = 701
    sstore_trending3_1_percentage = '18.8%'
    sstore_trending3_2_name = 'Justin Bieber'
    sstore_trending3_2_votes = 470
    sstore_trending3_2_percentage = '12.6%'
    sstore_trending3_3_name = 'Celine Dion'
    sstore_trending3_3_votes = 463
    sstore_trending3_3_percentage = '12.4%'
    return sstore_trending3_1_name, sstore_trending3_1_votes, sstore_trending3_1_percentage,  \
            sstore_trending3_2_name, sstore_trending3_2_votes, sstore_trending3_2_percentage, \
            sstore_trending3_3_name, sstore_trending3_3_votes, sstore_trending3_3_percentage

# Get trending 3 from H-Store
# ========
def getHStoreTrending3():
    hstore_trending3_1_name = 'Louise Burns'
    hstore_trending3_1_votes = 703
    hstore_trending3_1_percentage = '18.8%'
    hstore_trending3_2_name = 'Celine Dion'
    hstore_trending3_2_votes = 471
    hstore_trending3_2_percentage = '12.6%'
    hstore_trending3_3_name = 'Justin Bieber'
    hstore_trending3_3_votes = 464
    hstore_trending3_3_percentage = '12.4%'
    return hstore_trending3_1_name, hstore_trending3_1_votes, hstore_trending3_1_percentage,  \
            hstore_trending3_2_name, hstore_trending3_2_votes, hstore_trending3_2_percentage, \
            hstore_trending3_3_name, hstore_trending3_3_votes, hstore_trending3_3_percentage


# Logins
# ========

# User login
# ---------
# Verb:      POST
# Route:     /REST/1.0/login/check
# Form data: <string:user_name>
# Response:  {<int:user_id>}
@app.route('/REST/1.0/login/check', methods=['POST'])
def check_login():
    db = open('data/users.json','r')
    data = json.load(db)
    target_user = request.form['user_name']
    for u in data:
        if u['user_name'] == target_user:
            return json.dumps(subdict(u, ['user_id']), ensure_ascii=True)
    return '{}', 404

# Stations
# =========

# Get nearby stations
# ---------
# Verb:     GET
# Route:    /REST/1.0/stations/all
# Response: [ {<int:station_id>,<float:lat>,<float:lon>,<string:address>}, ... ]
@app.route('/REST/1.0/stations/all')
def all_stations():
    try:
        db = open('/home/dramage/bikeshare-web/data/stations.json','r')
    except:
        syslog.syslog(syslog.LOG_ERR, "could not open stations.json")

    data = json.load(db)
    return json.dumps(data, ensure_ascii=True)
# Verb:     GET
# Route:    /REST/1.0/stations/all/<float:lat>/<float:lon>/<float:rad>
# Response: [ {<int:station_id>,<float:lat>,<float:lon>,<string:address>}, ... ]
@app.route('/REST/1.0/stations/all/<float:lat>/<float:lon>/<float:rad>')
def all_stations_in_rad(lat, lon, rad):
    return all_stations()

# Get individual station info
# ---------
# Verb:     GET
# Route:    /REST/1.0/stations/info/<int:station_id>
# Response: {<int:num_bikes>,<int:num_docks>,<string:address>,<float:price>}
@app.route('/REST/1.0/stations/info/<int:station_id>')
def stations_info(station_id):
    s = '/home/dramage/bikeshare-web/data/station_' + str(station_id) + '.json'
    print s
    try:
        db = open(s,'r')
    except IOError:
        return '{}', 404
    data = json.load(db)
    return json.dumps(data, ensure_ascii=True)

# Bikes
# ========

# Get current bike positions
# ---------
# Verb:     GET
# Route:    /REST/1.0/bikes/active
# Response: [ {<int:bike_id>,<float:lat>,<float:lon>}, ... ]
@app.route('/REST/1.0/bikes/active')
def active_bikes():
    db = open('data/bikes.json','r')
    data = json.load(db)
    return json.dumps(data, ensure_ascii=True)
# Verb:     GET
# Route:    /REST/1.0/bikes/active/<float:lat>/<float:lon>/<float:rad>
# Response: [ {<int:bike_id>,<float:lat>,<float:lon>}, ... ]
@app.route('/REST/1.0/bikes/active/<float:lat>/<float:lon>/<float:rad>')
def active_bikes_in_rad(lat, lon, rad):
    return active_bikes()

# Get individual bike info
# ---------
# Verb:     GET
# Route:    /REST/1.0/bikes/info/<int:bike_id>
# Response: {<float:lat>,<float:lon>,<float:distance>,<int:time>,
#            <[ string, ... ]:reports>}
@app.route('/REST/1.0/bikes/info/<int:bike_id>')
def bike_info(bike_id):
    s = 'data/bike_' + str(bike_id) + '.json'
    try:
        db = open(s,'r')
    except IOError:
        return '{}', 404
    data = json.load(db)
    return json.dumps(data, ensure_ascii=True)

# Checkout bike
# ---------
# Verb:      POST
# Route:     /REST/1.0/bikes/checkout
# Form data: <int:station_id>
# Response:  {<int:bike_id>}
@app.route('/REST/1.0/bikes/checkout', methods=['POST'])
def checkout_bike():
    db = open('data/checkout.json','r')
    data = json.load(db)
    target_station = request.form['station_id']
    if target_station == str(data['station_id']):
        bikes = data['bikes']
        return json.dumps(bikes[0], ensure_ascii=True)
    return '{}', 403

# Checkin bike
# ---------
# Verb:      POST
# Route:     /REST/1.0/bikes/checkin
# Form data: <int:bike_id>,<int:station_id>
# Response:  {<float:price>,<float:discount>}
@app.route('/REST/1.0/bikes/checkin', methods=['POST'])
def checkin_bike():
    db = open('data/checkin.json','r')
    data = json.load(db)
    target_station = request.form['station_id']
    target_bike = request.form['bike_id']
    if target_station == str(data['station_id']):
        if data['num_docks'] > 0:
            price = float(data['price']) - (float(data['price']) * data['discount'])
            retn = { 'price': price, 'discount': data['discount'] }
            return json.dumps(retn, ensure_ascii=True)
    return '{}', 403

# Get/send recent bike positional data
# ---------
# Helper function which calls either the get or send version of this function,
# depending on which HTTP verb is used.
@app.route('/REST/1.0/bikes/pos/<int:bike_id>', methods=['GET','POST'])
def bike_pos(bike_id):
    if request.method == 'GET':
        return get_bike_position(bike_id)
    else:
        return send_bike_position(bike_id)
# Verb:     GET
# Route:    /REST/1.0/bikes/pos/<int:bike_id>
# Response: [ {<float:lat>,<float:lon>,<int:time>}, ... ]
def get_bike_position(bike_id):
    s = 'data/bikepos_' + str(bike_id) + '.json'
    try:
        db = open(s,'r')
    except IOError:
        return '{}', 404
    data = json.load(db)
    return json.dumps(data, ensure_ascii=True)
# Verb:      POST
# Route:     /REST/1.0/bikes/pos/<int:bike_id>
# Form data: <float:lat>,<float:lon>
# Response:  {}
def send_bike_position(bike_id):
    lat = request.form['lat']
    lon = request.form['lon']
    s = 'data/bikepos_' + str(bike_id) + '.json'
    try:
        db = open(s,'r')
    except IOError:
        return '{}', 404
    return '{}'

# Helper function. Extracts and returns only the set of key/value pairs that
# we want from a given dict.
def subdict(d, keys):
    d2 = dict()
    for k, v in d.iteritems():
        if k in keys:
            d2[k] = v
    return d2

# ================
# Main app function definitions
# ================

# This is a GET route to display the "view all stations" page
@app.route('/stations')
def view_all_stations():
    return render_template('stations.html')

# This is a GET route to display the "view all bikes" page
@app.route('/bikes')
def view_all_bikes():
    return render_template('bikes.html')

# This is a GET route to display the "view all riders" page
@app.route('/users')
def view_all_riders():
    return render_template('users.html')


@app.route('/_start_voting')
def start_voting():
    return jsonify(removal_votes = 5000)

@app.route('/_get_removal_votes')
def get_removal_votes():
    return jsonify(removal_votes = 3428)
    

@app.route('/_get_results')
def get_results():
    retVal = getResults()
    retVal.extend(getHStoreTop3())
    retVal.extend(getHStoreBottom3())
    retVal.extend(getHStoreTrending3())
    retVal.extend([3428])
        
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
    

# This is a GET route to display a single bike page of a given name
@app.route('/bike/<int:bike_id>')
def view_bike(bike_id):
    return render_template('bikes.html',bike_id=bike_id)

# This is a GET route to display a single station page of a given name
@app.route('/station/<int:statio_id>')
def view_station(station_id):
    return render_template('stations.html',station_id=station_id)

# This is a GET route to display a single user page of a given name
@app.route('/user/<int:user_id>')
def view_user(user_id):
    return render_template('users.html',user_id=user_id)

@app.route('/javascript/<path:path>', methods=['GET','OPTIONS'])
def js_proxy(path):
    return send_from_directory(app.root_path + '/javascript/', path)

@app.errorhandler(404)
def page_not_found(e):
    if re.match('/REST',request.path):
        return '{}', 404
    else:
        return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    if re.match('/REST',request.path):
        return '{}', 500
    else:
        return render_template('500.html'), 500

if __name__ == '__main__':
    if debug:
        app.run(host='127.0.0.1', port=8081, debug=True)
    else:
        app.run(host='0.0.0.0', port=8081, debug=True)


