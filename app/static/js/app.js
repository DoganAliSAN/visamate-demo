document.addEventListener("DOMContentLoaded", () => {
  let pdfHeight;
  let pdfDoc = null;
  let pageNum = 1; // Current page number
  let scale = 1; // Adjust the scale based on your needs
  let scale_two; // Adjust the scale based on your needs
  let canvas = document.getElementById("pdfCanvas");
  let ctx = canvas.getContext("2d");

  let overlayCanvas = document.getElementById("overlayCanvas");
  let overlayCtx = overlayCanvas.getContext("2d");
  let fileInput = document.getElementById("file-input");
  let fileName = document.getElementById('filename');
  let startX, startY, endX, endY;
  let isDragging = false;
  let filename; // Define filename variable outside of event listener


  // Function to render PDF page
  let renderTask;
  function renderPage(num) {
    if (renderTask) {
      // Cancel the ongoing render task
      renderTask.cancel();
    }
  
    pdfDoc.getPage(num).then(function (page) {
      let viewport = page.getViewport({scale});

      // Set fixed width and height for the canvas elements
      const fixedCanvasWidth = 600; // Set your desired fixed width
      const fixedCanvasHeight = window.innerHeight; // Set your desired fixed height
  
      // Calculate the scaling factor
      const scaleX = fixedCanvasWidth / viewport.width;
      const scaleY = fixedCanvasHeight / viewport.height;
      //
      const scaleToFit = Math.min(scaleX, scaleY) ;
      // Update the viewport with the scaled dimensions
      viewport = page.getViewport({scale: scaleToFit});

      // viewport.viewBox[2] = fixedCanvasWidth;
      // viewport.viewBox[3] = fixedCanvasHeight;
      scale_two = scaleToFit;
  
      // Update canvas dimensions
      canvas.width = fixedCanvasWidth;
      canvas.height = fixedCanvasHeight ;
  
      overlayCanvas.width = fixedCanvasWidth ;
      overlayCanvas.height = fixedCanvasHeight ;
  
      canvas.style.display = "block";
      overlayCanvas.style.display = "block";
      // Assign pdfHeight
      pdfHeight = viewport.height;
  
      let renderContext = {
        canvasContext: ctx,
        viewport: viewport,
      };
  
      // Start a new render task
      renderTask = page.render(renderContext);
      renderTask.promise.then(
        function () {
          if (isDragging) {
            drawRectangle(); // Use the overlayCtx to draw the rectangle
          }
        },
        function (err) {
          console.error("Render task cancelled or failed: ", err);
        }
      );
    });
  }
  
  // Function to draw a rectangle based on the user's selection
  function drawRectangle() {
    // Clear previous rectangle
    overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

    // Adjust coordinates based on scaling factor
    let scaledStartX = startX / scale;
    let scaledStartY = startY / scale;
    let scaledEndX = endX / scale;
    let scaledEndY = endY / scale;

    // Draw a new rectangle
    overlayCtx.beginPath();
    overlayCtx.rect(scaledStartX, scaledStartY, scaledEndX - scaledStartX, scaledEndY - scaledStartY);
    overlayCtx.strokeStyle = "blue";
    overlayCtx.stroke();
  }
  // Set up canvas event listeners for overlayCanvas
  overlayCanvas.addEventListener("mousedown", (e) => {
    startX = e.offsetX;
    startY = e.offsetY;

    isDragging = true;
  });

  overlayCanvas.addEventListener("mousemove", (e) => {
    if (isDragging) {
      endX = e.offsetX;
      endY = e.offsetY;
      drawRectangle(); // Draw onto the overlayCtx
    }
  });

  overlayCanvas.addEventListener("mouseup", (e) => {
    if (!isDragging) {
      return;
    }
    isDragging = false;
    // Adjust coordinates based on scaling factor
    let scaledStartX = startX / scale_two;
    let scaledStartY = startY / scale_two;

    let scaledEndX = endX / scale_two;
    let scaledEndY = endY / scale_two;
  
    let width = scaledEndX - scaledStartX;
    let height = scaledEndY - scaledStartY;
    
    // Capture the current page number
    let currentPageNum = pageNum;

    // Send  other parameters to the server
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
        page_num: currentPageNum, 
        pdfHeight: pdfHeight / scale_two,

      }),
    })
    .then(response => response.json())
    .catch(error => console.error("Error:", error));
    $('#status').text('Kaydedildi!');
  });
  
  
  // Enable interaction with the overlayCanvas
  overlayCanvas.style.pointerEvents = "auto";

  // Event listener for file input
  fileInput.addEventListener("change", (e) => {

    pageNum=1;
    document.getElementById('file-form').submit();
    let file = e.target.files[0];

    if (file.type !== "application/pdf") {
      alert("Please select a PDF file.");
      return;
    }

    // Clear the canvas before rendering the new PDF
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

    // Create form data
    let formData = new FormData();
    formData.append("pdfFile", file);

    filename = file.name;

    let fileReader = new FileReader();
    fileReader.onload = function () {
      let typedarray = new Uint8Array(this.result);
      pdfjsLib.getDocument(typedarray).promise.then(function (pdfDoc_) {
        pdfDoc = pdfDoc_;

        renderPage(pageNum);
      });
    };
    fileReader.readAsArrayBuffer(file);

  });


  // Function for updating page information
  function updatePageInfo() {
    document.getElementById(
      "pageInfo"
    ).textContent = `Page ${pageNum} of ${pdfDoc.numPages}`;
  }

  // Function for rendering the previous page
  function onPrevPage() {
    if (pageNum <= 1) {
      return; // Already at the first page
    }
    pageNum--;
    renderPage(pageNum);
    updatePageInfo();
  }

  // Function for rendering the next page
  function onNextPage() {
    if (pageNum >= pdfDoc.numPages) {
      return; // Already at the last page
    }
    pageNum++;
    renderPage(pageNum);
    updatePageInfo();
  }

  // Event listener for the previous page button
  document.getElementById("prevPage").addEventListener("click", onPrevPage);

  // Event listener for the next page button
  document.getElementById("nextPage").addEventListener("click", onNextPage);
  
  /*
  // Clear the rectangle on the overlay canvas
  document.getElementById("clearRect").addEventListener("click", () => {
    overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
  });
  */

  // Specify the workerSrc for PDF.js
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.worker.min.js";
});
