document.addEventListener("DOMContentLoaded", () => {
  let pdfHeight;
  let pdfDoc = null;
  let pageNum = 1; // Current page number
  let scale = 1; // Default scale
  let scale_two; // Adjusted scale based on canvas size
  let canvas = document.getElementById("pdfCanvas");
  let ctx = canvas.getContext("2d");

  let overlayCanvas = document.getElementById("overlayCanvas");
  let overlayCtx = overlayCanvas.getContext("2d");
  let fileInput = document.getElementById("file-input");
  let fileName = document.getElementById("filename");
  let startX, startY, endX, endY;
  let isDragging = false;
  let filename; // Variable to hold the filename

  let renderTask;

  // Function to render a PDF page
  function renderPage(num) {
    if (renderTask) {
      // Cancel the ongoing render task
      renderTask.cancel();
    }

    pdfDoc.getPage(num).then(function (page) {
      let viewport = page.getViewport({ scale });

      // Fixed dimensions for canvas
      const fixedCanvasWidth = 600;
      const fixedCanvasHeight = window.innerHeight;

      // Calculate scaling factor to fit canvas
      const scaleX = fixedCanvasWidth / viewport.width;
      const scaleY = fixedCanvasHeight / viewport.height;
      const scaleToFit = Math.min(scaleX, scaleY);

      viewport = page.getViewport({ scale: scaleToFit });
      scale_two = scaleToFit;

      canvas.width = fixedCanvasWidth;
      canvas.height = fixedCanvasHeight;
      overlayCanvas.width = fixedCanvasWidth;
      overlayCanvas.height = fixedCanvasHeight;

      canvas.style.display = "block";
      overlayCanvas.style.display = "block";

      pdfHeight = viewport.height;

      let renderContext = {
        canvasContext: ctx,
        viewport: viewport,
      };

      renderTask = page.render(renderContext);
      renderTask.promise.catch((err) => {
        console.error("Render task failed: ", err);
      });
    });
  }

  // Function to draw a rectangle on the overlay canvas
  function drawRectangle() {
    overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

    // Adjust coordinates based on dynamic scaling factor
    let scaledStartX = startX * scale_two;
    let scaledStartY = startY * scale_two;
    let scaledEndX = endX * scale_two;
    let scaledEndY = endY * scale_two;

    overlayCtx.beginPath();
    overlayCtx.rect(
      scaledStartX,
      scaledStartY,
      scaledEndX - scaledStartX,
      scaledEndY - scaledStartY
    );
    overlayCtx.strokeStyle = "blue";
    overlayCtx.stroke();
  }

  // Mouse event listeners for rectangle drawing
  overlayCanvas.addEventListener("mousedown", (e) => {
    startX = e.offsetX / scale_two; // Adjust based on scale
    startY = e.offsetY / scale_two;
    isDragging = true;
  });

  overlayCanvas.addEventListener("mousemove", (e) => {
    if (isDragging) {
      endX = e.offsetX / scale_two; // Adjust based on scale
      endY = e.offsetY / scale_two;
      drawRectangle();
    }
  });

  overlayCanvas.addEventListener("mouseup", (e) => {
    if (!isDragging) return;

    isDragging = false;

    let scaledStartX = startX;
    let scaledStartY = startY;
    let scaledEndX = endX;
    let scaledEndY = endY;
    let width = scaledEndX - scaledStartX;
    let height = scaledEndY - scaledStartY;

    fetch("/save_contract", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        startX: scaledStartX,
        startY: scaledStartY,
        width: width,
        height: height,
        filename: filename,
        page_num: pageNum,
        pdfHeight: pdfHeight / scale_two,
      }),
    })
      .then((response) => response.json())
      .then(() => {
        document.getElementById("status").textContent = "Kaydedildi!";
      })
      .catch((error) => console.error("Error:", error));
  });

  // File input change event
  fileInput.addEventListener("change", (e) => {
    if (pdfDoc) {
      pdfDoc.destroy();
      pdfDoc = null;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

    let file = e.target.files[0];
    if (file.type !== "application/pdf") {
      alert("Please select a PDF file.");
      return;
    }

    filename = file.name;
    let fileReader = new FileReader();

    fileReader.onload = function () {
      let typedarray = new Uint8Array(this.result);
      loadPDF(typedarray);
    };

    fileReader.readAsArrayBuffer(file);
  });

  // Function to load the PDF with retry mechanism
  function loadPDF(typedarray, retries = 3) {
    pdfjsLib
      .getDocument(typedarray)
      .promise.then(function (pdfDoc_) {
        pdfDoc = pdfDoc_;
        pageNum = 1;
        renderPage(pageNum);
      })
      .catch((err) => {
        if (retries > 0) {
          console.warn(`Retrying PDF load, attempts left: ${retries}`);
          setTimeout(() => loadPDF(typedarray, retries - 1), 1000);
        } else {
          console.error("Failed to load PDF document: ", err);
        }
      });
  }

  // Update page info display
  function updatePageInfo() {
    document.getElementById(
      "pageInfo"
    ).textContent = `Page ${pageNum} of ${pdfDoc.numPages}`;
  }

  // Navigation controls
  document.getElementById("prevPage").addEventListener("click", () => {
    if (pageNum > 1) {
      pageNum--;
      renderPage(pageNum);
      updatePageInfo();
    }
  });

  document.getElementById("nextPage").addEventListener("click", () => {
    if (pageNum < pdfDoc.numPages) {
      pageNum++;
      renderPage(pageNum);
      updatePageInfo();
    }
  });

  // Set worker source
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.worker.min.js";
});