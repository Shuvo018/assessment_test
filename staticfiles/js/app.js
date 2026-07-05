// Timer
document.addEventListener("DOMContentLoaded", () => {
    const timerEl = document.getElementById("timer");
    const testForm = document.getElementById("test-form");

    if (!timerEl || !testForm) {
        return;
    }

    const durationMinutes = parseInt(timerEl.dataset.durationMinutes || "0", 10);
    let totalSeconds = durationMinutes * 60;

    if (totalSeconds <= 0) {
        return;
    }

    timerEl.textContent = `⏱ ${String(durationMinutes).padStart(2, "0")}:00`;

    const interval = window.setInterval(() => {
        totalSeconds--;
        const m = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
        const s = String(totalSeconds % 60).padStart(2, "0");
        timerEl.textContent = `⏱ ${m}:${s}`;

        if (totalSeconds <= 60) {
            timerEl.classList.add("warning");
        }

        if (totalSeconds <= 0) {
            window.clearInterval(interval);
            testForm.submit();
        }
    }, 1000);
});

// Highlight selected
function markSelected(qPk, radio) {
    document.querySelectorAll(`[id^="label_${qPk}_"]`).forEach(l => l.classList.remove("selected"));
    radio.closest("label").classList.add("selected");
}