from flask import redirect, render_template, session,\
        request, abort, Blueprint, url_for
from sqlalchemy import or_
from app.models import Order, SupplierOrder, Itinerary,\
        Frag, City, User, db as alchemydb, Match
from app.base.common import isSession
import json

flask_app = Blueprint('views', __name__, url_prefix='')
db = alchemydb.session


# 订单管理
@flask_app.route('/', methods=['GET'])
def indexView():
    return redirect(url_for('views.orderView'))


# 订单管理
@flask_app.route('/order', methods=['GET'])
def orderView():
    if isSession():
        email = session.get('username')
        id = session.get('user_id')
        status = int(request.args.get('status', -1))
        query = db.query(SupplierOrder).\
            filter_by(supplier_id=id)
        if status != -1:
            query = query.filter_by(status=status)
        query = query.all()
        return render_template('order.html',
                               orders=query,
                               status=status,
                               username=email)
    return redirect(url_for('auth.login'))


# 订单详情
@flask_app.route('/order/<id>', methods=['GET', 'PUT'])
def orderInfoView(id):
    if isSession():
        if request.method == 'GET':
            email = session.get('username')
            user_id = session.get('user_id')
            query = db.query(Order).filter_by(id=id).one_or_none()
            if not query:
                abort(400, '订单不存在')
            isAuth = db.query(SupplierOrder).filter_by(order_id=id).\
                filter_by(supplier_id=user_id).one_or_none()
            if not isAuth:
                abort(400, '没有权限')
            action = request.args.get('action', None)
            if action == 'accept':
                isAuth.status = 1
                db.commit()
                return redirect(url_for('views.orderInfoView', id=id))
            elif action == 'refuse':
                isAuth.status = 5
                db.commit()
                return redirect('/order')
            if isAuth.status == 1:
                itinerary = db.query(Itinerary).filter_by(supplier_id=user_id)
            else:
                itinerary = []
            return render_template('order_info.html',
                                   username=email,
                                   status=isAuth.status,
                                   itinerary=itinerary,
                                   order=query)
        if request.method == 'PUT':
            user_id = session.get('user_id')
            it_id = request.form.get('it_id')
            query = db.query(SupplierOrder).\
                filter_by(order_id=id).\
                filter_by(supplier_id=user_id).one_or_none()
            query.it_id = it_id
            query.status = 2
            db.commit()
            order = db.query(Order).get(id)
            order.status = 2
            db.commit()
            return '{"success": "success"}'
    return redirect(url_for('auth.login'))


# 旅行路线
@flask_app.route('/itinerary')
def itinerary():
    if isSession():
        status = int(request.args.get('status', -1))
        user_id = session.get('user_id')
        email = session.get('username')
        query = db.query(Itinerary).filter_by(supplier_id=user_id)
        if status > -1 and status < 2:
            query = query.filter_by(status=status)
        query = query.all()
        return render_template('itinerary.html',
                               status=status,
                               username=email,
                               itary=query)
    return redirect(url_for('auth.login'))


# 旅行路线
@flask_app.route('/itinerary/create', methods=['GET', 'POST'])
def itineraryCreate():
    if isSession():
        userid = session.get('user_id')
        email = session.get('username')
        if request.method == 'GET':
            return render_template('chuangjianluxian.html', username=email)
        elif request.method == 'POST':
            data = request.form
            it = Itinerary(**data)
            it.supplier_id = userid
            db.add(it)
            db.commit()
            url = '/itinerary/create/' + str(it.id)
            return json.dumps({'url': url})
    return redirect(url_for('auth.login'))


@flask_app.route('/itinerary/create/<it_id>', methods=['GET', 'POST'])
def itineraryCreate2(it_id):
    if isSession():
        if request.method == 'GET':
            email = session.get('email')
            id = session.get('user_id')
            it = db.query(Itinerary).filter_by(id=it_id).one_or_none()
            qq = db.query(Match).filter_by(sup_id=id)
            countrys = []
            for q in qq:
                countrys.append(q.countryid)
            cityList = db.query(
                City.cityid, City.cityname_cn).filter(or_(
                    City.countryid == v for v in list(set(countrys)))
                ).all()
            user = db.query(User).get(id)
            return render_template('xingchengxinxi.html', it=it, email=email,
                                   cityList=cityList, user=user)
        elif request.method == 'POST':
            data = request.form.get('data')
            it = db.query(Itinerary).filter_by(id=it_id).one_or_none()
            strt = ''
            for x in json.loads(data):
                strt += str(x) + ':'
            it.pieces = strt[:-1]
            it.status = 1
            db.commit()
            return 'success'
    return redirect(url_for('auth.login'))


@flask_app.route('/itinerary/modify/<it_id>/<method>', methods=['GET', 'POST'])
def itineraryModify(it_id, method):
    if isSession():
        email = session.get('email')
        user_id = session.get('user_id')
        it = db.query(Itinerary).filter_by(id=it_id,
                                           supplier_id=user_id).one_or_none()
        if it is None:
            return redirect('/itinerary')
        if request.method == 'GET':
            if method == 'base':
                lights = json.loads(it.light)
                return render_template('modify_base.html', it=it, email=email,
                                       lights=lights)
            if method == 'it':
                da = {}
                days = it.pieces.split(':')
                da = []
                for day in days:
                    ps = day.split(',')
                    d_list = []
                    for p in ps:
                        q = db.query(Frag).filter_by(id=p).one_or_none()
                        if not q:
                            print(ps)
                            continue
                        d_list.append({
                            'id': p,
                            'type': ['xc1.png', 'xc2.png', 'xc3.png',
                                     'xc3.png', 'xc3.png', 'xc3.png'][q.type],
                            'name': q.name_cn
                        })
                    da.append(d_list)
                qq = db.query(Match).filter_by(sup_id=user_id)
                countrys = []
                for q in qq:
                    countrys.append(q.countryid)
                cityList = db.query(
                    City.cityid, City.cityname_cn).filter(or_(
                        City.countryid == v for v in list(set(countrys)))
                    ).all()
                user = db.query(User).get(user_id)
                return render_template('xingchengxinxi.html',
                                       da=json.dumps(da), cityList=cityList,
                                       it=it, email=email, user=user)
            if method == 'price':
                try:
                    price = json.loads(it.price)
                except:
                    price = []
                notice = it.notice
                return render_template('price.html', it=it, price=price,
                                       notice=notice)
        elif request.method == 'POST':
            if method == 'base':
                data = request.form
                for k in data:
                    setattr(it, k, data[k])
                db.commit()
                return '{"success": "success"}'
            if method == 'it':
                data = request.form.get('data')
                strt = ''
                for x in json.loads(data):
                    strt += str(x) + ':'
                it.pieces = strt[:-1]
                db.commit()
                return 'success'
            if method == 'price':
                price = request.form.get('price')
                notice = request.form.get('notice')
                it.price = price
                it.notice = notice
                db.commit()
    return redirect(url_for('auth.login'))


@flask_app.route('/itinerary/<it_id>', methods=['GET', 'DELETE'])
def itineraryInfo(it_id):
    if isSession():
        if request.method == 'GET':
            it = db.query(Itinerary).filter_by(id=it_id).one_or_none()
            if it.status == 0:
                return redirect('/itinerary/create/{}'.format(it_id))
            _days = it.pieces.split(':')
            days = []
            for day in _days:
                pieces = day.split(',')
                tmp = []
                for piece in pieces:
                    tmp.append(db.query(Frag).
                               filter_by(id=str(piece)).one_or_none())
                days.append(tmp)
        elif request.method == 'DELETE':
            user_id = session.get('user_id')
            it = db.query(Itinerary).filter_by(
                id=it_id, supplier_id=user_id).one_or_none()
            if it is None:
                abort(401, '没有权限')
            else:
                db.delete(it)
                db.commit()
                return json.dumps({"success": "success"})
        return render_template("yulan_biaozhun.html", it=it, pieces=days)
    return redirect(url_for('auth.login'))


@flask_app.route('/getmypiece')
def getfpiece():
    if isSession():
        id = session.get('user_id')
        query = db.query(Frag).filter_by(sup_id=id).all()
        plist = []
        clist = []
        for que in query:
            tmp = {}
            tmp['id'] = que.id
            tmp['cityid'] = que.cityid
            tmp['name_cn'] = que.city_name.cityname_cn
            tmp['price'] = float(que.price)
            tmp['description'] = que.description
            tmp['cover'] = que.cover
            plist.append(tmp)
            clist.append(tmp['name_cn'])
        data = [{'piecelist': plist, 'citylist': clist}]
    return json.dumps(data)
