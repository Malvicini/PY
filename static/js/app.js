document.addEventListener('DOMContentLoaded', function(){
  const famList = document.getElementById('family-list')
  const sidebar = document.getElementById('sidebar')
  const sidebarToggle = document.getElementById('sidebar-toggle')
  const main = document.getElementById('main')

  // Initialize modern sidebar manager
  const sidebarManager = new SidebarManager()

  // Handle window resize for PDF container updates
  window.addEventListener('resize', () => {
    const pdfContainer = document.getElementById('pdf-container')
    updateScrollState(pdfContainer)
  })

  function el(tag, cls, text){
    const e = document.createElement(tag)
    if(cls) e.className = cls
    if(text !== undefined) e.textContent = text
    return e
  }

  fetch('/api/families')
    .then(r => {
      if (!r.ok) {
        throw new Error('HTTP ' + r.status + ': ' + r.statusText);
      }
      return r.json();
    })
    .then(data => {
      window.allFamilies = data // store for filtering
      // Load all groups/machines data for search
      return Promise.all([
        fetch('/api/all_groups_machines').then(r => r.json()),
        fetch('/api/all_sequences').then(r => r.json()) // Load all sequences once
      ])
    })
    .then(([groupsData, sequencesData]) => {
      window.allGroupsMachines = groupsData
      window.allSequences = sequencesData || [] // Store sequences for filtering
      renderFamilies(window.allFamilies)
    })
    .catch(err => { famList.textContent = 'Errore caricamento dati'; console.error(err) })

  // Search functionality with debouncing
  const searchInput = document.getElementById('search-input')
  let searchTimeout
  searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout)
    const query = e.target.value.toLowerCase().trim()
    // Debounce: wait 300ms before filtering
    searchTimeout = setTimeout(() => {
      filterFamilies(query)
    }, 300)
  })

  function filterFamilies(query){
    if(!query){
      renderFamilies(window.allFamilies)
      return
    }
    
    const queryLower = query.toLowerCase()
    const exactMatches = []
    const partialMatches = []
    
    // Filter from already-loaded data (no API calls)
    window.allFamilies.forEach(fam => {
      // Get sequences for this family from cached allSequences
      const seqs = (window.allSequences || []).filter(s => 
        s.family_code && s.family_code.toLowerCase() === fam.family_code.toLowerCase()
      )
      
      // Check if family matches
      const familyMatches = matchesQuery(fam, query)
      
      // Add family_code to sequences for full_code matching
      seqs.forEach(seq => seq.family_code = fam.family_code)
      
      // Check sequences
      const matchingSeqs = seqs.filter(seq => matchesQuery(seq, query))
      
      // Check groups/machines for this family
      const familyGroupsMachines = window.allGroupsMachines.filter(gm => gm.cod.toLowerCase() === fam.family_code.toLowerCase())
      
      // Group by sequence
      const seqGroups = {}
      familyGroupsMachines.forEach(gm => {
        const seqId = gm.pro.toString().padStart(3, '0') // normalize to 3 digits
        if(!seqGroups[seqId]) seqGroups[seqId] = []
        seqGroups[seqId].push(gm)
      })
      
      // Check which sequences have matching details
      const sequencesWithDetails = []
      seqs.forEach(seq => {
        const seqGm = seqGroups[seq.sequence_id] || []
        const hasMatchingDetails = seqGm.some(gm => matchesQuery(gm, query))
        if(hasMatchingDetails){
          seq.groups_machines = seqGm
          sequencesWithDetails.push(seq)
        }
      })
      
      if(familyMatches || matchingSeqs.length > 0 || sequencesWithDetails.length > 0){
        // Combine matching sequences from both sources
        const allMatchingSeqs = [...matchingSeqs]
        sequencesWithDetails.forEach(seq => {
          if(!allMatchingSeqs.find(s => s.sequence_id === seq.sequence_id)){
            allMatchingSeqs.push(seq)
          }
        })
        
        if(allMatchingSeqs.length > 0){
          exactMatches.push({ ...fam, sequences: allMatchingSeqs, shouldExpand: true })
        } else {
          partialMatches.push({ ...fam, sequences: seqs, shouldExpand: false })
        }
      }
    })
    
    // Combine results: exact matches first, then partial
    const allResults = [...exactMatches, ...partialMatches]
    renderFamilies(allResults, query)
  }

  function matchesQuery(obj, query){
    const fields = ['family_code', 'family_name', 'sequence_id', 'description', 'articolo', 'desart', 'tipo']    // Also check full code for sequences
    if(obj.sequence_id && obj.family_code){
      fields.push('full_code') // We'll add this dynamically
      obj.full_code = obj.family_code + obj.sequence_id
    }    return fields.some(field => {
      const val = (obj[field] || '').toString().toLowerCase()
      return val.includes(query)
    })
  }

  function renderFamilies(families, query = ''){
    famList.innerHTML = ''
    // sort alphabetically by family_name (fallback to family_code)
    families.sort((a,b) => {
      const A = (a.family_name || a.family_code || '').toString().toLowerCase()
      const B = (b.family_name || b.family_code || '').toString().toLowerCase()
      return A.localeCompare(B)
    })
    families.forEach(f => {
        const item = el('div','family-item')
      const toggle = el('div','toggle','+')
      const name = el('div','name', (f.family_code || '') + (f.family_code && f.family_name ? ' — ' : '') + (f.family_name || ''))
      const seqContainer = el('div','sequences hidden')

      // attach data attrs for code and name
      item.dataset.familyCode = f.family_code || f.family_id || ''
      item.dataset.familyName = (f.family_name || f.family_code || '')

      toggle.addEventListener('click', () => {
        if(seqContainer.classList.contains('hidden')){
          // expand: load sequences
          toggle.textContent = '-' 
          loadSequences(item.dataset.familyCode, item.dataset.familyName, seqContainer, '', f.sequences)
          seqContainer.classList.remove('hidden')
        } else {
          // collapse
          toggle.textContent = '+'
          seqContainer.classList.add('hidden')
        }
      })

      // Auto-expand if there's a query and family has sequences or should expand
      if(query && (f.sequences && f.sequences.length > 0 || f.shouldExpand)){
        toggle.textContent = '-'
        loadSequences(item.dataset.familyCode, item.dataset.familyName, seqContainer, query, f.sequences)
        seqContainer.classList.remove('hidden')
      }

      item.appendChild(toggle)
      item.appendChild(name)
      item.appendChild(seqContainer)
      famList.appendChild(item)
    })
  }

  function loadSequences(family_code, family_name, container, query = '', preloadedSequences = null){
    if(preloadedSequences && preloadedSequences.length > 0){
      // Use preloaded sequences
      renderSequences(preloadedSequences, family_name, container, query, family_code)
      return
    }
    container.innerHTML = 'Caricamento...'
    fetch('/api/sequences?family_code=' + encodeURIComponent(family_code))
      .then(r => r.json())
      .then(data => {
        renderSequences(data, family_name, container, query, family_code)
      })
      .catch(err => { 
        container.textContent = 'Errore: ' + (err.message || 'Richiesta fallita'); 
        console.error('Errore caricamento sequenze per', family_code, err) 
      })
  }

  function renderSequences(data, family_name, container, query = '', family_code = ''){
    container.innerHTML = ''
    if(!data || data.length === 0){
      container.textContent = 'Nessuna sequenza trovata'
      return
    }
    // Filter sequences if query provided
    if(query){
      data = data.filter(seq => matchesQuery(seq, query))
    }
    data.forEach(s => {
      s.family_name = family_name
      // Show full code: family_code + sequence_id
      const fullCode = (family_code || '') + s.sequence_id
      const node = el('div','sequence', fullCode + ' — ' + (s.description || ''))
      node.addEventListener('click', () => {
        // Load groups and machines details
        if(s.groups_machines){
          // Use preloaded data
          renderGroupsMachines(s.groups_machines, s.sequence_id)
        } else {
          loadGroupsMachines(family_code, s.sequence_id)
        }
        
        const pdfContainer = document.getElementById('pdf-container')
        if(pdfContainer) pdfContainer.innerHTML = '<div id="pdf-placeholder">Caricamento anteprima...</div>'
        console.log('DEBUG JS: Requesting PDF for fullCode:', fullCode)
        fetch('/api/fetch_pdf_local', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ code: fullCode })
        }).then(r => {
          console.log('DEBUG JS: Fetch response status:', r.status)
          if(!r.ok) return r.json().then(j => Promise.reject(j))
          return r.blob()
        }).then(blob => {
          console.log('DEBUG JS: Blob received, size:', blob.size)
          const url = URL.createObjectURL(blob)
          const containerEl = document.getElementById('pdf-container')
          if(!containerEl){ console.error('pdf-container missing'); return }
          containerEl.innerHTML = ''
          const embed = document.createElement('embed')
          embed.src = url
          embed.type = 'application/pdf'
          embed.style.width = '100%'
          embed.style.height = '100%'
          containerEl.appendChild(embed)
          updateScrollState(containerEl)  // Recalculate scrollbar after PDF loads
          const blocker = document.getElementById('pdf-blocker')
          if(blocker) blocker.style.display = 'block'
          setTimeout(()=> URL.revokeObjectURL(url), 60000)
        }).catch(err => {
          console.error('DEBUG JS: PDF loading error:', err)
          const containerEl = document.getElementById('pdf-container')
          if(containerEl) {
            containerEl.innerHTML = '<div style="color:red">❌ PDF mancante per: '+fullCode+'</div>'
            updateScrollState(containerEl)
          }
        })
      })
      container.appendChild(node)
    })
  }

  function showStudyDetail(seq){
    const area = document.getElementById('study-detail')
    area.innerHTML = ''
    const t = el('div','title', seq.sequence_id + ' — ' + (seq.description || ''))
    const meta = el('div','meta', 'Codice: ' + (seq.sequence_id || ''))
    const d = el('div','desc', seq.description || '')
  const btn = el('button','adi-btn','Apri PDF locale')
  btn.addEventListener('click', () => {
    // Usa seq.sequence_id che dovrebbe già contenere il codice completo (famiglia + numero)
    const fullSeqCode = seq.sequence_id || seq.code || ''
    console.log('DEBUG JS: Requesting PDF for fullSeqCode:', fullSeqCode)
    // request PDF from local drawings directory
    fetch('/api/fetch_pdf_local', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ code: fullSeqCode })
    }).then(r => {
      if(!r.ok) return r.json().then(j => Promise.reject(j))
      return r.blob()
    }).then(blob => {
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank')
      setTimeout(()=> URL.revokeObjectURL(url), 60000)
    }).catch(err => { console.error(err); alert('❌ PDF mancante: '+fullSeqCode) })
  })
  const ideBtn = el('div')
    area.appendChild(t)
    area.appendChild(meta)
  area.appendChild(d)
  area.appendChild(btn)
  }

  // credentials/modal and remote fetch flows removed

  // init-folders button removed from UI; use create_drawings_structure.py instead

  function loadGroupsMachines(family_code, sequence_id){
    // Use local data
    const data = window.allGroupsMachines.filter(gm => 
      gm.cod.toLowerCase() === family_code.toLowerCase() && 
      gm.pro.toString().padStart(3, '0') === sequence_id
    )
    renderGroupsMachines(data, sequence_id)
  }

  function renderGroupsMachines(data, sequence_id, container){
    // Clear previous content
    const groupCell = document.getElementById('toolbar-r2-c1')
    const machineCell = document.getElementById('toolbar-r2-c2')
    if(groupCell) groupCell.innerHTML = ''
    if(machineCell) machineCell.innerHTML = ''

    if(!data || data.length === 0){
      if(groupCell) groupCell.textContent = 'Nessun dettaglio'
      if(machineCell) machineCell.textContent = 'Nessun dettaglio'
      return
    }

    // Separate groups and machines
    const groups = data.filter(item => item.tipo.toLowerCase().includes('gruppo') || item.tipo.toLowerCase().includes('g'))
    const machines = data.filter(item => item.tipo.toLowerCase().includes('macchina') || item.tipo.toLowerCase().includes('m'))

    // Render groups in toolbar-r2-c1
    if(groups.length > 0 && groupCell){
      const groupList = groups.map(item => `${item.articolo || 'N/A'}: ${item.desart || 'Nessuna descrizione'}`).join('<br>')
      groupCell.innerHTML = groupList
    } else if(groupCell){
      groupCell.textContent = 'Nessun gruppo'
    }

    // Render machines in toolbar-r2-c2
    if(machines.length > 0 && machineCell){
      const machineList = machines.map(item => `${item.articolo || 'N/A'}: ${item.desart || 'Nessuna descrizione'}`).join('<br>')
      machineCell.innerHTML = machineList
    } else if(machineCell){
      machineCell.textContent = 'Nessuna macchina'
    }
  }

  // Force scroll state update and reflow
  function updateScrollState(container) {
    if (!container) return
    
    // Force reflow by toggling display
    container.style.display = 'none'
    container.offsetHeight  // read offsetHeight to trigger reflow
    container.style.display = ''
    
    // Clamp scrollTop to max available scroll
    if (container.scrollTop > container.scrollHeight - container.clientHeight) {
      container.scrollTop = Math.max(0, container.scrollHeight - container.clientHeight)
    }
  }
  
  // ResizeObserver to catch size changes
  function initScrollObserver() {
    const pdfContainer = document.getElementById('pdf-container')
    if (!pdfContainer) return
    
    const observer = new ResizeObserver(() => {
      updateScrollState(pdfContainer)
    })
    observer.observe(pdfContainer)
  }
  initScrollObserver()
  
})
