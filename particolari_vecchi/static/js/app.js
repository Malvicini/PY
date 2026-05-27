const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-input');
const fileList = document.getElementById('file-list');
const resultsCount = document.getElementById('results-count');
const statusMessage = document.getElementById('status-message');
const clearButton = document.getElementById('clear-button');

searchForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  await performSearch();
});

clearButton.addEventListener('click', () => {
  searchInput.value = '';
  fileList.innerHTML = '';
  resultsCount.textContent = 'Nessuna ricerca ancora eseguita';
  statusMessage.textContent = '';
});

async function performSearch() {
  const code = searchInput.value.trim();
  if (!code) {
    resultsCount.textContent = 'Inserisci un codice per avviare la ricerca.';
    fileList.innerHTML = '';
    statusMessage.textContent = '';
    return;
  }

  resultsCount.textContent = 'Sto cercando...';
  statusMessage.textContent = '';
  fileList.innerHTML = '';

  try {
    const response = await fetch(`/api/search?code=${encodeURIComponent(code)}`);
    const data = await response.json();
    if (!response.ok) {
      resultsCount.textContent = 'Errore nella ricerca';
      statusMessage.textContent = data.error || 'Si è verificato un errore durante la ricerca.';
      return;
    }

    if (!data.files || data.files.length === 0) {
      resultsCount.textContent = `Nessun file trovato per: ${code}`;
      fileList.innerHTML = `<div class="no-results">Non sono stati trovati file corrispondenti. Verifica il codice e riprova.</div>`;
      return;
    }

    resultsCount.textContent = `${data.count} file trovati per: ${code}`;
    fileList.innerHTML = data.files.map(createFileCard).join('');
  } catch (error) {
    resultsCount.textContent = 'Errore di rete';
    statusMessage.textContent = error.message || 'Impossibile contattare il server.';
  }
}

function createFileCard(file) {
  return `
    <article class="file-card">
      <div>
        <h2>${escapeHtml(file.name)}</h2>
        <p>${escapeHtml(file.folder || 'Radice archivio')}</p>
      </div>
      <div class="file-meta">
        <span class="meta-pill">Dimensione: ${file.size_label}</span>
        <a class="download-button" href="${encodeURI(file.download_url)}" target="_blank" rel="noreferrer noopener">Scarica</a>
      </div>
    </article>
  `;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

window.addEventListener('DOMContentLoaded', () => {
  searchInput.focus();
});
