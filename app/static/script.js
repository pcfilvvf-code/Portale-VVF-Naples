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
  const forceSelect = document.getElementById('forceSelect');
  
  if (isShiftActive) {
    // FERMA IL TURNO
    fetch('/api/turno/stop', { method: 'POST' })
      .then(res => res.json())
      .then(() => {
        isShiftActive = false;
        clearInterval(shiftInterval);
        updateShiftUI();
        // RICARICA LA PAGINA per aggiornare la tabella "Personale in Servizio"
        window.location.reload(); 
      });
  } else {
    // INIZIA IL TURNO
    const formData = new FormData();
    if (forceSelect && forceSelect.value) {
      formData.append('force_id', forceSelect.value);
    }
    
    fetch('/api/turno/start', { method: 'POST', body: formData })
      .then(res => res.json())
      .then(data => {
        if (data.inizio) {
          shiftStartTime = new Date(data.inizio);
          isShiftActive = true;
          updateShiftUI();
          startTimer();
          // RICARICA LA PAGINA per aggiornare la tabella "Personale in Servizio"
          window.location.reload();
        }
      });
  }
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
  shiftInterval = setInterval(updateTimeDisplay, 1000); // Aggiorna ogni secondo
}

function updateTimeDisplay() {
  if (!shiftStartTime) return;
  
  const now = new Date();
  const diffMs = now - shiftStartTime;
  
  const totalSeconds = Math.floor(diffMs / 1000);
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
  if (dropdown && dropdown.classList.contains('show')) {
    dropdown.classList.remove('show');
  }
};