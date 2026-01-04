// function loadLogs() {
//   fetch("/api/logs")
//     .then(res => res.json())
//     .then(logs => {
//       const tbody = document.querySelector("#emailTable tbody");
//       tbody.innerHTML = "";

//       logs.reverse().forEach(log => {
//         const row = document.createElement("tr");
//         row.innerHTML = `
//           <td>${log.from || "-"}</td>
//           <td>${log.subject || "-"}</td>
//           <td>${log.priority || "-"}</td>
//           <td>${log.status || "-"}</td>
//           <td>${log.time || "-"}</td>
//         `;
//         tbody.appendChild(row);
//       });
//     });
// }

// loadLogs();
// setInterval(loadLogs, 10000);

const socket = io();

let emails = [];
let lastCount = 0;
let audioUnlocked = false;

// Elements
const popup = document.getElementById("popup");
const audio = document.getElementById("alertSound");

// ----------------------------------
// 🔐 XSS SAFETY (VERY IMPORTANT)
// ----------------------------------
function esc(str) {
    return String(str || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

// CSS-safe status class
function statusClass(status) {
    if (!status) return "";
    return status.toLowerCase().replace(/\s+/g, "-");
}

// Unlock sound (browser policy)
document.body.addEventListener("click", () => {
    audioUnlocked = true;
});

// ----------------------------------
// UI HELPERS
// ----------------------------------
function showPopup() {
    popup.style.display = "block";
    setTimeout(() => popup.style.display = "none", 4000);
}

function playSound() {
    if (audioUnlocked) {
        audio.currentTime = 0;
        audio.play().catch(() => {});
    }
}

// ----------------------------------
// CHARTS
// ----------------------------------
function updateCharts() {
    const priorityCount = { HIGH: 0, MEDIUM: 0, LOW: 0 };
    const hourMap = {};

    emails.forEach(e => {
        if (e.priority) priorityCount[e.priority]++;
        if (e.time) {
            const hour = e.time.slice(0, 13); // YYYY-MM-DD HH
            hourMap[hour] = (hourMap[hour] || 0) + 1;
        }
    });

    priorityChart.data.datasets[0].data = [
        priorityCount.HIGH,
        priorityCount.MEDIUM,
        priorityCount.LOW
    ];
    priorityChart.update();

    timeChart.data.labels = Object.keys(hourMap);
    timeChart.data.datasets[0].data = Object.values(hourMap);
    timeChart.update();
}

// ----------------------------------
// UI UPDATE
// ----------------------------------
function updateUI() {
    document.getElementById("totalEmails").innerText = emails.length;
    document.getElementById("queuedCount").innerText =
        emails.filter(e => e.status === "Queued").length;
    document.getElementById("replyCount").innerText =
        emails.filter(e => e.status?.startsWith("Replied")).length;
    document.getElementById("lowPriority").innerText =
        emails.filter(e => e.priority === "LOW").length;

    const q = document.getElementById("searchBox").value.toLowerCase();
    const tbody = document.getElementById("emailTable");
    tbody.innerHTML = "";

    emails
        .filter(e =>
            (e.from || "").toLowerCase().includes(q) ||
            (e.subject || "").toLowerCase().includes(q)
        )
        .slice()
        .reverse()
        .forEach(e => {
            tbody.insertAdjacentHTML("beforeend", `
                <tr>
                    <td>${esc(e.from)}</td>
                    <td>${esc(e.subject)}</td>
                    <td>${esc(e.priority)}</td>
                    <td class="${statusClass(e.status)}">${esc(e.status)}</td>
                    <td>${esc(e.time)}</td>
                </tr>
            `);
        });

    updateCharts();
}

// ----------------------------------
// 🔥 REAL-TIME SOCKET UPDATE
// ----------------------------------
socket.on("dashboard_update", data => {
    if (!Array.isArray(data)) return;

    // 🔔 Detect NEW email(s)
    if (data.length > lastCount) {
        showPopup();
        playSound();
    }

    lastCount = data.length;
    emails = data;

    updateUI();
});

// ----------------------------------
// INITIAL LOAD (fallback safety)
// ----------------------------------
fetch("/api/data", { cache: "no-store" })
    .then(r => r.json())
    .then(data => {
        if (Array.isArray(data)) {
            emails = data;
            lastCount = data.length;
            updateUI();
        }
    })
    .catch(() => {});
