function loadData(text) {
    // This function will have unexpected results if text is not in the expected format
    // Each row is separated by \n
    let rows = text.split("\n");
    let n = rows.length - 1; // Last row and last column are requirements
    let matrix = [];
    for (let i = 0; i < n; i++) {
        // Each column is separated by " "
        columns = rows[i].split(" ");
        for (let j = 0; j < n; j++) {
            matrix.push(columns[j]); // Note that matrix is flattened
        }
    }
    // Requirements per column are found on last row
    let lastRow = rows[n].split(" ");
    let cj = [];
    for (let j = 0; j < n; j++) {
        cj.push(lastRow[j]);
    }
    // Requirements per row are found in the last column
    let ri = [];
    for (let i = 0; i < n; i++) {
        let currentRow = rows[i].split(" ");
        ri.push(currentRow[n]);
    }
    // Find start and end positions, found on first column and last row
    positions = [];
    for (let i = 0; i < n && positions.length < 2; i++) {
        let j = 0;
        let index = i*n + j;
        if (matrix[index] !== "N") {
            positions.push({i});
        }
    }
    for (let j = 0; j < n && positions.length < 2; j++) {
        let i = n-1;
        let index = i*n + j;
        if (matrix[index] !== "N") {
            positions.push({j});
        }
    }

    return [matrix, ri, cj, positions];
}

function reset() {
    document.querySelector(".rowIndex")
    document.querySelector(".colIndex")
    document.querySelector(".rowRequi")
    document.querySelector(".colRequi")
    document.querySelector(".solution")
}

async function loadGrid(event) {
    // Read
    const file = event.target.files.item(0);
    const text = await file.text();
    text.replace("\r", "");

    // Parse data
    const [matrix, ri, cj, positions] = loadData(text);
    const n = ri.length;  // Should be equal to cj.length

    // Set style that depends on n
    document.querySelector(':root').style.setProperty('--n', n);
    document.querySelector(".container.inactive").classList.remove("inactive");

    // Create elements for rowIndex
    for (let i = 1; i <= n; i++) {
        let child = document.createElement("div");
        child.innerText = i;
        document.querySelector(".rowIndex").appendChild(child);
    }

    // Create elements for colIndex
    for (let j = 1; j <= n; j++) {
        let child = document.createElement("div");
        child.innerText = j;
        document.querySelector(".colIndex").appendChild(child);
    }

    let startPosition = positions[0];
    if ('i' in startPosition) {
        document.querySelector(`.rowIndex :nth-child(${startPosition.i + 1})`).classList.add("startPosition");
    }
    else {
        document.querySelector(`.colIndex :nth-child(${startPosition.j + 1})`).classList.add("startPosition");
    }

    
    let endPosition = positions[1];
    if ('i' in endPosition) {
        document.querySelector(`.rowIndex :nth-child(${endPosition.i + 1})`).classList.add("endPosition");
    }
    else {
        document.querySelector(`.colIndex :nth-child(${endPosition.j + 1})`).classList.add("endPosition");
    }

    // Create elements for rowRequi
    for (let i = 0; i < n; i++) {
        let child = document.createElement("div");
        child.innerText = ri[i];
        document.querySelector(".rowRequi").appendChild(child);
    }

    // Create elements for colRequi
    for (let j = 0; j < n; j++) {
        let child = document.createElement("div");
        child.innerText = cj[j];
        document.querySelector(".colRequi").appendChild(child);
    }

    // Create elementos for solution
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            let index = i*n + j;
            let child = document.createElement("div");
            child.classList.add(matrix[index]);
            document.querySelector(".solution").appendChild(child);
        }
    }
}

document.querySelector("#opti-file").onchange = loadGrid;