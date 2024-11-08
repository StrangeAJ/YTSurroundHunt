function showProgressBar() {
    document.getElementById("progress-bar").style.display = "block";
}

function hideProgressBar() {
    document.getElementById("progress-bar").style.display = "none";
}

function updateProgress(count) {
    const progressBar = document.querySelector('.progress-bar-inner');
    const percentage = (count / 10) * 100;
    progressBar.style.width = percentage + '%';
}

function getSystemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function setTheme(theme) {
    if (theme === "dark") {
        document.body.classList.add("dark-theme");
    } else {
        document.body.classList.remove("dark-theme");
    }
    localStorage.setItem("theme", theme);
}

function toggleTheme() {
    const currentTheme = localStorage.getItem("theme") || getSystemTheme();
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    setTheme(newTheme);
}

window.onload = function () {
    hideProgressBar();
    const savedTheme = localStorage.getItem("theme");
    const theme = savedTheme || getSystemTheme();
    setTheme(theme);
    window.matchMedia("(prefers-color-scheme: dark)").addListener((e) => {
        if (!localStorage.getItem("theme")) {
            setTheme(e.matches ? "dark" : "light");
        }
    });
};