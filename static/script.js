const video = document.getElementById('video');
const openCameraBtn = document.getElementById('openCamera');
const captureBtn = document.getElementById('capture');
const result = document.getElementById('result');

let stream = null;

// Fungsi buka kamera
openCameraBtn.addEventListener('click', () => {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then((mediaStream) => {
      stream = mediaStream;
      video.srcObject = stream;
      video.style.display = 'block';
      captureBtn.style.display = 'inline';
      openCameraBtn.disabled = true; // Disable tombol buka kamera
    })
    .catch((err) => {
      console.error('Gagal membuka kamera:', err);
      alert('Gagal membuka kamera.');
    });
});

document.addEventListener('keydown', function(event) {
  if (event.key === 'c') {
    if (captureBtn.style.display !== 'none') {
      captureBtn.click();  // Simulasikan klik capture
    }
  }
document.addEventListener("DOMContentLoaded", function () {
  const manualForm = document.getElementById("manual-form");

  if (manualForm) {
    manualForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = new FormData(manualForm);

      fetch("/manual", {
        method: "POST",
        body: formData
      })
      .then(resp => resp.json())
      .then(data => {
        const p = data.pemancar;
        const s = data.status;
        const t = data.kelistrikan.tegangan;
        const a = data.kelistrikan.arus;
        const ups = data.kelistrikan.UPS;
        const genset = data.kelistrikan.Genset;

        document.getElementById("manual-result").innerHTML = `
        ✅ Laporan Disimpan<br>
        ID: ${data.id}<br>
        Petugas: ${data.petugas}<br>
        <strong>UPS</strong><br>
        RS=${ups.RS}, RN=${ups.RN}, ST=${ups.ST}, SN=${ups.SN}, TR=${ups.TR}, TN=${ups.TN}, Freq=${ups.freq}<br>
        <strong>Genset</strong><br>
        RS=${genset.RS}, RN=${genset.RN}, ST=${genset.ST}, SN=${genset.SN}, TR=${genset.TR}, TN=${genset.TN}, Freq=${genset.freq}<br>
        <a href="${data.laporan_url}" download>⬇ Unduh JSON</a>
        <a href="${data.pdf_url}" download>📄 Unduh PDF</a>
      `;

      })
      .catch(err => {
        alert("Gagal menyimpan laporan.");
        console.error(err);
      });
    });
  }
});


  

  if (event.key === 'q') {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
      video.style.display = 'none';
      captureBtn.style.display = 'none';
      openCameraBtn.disabled = false;
      result.textContent = 'Kamera dimatikan.';
    }
  }
});

captureBtn.addEventListener('click', () => {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0);

  canvas.toBlob((blob) => {
    const formData = new FormData();
    formData.append('image', blob, 'capture.png');

    fetch('/upload', {
      method: 'POST',
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
      result.innerHTML = `
        <strong>Forward Power:</strong> ${data.forward_power}<br>
        <strong>Reflected Power:</strong> ${data.reflected_power}
      `;
      
      // (Opsional) Matikan kamera setelah scan
      // if (stream) {
      //   stream.getTracks().forEach(track => track.stop());
      //   stream = null;
      //   video.style.display = 'none';
      //   captureBtn.style.display = 'none';
      //   openCameraBtn.disabled = false;
      // }
    })
    .catch(err => {
      result.textContent = 'Gagal mengirim gambar: ' + err;
    });
  }, 'image/png');
});
