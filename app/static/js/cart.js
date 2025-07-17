window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.quantity button').forEach(button => {
        button.addEventListener('click', function () {
            const input = button.parentElement.parentElement.querySelector('input');
            const productId = input.dataset.id
            const cartRow = document.getElementById(`cart${productId}`);
            const count = cartRow.querySelector('.cuisine-count')
            const oldValue = parseFloat(input.value);

            let newVal;
            if (button.classList.contains('btn-plus')) {
                if(oldValue < parseInt(count.innerText)){
                    newVal = oldValue + 1;
                } else {
                    newVal = oldValue
                }
            } else {
                if (oldValue > 1) {
                    newVal = oldValue - 1;
                } else {
                    newVal = 1;
                }
            }

            input.value = newVal;
            updateCart(productId, input);
        });
    });
});

function updateCartCounterUI(data) {
    let cartCounters = document.getElementsByClassName("cart-counter");
    for (let c of cartCounters)
        c.innerText = data
}

function updateCartAmountUI(data) {
    let cartAmounts = document.getElementsByClassName("cart-amount");
    for (let c of cartAmounts)
        c.innerText = data.toLocaleString()
}

function addToCart(id, name, price, image, count=100) {
    fetch("/api/carts", {
        method: "post",
        body: JSON.stringify({
            "id": id,
            "name": name,
            "price": price,
            "image": image,
            "count": count
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        updateCartCounterUI(data)
    })
}

function isInteger(value) {
  return Number.isInteger(Number(value));
}

function handleUpdateCart(productId, obj) {
     const cartRow = document.getElementById(`cart${productId}`);
     const count = cartRow.querySelector('.cuisine-count')

     if(isInteger(obj.value)){
         if(obj.value > parseInt(count.innerText)){
            obj.value = parseInt(count.innerText)
         } else if (obj.value <= 0){
            obj.value = 1
         }
     } else {
        obj.value = 1
     }

     updateCart(productId, obj)
}
function updateCart(productId, obj) {
    fetch(`/api/carts/${productId}`, {
        method: "put",
        body: JSON.stringify({
            'quantity': obj.value
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        updateCartCounterUI(data.total_quantity);
        updateCartAmountUI(data.total_amount);

        const cartRow = document.getElementById(`cart${productId}`)
        const price = cartRow.querySelector('.price')
        const totalPrice = cartRow.querySelector('.total-price')

        const total = parseFloat(price.innerText.replace(/[^\d]/g, '')) * parseInt(obj.value)
        totalPrice.innerText = total.toLocaleString()
    })
}

function deleteProductInCart(productId) {
    if (confirm("Bạn có chắc chắc xóa không?") === true) {
        fetch(`/api/carts/${productId}`, {
            method: "DELETE"
        }).then(res => res.json())
            .then(data => {
                updateCartCounterUI(data.total_quantity);
                updateCartAmountUI(data.total_amount);

                const cartRow = document.getElementById(`cart${productId}`);
                const noteRow = cartRow.nextElementSibling;

                cartRow.style.display = "none";
                if (noteRow) {
                    noteRow.style.display = "none";
                }

                if (data.total_quantity === 0) {
                    document.querySelector('.table-responsive').style.display = 'none';
                    document.querySelector('.order-info').style.display = 'none';

                    const emptyMsg = document.createElement('div');
                    emptyMsg.className = 'text-center my-5';
                    emptyMsg.innerHTML = '<span class="fs-3">Không có món ăn nào trong giỏ hàng</span>';
                    const container = document.querySelector('.cart-info');
                    container.appendChild(emptyMsg);
                }
            })
    }
}
