document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('load-more-btn');
    if (!btn) return;

    btn.addEventListener('click', () => {
        const hiddenReviews = document.querySelectorAll('.review-item[style*="display: none"]');
        hiddenReviews.forEach(item => item.style.display = 'block');
        btn.style.display = 'none'; // Ẩn nút sau khi nhấn
    });
});