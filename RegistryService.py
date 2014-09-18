__author__ = 'mscholz'

import json
import bottle
from bottle import route, run, request, abort, error, response
from pymongo import Connection
from mongokit import *
from json import dumps


connection = Connection('localhost', 27017)
db = connection.mydatabase


# Group Assets and Services
## Assets and Services Collection [/AssetsServices]
### List [GET]
@route('/AssetsServices', method='GET')
def list_assets():
    allAssets = list(db.assets.find())

    for asset in allAssets:
        asset.pop("_id", None)

    response.content_type = 'application/json'
    return dumps(allAssets)


### Create [POST]
@route('/AssetsServices', method='POST')
def associate_asset():
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    newAsset = json.loads(data)
    if not 'assetHash' in newAsset:
        abort(400, 'assetHash not specified')
    if not 'serviceToken' in newAsset:
        abort(400, 'serviceToken not specified')
    if not 'URI' in newAsset:
        abort(400, 'URI not specified')

    validKeys = ['assetHash', 'serviceToken', 'URI', 'description', 'metadata']
    for key in newAsset:
        if key not in validKeys:
            abort(400, key + ' is not a valid key')

    asset = db.assets.find_one(
        {'$and': [{'assetHash': newAsset['assetHash']}, {'serviceToken': newAsset['serviceToken']}]})
    if asset:
        try:
            db.assets.remove(asset)
        except Exception as exception:
            abort(400, str(exception))

    try:
        db.assets.save(newAsset)
    except Exception as exception:
        abort(400, str(exception))


## Assets and Services Member [/AssetsServices/:assetHash]
### Read [GET]
@route('/AssetsServices/:assetHash', method='GET')
def get_assets(assetHash):
    assets = list(db.assets.find({'assetHash': assetHash}))
    if not assets:
        abort(404, 'No asset with assetHash %s' % assetHash)

    for asset in assets:
        asset.pop("_id", None)

    response.content_type = 'application/json'
    return dumps(assets)


### Delete [DELETE]
@route('/AssetsServices/:assetHash', method='DELETE')
def delete_assets(assetHash):
    assets = db.assets.find({'assetHash': assetHash})
    if not assets:
        abort(404, 'No assets with assetHash %s' % assetHash)

    try:
        db.assets.remove({'assetHash': assetHash})
    except Exception as exception:
        abort(400, str(exception))


## Assets and Services Member [/AssetsServices/:assetHash/:serviceToken]
### Read [GET]
@route('/AssetsServices/:assetHash/:serviceToken', method='GET')
def get_asset(assetHash, serviceToken):
    asset = db.assets.find_one({'$and': [{'assetHash': assetHash}, {'serviceToken': serviceToken}]})

    if not asset:
        abort(404, 'No asset with assetHash %s and serviceToken %s' % assetHash, serviceToken)

    try:
        del asset['_id']
    except KeyError:
        pass

    response.content_type = 'application/json'
    return dumps(asset)


### Update [PUT]
@route('/AssetsServices/:assetHash/:serviceToken', method='PUT')
def update_asset(assetHash, serviceToken):
    asset = db.assets.find_one({'$and': [{'assetHash': assetHash}, {'serviceToken': serviceToken}]})

    if not asset:
        abort(404, 'No asset with assetHash %s and serviceToken %s' % assetHash, serviceToken)

    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    newJson = json.loads(data)

    asset.update(newJson)

    try:
        db.assets.save(asset)
    except Exception as exception:
        abort(400, str(exception))


### Delete [DELETE]
@route('/AssetsServices/:assetHash/:serviceToken', method='DELETE')
def delete_asset(assetHash, serviceToken):
    asset = db.assets.find_one({'$and': [{'assetHash': assetHash}, {'serviceToken': serviceToken}]})

    if not asset:
        abort(404, 'No asset with assetHash %s and serviceToken %s' % assetHash, serviceToken)

    try:
        db.assets.remove({'$and': [{'assetHash': assetHash}, {'serviceToken': serviceToken}]})
    except Exception as exception:
        abort(400, str(exception))


# Group Service Registry
## Service Registry Collection [/ServiceRegistry]
### List [GET]
@route('/ServiceRegistry', method='GET')
def list_services():
    allServices = list(db.services.find())

    for service in allServices:
        service.pop("_id", None)

    response.content_type = 'application/json'
    return dumps(allServices)


### Create [POST]
@route('/ServiceRegistry', method='POST')
def register_service():
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    newService = json.loads(data)
    if not 'serviceName' in newService:
        abort(400, 'serviceName not specified')
    if not 'serviceToken' in newService:
        abort(400, 'serviceToken not specified')
    if not 'serviceDescription' in newService:
        abort(400, 'serviceDescription not specified')

    validKeys = ['serviceName', 'serviceToken', 'serviceDescription']
    for key in newService:
        if key not in validKeys:
            abort(400, key + ' is not a valid key')

    try:
        db.services.save(newService)
    except Exception as exception:
        abort(400, str(exception))


## Service Registry Member [/ServiceRegistry/:serviceToken]
### Read [GET]
@route('/ServiceRegistry/:serviceToken', method='GET')
def get_service(serviceToken):
    service = db.services.find_one({'serviceToken': serviceToken})
    if not service:
        abort(404, 'No service with serviceToken %s' % serviceToken)

    service.pop("_id", None)
    return service


### Update [PUT]
@route('/ServiceRegistry/:serviceToken', method='PUT')
def update_service(serviceToken):
    service = db.services.find_one({'serviceToken': serviceToken})
    if not service:
        abort(404, 'No service with serviceToken %s' % serviceToken)

    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    newJson = json.loads(data)

    validKeys = ['serviceName', 'serviceToken', 'serviceDescription']
    for key in newJson:
        if key not in validKeys:
            abort(400, key + ' is not a valid key')

    service.update(newJson)

    try:
        db.services.save(service)
    except Exception as exception:
        abort(400, str(exception))


### Delete [DELETE]
@route('/ServiceRegistry/:serviceToken', method='DELETE')
def delete_service(serviceToken):
    service = db.services.find_one({'serviceToken': serviceToken})
    if not service:
        abort(404, 'No service with serviceToken %s' % serviceToken)

    try:
        db.services.remove({'serviceToken': serviceToken})
    except Exception as exception:
        abort(400, str(exception))


run(host='localhost', port=8080, reloader=True, Debug=True)


