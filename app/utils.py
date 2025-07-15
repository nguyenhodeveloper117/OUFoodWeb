def stats_cart_quantity(cart):
    total_quantity = 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']

    return total_quantity


def stats_cart_amount(cart):
    total_amount = 0

    if cart:
        for c in cart.values():
            total_amount += c['quantity'] * c['price']

    return total_amount


def stats_cart(cart):
    total_amount, total_quantity = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        "total_quantity": total_quantity,
        "total_amount": total_amount
    }
