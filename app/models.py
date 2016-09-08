from app.base.func import CSVToList
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import or_
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_sqlalchemy import SQLAlchemy
from config import config
import json

db = SQLAlchemy()
Base = db.Model
Column = db.Column
Integer = db.Integer
String = db.String
Date = db.Date
DateTime = db.DateTime
Boolean = db.Boolean
ForeignKey = db.ForeignKey
Float = db.Float

type_dict = ['不限', '景点', '酒店', '活动', '餐馆', '购物']
why_dict = ['圆满', '历险', '思考人生', '天伦之乐', '商务考察', '游学']
stay_dict = ['经济型', '普通型', '奢华型']
wk_status_dict = ['待补充', '匹配中', '待选择', '待发布', '下线中', '出行中',
                  '已完成']
sup_status_dict = ['待处理', '制作中', '待选择', '募集中', '出行中',
                   '已拒绝', '未中标', '已完成']
topic_dict = ['亲子旅行', '游学旅行', '企业考察', '度假旅行',
              '团队建设或奖励', '时尚之旅', '运动旅行', '美食之旅',
              '邮轮旅行', '火车之旅', '蜜月旅行', '文化之旅', '全球节日之旅',
              '粉丝之旅', '彩虹之旅', '医疗保健旅行', '财富投资之旅',
              '自然风光之旅', '著名酒店体验之旅', '自驾之旅', '海岛旅行',
              '公务机旅行', '同学聚会', '闺蜜之旅']
tran_dict = ['飞机', '火车', '大巴', '自驾']
airplane_dict = ['经济舱', '公务舱', '头等舱']
hotel_dict = ['国际连锁酒店', 'Airbnb(公寓/别墅', '精品酒店（当地特色', '度假村']
hotel_brand_dict = ['STARWOOD', 'MARRIOTT', 'HILTON', 'HYATT', 'IHG', 'ACCOR',
                    'FOUR SEASON']
food_dict = ['当地特色美食', '经济快餐', '米其林餐厅', '餐饮自理', '中餐', '其他']
visa_dict = ['已有签证', '自己办理', '协助办理']
budget_dict = ['5000-15000（经济型）', '15000-25000（品质型）',
               '25000-35000（高价型）', '35000以上（奢华型）']


class User(Base):
    __tablename__ = 'userinfo'

    id = Column(Integer, primary_key=True)
    email = Column(String(128), nullable=False)
    pwd = Column(String(64), nullable=False)
    phone = Column(String(32), nullable=False)
    licence = Column(String(128), nullable=False)
    company = Column(String(128), nullable=False)
    location = Column(String(128), default='')
    introduce = Column(String(1024), nullable=False)
    service = Column(String(512))
    active = Column(Integer, default=0)
    createtime = Column(DateTime, default=func.now())

    def __init__(self, id, email):
        self.id = id
        self.email = email

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'chgpwd': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        # db.session.add(self)

        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        # db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.name

    def serialize(self):
        r = {
            'id': self.id,
            'company': self.company,
            'introduce': self.introduce,
        }
        return r


class SupplierOrder(Base):
    __tablename__ = 'sup_and_order'
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('userinfo.id'))
    status = Column(Integer)
    order_id = Column(Integer, ForeignKey('wk_order.id'))
    it_id = Column(Integer, ForeignKey('itinerary.id'))

    order = relationship('Order', back_populates='supplier')
    it = relationship('Itinerary')

    def __init__(self, supplier_id, order_id):
        self.supplier_id = supplier_id
        self.order_id = order_id
        self.status = 0

    @property
    def status_cn(self):
        try:
            return sup_status_dict[self.status]
        except:
            return 'None'


class Order(Base):
    __tablename__ = 'wk_order'

    id = Column(Integer, primary_key=True)
    wk_id = Column(Integer, nullable=False)
    wk_name = Column(String(32), nullable=False)
    wk_port = Column(String(128), nullable=False)
    begin_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    people_num = Column(Integer, nullable=False)
    is_determined = Column(Boolean, nullable=False)
    city_id = Column(String(255))
    departure = Column(String(32))
    recity = Column(String(32))
    topic = Column(String(32))
    status = Column(Integer, default=0)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now())

    info = relationship('OrderInfo', uselist=False, back_populates='order')
    supplier = relationship('SupplierOrder', back_populates='order')

    @property
    def city_id_cn(self):
        citys = []
        cityname = ''
        countrys = json.loads(self.city_id)
        for country in countrys:
            for city in country['city']:
                citys.append(city)
        cityname = db.session.query(City.cityname_cn).filter(
            or_(City.cityid == i for i in citys))
        return cityname

    @property
    def status_cn(self):
        try:
            return wk_status_dict[self.status]
        except:
            return 'None'

    @property
    def topic_cn(self):
        try:
            li = []
            for x in CSVToList(self.topic):
                li.append(topic_dict[x])
            return li
        except:
            return []

    @property
    def days_num(self):
        return (self.end_date - self.begin_date).days

    def serialize(self, get_all=False):
        r = {
            'id': self.id,
            'wk_id': self.wk_id,
            'wk_name': self.wk_name,
            'wk_port': self.wk_port,
            'begin_date': str(self.begin_date),
            'end_date': str(self.end_date),
            'people_num': self.people_num,
            'is_determined': self.is_determined,
            'city_id': json.loads(self.city_id),
            'departure': self.departure,
            'recity': self.recity,
            'topic': CSVToList(self.topic),
            'status': self.status,
            'create_time': str(self.create_time),
            'update_time': str(self.update_time)
        }
        if get_all:
            s = self.info
            rr = {
                'favor_tran': s.favor_tran,
                'favor_airplane': s.favor_airplane,
                'favor_hotel': s.favor_hotel,
                'favor_hotel_brand': s.favor_hotel_brand,
                'favor_food': s.favor_food,
                'favor_visa': s.favor_visa,
                'favor_budget': s.favor_budget,
                'remark': s.remark
            }
            r.update(rr)
        return r

    def php_serialize(self):
        return {
            'origin': self.departure,
            'destinations': self.city_id_cn,
            'pdtnums': self.people_num
        }


class OrderInfo(Base):
    __tablename__ = 'order_info'

    id = Column(Integer, primary_key=True)
    favor_tran = Column(Integer)
    favor_airplane = Column(Integer)
    favor_hotel = Column(Integer)
    favor_hotel_brand = Column(Integer)
    favor_food = Column(Integer)
    favor_visa = Column(Integer)
    favor_budget = Column(Integer)
    favor_why = Column(Integer)
    favor_stay = Column(Integer)
    favor_budget = Column(Integer)
    is_shopping = Column(Integer)
    remark = Column(String(255))
    order_id = Column(Integer, ForeignKey('wk_order.id'), unique=True)

    order = relationship('Order', back_populates='info')

    @property
    def tran_cn(self):
        try:
            return tran_dict[self.favor_tran]
        except:
            return 'None'

    @property
    def airplane_cn(self):
        try:
            return airplane_dict[self.favor_airplane]
        except:
            return 'None'

    @property
    def hotel_cn(self):
        try:
            return hotel_dict[self.favor_hotel]
        except:
            return 'None'

    @property
    def hotel_brand_cn(self):
        try:
            return hotel_brand_dict[self.favor_hotel_brand]
        except:
            return 'None'

    @property
    def food_cn(self):
        try:
            return food_dict[self.favor_food]
        except:
            return 'None'

    @property
    def visa_cn(self):
        try:
            return visa_dict[self.favor_visa]
        except:
            return 'None'

    @property
    def budget_cn(self):
        try:
            return budget_dict[self.favor_budget]
        except:
            return 'None'

    @property
    def why_cn(self):
        try:
            return why_dict[self.favor_why]
        except:
            return 'None'

    @property
    def stay_cn(self):
        try:
            return stay_dict[self.favor_stay]
        except:
            return 'None'


class City(Base):
    __tablename__ = 'city_config'

    cityid = Column(Integer, primary_key=True)
    countryid = Column(Integer, nullable=False)
    cityname_cn = Column(String(255), nullable=False)
    cityname_en = Column(String(255), nullable=False)
    city_cover = Column(String(128), nullable=False)


class Country(Base):
    __tablename__ = 'country_config'

    countryid = Column(Integer, primary_key=True)
    continentid = Column(Integer, nullable=False)
    countryname_cn = Column(String(255), nullable=False)
    countryname_en = Column(String(255), nullable=False)
    country_cover = Column(String(128), nullable=False)


class Itinerary(Base):
    __tablename__ = 'itinerary'

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('userinfo.id'))
    title = Column(String(512), nullable=False)
    coverimg = Column(String(256), nullable=False)
    pieces = Column(String(1024))
    price = Column(String(1024))
    notice = Column(String(1024))
    light = Column(String(1024), nullable=False)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=False)
    status = Column(Integer, nullable=False, default=0)

    @property
    def status_cn(self):
        return ['编辑中', '已完成', '废弃'][self.status]

    def serialize(self):
        r = {
            'id': self.id,
            'sup_id': self.supplier_id,
            'title': self.title,
            'coverimg': config.host_url + self.coverimg,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'light': json.loads(self.light),
            'pieces': self.pieces,
            'notice': self.notice,
            'prices': self.price
        }
        for l in r['light']:
            l['light_img'] = config.host_url + l['light_img']
        return r

    def php_serialize(self):
        price = json.loads(self.price)
        return {
            'pdtprice': ['count'],
            'pdtcprice': price['chlid'],
            'pdtdprice': price['soloroom'],
            'itineraryid': self.id,
            'pdttitle': self.title,
            'img': config.host_url + self.coverimg,
            'goofftime': str(self.begin_date),
            'pdtday': (self.start_date - self.end_date).days,
            'token': config.php_token
        }


class Frag(Base):
    __tablename__ = 'frag'

    id = Column(Integer, primary_key=True)
    cityid = Column(ForeignKey('city_config.cityid'))
    sup_id = Column(Integer)
    name_cn = Column(String(255))
    name_en = Column(String(255))
    price = Column(Float)
    description = Column(String(255))
    period = Column(String(255))
    cover = Column(String(255))
    ticket = Column(String(255))
    tel = Column(String(255))
    url = Column(String(255))
    address = Column(String(255))
    lat = Column(Float, default=0)
    lng = Column(Float, default=0)
    type = Column(Integer)
    city_name = relationship('City', foreign_keys=[cityid])

    def serialize(self):
        r = {
            'id': self.id,
            'sup_id': self.sup_id,
            'name_cn': self.name_cn,
            'name_en': self.name_en,
            'price': str(self.price),
            'description': self.description,
            'type': self.type
        }

        if self.sup_id is None:
            r['cover'] = 'http://p.igenwo.com/static/' + self.cover
        else:
            r['cover'] = config.host_url + '/static/' + self.cover
        return r


class Match(Base):
    __tablename__ = 'match_table'

    id = Column(Integer, primary_key=True)
    sup_id = Column(ForeignKey('userinfo.id'))
    countryid = Column(ForeignKey('country_config.countryid'))
    topic = Column(Integer)

    def __init__(self, sup_id, countryid, topic):
        self.sup_id = sup_id
        self.countryid = countryid
        self.topic = topic
