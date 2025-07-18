from flask_login import logout_user, login_user, current_user
from app import app, login, dao, google, admin, utils
from flask import render_template, redirect, flash, request, url_for, session, jsonify
from datetime import datetime
from models import Restaurant, CuisineType, Role
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
            if u.role == Role.MANAGER:
                return redirect("/manager/view/order")
            else:
                next = request.args.get('next')
                return redirect(next if next else '/')
        flash("Tên đăng nhập hoặc mật khẩu không chính xác", "danger")
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
        add_user(name=user_info['name'], username=user_info['email'], password="123456", email=user_info['email'],
                 phone=datetime.now().strftime("%H%M%S"))

    u = dao.auth_user(username=user_info['email'], password="123456")
    if u:
        login_user(u)
        return redirect('/')
    return render_template("/register")


@app.context_processor
def common_response():
    return {
        'cart_stats': {
            'total_quantity': utils.stats_cart_quantity(session.get('cart'))
        }
    }


@app.route('/cart')
def cart():
    context = common_response()
    context['cart_stats'].update({
        'total_amount': utils.stats_cart_amount(session.get('cart'))
    })
    return render_template('cart.html', **context)


@app.route("/api/carts", methods=['post'])
def add_to_cart():
    cart = session.get('cart')
    if not cart:
        cart = {}

    id = str(request.json.get('id'))
    name = request.json.get('name')
    price = request.json.get('price')
    image = request.json.get('image')
    count = request.json.get('count')

    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            "id": id,
            "name": name,
            "price": price,
            "image": image,
            "count": count,
            "quantity": 1
        }

    session['cart'] = cart
    return jsonify(utils.stats_cart_quantity(cart))


@app.route('/api/carts/<product_id>', methods=['put'])
def update_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        quantity = request.json.get('quantity')
        cart[product_id]['quantity'] = int(quantity)

        session['cart'] = cart

    return jsonify(utils.stats_cart(cart))


@app.route('/api/carts/<product_id>', methods=['delete'])
def delete_product_in_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        del cart[product_id]

        if cart:
            session['cart'] = cart
        else:
            session.pop('cart', None)

    return jsonify(utils.stats_cart(cart))

@app.route("/manager/view/order")
def view_order():
    orders = dao.get_order()
    return render_template("manager/order_accept.html", orders=orders)

@app.route("/manager/view/oder_detail/<order_id>")
def update_status_order(order_id):
    order_details = dao.get_order_detail(order_id)
    return render_template("manager/order_detail.html", order_details=order_details, count=len(order_details))

@app.route("/api/update/status/order", methods=['PATCH'])
def update_status_order_approve():
    order_id = request.json.get('order_id')
    status = request.json.get('status')
    result = dao.update_order(order_id, status)
    print(result)
    return jsonify({'result':result})

@app.route("/manager/cuisine/manager")
def view_cuisine_manager():
    cuisines = dao.get_cuisine(current_user.id)
    print(cuisines)
    return render_template("manager/cuisine_manager.html", cuisines=cuisines)
                           
@app.route("/api/manager/delete/cuisine", methods=['DELETE'])
def cuisine_delete():
    cuisine_id = request.json.get("cuisine_id")
    result = dao.delete_cuisine(cuisine_id)
    print(result)
    return jsonify({"result":result})

@app.route("/manager/add/cuisine/<restaurant_id>", methods=['POST', 'GET'])
def cuisine_add(restaurant_id):
    err_msg = None
    cuisines_type = dao.get_cuisine_type(restaurant_id)
    if request.method == "POST":
        cuisine_name = request.form.get("name")
        cuisine_description = request.form.get("description")
        cuisine_price = request.form.get("price")
        cuisine_type = request.form.get("cuisine_type")
        cuisine_avatar = request.files.get("cuisine_avatar")
        if cuisine_name is None or cuisine_description is None or cuisine_price is None or cuisine_type is None or cuisine_avatar is None:
            print("Hello")
            err_msg = "vui lòng điền đầy đủ thông tin món ăn"
            return render_template("manager/cuisine_add.html", cuisines_type=cuisines_type, err_msg=err_msg)
        dao.cuisine_add(cuisine_name, cuisine_price, cuisine_avatar, cuisine_description, cuisine_type)
        return redirect("/manager/cuisine/manager")
    return render_template("manager/cuisine_add.html", cuisines_type=cuisines_type, restaurant_id= restaurant_id)

@app.route("/api/update/quantity", methods=['PUT'])
def update_quantity_cuisine():
    cuisine_id = request.json.get('cuisine_id')
    quantity = request.json.get('quantity')
    quantity = int(quantity)
    result = dao.update_quantity(cuisine_id, quantity)
    return jsonify({'result':result})


@app.route("/manager/reputation/statistics")
def reputation_statistics():
    if current_user.is_authenticated:
        reviews = dao.get_review(current_user.id)
        print(reviews)
    return render_template("manager/reputation_statistics.html", reviews=reviews)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
