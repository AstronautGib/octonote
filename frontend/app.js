(() => {
  const API_BASE = 'http://localhost:8000';

  const recordBtn = document.getElementById('recordBtn');
  const recordLabel = document.getElementById('recordLabel');
  const fileInput = document.getElementById('fileInput');
  const fileNameEl = document.getElementById('fileName');
  const processBtn = document.getElementById('processBtn');
  const statusMsg = document.getElementById('statusMsg');
  const waveform = document.getElementById('waveform');
  const transcriptBox = document.getElementById('transcriptBox');
  const saveBtn = document.getElementById('saveBtn');
  const copyJsonBtn = document.getElementById('copyJsonBtn');
  const savedList = document.getElementById('savedList');
  const refreshSavedBtn = document.getElementById('refreshSavedBtn');

  const fields = {
    patient_label: document.getElementById('f_patient_label'),
    shift: document.getElementById('f_shift'),
    bp: document.getElementById('v_bp'),
    hr: document.getElementById('v_hr'),
    temp: document.getElementById('v_temp'),
    rr: document.getElementById('v_rr'),
    spo2: document.getElementById('v_spo2'),
    pain: document.getElementById('v_pain'),
    subjective: document.getElementById('f_subjective'),
    objective: document.getElementById('f_objective'),
    actions: document.getElementById('f_actions'),
    medications: document.getElementById('f_medications'),
    assessment: document.getElementById('f_assessment'),
    plan: document.getElementById('f_plan'),
    flags: document.getElementById('f_flags'),
  };

  let mediaRecorder = null;
  let recordedChunks = [];
  let audioBlob = null;
  let audioFilename = null;

  function setStatus(text) {
    statusMsg.textContent = text || '';
  }

  function enableProcessing(filename) {
    audioFilename = filename;
    fileNameEl.textContent = filename;
    processBtn.disabled = false;
  }

  // --- Recording ---

  recordBtn.addEventListener('click', async () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recordedChunks = [];
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) recordedChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        audioBlob = new Blob(recordedChunks, { type: 'audio/webm' });
        stream.getTracks().forEach((track) => track.stop());
        recordBtn.classList.remove('recording');
        recordLabel.textContent = 'Start recording';
        waveform.classList.remove('active');
        enableProcessing('recorded-audio.webm');
        setStatus('Recording captured — ready to transcribe.');
      };

      mediaRecorder.start();
      recordBtn.classList.add('recording');
      recordLabel.textContent = 'Stop recording';
      waveform.classList.add('active');
      setStatus('Recording...');
    } catch (err) {
      setStatus('Microphone access denied or unavailable.');
    }
  });

  // --- File upload ---

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      audioBlob = fileInput.files[0];
      enableProcessing(fileInput.files[0].name);
      setStatus('File ready — click "Transcribe & structure".');
    }
  });

  // --- Process ---

  processBtn.addEventListener('click', async () => {
    if (!audioBlob) return;

    processBtn.disabled = true;
    setStatus('Transcribing locally, then asking Claude to structure the note...');

    const formData = new FormData();
    formData.append('audio', audioBlob, audioFilename);

    try {
      const res = await fetch(`${API_BASE}/api/process`, { method: 'POST', body: formData });
      const data = await res.json();

      if (!res.ok) {
        setStatus(`Error: ${data.detail || 'something went wrong.'}`);
        processBtn.disabled = false;
        return;
      }

      transcriptBox.value = data.transcript || '';
      populateNote(data.note || {});
      setStatus('Done — review the chart entry on the right, then save it.');
    } catch (err) {
      setStatus('Request failed. Is the backend running (uvicorn backend.main:app)?');
    } finally {
      processBtn.disabled = false;
    }
  });

  function populateNote(note) {
    fields.patient_label.value = note.patient_label || '';
    fields.shift.value = note.shift || '';

    const vitals = note.vitals || {};
    fields.bp.value = vitals.blood_pressure || '';
    fields.hr.value = vitals.heart_rate || '';
    fields.temp.value = vitals.temperature || '';
    fields.rr.value = vitals.respiratory_rate || '';
    fields.spo2.value = vitals.oxygen_saturation || '';
    fields.pain.value = vitals.pain_level || '';

    fields.subjective.value = note.subjective || '';
    fields.objective.value = note.objective || '';
    fields.actions.value = (note.actions_taken || []).join('\n');
    fields.medications.value = (note.medications || [])
      .map((m) => [m.name || '', m.dose || '', m.time || ''].join(' | '))
      .join('\n');
    fields.assessment.value = note.assessment || '';
    fields.plan.value = note.plan || '';

    fields.flags.innerHTML = '';
    (note.flags || []).forEach((flag) => {
      const li = document.createElement('li');
      li.textContent = flag;
      fields.flags.appendChild(li);
    });
  }

  function currentNoteAsJson() {
    const flags = Array.from(fields.flags.children).map((li) => li.textContent);
    const actions_taken = fields.actions.value.split('\n').map((s) => s.trim()).filter(Boolean);
    const medications = fields.medications.value
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [name = '', dose = '', time = ''] = line.split('|').map((s) => s.trim());
        return { name, dose, time };
      });

    return {
      patient_label: fields.patient_label.value,
      shift: fields.shift.value,
      vitals: {
        blood_pressure: fields.bp.value,
        heart_rate: fields.hr.value,
        temperature: fields.temp.value,
        respiratory_rate: fields.rr.value,
        oxygen_saturation: fields.spo2.value,
        pain_level: fields.pain.value,
      },
      subjective: fields.subjective.value,
      objective: fields.objective.value,
      actions_taken,
      medications,
      assessment: fields.assessment.value,
      plan: fields.plan.value,
      flags,
    };
  }

  copyJsonBtn.addEventListener('click', async () => {
    await navigator.clipboard.writeText(JSON.stringify(currentNoteAsJson(), null, 2));
    setStatus('Note copied to clipboard as JSON.');
  });

  // --- Save / load saved entries ---

  saveBtn.addEventListener('click', async () => {
    setStatus('Saving...');
    try {
      const res = await fetch(`${API_BASE}/api/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcript: transcriptBox.value,
          note: currentNoteAsJson(),
        }),
      });
      if (!res.ok) throw new Error('save failed');
      setStatus('Entry saved.');
      loadSavedEntries();
    } catch (err) {
      setStatus('Could not save — is the backend running?');
    }
  });

  async function loadSavedEntries() {
    try {
      const res = await fetch(`${API_BASE}/api/notes`);
      const entries = await res.json();

      savedList.innerHTML = '';
      if (!entries.length) {
        savedList.innerHTML = '<li class="saved-empty">No saved entries yet.</li>';
        return;
      }

      entries.forEach((entry) => {
        const li = document.createElement('li');
        const label = entry.note.patient_label || 'Unlabeled entry';
        li.innerHTML = `${label} <span class="saved-time">— ${entry.created_at}</span>`;
        li.addEventListener('click', () => populateNote(entry.note));
        savedList.appendChild(li);
      });
    } catch (err) {
      savedList.innerHTML = '<li class="saved-empty">Could not load saved entries.</li>';
    }
  }

  refreshSavedBtn.addEventListener('click', loadSavedEntries);
  loadSavedEntries();
})();
