document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("page");

  // CSV Download
  const btn = document.getElementById("downloadCSV");
  if (btn) {
    btn.onclick = () => {
      fetch("/api/data")
        .then(r => r.json())
        .then(data => {
          let csv = "From,Subject,Priority,Status,Time\n";
          data.forEach(r => {
            csv += `"${r.from}","${r.subject}",${r.priority},${r.status},${r.time}\n`;
          });

          const blob = new Blob([csv], { type: "text/csv" });
          const a = document.createElement("a");
          a.href = URL.createObjectURL(blob);
          a.download = "email_logs.csv";
          a.click();
        });
    };
  }
});
