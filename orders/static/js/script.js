document.addEventListener("DOMContentLoaded", function () {
    // Add a "scrolled" class to the navbar once the page is scrolled down.
    var navbar = document.querySelector(".navbar");
    if (!navbar) return;

    function onScroll() {
        navbar.classList.toggle("scrolled", window.scrollY > 50);
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
});
