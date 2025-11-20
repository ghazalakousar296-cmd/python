const form = document.getElementById("transcriber-form");
const spinner = document.getElementById("submit-spinner");
const statusArea = document.getElementById("status-area");
const transcriptionCard = document.getElementById("transcription-card");
const transcriptionText = document.getElementById("transcription-text");
const copyBtn = document.getElementById("copy-btn");

const setStatus = (message, type = "info") => {
  statusArea.classList.remove("d-none", "alert-info", "alert-success", "alert-danger");
  statusArea.classList.add(`alert-${type}`);
  statusArea.textContent = message;
};

const resetStatus = () => {
  statusArea.classList.add("d-none");
  statusArea.textContent = "";
};

const toggleLoading = (isLoading) => {
  spinner.classList.toggle("d-none", !isLoading);
  form.querySelector("button[type='submit']").disabled = isLoading;
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resetStatus();
  transcriptionCard.classList.add("d-none");

  const videoUrl = event.target.videoUrl.value.trim();
  if (!videoUrl) {
    setStatus("Please paste a valid YouTube URL.", "danger");
    return;
  }

  toggleLoading(true);
  setStatus("Downloading video and preparing audio…", "info");

  try {
    const response = await fetch("/transcribe", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ videoUrl }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Transcription failed.");
    }

    const text = payload.text || "(No text returned. Check raw response.)";
    transcriptionText.textContent = text.trim();
    transcriptionCard.classList.remove("d-none");
    setStatus("Transcription complete!", "success");
  } catch (error) {
    console.error(error);
    setStatus(error.message, "danger");
  } finally {
    toggleLoading(false);
  }
});

copyBtn.addEventListener("click", async () => {
  const text = transcriptionText.textContent.trim();
  if (!text) return;

  try {
    await navigator.clipboard.writeText(text);
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy Text"), 1500);
  } catch (error) {
    console.error("Clipboard copy failed", error);
  }
});

