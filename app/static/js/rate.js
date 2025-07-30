const stars = document.querySelectorAll('.star-rating .star');
  const ratingInput = document.getElementById('ratingValue');

  stars.forEach(star => {
    star.addEventListener('mouseover', () => {
      resetStars();
      highlightStars(star.dataset.value);
    });

    star.addEventListener('mouseout', () => {
      resetStars();
      highlightStars(ratingInput.value); // giữ lại đánh giá đã chọn
    });

    star.addEventListener('click', () => {
      ratingInput.value = star.dataset.value;
    });
  });

  function highlightStars(rating) {
    stars.forEach(star => {
      if (star.dataset.value <= rating) {
        star.classList.add('hover');
      }
    });
  }

  function resetStars() {
    stars.forEach(star => star.classList.remove('hover', 'selected'));
  }

  let order_detail_id_click = null

  function getOrderId(order_detail_id){
       order_detail_id_click = order_detail_id
  }

  function confirm_rate(){
    if(ratingInput.value == 0){
        alert("Vui lòng đánh giá sao")
        return
    }
     fetch("/api/rate/restaurant", {
        method: "POST",
        body: JSON.stringify({
            'order_detail_id':order_detail_id_click,
            'content': document.getElementById("content").value,
            'star' : ratingInput.value
        }),
        headers:{
            'Content-Type':'application/json'
        }
    }).then(res => res.json().then(data =>{
        if(data.result == "true"){
            alert("Đánh giá thành công")
            document.getElementById(`button_rate_${order_detail_id_click}`).disabled  = true
            const modal = bootstrap.Modal.getInstance(document.getElementById('ratingModal'));
            modal.hide();
        }
    }))
  }
