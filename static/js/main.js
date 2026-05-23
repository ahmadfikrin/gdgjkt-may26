/* -------------------------------------------------------------
   ANTI FITNAH INTERACTIVE JAVASCRIPT SYSTEM
   Handles all AJAX requests, dynamic DOM renders, and animations.
   ------------------------------------------------------------- */

document.addEventListener("DOMContentLoaded", () => {
    
    // --- Elements ---
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    
    // Text Tab elements
    const verifyTextBtn = document.getElementById("verify-text-btn");
    const claimTextInput = document.getElementById("claim-text");
    
    // URL Tab elements
    const verifyUrlBtn = document.getElementById("verify-url-btn");
    const claimUrlInput = document.getElementById("claim-url");
    
    // Image Tab elements
    const verifyImageBtn = document.getElementById("verify-image-btn");
    const claimImageInput = document.getElementById("claim-image");
    const imageDragArea = document.getElementById("image-drag-area");
    const imgPreviewBox = document.getElementById("img-preview-box");
    const imgPreview = document.getElementById("img-preview");
    const removeImgBtn = document.getElementById("remove-img-btn");
    const imageHintText = document.getElementById("image-hint-text");
    
    // Results Panel elements
    const resultInitial = document.getElementById("result-initial");
    const resultLoading = document.getElementById("result-loading");
    const resultOutput = document.getElementById("result-output");
    
    const verdictBanner = document.getElementById("verdict-banner");
    const verdictText = document.getElementById("verdict-text");
    const confidencePercentage = document.getElementById("confidence-percentage");
    const gaugeFillCircle = document.getElementById("gauge-fill-circle");
    
    const resultTitle = document.getElementById("result-title");
    const resultCategory = document.getElementById("result-category");
    const resultEngine = document.getElementById("result-engine");
    const resultExplanation = document.getElementById("result-explanation");
    const resultSourceUrl = document.getElementById("result-source-url");
    const resultSourceText = document.getElementById("result-source-text");
    
    const scrapedMetaBox = document.getElementById("scraped-meta-box");
    const scrapedTitle = document.getElementById("scraped-title");
    const scrapedSnippet = document.getElementById("scraped-snippet");
    
    const ocrMetaBox = document.getElementById("ocr-meta-box");
    const ocrExtractedText = document.getElementById("ocr-extracted-text");
    
    // KB Table Elements
    const kbTableBody = document.getElementById("kb-table-body");
    const syncKbBtn = document.getElementById("sync-kb-btn");
    const kbSyncTime = document.getElementById("kb-sync-time");
    const headerTotalCount = document.getElementById("header-total-count");

    let uploadedFile = null;

    // --- Inisialisasi Awal ---
    loadKbDatabase();

    // --- 1. Tab Switcher Logic ---
    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            const targetTab = button.getAttribute("data-tab");
            
            // Remove active states
            tabButtons.forEach(btn => btn.classList.remove("active"));
            tabContents.forEach(content => content.classList.remove("active"));
            
            // Set active states
            button.classList.add("active");
            document.getElementById(targetTab).classList.add("active");
        });
    });

    // --- 2. Image Upload & Drag-Drop Logic ---
    imageDragArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        imageDragArea.classList.add("drag-over");
    });

    imageDragArea.addEventListener("dragleave", () => {
        imageDragArea.classList.remove("drag-over");
    });

    imageDragArea.addEventListener("drop", (e) => {
        e.preventDefault();
        imageDragArea.classList.remove("drag-over");
        
        if (e.dataTransfer.files.length > 0) {
            handleImageSelection(e.dataTransfer.files[0]);
        }
    });

    claimImageInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleImageSelection(e.target.files[0]);
        }
    });

    function handleImageSelection(file) {
        if (!file.type.startsWith("image/")) {
            alert("Harap unggah file gambar yang valid (PNG/JPG/JPEG)");
            return;
        }
        uploadedFile = file;
        
        // Show Preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imgPreview.src = e.target.result;
            imgPreviewBox.style.display = "block";
            // Sembunyikan elemen info drag
            document.querySelector(".drag-content").style.display = "none";
        };
        reader.readAsDataURL(file);
    }

    removeImgBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();
        uploadedFile = null;
        claimImageInput.value = "";
        imgPreview.src = "#";
        imgPreviewBox.style.display = "none";
        document.querySelector(".drag-content").style.display = "block";
    });


    // --- 3. Verification Renders & Animations ---
    function showLoading(message) {
        document.getElementById("loading-message").innerText = message;
        resultInitial.style.display = "none";
        resultOutput.style.display = "none";
        resultLoading.style.display = "flex";
    }

    function hideLoading() {
        resultLoading.style.display = "none";
    }

    function renderVerificationResult(data) {
        hideLoading();
        resultOutput.style.display = "block";
        
        // Set Judul, Penjelasan, Mesin, Kategori
        resultTitle.innerText = data.title;
        resultExplanation.innerText = data.explanation;
        resultCategory.innerText = data.category;
        resultEngine.innerText = data.engine_used;
        
        // Set Source Link
        if (data.source) {
            resultSourceUrl.href = data.source;
            resultSourceText.innerText = `Buka Rujukan Resmi (${new URL(data.source).hostname})`;
            document.querySelector(".source-link-box").style.display = "flex";
        } else {
            document.querySelector(".source-link-box").style.display = "none";
        }

        // Set Banner Verdict (Hoax, Fakta, Warning)
        verdictBanner.className = "verdict-banner"; // reset class
        if (data.status.includes("HOAX")) {
            verdictBanner.classList.add("hoax");
            verdictText.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${data.status}`;
        } else if (data.status.includes("FAKTA")) {
            verdictBanner.classList.add("fact");
            verdictText.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${data.status}`;
        } else {
            verdictBanner.classList.add("warning");
            verdictText.innerHTML = `<i class="fa-solid fa-circle-info"></i> ${data.status}`;
        }

        // Animate circular gauge
        const percentage = data.confidence;
        confidencePercentage.innerText = `${percentage}%`;
        
        // Lingkaran keliling SVG adalah 2 * pi * 40 = 251.2
        const dashArray = 251.2;
        const dashOffset = dashArray - (percentage / 100) * dashArray;
        
        // Trigger transisi
        setTimeout(() => {
            gaugeFillCircle.style.strokeDashoffset = dashOffset;
            // Ubah warna gauge sesuai status kebenaran
            if (data.status.includes("HOAX")) {
                gaugeFillCircle.style.stroke = "var(--color-hoax)";
            } else if (data.status.includes("FAKTA")) {
                gaugeFillCircle.style.stroke = "var(--color-fact)";
            } else {
                gaugeFillCircle.style.stroke = "var(--color-warning)";
            }
        }, 100);

        // Render URL scraping metadata jika tersedia
        if (data.scraped_data) {
            scrapedMetaBox.style.display = "block";
            scrapedTitle.innerText = data.scraped_data.title;
            scrapedSnippet.innerText = data.scraped_data.snippet;
        } else {
            scrapedMetaBox.style.display = "none";
        }

        // Render OCR extracted text metadata jika tersedia
        if (data.extracted_text) {
            ocrMetaBox.style.display = "block";
            ocrExtractedText.innerText = data.extracted_text;
        } else {
            ocrMetaBox.style.display = "none";
        }
    }


    // --- 4. API Requests Handler ---

    // A. Verify Text
    verifyTextBtn.addEventListener("click", async () => {
        const text = claimTextInput.value.trim();
        if (!text) {
            alert("Harap masukkan klaim atau pertanyaan terlebih dahulu.");
            return;
        }

        showLoading("Sedang mencocokkan kata kunci klaim dengan database...");

        try {
            const response = await fetch("/api/verify/text", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text })
            });
            const data = await response.json();
            
            if (response.ok) {
                renderVerificationResult(data);
            } else {
                alert(`Gagal menganalisis kueri: ${data.detail}`);
                hideLoading();
            }
        } catch (error) {
            alert("Terjadi kesalahan koneksi ke server.");
            hideLoading();
        }
    });

    // B. Verify URL
    verifyUrlBtn.addEventListener("click", async () => {
        const url = claimUrlInput.value.trim();
        if (!url) {
            alert("Harap masukkan tautan / URL terlebih dahulu.");
            return;
        }

        showLoading("Menghubungi tautan & merayap meta deskripsi halaman...");

        try {
            const response = await fetch("/api/verify/url", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url })
            });
            const data = await response.json();
            
            if (response.ok) {
                renderVerificationResult(data);
            } else {
                alert(`Gagal mengekstrak tautan: ${data.error || data.detail}`);
                hideLoading();
            }
        } catch (error) {
            alert("Terjadi kesalahan koneksi ke server.");
            hideLoading();
        }
    });

    // C. Verify Image Upload (OCR)
    verifyImageBtn.addEventListener("click", async () => {
        if (!uploadedFile) {
            alert("Harap pilih atau letakkan file tangkapan layar terlebih dahulu.");
            return;
        }

        showLoading("Menjalankan pemindaian OCR untuk ekstraksi teks gambar...");

        const formData = new FormData();
        formData.append("file", uploadedFile);
        
        const hintText = imageHintText.value.trim();
        if (hintText) {
            formData.append("extracted_text_hint", hintText);
        }

        try {
            const response = await fetch("/api/verify/image", {
                method: "POST",
                body: formData
            });
            const data = await response.json();
            
            if (response.ok) {
                renderVerificationResult(data);
            } else {
                alert(`Gagal melakukan OCR gambar: ${data.error || data.detail}`);
                hideLoading();
            }
        } catch (error) {
            alert("Terjadi kesalahan koneksi ke server.");
            hideLoading();
        }
    });


    // --- 5. Database KB Actions & Sync ---

    // Fetch and Load KB Table List
    async function loadKbDatabase() {
        try {
            const response = await fetch("/api/kb/status");
            const data = await response.json();
            
            kbSyncTime.innerText = data.last_sync;
            headerTotalCount.innerText = data.total_count;
            
            // Populate Table
            kbTableBody.innerHTML = "";
            
            data.issues.forEach(issue => {
                const tr = document.createElement("tr");
                
                // Set badge class
                let statusClass = "warning";
                if (issue.status.includes("HOAX")) statusClass = "hoax";
                if (issue.status.includes("FAKTA")) statusClass = "fact";
                
                tr.innerHTML = `
                    <td><strong>#${issue.id}</strong></td>
                    <td><span class="badge badge-category">${issue.category}</span><br><strong>${issue.title}</strong></td>
                    <td class="text-secondary">${issue.claim}</td>
                    <td><span class="status-badge ${statusClass}">${issue.status}</span></td>
                    <td><span class="table-accuracy">${issue.confidence}%</span></td>
                    <td>
                        <a href="${issue.source}" target="_blank" class="table-source-link">
                            <i class="fa-solid fa-link"></i> Rujukan
                        </a>
                    </td>
                    <td>
                        <button class="table-action-btn" data-claim="${issue.claim}">
                            Uji Kueri
                        </button>
                    </td>
                `;
                kbTableBody.appendChild(tr);
            });

            // Bind click to test query button on table
            document.querySelectorAll(".table-action-btn").forEach(btn => {
                btn.addEventListener("click", () => {
                    const claim = btn.getAttribute("data-claim");
                    
                    // Switch tab to Text
                    document.querySelector("[data-tab='text-tab']").click();
                    claimTextInput.value = claim;
                    
                    // Scroll to workspace
                    document.querySelector(".input-panel").scrollIntoView({ behavior: "smooth" });
                    
                    // Trigger verify click
                    verifyTextBtn.click();
                });
            });

        } catch (error) {
            kbTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-4 text-hoax">
                        <i class="fa-solid fa-triangle-exclamation"></i> Gagal memuat data basis pengetahuan utama.
                    </td>
                </tr>
            `;
        }
    }

    // Sync KB with GitHub
    syncKbBtn.addEventListener("click", async () => {
        const icon = syncKbBtn.querySelector("i");
        icon.classList.add("spinning");
        syncKbBtn.disabled = true;
        
        try {
            const response = await fetch("/api/kb/sync", {
                method: "POST"
            });
            const data = await response.json();
            
            if (response.ok) {
                alert(data.message);
                loadKbDatabase(); // Reload table
            } else {
                alert(`Gagal sinkronisasi: ${data.message}`);
            }
        } catch (error) {
            alert("Gagal terhubung ke server untuk sinkronisasi.");
        } finally {
            icon.classList.remove("spinning");
            syncKbBtn.disabled = false;
        }
    });

});
