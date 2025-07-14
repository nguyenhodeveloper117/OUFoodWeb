from flask_login import logout_user, login_user
from app import app, login, dao, google, admin
from flask import render_template, redirect, flash, request, url_for, session
from datetime import  datetime
from models import Restaurant, CuisineType
from dao import add_user

@app.route("/")
def home():
    keyword = request.args.get('keyword', '')
    type_filter = request.args.get('type')
    location_filter = request.args.get('location')
    cuisine_type_id = request.args.get('cuisine_type')

    query = Restaurant.query

    if keyword:
        query = query.filter(Restaurant.name.ilike(f'%{keyword}%'))
    if type_filter:
        query = query.filter(Restaurant.type == type_filter)
    if location_filter:
        query = query.filter(Restaurant.location == location_filter)
    if cuisine_type_id:
        query = query.join(Restaurant.cuisine_types).filter(CuisineType.id == cuisine_type_id)

    restaurants = query.all()

    types = [r.type for r in Restaurant.query.with_entities(Restaurant.type).distinct()]
    locations = [r.location for r in Restaurant.query.with_entities(Restaurant.location).distinct()]
    cuisine_types = CuisineType.query.all()

    return render_template('index.html',
                           restaurants=restaurants,
                           types=types,
                           locations=locations,
                           cuisine_types=cuisine_types)


@app.route('/restaurant/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    r = Restaurant.query.get_or_404(restaurant_id)

    # Lấy các cuisine từ tất cả cuisine_type liên kết
    cuisines = []
    for ct in r.cuisine_types:
        cuisines.extend(ct.cuisines)

    keyword = request.args.get('keyword', '').strip().lower()
    food_type = request.args.get('food_type')
    beverage_type = request.args.get('beverage_type')

    food_cuisines = [
        c for c in cuisines
        if c.food_type and
           (not keyword or keyword in c.name.lower()) and
           (not food_type or c.food_type.name == food_type)
    ]

    beverage_cuisines = [
        c for c in cuisines
        if c.beverage_type and
           (not keyword or keyword in c.name.lower()) and
           (not beverage_type or c.beverage_type.name == beverage_type)
    ]

    return render_template('restaurant_cuisine.html',
                           restaurant=r,
                           food_cuisines=food_cuisines,
                           beverage_cuisines=beverage_cuisines,
                           keyword=keyword,
                           food_type=food_type,
                           beverage_type=beverage_type)


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = dao.auth_user(username=username, password=password)
        if u:
            login_user(u)
            return redirect('/')  # dieu huong ve trang chu
    return render_template('login.html')


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password)
    if u:
        login_user(u)
    else:
        flash("Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin đăng nhập.", "danger")
    return redirect('/admin')


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = None
    if request.method == 'POST':
        confirm = request.form.get('confirm')
        password = request.form.get('password')

        if password == confirm:
            data = {
                'name': request.form.get('name'),
                'username': request.form.get('username'),
                'password': password,
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address')
            }
            avatar = request.files.get('avatar')
            add_user(avatar=avatar, **data)
            return redirect('/login')
        else:
            err_msg = 'Mật khẩu KHÔNG khớp!'

    return render_template('register.html', err_msg=err_msg)


@app.route('/login/google')
def login():
    redirect_uri = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    session['user'] = user_info
    print(user_info)
    if dao.get_user_by_email(user_info['email']) is None:
        add_user(name=user_info['name'], username=user_info['email'], password="123456", email=user_info['email'], phone=datetime.now().strftime("%H%M%S"))

    u = dao.auth_user(username=user_info['email'], password="123456")
    if u:
        login_user(u)
        return redirect('/')
    return render_template("/register")


if __name__ == "__main__":
    app.run(debug=True, port=8000)
