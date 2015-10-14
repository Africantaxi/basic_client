#coding: utf-8
from flask import Flask, render_template, request, redirect
import requests, json, os, sys
from copy import deepcopy

app = Flask(__name__)
app.config.from_object('default_settings')
if 'BASIC_SETTINGS' in os.environ.keys():
    app.config.from_envvar('BASIC_SETTINGS')


headers_request = {
    "X-VERSION": 2,
    "Accept": "application/json",
}


headers_request_post = dict({"content-type": "application/json"}, **headers_request)
base_url = app.config['BASE_URL']

class SettingError(Exception):
    pass

def make_headers(is_post=False):
    if is_post:
        headers = deepcopy(headers_request_post)
    else:
        headers = deepcopy(headers_request)
    headers['X-API-KEY'] = request.args.get('apikey', app.config['X_API_KEY'])
    if headers['X-API-KEY'] is None:
        raise SettingError
    return headers

@app.errorhandler(SettingError)
def errorapikey(error):
    return render_template('get_token.html', page=str(request.url_rule.rule))


@app.route("/")
def index():
    get_location = 'lat' not in request.args.keys()
    lat = request.args.get('lat', 48.8)
    lon = request.args.get('lon', 2.3)
    headers = make_headers()
    r = requests.get('{}/taxis/?lat={}&lon={}'.format(base_url, lat, lon),
            headers=headers)
    if r.status_code != 200:
        return render_template('templates/error.html', erreur=r.json()['message'])
    return render_template('index.html',
            taxis=r.json()['data'], lat=lat, lon=lon, get_location=get_location,
            apikey=headers['X-API-KEY'])

@app.route('/hail/')
def hail():
    taxi_id = request.args.get('taxi_id')
    operateur = request.args.get('operateur')
    customer_lat = request.args.get('lat', 48.8)
    customer_lon = request.args.get('lon', 2.3)


    r = requests.get('http://api-adresse.data.gouv.fr/reverse/?lat={}&lon={}'.\
            format(customer_lat, customer_lon))
    if r.status_code == 200 and 'features' in r.json():
        p = r.json()['features'][0]['properties']
        customer_address = p.get('label', p['name'])
    else:
        customer_address = u'Gare de Lyon, Paris'

    payload = {
        'data': [
            {
                'customer_id': 'moi',
                'customer_lat': float(customer_lat),
                'customer_lon': float(customer_lon),
                'customer_address': customer_address,
                'customer_phone_number': '089838493',
                'taxi_id': taxi_id,
                'operateur': operateur
            }
        ]
    }
    headers = make_headers(True)
    r = requests.post('{}/hails/'.format(base_url), headers=headers,
            data=json.dumps(payload))
    if r.status_code < 200 or r.status_code >= 300:
        return render_template('error.html', erreur=r.json()['message'])
    return redirect('/hail/{}?apikey={}'.format(r.json()['data'][0]['id'],
        headers['X-API-KEY']))

@app.route('/hail/<hail_id>')
def hail_id(hail_id):
    headers = make_headers()
    r = requests.get('{}/hails/{}'.format(base_url, hail_id), headers=headers)
    if r.status_code != 200:
        render_template('error.html', erreur=r.json()['message'])
    status = r.json()['data'][0]['status']
    map_first_status = {'emitted': u'Émis', 'received': u'Reçu',
            'sent_to_operator': u'Envoyé à l\'opérateur',
            'received_by_operator': u'Reçu par l\'opérateur',
            'received_by_taxi': u'Reçu par le taxi'
    }

    if status in map_first_status.keys():
        return render_template('hail_waiting.html', status=map_first_status[status])

    if status == 'accepted_by_taxi':
        return render_template('accept_hail.html', hail_id=hail_id,
                apikey=headers['X-API-KEY'])
    final_status = {
            'declined_by_taxi': u'Le taxi a refusé la course',
            'accepted_by_customer': u'Le taxi arrive',
            'declined_by_customer': u'Vous avez annulé la course',
            'incident_customer': u'Incident client',
            'incident_taxi': u'Incident taxi',
            'timeout_customer': u'Timeout client',
            'timeout_taxi': u'Timeout taxi',
            'outdated_customer': u'outdated customer',
            'outdated_taxi': u'outdated taxi',
            'failure': u'Quelque chose s\'est mal passé',
    }

    if status in final_status.keys():
        return render_template('final_status.html', status=final_status[status])
    return render_template('final_status.html', status='Status inconnu')

@app.route('/hail/<hail_id>/accept')
def accept_hail(hail_id):
    payload = {'data': [
        {'status': 'accepted_by_customer'}
    ]}
    headers = make_headers(True)
    r = requests.put('{}/hails/{}/'.format(base_url, hail_id), headers=headers,
            data=json.dumps(payload))
    if r.status_code < 200 or r.status_code >= 300:
        return render_template('error.html', erreur=r.json()['message'])
    return redirect('/hail/{}?apikey={}'.format(hail_id, headers['X-API-KEY']))


if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run(port=app.config['PORT'])
