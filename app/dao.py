import hashlib
import cloudinary.uploader
from app import app, db

from models import User, Order, Payment, OrderDetail, Cuisine


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))

    if role:
        u = u.filter(User.role.__eq__(role))

    return u.first()


def get_user_by_id(id):
    return User.query.get(id)


def add_user(name, username, password, email, phone, address=None, avatar=None):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()

    u = User(
        name=name,
        username=username,
        password=password,
        email=email,
        phone=phone,
        address=address
    )

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_order():
    return (db.session.query(
        Order.id,
        User.name,
        Order.created_date,
        Payment.total,
        Order.status
    ).join(
        User, Order.user_id == User.id
    ).join(
        Payment, Payment.order_id == Order.id
    ).order_by(Order.id))


def get_order_detail(order_id):
    return (
        db.session.query(
            Order.id,
            Order.created_date,
            Payment.created_date,
            OrderDetail.note,
            Cuisine.id,
            Cuisine.name,
            OrderDetail.quantity,
            Cuisine.price
        ).join(
            Payment, Payment.order_id == Order.id
        ).join(
            OrderDetail, OrderDetail.order_id == Order.id
        ).join(
            Cuisine, Cuisine.id == OrderDetail.cuisine_id
        ).filter(Order.id == order_id)
        .order_by(OrderDetail.id).all()
    )