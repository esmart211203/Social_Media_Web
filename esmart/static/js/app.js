let settingsmenu = document.querySelector('.settings-menu');
let darkBtn = document.getElementById("dark-btn");

function SettingMenuToggle() {
    settingsmenu.classList.toggle("settings-menu-height");
}
darkBtn.onclick = function () {
    darkBtn.classList.toggle("dark-btn-on");
    document.body.classList.toggle("dark-theme");

    if (localStorage.getItem("thame") == "light") {
        localStorage.setItem("thame", "dark");
    } else {
        localStorage.setItem("thame", "light");
    }
}

if (localStorage.getItem("thame") == "light") {
    darkBtn.classList.remove("dark-btn-on");
    document.body.classList.remove("dark-thame");
} else if (localStorage.getItem("thame") == "dark") {
    darkBtn.classList.add("dark-btn-on");
    document.body.classList.add("dark-thame");
} else {
    localStorage.setItem("thame", "light");
}


// #search
document.getElementById("search-form").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {

        document.getElementById("search-form").submit();
    }
});
