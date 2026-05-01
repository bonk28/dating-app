// Transitions fluides entre les pages
document.addEventListener('DOMContentLoaded', function() {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    document.body.style.transform = 'translateY(10px)';
    requestAnimationFrame(function() {
        document.body.style.opacity = '1';
        document.body.style.transform = 'translateY(0)';
    });
});

// Preloader
window.addEventListener('beforeunload', function() {
    document.body.style.opacity = '0';
    document.body.style.transform = 'translateY(-10px)';
});
