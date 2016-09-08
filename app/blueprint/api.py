from app.models import Order, OrderInfo, Itinerary, User,\
   Frag, db as alchemy, SupplierOrder, City, Country
from app.base.func import listToCSV, update_db
from flask import request, abort, session, Blueprint, Response
from flask_cors import CORS
from sqlalchemy import or_
import json
import requests
from config import config

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api_v1')
CORS(api_v1)
db = alchemy.session


@api_v1.route('/order', methods=['GET', 'POST', 'PUT'])
def orderHandler():
    if request.method == 'GET':
        wk_id = request.args.get('wk_id')
        status = request.args.get('status', None)
        if not wk_id:
            abort(400, 'wk_id is None')
        try:
            query = db.query(Order).\
                    filter_by(wk_id=wk_id)
        except Exception as e:
            print('--Error: /order GET --Exception: %s' % e)
            abort(400)
        if status:
            query = query.filter_by(status=status)
        res = [i.serialize() for i in query]
        if int(status) > 1:
            i = 0
            for order in query:
                q = db.query(SupplierOrder).filter_by(order_id=order.id).\
                        filter_by(status=2).first()
                it_id = q.it_id
                sup_id = q.supplier_id
                it = db.query(Itinerary).get(it_id)
                sup = db.query(User).get(sup_id)
                res[i].update({'itinerary': it.serialize()})
                res[i].update({'supplier': sup.serialize()})
                i += 1
        return Response(json.dumps(res), mimetype='application/json')
    if request.method == 'POST':
        req = json.loads(request.form.get('data'))
        if not req:
            req = request.get_json()
        # req = request.get_json()
        # # 验证post_id避免重复提交
        # if cache.get(req['post_id']):
        #     abort(400, '重复提交')
        # else:
        #     cache.set(req['post_id'], 1, timeout=10)
        #  创建对象
        try:
            order_data = req['data']
            order_data['topic'] = listToCSV(order_data['topic'])
            order_data['city_id'] = json.dumps(order_data['city_id'])
            order = Order(**order_data)
            db.add(order)
            db.commit()
        except Exception as e:
            print(e)
            abort(400, '参数错误，{}'.format(e))
        res = json.dumps({'order_id': order.id})
        return Response(res, mimetype='application/json')
    if request.method == 'PUT':
        req = json.loads(request.form.get('data'))
        if not req:
            req = request.get_json()
        orderInfo = db.query(OrderInfo).filter_by(
            order_id=req['order_id']).one_or_none()
        if not orderInfo:
            order = db.query(Order).filter_by(
                id=req['order_id']).one_or_none()
            if not order:
                abort(400, 'order_id错误')
            order.status = 1
            db.add(OrderInfo(**req))
            users = db.query(User)
            # TODO: 这里进行匹配
            for user in users:
                db.add(SupplierOrder(user.id, req['order_id']))
        else:
            update_db(orderInfo, req)
        db.commit()
        # # 匹配商家
        # city = db.query(City).filter_by(
        #     cityid=order.city_id).first_or_404()
        # # 匹配国家
        # ma = db.query(Match).filter_by(countryid=city.countryid)
        # # 匹配主题
        # if len(ma) > 3:
        #     mb = ma.filter_by(topic=order.topic)
        #     if len(mb) > 2:
        #         m = mb.limit(3)
        #     else:
        #         m = ma.limit(3)
        # else:
        #     m = mb
        # db.commit()
        res = {'order_id': req['order_id']}
        return Response(json.dumps(res), mimetype='application/json')


@api_v1.route('/order/<order_id>', methods=['GET', 'PUT'])
def orderInfoHandler(order_id):
    order = db.query(Order).filter_by(id=order_id).one_or_none()
    if not order:
        abort(400, 'order_id错误')
    if request.method == 'GET':
        res = order.serialize(get_all=True)
        if order.status == 3:
            q = db.query(SupplierOrder).filter_by(order_id=order.id).\
                    filter_by(status=3).first()
            it_id = q.it_id
            sup_id = q.supplier_id
            it = db.query(Itinerary).get(it_id)
            sup = db.query(User).get(sup_id)
            res.update({'itinerary': it.serialize()})
            res.update({'supplier': sup.serialize()})
        res = json.dumps(res)
        return Response(res, mimetype='application/json')

    if request.method == 'PUT':
        data = request.form.get('data', None)
        if not data:
            data = request.get_json()
        else:
            data = json.loads(data)
        status = data['status']
        order.status = status
        # 玩咖选择行程
        if status == 3:
            it_id = request.args.get('it_id', None)
            if not it_id:
                abort(400, '没有行程id')
            q = db.query(SupplierOrder).filter_by(order_id=order_id).\
                filter_by(it_id=it_id)
            q.status = 3
            o = db.query(SupplierOrder).filter_by(order_id=order_id).\
                filter(SupplierOrder.it_id != it_id)
            o.status = 6
            # 调用php后端接口
            it = db.query(Itinerary).get(it_id)
            data = order.php_serialize()
            data.update(it.php_serialize())
            http_code = requests.post(config.php_api_url,
                                      data=data)
            if http_code != 200:
                abort(400, 'php后端请求失败')
        db.commit()
        res = json.dumps({"success": "success"})
        return Response(res, mimetype='application/json')


@api_v1.route('/itinerary/<id>', methods=['GET'])
def itHandler(id):
    order = db.query(Itinerary).filter_by(id=id).one_or_none()
    if not order:
        abort(400, 'id错误')
    res = json.dumps(order.serialize())
    return Response(res, mimetype='application/json')


@api_v1.route('/supplier/<id>', methods=['GET'])
def userHandler(id):
    order = db.query(User).filter_by(id=id).one_or_none()
    if not order:
        abort(400, 'id错误')
    res = json.dumps(order.serialize())
    return Response(res, mimetype='application/json')


@api_v1.route('/piece/<id>', methods=['GET'])
def pieceHandler(id):
    order = db.query(Frag).filter_by(id=id).one_or_none()
    if not order:
        abort(400, 'id错误')
    res = json.dumps(order.serialize())
    return Response(res, mimetype='application/json')


@api_v1.route('/pieces', methods=['POST'])
def piecesHandler():
    dlist = request.form.get('data', None)
    if dlist is None:
        dlist = request.get_json()
        if dlist is None:
            abort(400, '数据错误')
    else:
        dlist = json.loads(dlist)
    res = []
    for dl in dlist:
        ps = db.query(Frag).filter(or_(Frag.id == v for v in dl)).all()
        xl = []
        for p in ps:
            xl.append(p.serialize())
        res.append(xl)
    res = json.dumps(res)
    return Response(res, mimetype='application/json')


@api_v1.route('/piecelist', methods=['GET'])
def pieceListHandler():
    userid = session.get('user_id')
    keyword = request.args.get('keyword', None)
    cityid = request.args.get('cityid', None)
    ptype = int(request.args.get('type', None))
    page = int(request.args.get('page', 0))
    q = db.query(Frag)
    if ptype == 5:
        q = q.filter(Frag.sup_id == userid)
    elif ptype:
        q = q.filter(Frag.type == ptype)
    if cityid:
        q = q.filter(Frag.cityid == cityid)
    if keyword:
        q = q.filter(Frag.name_cn.like('%{}%'.format(keyword)))
    res = []
    start = page * 40
    end = ((page + 1) * 40)
    for _q in q[start: end]:
        res.append(_q.serialize())
    res = json.dumps(res)
    return Response(res, mimetype='application/json')


@api_v1.route('/cityid', methods=['POST'])
def cityIdHandler():
    data = request.form.get('data', '[]')
    req = json.loads(data)
    res = []
    for re in req:
        city = db.query(City).filter_by(cityname_cn=re).one_or_none()
        if not city:
            abort(400, '没有这个城市')
        res.append(city.city_id)
    return Response(json.dumps(res), mimetype='application/json')


@api_v1.route('/country', methods=['GET'])
def countryHandler():
    countrys = db.query(Country)
    res = []
    for country in countrys:
        res.append({'name_cn': country.countryname_cn,
                    'name_en': country.countryname_en,
                    'id': country.countryid})
    return Response(json.dumps(res), mimetype='application/json')


@api_v1.route('/city', methods=['GET', 'POST'])
def cityHandler():
    if request.method == 'GET':
        countryid = request.args.get('countryid', None)
        like = request.args.get('like', None)
        if not (countryid or like):
            abort(400, '没有传参')
        query = db.query(City)
        if countryid:
            query = query.filter(City.countryid == countryid)
        if like:
            query = query.filter(or_(
                City.cityname_cn.like('%'+like+'%'),
                City.cityname_en.like('%'+like+'%')))
        res = []
        for city in query:
            res.append({'name_cn': city.cityname_cn,
                        'name_en': city.cityname_en,
                        'countryid': city.countryid,
                        'id': city.cityid})
        return Response(json.dumps(res), mimetype='application/json')
    if request.method == 'POST':
        req = json.loads(request.form.get('data', '[]'))
        if not req:
            req = request.get_json()
        res = []
        for r in req:
            city = db.query(City).filter(City.cityid == r).one_or_none()
            res.append({'name_cn': city.cityname_cn,
                        'name_en': city.cityname_en,
                        'countryid': city.countryid,
                        'id': city.cityid})
        return Response(json.dumps(res), mimetype='application/json')
