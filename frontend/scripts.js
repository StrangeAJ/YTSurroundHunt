const API_BASE_URL = (window.API_BASE_URL || "").replace(/\/$/, "");

const YOUTUBE_LOGO =
    "https://www.youtube.com/s/desktop/6b8b1b0d/img/favicon_32x32.png";

function getProgressElements() {
    const bar = document.getElementById("progress-bar");
    return { bar, inner: bar.querySelector(".progress-bar-inner") };
}

function showProgressBar() {
    const { bar, inner } = getProgressElements();
    inner.style.width = "0";
    bar.style.display = "block";
    bar.classList.add("indeterminate");
    bar.setAttribute("aria-valuenow", "0");
}

function completeProgressBar() {
    const { bar, inner } = getProgressElements();
    bar.classList.remove("indeterminate");
    inner.style.width = "100%";
    bar.setAttribute("aria-valuenow", "100");
    setTimeout(hideProgressBar, 400);
}

function hideProgressBar() {
    const { bar, inner } = getProgressElements();
    bar.style.display = "none";
    bar.classList.remove("indeterminate");
    inner.style.width = "0";
    bar.setAttribute("aria-valuenow", "0");
}

function showMessage(text) {
    const list = document.getElementById("flashes");
    const item = document.createElement("li");
    item.textContent = text;
    list.replaceChildren(item);
}

function buildQualityTable(qualities) {
    const table = document.createElement("table");
    table.setAttribute("border", "1");

    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    ["Format ID", "Audio Bitrate"].forEach((label) => {
        const th = document.createElement("th");
        th.textContent = label;
        headRow.append(th);
    });
    thead.append(headRow);

    const tbody = document.createElement("tbody");
    qualities.forEach(([formatId, bitrate]) => {
        const row = document.createElement("tr");
        const idCell = document.createElement("td");
        idCell.textContent = formatId;
        const bitrateCell = document.createElement("td");
        bitrateCell.textContent = bitrate;
        row.append(idCell, bitrateCell);
        tbody.append(row);
    });

    table.append(thead, tbody);
    return table;
}

function renderResults(results) {
    const container = document.getElementById("results");
    container.replaceChildren();

    if (!results.length) {
        showMessage("No multi-channel audio results found.");
        return;
    }

    const heading = document.createElement("h2");
    heading.textContent = "Search Results";
    container.append(heading);

    results.forEach((result) => {
        const section = document.createElement("section");
        section.className = "result";

        const title = document.createElement("h3");
        const link = document.createElement("a");
        link.href = result.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";

        const logo = document.createElement("img");
        logo.src = YOUTUBE_LOGO;
        logo.alt = "YouTube";
        logo.className = "youtube-logo";
        link.append(logo);

        const titleText = document.createElement("span");
        titleText.textContent = ` ${result.title}`;
        title.append(link, titleText);

        const tableWrap = document.createElement("div");
        tableWrap.className = "table-wrap";
        tableWrap.append(buildQualityTable(result.audio_qualities));

        section.append(title, tableWrap);
        container.append(section);
    });
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

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("search-form");
    if (form) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            document.getElementById("flashes").replaceChildren();
            document.getElementById("results").replaceChildren();
            showProgressBar();

            try {
                const response = await fetch(`${API_BASE_URL}/search`, {
                    method: "POST",
                    body: new FormData(form),
                });
                const payload = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(payload.error || "Search failed.");
                }
                completeProgressBar();
                renderResults(payload.results || []);
            } catch (error) {
                hideProgressBar();
                showMessage(error.message);
            }
        });
    }

    hideProgressBar();
    const savedTheme = localStorage.getItem("theme");
    const theme = savedTheme || getSystemTheme();
    setTheme(theme);
    window.matchMedia("(prefers-color-scheme: dark)").addListener((event) => {
        if (!localStorage.getItem("theme")) {
            setTheme(event.matches ? "dark" : "light");
        }
    });
});
