document.addEventListener("DOMContentLoaded", () => {
    document.querySelector(".btn.login")?.addEventListener("click", () => {
        window.location.href = "/login/";
    });

    document.querySelector(".btn.register")?.addEventListener("click", () => {
        window.location.href = "/register/";
    });
});