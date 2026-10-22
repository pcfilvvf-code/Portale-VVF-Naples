let isShiftActive = false;
let shiftInterval = null;
let shiftStartTime = null;

window.onload = function() {
  fetch('/api/turno/status')
    .then(res => res.json())
    .then(data => {
      if (data.active) {
        shiftStartTime = new Date(data.inizio);
        isShiftActive = true;
        updateShiftUI();
        startTimer();
      } else {
        isShiftActive = false;
        updateShiftUI();
      }
    })
    .catch(err => console.error("Errore:", err));
};

function toggleShift() {
  if (isShiftActive) {
    fetch('/api/turno/stop', { method: 'POST' })
      .then(res => res.json())
      .then(() => {
        isShiftActive = false;
        clearInterval(shiftInterval);
        updateShiftUI();
        window.location.reload(); 
      });
  } else {
    document.getElementById('screenshotModal').classList.add('show');
    document.getElementById('modalScreenshotInput').focus();
    document.getElementById('modalError').style.display = 'none';
  }
}

function closeModal() {
  document.getElementById('screenshotModal').classList.remove('show');
  document.getElementById('modalScreenshotInput').value = '';
  document.getElementById('modalError').style.display = 'none';
}

function submitShiftStart() {
  const forceSelect = document.getElementById('forceSelect');
  const screenshotInput = document.getElementById('modalScreenshotInput');
  const errorText = document.getElementById('modalError');
  const urlValue = screenshotInput.value.trim();

  // 1. Controllo se è vuoto
  if (!urlValue) {
    errorText.innerText = "Devi inserire un link per continuare!";
    errorText.style.display = 'block';
    return;
  }

  // 2. Controllo se è un link Discord o Gyazo
  const isDiscord = urlValue.startsWith('https://cdn.discordapp.com/') || urlValue.startsWith('https://media.discordapp.net/');
  const isGyazo = urlValue.startsWith('https://gyazo.com/') || urlValue.startsWith('https://i.gyazo.com/');

  if (!isDiscord && !isGyazo) {
    errorText.innerText = "Link non valido! Inserisci un link di Discord o Gyazo.";
    errorText.style.display = 'block';
    return;
  }

  // Se i controlli passano, procedi
  errorText.style.display = 'none';
  const formData = new FormData();
  if (forceSelect && forceSelect.value) formData.append('force_id', forceSelect.value);
  formData.append('screenshot_url', urlValue);

  fetch('/api/turno/start', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
      if (data.inizio) {
        shiftStartTime = new Date(data.inizio);
        isShiftActive = true;
        updateShiftUI();
        startTimer();
        closeModal();
        window.location.reload();
      }
    });
}

function updateShiftUI() {
  const btnMain = document.getElementById('shiftBtnMain');
  const btnMainText = document.getElementById('shiftBtnMainText');
  const statusMainText = document.getElementById('shiftStatusMainText');
  if (!btnMain || !btnMainText || !statusMainText) return;

  if (isShiftActive) {
    btnMain.className = 'btn-main-shift active';
    btnMainText.innerText = 'Termina Turno';
    statusMainText.innerText = 'ATTIVO';
    statusMainText.style.color = '#2e7d32';
  } else {
    btnMain.className = 'btn-main-shift inactive';
    btnMainText.innerText = 'Inizia Turno';
    statusMainText.innerText = 'NON ATTIVO';
    statusMainText.style.color = '#c62828';
    const elDurata = document.getElementById('turnoDurata');
    if (elDurata) elDurata.innerText = `Durata: 00h 00m 00s`;
  }
}

function startTimer() {
  updateTimeDisplay();
  shiftInterval = setInterval(updateTimeDisplay, 1000);
}

function updateTimeDisplay() {
  if (!shiftStartTime) return;
  const now = new Date();
  const totalSeconds = Math.floor((now - shiftStartTime) / 1000);
  const ore = Math.floor(totalSeconds / 3600);
  const minuti = Math.floor((totalSeconds % 3600) / 60);
  const secondi = totalSeconds % 60;
  const durataString = `${ore.toString().padStart(2, '0')}h ${minuti.toString().padStart(2, '0')}m ${secondi.toString().padStart(2, '0')}s`;
  const elDurata = document.getElementById('turnoDurata');
  if (elDurata) elDurata.innerText = `Durata: ${durataString}`;
}

function toggleUserDropdown(event) {
  event.stopPropagation();
  const dropdown = document.getElementById('userDropdown');
  if (dropdown) dropdown.classList.toggle('show');
}

window.onclick = function() {
  const dropdown = document.getElementById('userDropdown');
  if (dropdown && dropdown.classList.contains('show')) dropdown.classList.remove('show');
};