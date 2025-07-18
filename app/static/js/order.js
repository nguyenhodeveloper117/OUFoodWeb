document.addEventListener("DOMContentLoaded", function () {

    //Xac nhan don hang
    const button_approve = document.getElementById("btn_approve")
    if(button_approve){
        button_approve.addEventListener("click", function(){
            const data = this.dataset.orderId
            fetch("/api/update/status/order", {
                method: 'PATCH',
                body: JSON.stringify({
                    'order_id' : data,
                    'status':"Processing"
                }),
                headers:{
                    "Content-Type":"application/json"
                }
            }).then(res => res.json().then(data =>{
                if(data.result == true){
                    alert("Cập nhật thành công")
                    window.location.href = "/manager/view/order"
                }
            }))
        })
    }

    //Xu ly xong don hang
    const button_processed = document.getElementById("btn_processed")
    if(button_processed){
        button_processed.addEventListener("click", function(){
            const data = this.dataset.orderId
            fetch("/api/update/status/order", {
                method: 'PATCH',
                body: JSON.stringify({
                    'order_id' : data,
                    'status': 'Processed'
                }),
                headers:{
                    "Content-Type":"application/json"
                }
            }).then(res => res.json().then(data =>{
                if(data.result == true){
                    alert("Cập nhật thành công")
                    window.location.href = "/manager/view/order"
                }
            }))
        })
    }

    //Xu ly quay lai
    const button_comeback = document.getElementById("btn_comeback")
    if(button_comeback){
        button_comeback.addEventListener("click", function(){
            window.location.href = "/manager/view/order"
        })
    }
})


function cuisineRemove(cuisine_id){
    if(confirm("Bạn có chắc là xóa món ăn này không?") === true){
        fetch("/api/manager/delete/cuisine", {
            method: "DELETE",
            body: JSON.stringify({
                'cuisine_id': cuisine_id
            }),
            headers:{
                "Content-Type": "application/json"
            }
        }).then(res => res.json().then(data => {
                if(data.result == true){
                    const row = document.getElementById(`row_${cuisine_id}`);
                    if(row){
                        row.remove()
                    }
                }
         }))
    }
}

let currentItemId = null; // Biến toàn cục lưu id đang chỉnh

function openQuantityModal(itemId) {
    currentItemId = itemId;
    const quantity_input = document.getElementById('quantityInput')
    quantity_input.value = document.getElementById(`cuisine_count_${itemId}`).textContent.trim()
    const modal = new bootstrap.Modal(document.getElementById('quantityModal'));
    modal.show();
}

function confirm(){
    const quantity_input = document.getElementById('quantityInput').value
    fetch("/api/update/quantity", {
        method: "PUT",
        body: JSON.stringify({
            'cuisine_id':currentItemId,
            'quantity': quantity_input
        }),
        headers:{
            'Content-Type':'application/json'
        }
    }).then(res => res.json().then(data => {
        if(data.result == true){
            document.getElementById(`cuisine_count_${currentItemId}`).textContent = quantity_input;
        }
    }))

    const modal = bootstrap.Modal.getInstance(document.getElementById('quantityModal'));
    modal.hide();

}