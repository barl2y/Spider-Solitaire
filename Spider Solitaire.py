<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>엘리멘탈 타일 매치 - No Moves Impact Edition</title>
    <style>
        :root {
            --bg-color: #0d0f17;
            --card-bg: #1a1d2e;
            --accent-red: #ff3366;
            --accent-cyan: #00f2fe;
            --accent-purple: #9d50bb;
            --text-color: #f0f4f8;
        }

        * {
            box-sizing: border-box;
            user-select: none;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .game-container {
            width: 100%;
            max-width: 480px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 10;
        }

        .header {
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            background: rgba(26, 29, 46, 0.8);
            padding: 15px 20px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
        }

        .score-board, .moves-board {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .label {
            font-size: 12px;
            color: #8a94a6;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }

        .value {
            font-size: 24px;
            font-weight: 800;
            color: var(--accent-cyan);
            text-shadow: 0 0 10px rgba(0, 242, 254, 0.4);
        }

        .game-title {
            font-size: 20px;
            font-weight: 900;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .grid-container {
            width: 400px;
            height: 400px;
            background: rgba(15, 18, 30, 0.9);
            border-radius: 20px;
            padding: 12px;
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            grid-template-rows: repeat(6, 1fr);
            gap: 8px;
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.8), 0 10px 40px rgba(0, 0, 0, 0.5);
            border: 2px solid rgba(255, 255, 255, 0.05);
            position: relative;
        }

        .tile {
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 26px;
            cursor: pointer;
            transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.2s ease, opacity 0.2s;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            position: relative;
        }

        .tile:hover {
            transform: scale(1.06);
            z-index: 2;
        }

        .tile.selected {
            transform: scale(1.1);
            outline: 3px solid var(--accent-cyan);
            box-shadow: 0 0 20px var(--accent-cyan);
            z-index: 3;
        }

        /* 타일 요소별 컬러 스타일 */
        .type-0 { background: linear-gradient(135deg, #ff4e50, #f9d423); } /* 화염 */
        .type-1 { background: linear-gradient(135deg, #00c6ff, #0072ff); } /* 빙결 */
        .type-2 { background: linear-gradient(135deg, #a8ff78, #78ffd6); } /* 자연 */
        .type-3 { background: linear-gradient(135deg, #f80759, #bc4e9c); } /* 번개 */
        .type-4 { background: linear-gradient(135deg, #f7971e, #ffd200); } /* 광명 */

        .controls {
            margin-top: 20px;
            display: flex;
            gap: 12px;
        }

        .btn {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #fff;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            backdrop-filter: blur(5px);
        }

        .btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }

        .btn-test {
            background: linear-gradient(135deg, rgba(255, 51, 102, 0.3), rgba(157, 80, 187, 0.3));
            border-color: var(--accent-red);
            color: #ff99b3;
        }

        .btn-test:hover {
            background: linear-gradient(135deg, rgba(255, 51, 102, 0.6), rgba(157, 80, 187, 0.6));
            color: #fff;
            box-shadow: 0 0 15px rgba(255, 51, 102, 0.4);
        }

        /* 실패 화면 오버레이 */
        #fail-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(5, 5, 10, 0.85);
            backdrop-filter: blur(15px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s ease;
        }

        #fail-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        .fail-modal {
            text-align: center;
            transform: scale(0.7);
            transition: transform 0.5s cubic-bezier(0.19, 1, 0.22, 1);
            position: relative;
            z-index: 1002;
            padding: 40px;
            background: radial-gradient(circle, rgba(30, 10, 20, 0.9) 0%, rgba(10, 5, 12, 0.95) 100%);
            border-radius: 28px;
            border: 2px solid rgba(255, 0, 85, 0.4);
            box-shadow: 0 0 80px rgba(255, 0, 85, 0.3), inset 0 0 30px rgba(255, 0, 85, 0.2);
            max-width: 90%;
            width: 400px;
        }

        #fail-overlay.active .fail-modal {
            transform: scale(1);
        }

        .fail-title {
            font-size: 42px;
            font-weight: 900;
            color: #ff0055;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 20px #ff0055, 0 0 40px #ff0055;
            margin-bottom: 10px;
            animation: glitch 1.5s infinite alternate;
        }

        @keyframes glitch {
            0% { text-shadow: 0 0 20px #ff0055, 0 0 40px #ff0055, 3px 0 #00f2fe; }
            50% { text-shadow: 0 0 25px #ff0055, 0 0 50px #ff0055, -3px 0 #9d50bb; }
            100% { text-shadow: 0 0 20px #ff0055, 0 0 40px #ff0055, 2px 0 #00f2fe; }
        }

        .fail-reason {
            font-size: 16px;
            color: #d1d5db;
            margin-bottom: 25px;
            font-weight: 500;
            letter-spacing: -0.2px;
        }

        .fail-stats {
            background: rgba(0, 0, 0, 0.4);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .fail-stats-item {
            display: flex;
            justify-content: space-between;
            margin: 6px 0;
            font-size: 15px;
        }

        .fail-stats-item .val {
            font-weight: 700;
            color: #fff;
        }

        .retry-btn {
            background: linear-gradient(135deg, #ff0055, #9d50bb);
            color: #fff;
            border: none;
            padding: 16px 36px;
            border-radius: 50px;
            font-size: 18px;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 0 30px rgba(255, 0, 85, 0.5);
            transition: all 0.3s ease;
            width: 100%;
        }

        .retry-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 50px rgba(255, 0, 85, 0.8);
        }

        /* FX Canvas */
        #fx-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 1001;
        }

        .status-badge {
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 20px;
            background: rgba(0, 242, 254, 0.15);
            color: var(--accent-cyan);
            border: 1px solid rgba(0, 242, 254, 0.3);
            margin-top: 5px;
        }
    </style>
</head>
<body>

    <div class="game-container">
        <div class="header">
            <div class="score-board">
                <span class="label">점수</span>
                <span class="value" id="score">0</span>
            </div>
            <div style="text-align: center;">
                <div class="game-title">ELEMENTAL</div>
                <div class="status-badge" id="status-text">움직임 가능</div>
            </div>
            <div class="moves-board">
                <span class="label">남은 콤보</span>
                <span class="value" id="moves-left">30</span>
            </div>
        </div>

        <div class="grid-container" id="grid"></div>

        <div class="controls">
            <button class="btn" onclick="initGame()">게임 재시작</button>
            <button class="btn btn-test" onclick="forceNoMovesFail()">실패 화면 테스트 (강제)</button>
        </div>
    </div>

    <!-- 임팩트 이펙트 전용 Canvas -->
    <canvas id="fx-canvas"></canvas>

    <!-- 실패/게임오버 오버레이 (등불/벚꽃 대신 크림슨 노바 & 유리파쇄 임팩트 적용) -->
    <div id="fail-overlay">
        <div class="fail-modal">
            <div class="fail-title">NO MORE MOVES</div>
            <div class="fail-reason">더 이상 이동 가능한 블록이 없습니다!</div>
            
            <div class="fail-stats">
                <div class="fail-stats-item">
                    <span>최종 점수</span>
                    <span class="val" id="final-score">0</span>
                </div>
                <div class="fail-stats-item">
                    <span>달성 콤보</span>
                    <span class="val" id="final-combos">0</span>
                </div>
            </div>

            <button class="retry-btn" onclick="retryGame()">다시 도전하기</button>
        </div>
    </div>

    <script>
        const GRID_SIZE = 6;
        const ELEMENT_TYPES = [
            { icon: '🔥', class: 'type-0' },
            { icon: '❄️', class: 'type-1' },
            { icon: '🌿', class: 'type-2' },
            { icon: '⚡', class: 'type-3' },
            { icon: '💎', class: 'type-4' }
        ];

        let board = [];
        let score = 0;
        let combos = 0;
        let selectedTile = null;
        let isProcessing = false;
        let isGameOver = false;

        const gridEl = document.getElementById('grid');
        const scoreEl = document.getElementById('score');
        const failOverlay = document.getElementById('fail-overlay');
        const finalScoreEl = document.getElementById('final-score');
        const finalCombosEl = document.getElementById('final-combos');
        const statusTextEl = document.getElementById('status-text');

        // Canvas Effect Setup
        const canvas = document.getElementById('fx-canvas');
        const ctx = canvas.getContext('2d');
        let particles = [];
        let shockwaves = [];
        let glassShards = [];
        let animId = null;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        // 보드 생성 및 게임 초기화
        function initGame() {
            failOverlay.classList.remove('active');
            isGameOver = false;
            score = 0;
            combos = 0;
            scoreEl.textContent = score;
            statusTextEl.textContent = "움직임 가능";
            statusTextEl.style.borderColor = "rgba(0, 242, 254, 0.3)";
            statusTextEl.style.color = "var(--accent-cyan)";
            
            generateValidBoard();
            renderBoard();
        }

        function generateValidBoard() {
            do {
                board = [];
                for (let r = 0; r < GRID_SIZE; r++) {
                    let row = [];
                    for (let c = 0; c < GRID_SIZE; c++) {
                        row.push(Math.floor(Math.random() * ELEMENT_TYPES.length));
                    }
                    board.push(row);
                }
                clearMatchesOnStart();
            } while (!hasPossibleMoves());
        }

        // 초기 매칭 자동 제거
        function clearMatchesOnStart() {
            for (let r = 0; r < GRID_SIZE; r++) {
                for (let c = 0; c < GRID_SIZE; c++) {
                    if (c >= 2 && board[r][c] === board[r][c-1] && board[r][c] === board[r][c-2]) {
                        board[r][c] = (board[r][c] + 1) % ELEMENT_TYPES.length;
                    }
                    if (r >= 2 && board[r][c] === board[r-1][c] && board[r][c] === board[r-2][c]) {
                        board[r][c] = (board[r][c] + 1) % ELEMENT_TYPES.length;
                    }
                }
            }
        }

        // 보드 화면 렌더링
        function renderBoard() {
            gridEl.innerHTML = '';
            for (let r = 0; r < GRID_SIZE; r++) {
                for (let c = 0; c < GRID_SIZE; c++) {
                    const typeIdx = board[r][c];
                    const tile = document.createElement('div');
                    tile.className = `tile ${ELEMENT_TYPES[typeIdx].class}`;
                    tile.textContent = ELEMENT_TYPES[typeIdx].icon;
                    tile.dataset.row = r;
                    tile.dataset.col = c;
                    
                    if (selectedTile && selectedTile.row === r && selectedTile.col === c) {
                        tile.classList.add('selected');
                    }

                    tile.addEventListener('click', () => handleTileClick(r, c));
                    gridEl.appendChild(tile);
                }
            }
        }

        // 타일 클릭 이벤트 처리
        async function handleTileClick(r, c) {
            if (isProcessing || isGameOver) return;

            if (!selectedTile) {
                selectedTile = { row: r, col: c };
                renderBoard();
            } else {
                const r1 = selectedTile.row;
                const c1 = selectedTile.col;
                const r2 = r;
                const c2 = c;

                // 인접 타일 검사 (상하좌우)
                const isAdjacent = (Math.abs(r1 - r2) + Math.abs(c1 - c2)) === 1;

                if (isAdjacent) {
                    isProcessing = true;
                    // 스왑 실행
                    swapTiles(r1, c1, r2, c2);
                    renderBoard();

                    const matches = checkMatches();
                    if (matches.length > 0) {
                        selectedTile = null;
                        await processMatches();
                    } else {
                        // 유효 매칭이 없으면 원위치 스왑
                        await new Promise(res => setTimeout(res, 250));
                        swapTiles(r1, c1, r2, c2);
                        selectedTile = null;
                        renderBoard();
                        isProcessing = false;
                    }
                } else {
                    selectedTile = { row: r, col: c };
                    renderBoard();
                }
            }
        }

        function swapTiles(r1, c1, r2, c2) {
            const temp = board[r1][c1];
            board[r1][c1] = board[r2][c2];
            board[r2][c2] = temp;
        }

        // 매칭 검사
        function checkMatches() {
            let matchedCoords = new Set();

            // 가로 매칭
            for (let r = 0; r < GRID_SIZE; r++) {
                for (let c = 0; c < GRID_SIZE - 2; c++) {
                    let type = board[r][c];
                    if (type !== null && type === board[r][c+1] && type === board[r][c+2]) {
                        matchedCoords.add(`${r},${c}`);
                        matchedCoords.add(`${r},${c+1}`);
                        matchedCoords.add(`${r},${c+2}`);
                    }
                }
            }

            // 세로 매칭
            for (let c = 0; c < GRID_SIZE; c++) {
                for (let r = 0; r < GRID_SIZE - 2; r++) {
                    let type = board[r][c];
                    if (type !== null && type === board[r+1][c] && type === board[r+2][c]) {
                        matchedCoords.add(`${r},${c}`);
                        matchedCoords.add(`${r+1},${c}`);
                        matchedCoords.add(`${r+2},${c}`);
                    }
                }
            }

            return Array.from(matchedCoords).map(coord => {
                const [row, col] = coord.split(',').map(Number);
                return { row, col };
            });
        }

        // 매칭 터뜨리기 및 채우기 연쇄 프로세스
        async function processMatches() {
            let matches = checkMatches();
            
            while (matches.length > 0) {
                combos++;
                score += matches.length * 100;
                scoreEl.textContent = score;

                // 터짐 타일 비우기
                matches.forEach(({ row, col }) => {
                    board[row][col] = null;
                });
                renderBoard();
                await new Promise(res => setTimeout(res, 200));

                // 타일 내리기 & 새 타일 생성
                dropTiles();
                renderBoard();
                await new Promise(res => setTimeout(res, 250));

                matches = checkMatches();
            }

            isProcessing = false;

            // 핵심 조건: 이동 가능한 수가 남아있는지 자동 확인!
            if (!hasPossibleMoves()) {
                triggerNoMovesGameOver();
            }
        }

        function dropTiles() {
            for (let c = 0; c < GRID_SIZE; c++) {
                let emptyRow = GRID_SIZE - 1;
                for (let r = GRID_SIZE - 1; r >= 0; r--) {
                    if (board[r][c] !== null) {
                        board[emptyRow][c] = board[r][c];
                        if (emptyRow !== r) board[r][c] = null;
                        emptyRow--;
                    }
                }
                for (let r = emptyRow; r >= 0; r--) {
                    board[r][c] = Math.floor(Math.random() * ELEMENT_TYPES.length);
                }
            }
        }

        // 가능 이동 수 확인 알고리즘 (Swap 했을 때 매칭 가능한 조합이 존재하는가?)
        function hasPossibleMoves() {
            for (let r = 0; r < GRID_SIZE; r++) {
                for (let c = 0; c < GRID_SIZE; c++) {
                    // 오른쪽 타일과 교환 테스트
                    if (c < GRID_SIZE - 1) {
                        swapTiles(r, c, r, c + 1);
                        if (checkMatches().length > 0) {
                            swapTiles(r, c, r, c + 1); // 원복
                            return true;
                        }
                        swapTiles(r, c, r, c + 1); // 원복
                    }
                    // 아래쪽 타일과 교환 테스트
                    if (r < GRID_SIZE - 1) {
                        swapTiles(r, c, r + 1, c);
                        if (checkMatches().length > 0) {
                            swapTiles(r, c, r + 1, c); // 원복
                            return true;
                        }
                        swapTiles(r, c, r + 1, c); // 원복
                    }
                }
            }
            return false;
        }

        // 테스팅용: 강제로 가능 이동 수를 없앤 상태로 실패 트리거
        function forceNoMovesFail() {
            if (isGameOver) return;
            // 이동 불가능한 패턴으로 보드 설정 (체크판 교차 배치)
            let pattern = [
                [0, 1, 0, 1, 0, 1],
                [2, 3, 2, 3, 2, 3],
                [0, 1, 0, 1, 0, 1],
                [2, 3, 2, 3, 2, 3],
                [0, 1, 0, 1, 0, 1],
                [2, 3, 2, 3, 2, 3]
            ];
            board = pattern;
            renderBoard();
            
            triggerNoMovesGameOver();
        }

        // 더 이상 수가 없을 때 게임 중단 & 크림슨 셰터링 뇌전 실패 화면 연출
        function triggerNoMovesGameOver() {
            isGameOver = true;
            statusTextEl.textContent = "이동 불가 (중단)";
            statusTextEl.style.borderColor = "var(--accent-red)";
            statusTextEl.style.color = "var(--accent-red)";

            finalScoreEl.textContent = score;
            finalCombosEl.textContent = combos;

            // 임팩트 시각효과 발동 (유리 파쇄 Shards + 크림슨 뇌전 쇼크웨이브)
            launchCrimsonShatterImpact();

            setTimeout(() => {
                failOverlay.classList.add('active');
            }, 600);
        }

        function retryGame() {
            initGame();
        }

        // =========================================================
        // 등불/벚꽃이 아닌 "크림슨 노바 & 셰터링 스파크" 실패 연출
        // =========================================================
        function launchCrimsonShatterImpact() {
            particles = [];
            shockwaves = [];
            glassShards = [];

            const cx = window.innerWidth / 2;
            const cy = window.innerHeight / 2;

            // 1. 충격파 생성 (Shockwaves)
            shockwaves.push({
                x: cx,
                y: cy,
                radius: 10,
                maxRadius: Math.max(window.innerWidth, window.innerHeight) * 0.7,
                lineWidth: 30,
                alpha: 1,
                color: '#ff0055'
            });

            shockwaves.push({
                x: cx,
                y: cy,
                radius: 5,
                maxRadius: Math.max(window.innerWidth, window.innerHeight) * 0.5,
                lineWidth: 15,
                alpha: 1,
                color: '#00f2fe'
            });

            // 2. 파편 유리 조각 (Glass Shards Impact)
            for (let i = 0; i < 70; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * 22 + 5;
                glassShards.push({
                    x: cx,
                    y: cy,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    size: Math.random() * 20 + 8,
                    angle: Math.random() * Math.PI,
                    vAngle: (Math.random() - 0.5) * 0.3,
                    alpha: 1,
                    color: Math.random() > 0.3 ? '#ff0055' : (Math.random() > 0.5 ? '#9d50bb' : '#ffffff')
                });
            }

            // 3. 전기 스파크 입자 (Lightning Sparks)
            for (let i = 0; i < 120; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * 18 + 2;
                particles.push({
                    x: cx,
                    y: cy,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    life: 1,
                    decay: Math.random() * 0.02 + 0.015,
                    size: Math.random() * 4 + 2,
                    color: Math.random() > 0.4 ? '#ff0055' : '#ff9900'
                });
            }

            if (animId) cancelAnimationFrame(animId);
            animateImpact();
        }

        function animateImpact() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Shockwaves 그려주기
            shockwaves.forEach((sw, idx) => {
                sw.radius += (sw.maxRadius - sw.radius) * 0.12;
                sw.alpha -= 0.025;
                sw.lineWidth *= 0.96;

                if (sw.alpha > 0) {
                    ctx.save();
                    ctx.beginPath();
                    ctx.arc(sw.x, sw.y, sw.radius, 0, Math.PI * 2);
                    ctx.lineWidth = sw.lineWidth;
                    ctx.strokeStyle = sw.color;
                    ctx.globalAlpha = Math.max(0, sw.alpha);
                    ctx.shadowColor = sw.color;
                    ctx.shadowBlur = 30;
                    ctx.stroke();
                    ctx.restore();
                }
            });

            // 유리 파편 그려주기
            glassShards.forEach((shard) => {
                shard.x += shard.vx;
                shard.y += shard.vy;
                shard.vx *= 0.95;
                shard.vy *= 0.95;
                shard.angle += shard.vAngle;
                shard.alpha -= 0.015;

                if (shard.alpha > 0) {
                    ctx.save();
                    ctx.translate(shard.x, shard.y);
                    ctx.rotate(shard.angle);
                    ctx.globalAlpha = Math.max(0, shard.alpha);
                    ctx.fillStyle = shard.color;
                    ctx.shadowColor = shard.color;
                    ctx.shadowBlur = 15;

                    // 날카로운 삼각형 파편 형태
                    ctx.beginPath();
                    ctx.moveTo(0, -shard.size);
                    ctx.lineTo(shard.size / 2, shard.size);
                    ctx.lineTo(-shard.size / 2, shard.size / 2);
                    ctx.closePath();
                    ctx.fill();

                    ctx.restore();
                }
            });

            // 전기 스파크 입자
            particles.forEach((p) => {
                p.x += p.vx;
                p.y += p.vy;
                p.life -= p.decay;

                if (p.life > 0) {
                    ctx.save();
                    ctx.globalAlpha = p.life;
                    ctx.fillStyle = p.color;
                    ctx.shadowColor = p.color;
                    ctx.shadowBlur = 10;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }
            });

            if (shockwaves.some(s => s.alpha > 0) || glassShards.some(g => g.alpha > 0) || particles.some(p => p.life > 0)) {
                animId = requestAnimationFrame(animateImpact);
            } else {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }

        // 게임 자동 시작
        window.onload = initGame;
    </script>
</body>
</html>
```eof

요청하신 기능 및 실패 연출이 반영된 게임 파일이 생성되었습니다!

### 주요 반영 사항
1. **이동 가능 수 자동 검사 (`hasPossibleMoves`)**:
   - 블록 매칭 및 연쇄 폭발이 모두 끝난 후, 보드 내에서 단 한 건이라도 유효하게 스왑하여 터뜨릴 수 있는 조합이 존재하는지 자동으로 탐지합니다.
   - 더 이상 가능한 수(Match)가 없다면 즉시 게임이 중단됩니다.
2. **차별화된 실패 연출 (크림슨 노바 & Glass Shatter)**:
   - 기존의 등불/벚꽃 효과 대신, 화면 중앙에서 붉은 전율의 **충격파(Shockwave)**, **날카로운 크림슨 유리 파편(Glass Shards)**, 그리고 **전기 스파크 Particle**이 연쇄 폭발하는 임팩트를 연출했습니다.
   - 글리치 애니메이션 모달 및 네온 실패 화면 UI가 적용되었습니다.
3. **테스트 버튼 제공**:
   - 하단의 `실패 화면 테스트 (강제)` 버튼을 누르면 즉시 이동 불가능한 상황을 연출하여 실패 스크린과 시각 효과를 확인해보실 수 있습니다.
