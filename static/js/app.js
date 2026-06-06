// Timer
let totalSeconds = {{ test.duration_minutes }} * 60;
const timerEl = document.getElementById("timer");
const interval = setInterval(() => {
    totalSeconds--;
    const m = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
    const s = String(totalSeconds % 60).padStart(2, "0");
    timerEl.textContent = `⏱ ${m}:${s}`;
    if (totalSeconds <= 60) timerEl.classList.add("warning");
    if (totalSeconds <= 0) {
        clearInterval(interval);
        document.getElementById("test-form").submit();
    }
}, 1000);

// Highlight selected
function markSelected(qPk, radio) {
    document.querySelectorAll(`[id^="label_${qPk}_"]`).forEach(l => l.classList.remove("selected"));
    radio.closest("label").classList.add("selected");
}