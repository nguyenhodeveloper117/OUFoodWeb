import hashlib

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum
from datetime import datetime
from app import db, app


# BASE MODEL
class BaseModel(db.Model):
    __abstract__ = True
    created_date = db.Column(db.DateTime, default=datetime.now)
    updated_date = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


# ENUMS
class Role(RoleEnum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    MANAGER = "MANAGER"


class OrderStatus(RoleEnum):
    NEWORDER = "NEWORDER"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"


class PaymentStatus(RoleEnum):
    UNPAID = "UNPAID"
    PAID = "PAID"


class FoodType(RoleEnum):
    APPETIZER = "APPETIZER"
    MAIN = "MAIN"
    DESERT = "DESERT"


class BeverageType(RoleEnum):
    SOFTDRINK = "SOFTDRINK"
    DRINKINGWATER = "DRINKINGWATER"
    COFFEE = "COFFEE"
    JUICE = "JUICE"


# MODELS
class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(10), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=True)
    avatar = db.Column(db.String(255), nullable=False, default='https://res.cloudinary.com/dnwyvuqej/image/upload/v1733499646/default_avatar_uv0h7z.jpg')
    role = db.Column(db.Enum(Role), default=Role.CUSTOMER)

    reviews = db.relationship('Review', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)


class Review(BaseModel):
    __tablename__ = 'review'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)


class Order(BaseModel):
    __tablename__ = 'order'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.NEWORDER)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_details = db.relationship('OrderDetail', backref='order', lazy=True)
    payment = db.relationship('Payment', backref='order', uselist=False)


class OrderDetail(BaseModel):
    __tablename__ = 'order_detail'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    note = db.Column(db.String(255))

    cuisine_id = db.Column(db.Integer, db.ForeignKey('cuisine.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)


class Payment(BaseModel):
    __tablename__ = 'payment'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, default=0)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.UNPAID)

    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)


class CuisineType(BaseModel):
    __tablename__ = 'cuisine_type'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisines = db.relationship('Cuisine', backref='cuisine_type', lazy=True)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Cuisine(BaseModel):
    __tablename__ = 'cuisine'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255))
    description = db.Column(db.String(255))
    status = db.Column(db.Boolean, default=True)
    count = db.Column(db.Integer, default=0)

    cuisine_type_id = db.Column(db.Integer, db.ForeignKey('cuisine_type.id'), nullable=False)
    food_type = db.Column(db.Enum(FoodType))
    beverage_type = db.Column(db.Enum(BeverageType))

    order_details = db.relationship('OrderDetail', backref='cuisine', lazy=True)


class Restaurant(BaseModel):
    __tablename__ = 'restaurant'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255))
    type = db.Column(db.String(100))
    name = db.Column(db.String(100))
    introduce = db.Column(db.String(255))
    image = db.Column(db.String(255))

    reviews = db.relationship('Review', backref='restaurant', lazy=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Tạo user admin
        admin = User(
            name='Admin',
            username='admin',
            password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
            email='admin@example.com',
            phone='0909000000',
            address='123 Admin St',
            avatar='https://res.cloudinary.com/dnwyvuqej/image/upload/v1733499646/default_avatar_uv0h7z.jpg',
            role=Role.ADMIN
        )
        db.session.add(admin)

        # Tạo restaurant
        res1 = Restaurant(name='Bún Bò Huế', type='Quán ăn', location='TP.HCM', introduce='Đặc sản Huế ngon', image='https://res.cloudinary.com/dnwyvuqej/image/upload/v1752339222/download_vlt9jj.jpg',)
        res2 = Restaurant(name='Cơm Tấm Ba Ghiền', type='Nhà hàng', location='Quận 3', introduce='Cơm tấm nổi tiếng', image='https://res.cloudinary.com/dnwyvuqej/image/upload/v1752339222/download_1_haf8dl.jpg')
        db.session.add_all([res1, res2])

        # Tạo cuisine type
        ct1 = CuisineType(name='Món chính')
        ct2 = CuisineType(name='Đồ uống')
        db.session.add_all([ct1, ct2])
        db.session.flush()  # để lấy id

        # Tạo cuisine
        c1 = Cuisine(
            name='Bún Bò',
            price=45000,
            image='https://example.com/bunbo.jpg',
            description='Đậm vị Huế',
            count=10,
            cuisine_type_id=ct1.id,
            food_type=FoodType.MAIN
        )
        c2 = Cuisine(
            name='Trà Đào',
            price=15000,
            image='https://example.com/tradao.jpg',
            description='Mát lạnh',
            count=20,
            cuisine_type_id=ct2.id,
            beverage_type=BeverageType.JUICE
        )
        db.session.add_all([c1, c2])
        db.session.flush()

        # Tạo review
        r1 = Review(content='Ngon tuyệt!', rate=5, user_id=admin.id, restaurant_id=res1.id)
        r2 = Review(content='Ổn, giá hợp lý', rate=4, user_id=admin.id, restaurant_id=res2.id)
        db.session.add_all([r1, r2])

        # Tạo đơn hàng + chi tiết
        order = Order(user_id=admin.id, created_date=datetime.now(), status=OrderStatus.PROCESSING)
        db.session.add(order)
        db.session.flush()

        detail1 = OrderDetail(order_id=order.id, cuisine_id=c1.id, quantity=2, note='Ít cay')
        detail2 = OrderDetail(order_id=order.id, cuisine_id=c2.id, quantity=1, note='Ít đá')
        db.session.add_all([detail1, detail2])

        # Tạo thanh toán
        payment = Payment(order_id=order.id, total=105000, status=PaymentStatus.PAID)
        db.session.add(payment)

        db.session.commit()
        print("Đã tạo dữ liệu mẫu thành công!")
