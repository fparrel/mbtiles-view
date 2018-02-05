#!/usr/bin/env python

from flask import Flask,Response,jsonify,abort,redirect
import sqlite3
import sys

# Create flask application
application = Flask(__name__)
#application.config['UPLOAD_FOLDER'] = 'uploads'
#application.secret_key = keysnpwds['secret_key']

mbtiles_filename = None
tms = False

def getCnx():
    return sqlite3.connect(mbtiles_filename)

@application.route('/<int:z>/<int:x>/<int:y>.<ext>')
def serveTile(z,x,y,ext):
    if tms:
        y = (2 ** z) - y - 1
    req = 'SELECT tile_data FROM tiles WHERE zoom_level=%d AND tile_column=%d AND tile_row=%d' % (z,x,y)
    print req
    got = getCnx().execute(req).fetchone()
    if got != None:
        return Response(str(got[0]), mimetype='image/%s'%ext)
    else:
        abort(404)

@application.route('/info')
def getCenter():
    return jsonify({'centerlat':(bounds[1]+bounds[3])/2.0,'centerlon':(bounds[0]+bounds[2])/2.0,'minzoom':min_zoom,'name':map_name})

@application.route('/')
def index():
    return redirect('static/index.html')


## Program entry point

if __name__ == '__main__':
    # Start web server
    if len(sys.argv)==2:
        if sys.argv[1] in ('-h','--help'):
            print 'Usage: %s file.mbtiles tms (yes/no)' % sys.argv[0]
            exit()
    elif len(sys.argv)==3:
        mbtiles_filename = sys.argv[1]
        tms = sys.argv[2]=='yes'
    else:
        print 'Usage: %s file.mbtiles' % sys.argv[0]
        exit()
    cnx = sqlite3.connect(mbtiles_filename)
    bounds = map(float,cnx.execute("SELECT value FROM metadata WHERE name='bounds'").fetchall()[0][0].split(','))
    min_zoom = int(cnx.execute("SELECT MIN(zoom_level) FROM tiles;").fetchall()[0][0])
    map_name = cnx.execute("SELECT value FROM metadata WHERE name='name'").fetchall()[0][0]
    print bounds,min_zoom,map_name
    application.run(port=8080,debug=True)

