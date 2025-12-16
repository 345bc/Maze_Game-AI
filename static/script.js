let ROWS = 21;
let COLS = 25;
let CELL_SIZE = 28;

let gridData = [];
let startPos = null;
let endPos = null;
let currentMode = 'wall';
let isDrawing = false;
let isSolving = false;

const gridContainer = document.getElementById('grid-container');

function initGrid() {
    gridContainer.style.gridTemplateColumns = `repeat(${COLS}, ${CELL_SIZE}px)`;
    gridContainer.innerHTML = '';
    gridData = [];

    for (let r = 0; r < ROWS; r++) {
        let rowData = [];
        for (let c = 0; c < COLS; c++) {
            rowData.push(0);
            const cell = document.createElement('div');
            cell.id = `cell-${r}-${c}`;
            cell.className = `w-[${CELL_SIZE}px] h-[${CELL_SIZE}px] bg-white cursor-pointer transition-colors duration-150 hover:bg-slate-50`;
            
            cell.onmousedown = (e) => { e.preventDefault(); isDrawing = true; handleCellClick(r, c); };
            cell.onmouseenter = () => { if (isDrawing) handleCellClick(r, c); };
            cell.onmouseup = () => { isDrawing = false; };
            
            gridContainer.appendChild(cell);
        }
        gridData.push(rowData);
    }
}
document.addEventListener('mouseup', () => { isDrawing = false; });

// --- UPDATE VISUALS ---
function updateCellVisual(r, c, type) {
    const cell = document.getElementById(`cell-${r}-${c}`);
    if (!cell) return;
    
    cell.className = `w-[${CELL_SIZE}px] h-[${CELL_SIZE}px] cursor-pointer transition-all duration-300 border-none`;
    cell.innerHTML = '';

    switch (type) {
        case 'start': 
            cell.classList.add('bg-emerald-500', 'rounded-md', 'shadow-md', 'scale-90', 'z-10'); break;
        case 'end': 
            cell.classList.add('bg-rose-500', 'rounded-md', 'shadow-md', 'scale-90', 'z-10'); break;
        case 'wall': 
            cell.classList.add('bg-slate-800', 'rounded-sm'); break;
        case 'water': 
            cell.classList.add('bg-blue-400/80', 'backdrop-blur-sm'); break;
        case 'path': 
            cell.classList.add('bg-indigo-600', 'animate-pop', 'rounded-sm'); break;
        case 'visited': 
            cell.classList.add('bg-indigo-100', 'animate-pop'); break;
        default: 
            cell.classList.add('bg-white', 'hover:bg-slate-50'); 
    }
}

// --- LOGIC ---
function handleCellClick(r, c) {
    if (isSolving) return;

    if (currentMode === 'start') {
        if (startPos) {
            const [oldR, oldC] = startPos;
            startPos = null; refreshCell(oldR, oldC);
        }
        startPos = [r, c];
        gridData[r][c] = 0; 
        updateCellVisual(r, c, 'start');
    } 
    else if (currentMode === 'end') {
        if (endPos) {
            const [oldR, oldC] = endPos;
            endPos = null; refreshCell(oldR, oldC);
        }
        endPos = [r, c];
        gridData[r][c] = 0;
        updateCellVisual(r, c, 'end');
    } 
    else {
        if ((startPos && r===startPos[0] && c===startPos[1]) || 
            (endPos && r===endPos[0] && c===endPos[1])) return;

        if (currentMode === 'wall') gridData[r][c] = (gridData[r][c] === 1) ? 0 : 1;
        else if (currentMode === 'water') gridData[r][c] = (gridData[r][c] === 2) ? 0 : 2;
        refreshCell(r, c);
    }
}

function refreshCell(r, c) {
    if (startPos && r===startPos[0] && c===startPos[1]) return updateCellVisual(r, c, 'start');
    if (endPos && r===endPos[0] && c===endPos[1]) return updateCellVisual(r, c, 'end');
    const val = gridData[r][c];
    if (val === 1) updateCellVisual(r, c, 'wall');
    else if (val === 2) updateCellVisual(r, c, 'water');
    else updateCellVisual(r, c, 'empty');
}

function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.tool-btn').forEach(el => el.classList.remove('active'));
    const btn = document.getElementById(`btn-${mode}`);
    if(btn) btn.classList.add('active');
}

async function solve() {
    if (!startPos || !endPos) return alert("Vui lòng đặt điểm Start và End!");
    isSolving = true;
    for(let r=0; r<ROWS; r++) for(let c=0; c<COLS; c++) refreshCell(r, c);

    try {
        const res = await fetch('/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grid: gridData, start: startPos, end: endPos })
        });
        const data = await res.json();

        if (!data.path || data.path.length === 0) {
            alert("Không tìm thấy đường!");
            isSolving = false;
            return;
        }
        data.visited.forEach((node, i) => {
            setTimeout(() => { if (!isProtected(node)) updateCellVisual(node[0], node[1], 'visited'); }, 5 * i);
        });
        setTimeout(() => {
            data.path.forEach((node, i) => {
                setTimeout(() => { if (!isProtected(node)) updateCellVisual(node[0], node[1], 'path'); }, 20 * i);
            });
            isSolving = false;
        }, 5 * data.visited.length);
    } catch (e) { console.error(e); isSolving = false; }
}

function isProtected(node) {
    return (startPos && node[0]===startPos[0] && node[1]===startPos[1]) || (endPos && node[0]===endPos[0] && node[1]===endPos[1]);
}

function clearPath() { for(let r=0; r<ROWS; r++) for(let c=0; c<COLS; c++) refreshCell(r, c); }

function clearBoard() {
    startPos = null; endPos = null;
    gridData = gridData.map(row => row.map(() => 0));
    initGrid();
    isSolving = false;
}

function generateRandomMap() {
    for(let r=0; r<ROWS; r++) for(let c=0; c<COLS; c++) refreshCell(r, c);
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            if (startPos && r === startPos[0] && c === startPos[1]) continue;
            if (endPos && r === endPos[0] && c === endPos[1]) continue;
            const rand = Math.random(); 
            if (rand < 0.2) gridData[r][c] = 1; else if (rand < 0.3) gridData[r][c] = 2; else gridData[r][c] = 0;
            refreshCell(r, c);
        }
    }
}

async function generateMazeDFS() {
    try {
        const res = await fetch('/generate_maze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rows: ROWS, cols: COLS })
        });
        const data = await res.json();
        gridData = data.grid;
        startPos = data.start;
        endPos = data.end;
        for(let r=0; r<ROWS; r++) for(let c=0; c<COLS; c++) refreshCell(r,c);
    } catch (e) { console.error(e); }
}

document.addEventListener('DOMContentLoaded', () => { initGrid(); setMode('wall'); });