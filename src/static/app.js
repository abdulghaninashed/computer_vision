const videoInput = document.querySelector("#video-file");
const startButton = document.querySelector("#start-button");
const pauseButton = document.querySelector("#pause-button");
const stopButton = document.querySelector("#stop-button");
const settingsButton = document.querySelector("#settings-button");
const settingsDialog = document.querySelector("#settings-dialog");
const reportButton = document.querySelector("#report-button");
const reportDialog = document.querySelector("#report-dialog");
const centerLineSlider = document.querySelector("#center-line");
const centerLineValue = document.querySelector("#center-line-value");
const videoFeed = document.querySelector("#video-feed");
const videoPlaceholder = document.querySelector("#video-placeholder");
const statusElement = document.querySelector("#status");
const statusText = document.querySelector("#status-text");
const progress = document.querySelector("#progress");
const toast = document.querySelector("#toast");

let selectedVideo = null;
let isRunning = false;
let isHandlingStop = false;
let toastTimeout;
let displayedError = null;

const statusLabels = {
    ready: "جاهز",
    processing: "جارٍ التحليل",
    stopping: "جارٍ الإيقاف",
    paused: "متوقف مؤقتًا",
    stopped: "تم الإيقاف",
    completed: "اكتمل التحليل",
    error: "حدث خطأ",
};

function showToast(message, isError = false) {
    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.classList.add("visible");
    window.clearTimeout(toastTimeout);
    toastTimeout = window.setTimeout(() => toast.classList.remove("visible"), 3500);
}

function renderState(state) {
    isRunning = state.running;
    statusElement.dataset.state = state.status;
    statusText.textContent = statusLabels[state.status] || state.status;
    startButton.disabled = isRunning || !selectedVideo;
    videoInput.disabled = isRunning;
    stopButton.disabled = !isRunning;
    pauseButton.disabled = !isRunning || !["processing", "paused"].includes(state.status);
    pauseButton.innerHTML = state.status === "paused"
        ? '<span aria-hidden="true">▶</span> استئناف'
        : '<span aria-hidden="true">Ⅱ</span> إيقاف مؤقت';
    settingsButton.disabled = isRunning;
    progress.textContent = state.error
        ? state.error
        : state.status === "processing"
            ? "تتم معالجة الفيديو وإرسال الإطارات مباشرة"
            : state.status === "paused"
                ? "التتبع متوقف مؤقتًا"
            : state.status === "completed"
                ? "اكتملت معالجة الفيديو"
                : state.status === "stopped"
                    ? "أُوقفت المعالجة"
                    : "النظام جاهز لاستقبال فيديو";

    document.querySelector("#total-count").textContent = state.stats.total;
    document.querySelector("#going-count").textContent = state.stats.going;
    document.querySelector("#returning-count").textContent = state.stats.returning;

    if (state.status === "error" && state.error && displayedError !== state.error) {
        displayedError = state.error;
        videoFeed.style.display = "none";
        videoPlaceholder.style.display = "flex";
        videoPlaceholder.querySelector("strong").textContent = "تعذرت معالجة الفيديو";
        showToast(state.error, true);
    }
}

async function refreshState() {
    if (isHandlingStop) return;
    try {
        const response = await fetch("/api/state");
        if (!response.ok) throw new Error("تعذر قراءة حالة المعالجة");
        renderState(await response.json());
    } catch (error) {
        progress.textContent = error.message;
    }
}

videoInput.addEventListener("change", () => {
    selectedVideo = videoInput.files[0] || null;
    document.querySelector("#video-name").textContent =
        selectedVideo ? selectedVideo.name : "لم يتم اختيار فيديو";
    startButton.disabled = !selectedVideo || isRunning;
    videoFeed.removeAttribute("src");
    videoFeed.style.display = "none";
    videoPlaceholder.style.display = "flex";
    videoPlaceholder.querySelector("strong").textContent = selectedVideo
        ? "الفيديو جاهز للتحليل"
        : "الفيديو سيظهر هنا";
    displayedError = null;
});

centerLineSlider.addEventListener("input", () => {
    centerLineValue.textContent = `${centerLineSlider.value}%`;
});

settingsButton.addEventListener("click", () => settingsDialog.showModal());

pauseButton.addEventListener("click", async () => {
    pauseButton.disabled = true;
    try {
        const response = await fetch("/api/pause", { method: "POST" });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "تعذر تغيير حالة التتبع");
        await refreshState();
    } catch (error) {
        showToast(error.message, true);
    } finally {
        await refreshState();
    }
});

function displayReport(report) {
    const labels = {
        car: "سيارة",
        van: "فان",
        truck: "شاحنة",
        bus: "باص",
    };
    const formatCurrency = (amount) => `$${Number(amount).toFixed(2)}`;
    const rows = report.rows.map((row) => {
        const tableRow = document.createElement("tr");
        [
            labels[row.vehicle] || row.vehicle,
            row.count,
            formatCurrency(row.unit_price),
            formatCurrency(row.subtotal),
        ].forEach((value) => {
            const cell = document.createElement("td");
            cell.textContent = value;
            tableRow.append(cell);
        });
        return tableRow;
    });

    document.querySelector("#report-rows").replaceChildren(...rows);
    document.querySelector("#report-total-count").textContent = report.total_count;
    document.querySelector("#report-total-revenue").textContent =
        formatCurrency(report.total_revenue);
    reportDialog.showModal();
}

reportButton.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/report");
        const report = await response.json();
        if (!response.ok) throw new Error(report.error || "تعذر تحميل التقرير");
        displayReport(report);
    } catch (error) {
        showToast(error.message, true);
    }
});

document.querySelector("#report-close").addEventListener("click", () => {
    reportDialog.close();
});

startButton.addEventListener("click", async () => {
    if (!selectedVideo) return;
    const form = new FormData();
    form.append("video", selectedVideo);
    form.append("center_line_percent", centerLineSlider.value);
    startButton.disabled = true;

    try {
        const response = await fetch("/api/start", { method: "POST", body: form });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "تعذر بدء المعالجة");
        videoPlaceholder.style.display = "none";
        videoFeed.style.display = "block";
        videoFeed.src = `/video_feed?started=${Date.now()}`;
        displayedError = null;
        await refreshState();
    } catch (error) {
        showToast(error.message, true);
        startButton.disabled = false;
    }
});

stopButton.addEventListener("click", async () => {
    isHandlingStop = true;
    stopButton.disabled = true;
    try {
        const response = await fetch("/api/stop", { method: "POST" });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "تعذر إيقاف المعالجة");
        displayReport(result.report);

        let state;
        do {
            await new Promise((resolve) => window.setTimeout(resolve, 150));
            const stateResponse = await fetch("/api/state");
            state = await stateResponse.json();
            if (!stateResponse.ok) {
                throw new Error(state.error || "تعذر التحقق من إيقاف التتبع");
            }
        } while (state.running);

        const resetResponse = await fetch("/api/reset", { method: "POST" });
        const resetResult = await resetResponse.json();
        if (!resetResponse.ok) {
            throw new Error(resetResult.error || "تعذر تصفير العدّادات");
        }
    } catch (error) {
        showToast(error.message, true);
    } finally {
        isHandlingStop = false;
        await refreshState();
    }
});

videoFeed.addEventListener("load", () => {
    videoPlaceholder.style.display = "none";
    videoFeed.style.display = "block";
});

window.setInterval(refreshState, 700);
refreshState();
