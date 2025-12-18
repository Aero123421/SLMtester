
// Icons as SVG strings for reuse
const ICONS = {
    settings: '<svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
    robot: '<svg class="icon" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
    testTube: '<svg class="icon" viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12" stroke-width="0"/><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path><line x1="16" y1="8" x2="2" y2="22"></line><line x1="17.5" y1="15" x2="9" y2="15"></line></svg>',
    search: '<svg class="icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
    copy: '<svg class="icon" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>',
    check: '<svg class="icon" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>',
    x: '<svg class="icon" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>',
    chevronRight: '<svg class="icon" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>',
    chevronDown: '<svg class="icon" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"></polyline></svg>',
    edit: '<svg class="icon" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>',
    messageSquare: '<svg class="icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
    messageCircle: '<svg class="icon" viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>',
    barChart: '<svg class="icon" viewBox="0 0 24 24"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>'
};

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const form = document.getElementById('bench-form');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const logsContainer = document.getElementById('logs-container');
    const resultsGrid = document.getElementById('results-grid');
    const resultsTableBody = document.getElementById('results-table-body');
    const modelList = document.getElementById('model-list');
    const baseUrlInput = document.getElementById('base_url');
    const refreshModelsBtn = document.getElementById('refresh-models-btn');
    const selectAllBtn = document.getElementById('select-all-btn');
    const deselectAllBtn = document.getElementById('deselect-all-btn');
    const connectionStatus = document.getElementById('connection-status');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const modalOverlay = document.getElementById('modal-overlay');
    const modalClose = document.getElementById('modal-close');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');
    const globalProgressBar = document.getElementById('global-progress-bar');

    // Stats elements
    const statProgress = document.querySelector('#stat-progress .stat-value');
    const statPassRate = document.querySelector('#stat-pass-rate .stat-value');
    const statTimer = document.querySelector('#stat-timer .stat-value');

    // State
    let currentJobId = null;
    let pollInterval = null;
    let timerInterval = null;
    let startTime = null;
    let availableModels = [];
    let allResults = [];
    let expectedTotal = 0;
    let suiteInfo = null;
    let currentSuiteMeta = {};
    let currentSuitePath = null;
    let lastFocusedElement = null;

    // Chart instances
    let chartPassRate = null;
    let chartLatency = null;
    let chartCategoryPass = null;

    // Initialize
    init();

    async function init() {
        await Promise.all([
            loadModels(),
            loadSuiteInfo()
        ]);
        setupEventListeners();
    }

    async function loadSuiteInfo() {
        const suiteInfoEl = document.getElementById('suite-info');
        const suitePath = document.getElementById('suite_path')?.value || 'bench/suite.yaml';
        try {
            const res = await fetch(`/api/suite?suite_path=${encodeURIComponent(suitePath)}`);
            const data = await res.json();

            if (data.error) {
                suiteInfoEl.innerHTML = `<div class="suite-error">${data.error}</div>`;
                return;
            }

            suiteInfo = data;
            if (data && data.meta) currentSuiteMeta = data.meta;
            if (data && data.suite_path) currentSuitePath = data.suite_path;
            renderSuiteInfo(data);
        } catch (err) {
            suiteInfoEl.innerHTML = `<div class="suite-error">読み込みエラー: ${err.message}</div>`;
        }
    }

    function renderSuiteInfo(data) {
        const suiteInfoEl = document.getElementById('suite-info');

        let html = `<div class="suite-summary">合計 <strong>${data.total_tests}</strong> テスト / <strong>${data.categories.length}</strong> カテゴリ</div>`;
        html += '<div class="category-list">';

        for (const cat of data.categories) {
            html += `
                <div class="category-item">
                    <div class="category-header" data-cat="${cat.id}">
                        <span class="category-toggle">${ICONS.chevronRight}</span>
                        <span class="category-name">${cat.name}</span>
                        <span class="category-count">${cat.tests.length}</span>
                    </div>
                    <div class="category-tests hidden" id="cat-tests-${cat.id}">
                        ${cat.tests.map(t => `
                            <div class="test-item" title="${t.description}">
                                <span class="test-name">${t.name}</span>
                                ${t.modality === 'vision' ? '<span class="test-badge vision">VLM</span>' : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        html += '</div>';
        suiteInfoEl.innerHTML = html;

        // Toggle handlers
        suiteInfoEl.querySelectorAll('.category-header').forEach(header => {
            header.addEventListener('click', () => {
                const catId = header.dataset.cat;
                const testsEl = document.getElementById(`cat-tests-${catId}`);
                const toggle = header.querySelector('.category-toggle');
                testsEl.classList.toggle('hidden');
                toggle.innerHTML = testsEl.classList.contains('hidden') ? ICONS.chevronRight : ICONS.chevronDown;
            });
        });
    }

    function setupEventListeners() {
        form.addEventListener('submit', handleStart);
        refreshModelsBtn.addEventListener('click', loadModels);
        selectAllBtn.addEventListener('click', () => toggleAllModels(true));
        deselectAllBtn.addEventListener('click', () => toggleAllModels(false));

        const suiteSelect = document.getElementById('suite_path');
        if (suiteSelect) {
            suiteSelect.addEventListener('change', () => {
                loadSuiteInfo();
            });
        }

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
            });
        });

        modalClose.addEventListener('click', closeModal);
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });

        document.addEventListener('keydown', (e) => {
            if (modalOverlay.classList.contains('hidden')) return;

            if (e.key === 'Escape') {
                closeModal();
            } else if (e.key === 'Tab') {
                trapFocus(e);
            }
        });

        // Theme Toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);

            themeToggle.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-theme');
                const next = current === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', next);
                localStorage.setItem('theme', next);
                if (typeof Chart !== 'undefined' && (chartPassRate || chartLatency || chartCategoryPass)) {
                    renderSummary(); // Re-render charts for theme colors
                }
            });
        }

        // Sidebar Toggle
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                setTimeout(() => {
                    window.dispatchEvent(new Event('resize'));
                }, 300);
            });
        }

        // Table sorting
        document.querySelectorAll('.sortable').forEach(th => {
            th.addEventListener('click', () => handleSort(th));
        });

        // Search models
        const searchModels = document.getElementById('search-models');
        if (searchModels) {
            searchModels.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                document.querySelectorAll('.model-item').forEach(item => {
                    const name = item.querySelector('.model-name').textContent.toLowerCase();
                    item.style.display = name.includes(term) ? 'flex' : 'none';
                });
            });
        }

        // Search suites
        const searchSuites = document.getElementById('search-suites');
        if (searchSuites) {
            searchSuites.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                document.querySelectorAll('.category-item').forEach(group => {
                    const catName = group.querySelector('.category-name')?.textContent.toLowerCase() || '';
                    let hasVisibleTests = false;
                    const testsEl = group.querySelector('.category-tests');
                    const toggle = group.querySelector('.category-toggle');
                    const tests = group.querySelectorAll('.test-item');

                    tests.forEach(test => {
                        const testName = test.querySelector('.test-name').textContent.toLowerCase();
                        if (testName.includes(term) || catName.includes(term)) {
                            test.style.display = 'flex';
                            hasVisibleTests = true;
                        } else {
                            test.style.display = 'none';
                        }
                    });

                    if (hasVisibleTests) {
                        group.style.display = 'block';
                        if (term.length > 0 && testsEl) {
                            testsEl.classList.remove('hidden');
                            if (toggle) toggle.innerHTML = ICONS.chevronDown;
                        } else if (testsEl) {
                            testsEl.classList.add('hidden');
                            if (toggle) toggle.innerHTML = ICONS.chevronRight;
                        }
                    } else {
                        group.style.display = 'none';
                    }
                });
            });
        }

        // LLM Judge toggle
        const useLlmJudge = document.getElementById('use_llm_judge');
        const judgeModelGroup = document.getElementById('judge-model-group');
        if (useLlmJudge && judgeModelGroup) {
            useLlmJudge.addEventListener('change', () => {
                judgeModelGroup.style.display = useLlmJudge.checked ? 'block' : 'none';
            });
        }
    }

    // Sort
    let sortColumn = null;
    let sortDirection = 'asc';

    function handleSort(th) {
        const column = th.dataset.sort;
        if (sortColumn === column) {
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            sortColumn = column;
            sortDirection = 'asc';
        }

        document.querySelectorAll('.sortable').forEach(h => {
            h.classList.remove('asc', 'desc');
        });
        th.classList.add(sortDirection);

        const sorted = [...allResults].sort((a, b) => {
            let valA, valB;
            switch (column) {
                case 'model': valA = a.model || ''; valB = b.model || ''; break;
                case 'category': valA = a.category_name || ''; valB = b.category_name || ''; break;
                case 'name': valA = a.case_name || a.case_id || ''; valB = b.case_name || b.case_id || ''; break;
                case 'passed': valA = a.passed ? 1 : 0; valB = b.passed ? 1 : 0; break;
                case 'ttft': valA = a.ttft_ms || 0; valB = b.ttft_ms || 0; break;
                case 'e2e': valA = a.e2e_ms || 0; valB = b.e2e_ms || 0; break;
                default: return 0;
            }

            if (typeof valA === 'string') {
                const cmp = valA.localeCompare(valB);
                return sortDirection === 'asc' ? cmp : -cmp;
            } else {
                return sortDirection === 'asc' ? valA - valB : valB - valA;
            }
        });

        resultsTableBody.innerHTML = '';
        sorted.forEach((r, i) => {
            const originalIndex = allResults.indexOf(r);
            addResultRow(r, originalIndex);
        });
    }

    function setConnectionStatus(status, text) {
        const dot = connectionStatus.querySelector('.status-dot');
        const txt = connectionStatus.querySelector('.status-text');
        dot.className = 'status-dot ' + status;
        txt.textContent = text;
    }

    async function loadModels() {
        const baseUrl = baseUrlInput.value.trim();
        modelList.innerHTML = '<div class="model-loading">モデル読み込み中...</div>';
        setConnectionStatus('', '接続確認中...');

        try {
            const res = await fetch(`/api/models?base_url=${encodeURIComponent(baseUrl)}`);
            if (!res.ok) throw new Error('API error');
            const data = await res.json();

            if (data.error) {
                throw new Error(data.error);
            }

            availableModels = data.models;
            renderModelList();
            setConnectionStatus('connected', `接続済み (${availableModels.length} モデル)`);
            updateStartButton();
        } catch (err) {
            modelList.innerHTML = `<div class="model-error">接続エラー: ${err.message}<br>LM Studioが起動しているか確認してください。</div>`;
            setConnectionStatus('error', '接続失敗');
            startBtn.disabled = true;
        }
    }

    function renderModelList() {
        if (availableModels.length === 0) {
            modelList.innerHTML = '<div class="model-loading">モデルが見つかりません</div>';
            return;
        }

        modelList.innerHTML = availableModels.map((m, i) => {
            const badges = [];
            if (m.type === 'vlm') badges.push('<span class="model-badge vlm">VLM</span>');
            else if (m.type === 'llm') badges.push('<span class="model-badge llm">LLM</span>');

            const isLoaded = m.state === 'loaded';

            return `
                <label class="model-item">
                    <input type="checkbox" name="model" value="${m.id}">
                    <span class="model-name" title="${m.id}">${m.id}</span>
                    <div class="model-badges">
                        ${isLoaded ? '<span class="model-badge loaded">ON</span>' : ''}
                        ${badges.join('')}
                    </div>
                </label>
            `;
        }).join('');

        modelList.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', updateStartButton);
        });

        const judgeSelect = document.getElementById('judge_model');
        if (judgeSelect) {
            const currentValue = judgeSelect.value;
            judgeSelect.innerHTML = '<option value="">（テスト対象と同じモデル）</option>';
            availableModels.forEach(m => {
                const option = document.createElement('option');
                option.value = m.id;
                option.textContent = m.id;
                if (m.id === currentValue) option.selected = true;
                judgeSelect.appendChild(option);
            });
        }
    }

    function toggleAllModels(checked) {
        modelList.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = checked;
        });
        updateStartButton();
    }

    function getSelectedModels() {
        const checkboxes = modelList.querySelectorAll('input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    function updateStartButton() {
        const selected = getSelectedModels();
        startBtn.disabled = selected.length === 0;
        const btnText = startBtn.querySelector('.btn-text');
        btnText.textContent = selected.length > 0 ? `ベンチマーク開始 (${selected.length} モデル)` : 'モデルを選択してください';
    }

    async function handleStart(e) {
        e.preventDefault();

        const selectedModels = getSelectedModels();
        if (selectedModels.length === 0) {
            alert('モデルを選択してください');
            return;
        }

        allResults = [];
        resultsGrid.innerHTML = '';
        resultsTableBody.innerHTML = '';
        logsContainer.innerHTML = '';
        startBtn.classList.add('hidden');
        stopBtn.classList.remove('hidden');
        startTime = Date.now();
        statProgress.textContent = '0 / ?';
        statPassRate.textContent = '-';
        statTimer.textContent = '00:00';
        globalProgressBar.style.width = '0%';

        const config = {
            base_url: baseUrlInput.value,
            models: selectedModels,
            runs: parseInt(document.getElementById('runs').value),
            warmup: parseInt(document.getElementById('warmup').value),
            timeout: parseInt(document.getElementById('timeout').value),
            suite_path: document.getElementById('suite_path').value,
            use_llm_judge: document.getElementById('use_llm_judge').checked,
            judge_model: document.getElementById('judge_model').value || null
        };

        addLog('info', `ベンチマーク開始: ${selectedModels.length} モデル`);

        try {
            const res = await fetch('/api/bm/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            const data = await res.json();

            if (data.error) {
                addLog('error', data.error);
                resetUI();
                return;
            }

            currentJobId = data.job_id;
            expectedTotal = data.expected_total || 0;

            pollInterval = setInterval(pollStatus, 800);
            timerInterval = setInterval(updateTimer, 1000);
        } catch (err) {
            addLog('error', `開始エラー: ${err.message}`);
            resetUI();
        }
    }

    function updateTimer() {
        const delta = Math.floor((Date.now() - startTime) / 1000);
        const m = Math.floor(delta / 60).toString().padStart(2, '0');
        const s = (delta % 60).toString().padStart(2, '0');
        statTimer.textContent = `${m}:${s}`;
    }

    async function pollStatus() {
        if (!currentJobId) return;

        try {
            const res = await fetch(`/api/bm/${currentJobId}`);
            const data = await res.json();

            if (typeof data.expected_total === "number") {
                expectedTotal = data.expected_total;
            }
            if (data && data.suite_meta) currentSuiteMeta = data.suite_meta;
            if (data && data.suite_path) currentSuitePath = data.suite_path;

            data.logs.forEach((log, i) => {
                if (i >= logsContainer.children.length) {
                    addLogElement(log.type, log.msg);
                }
            });

            const startIndex = allResults.length;
            const newResults = data.results.slice(startIndex);
            newResults.forEach((r, i) => {
                const idx = startIndex + i;
                allResults.push(r);
                addResultCard(r, idx);
                addResultRow(r, idx);
            });

            updateStats();

            if (data.status === 'done' || data.status === 'failed' || data.status === 'cancelled') {
                stopPolling();
                if (data.status === 'done') {
                    addLog('success', 'ベンチマーク完了');
                    globalProgressBar.style.width = '100%';
                } else if (data.status === 'cancelled') {
                    addLog('warn', 'ベンチマークをキャンセルしました');
                } else {
                    addLog('error', 'ベンチマーク失敗');
                }
                renderSummary();
                activateTab('summary');
                resetUI();
            }
        } catch (err) {
            console.error(err);
        }
    }

    function stopPolling() {
        clearInterval(pollInterval);
        clearInterval(timerInterval);
        pollInterval = null;
        timerInterval = null;
    }

    function resetUI() {
        startBtn.classList.remove('hidden');
        stopBtn.classList.add('hidden');
    }

    function addLog(type, msg) {
        addLogElement(type, msg);
    }

    function addLogElement(type, msg) {
        const div = document.createElement('div');
        div.className = `log-line log-${type}`;
        div.textContent = msg;
        logsContainer.appendChild(div);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    function addResultCard(res, resultIndex) {
        const emptyState = resultsGrid.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        const card = document.createElement('div');
        card.className = 'result-card';

        let statusClass, statusText;
        if (res.status === 'skipped') { statusClass = 'skip'; statusText = 'スキップ'; }
        else if (res.status === 'error') { statusClass = 'error'; statusText = 'エラー'; }
        else if (res.passed) { statusClass = 'pass'; statusText = 'PASS'; }
        else { statusClass = 'fail'; statusText = 'FAIL'; }

        const shortModel = res.model.length > 25 ? res.model.substring(0, 22) + '...' : res.model;
        const ttft = res.ttft_ms ? res.ttft_ms.toFixed(0) : '-';
        const e2e = res.e2e_ms ? res.e2e_ms.toFixed(0) : '-';
        const preview = res.response_preview || res.reason || '';
        const caseName = res.case_name || res.case_id;
        const categoryName = res.category_name || '';
        const description = res.case_description || '';

        const isVariant = res.is_variant_test;
        const variantBadge = isVariant
            ? `<span class="variant-badge">${res.variant_pass_count}/${res.variant_total_count}</span>`
            : '';

        const ttftLabel = isVariant ? 'Avg TTFT' : 'TTFT';
        const e2eLabel = isVariant ? 'Avg E2E' : 'E2E';

        // A11y: Make card interactive
        card.setAttribute('role', 'button');
        card.setAttribute('tabindex', '0');
        const statusLabel = res.passed ? '合格' : (res.status === 'skipped' ? 'スキップ' : (res.status === 'error' ? 'エラー' : '不合格'));
        const cardLabel = `モデル: ${res.model}、テスト: ${caseName}、結果: ${statusLabel}`;
        card.setAttribute('aria-label', cardLabel);

        card.innerHTML = `
            <div class="card-header">
                <div>
                    <div class="card-category">${escapeHtml(categoryName)}</div>
                    <div class="card-case" title="${escapeHtml(description)}">
                        ${escapeHtml(caseName)}${variantBadge}
                    </div>
                    <div class="card-model" title="${res.model}">${shortModel}</div>
                </div>
                <span class="status-badge ${statusClass}">${statusText}</span>
            </div>
            <div class="card-body">
                <div class="card-stats">
                    <div class="card-stat">
                        <span class="card-stat-label">${ttftLabel}</span>
                        <span class="card-stat-value">${ttft} ms</span>
                    </div>
                    <div class="card-stat">
                        <span class="card-stat-label">${e2eLabel}</span>
                        <span class="card-stat-value">${e2e} ms</span>
                    </div>
                </div>
                <div class="card-response">${escapeHtml(preview)}</div>
            </div>
        `;

        card.addEventListener('click', () => showDetail(res, resultIndex));
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                showDetail(res, resultIndex);
            }
        });
        resultsGrid.appendChild(card);
    }

    function addResultRow(res, resultIndex) {
        const tr = document.createElement('tr');

        let statusClass, statusText;
        if (res.status === 'skipped') { statusClass = 'skip'; statusText = 'スキップ'; }
        else if (res.status === 'error') { statusClass = 'error'; statusText = 'エラー'; }
        else if (res.passed) { statusClass = 'pass'; statusText = 'PASS'; }
        else { statusClass = 'fail'; statusText = 'FAIL'; }

        const caseName = res.case_name || res.case_id;
        const categoryName = res.category_name || '';

        tr.innerHTML = `
            <td title="${escapeHtml(res.model)}">${escapeHtml(res.model.substring(0, 25))}...</td>
            <td><span class="category-badge">${escapeHtml(categoryName)}</span></td>
            <td title="${escapeHtml(res.case_description || '')}">${escapeHtml(caseName)}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td>${res.ttft_ms ? res.ttft_ms.toFixed(1) : '-'}</td>
            <td>${res.e2e_ms ? res.e2e_ms.toFixed(1) : '-'}</td>
        `;
        tr.style.cursor = 'pointer';
        tr.addEventListener('click', () => showDetail(res, resultIndex));
        resultsTableBody.appendChild(tr);
    }

    function showDetail(res, resultIndex) {
        lastFocusedElement = document.activeElement;
        const caseName = res.case_name || res.case_id;
        const categoryName = res.category_name || '';
        const description = res.case_description || '';
        const expectedAnswer = res.expected_answer || '';
        const evalReason = res.eval_reason || '';
        const testPrompt = res.test_prompt || '';
        const humanOverride = res.human_override;

        modalTitle.textContent = `[${categoryName}] ${caseName}`;

        let htmlContent = '<div class="modal-sections">';

        // Info
        htmlContent += '<div class="modal-section">';
        htmlContent += '<h4>📋 テスト情報</h4>';
        if (description) {
            htmlContent += `<div class="modal-row"><span class="modal-label">テスト内容:</span><span class="modal-value">${escapeHtml(description)}</span></div>`;
        }
        if (expectedAnswer) {
            htmlContent += `<div class="modal-row"><span class="modal-label">想定回答:</span><span class="modal-value">${escapeHtml(expectedAnswer)}</span></div>`;
        }
        htmlContent += `<div class="modal-row"><span class="modal-label">モデル:</span><span class="modal-value">${escapeHtml(res.model)}</span></div>`;
        htmlContent += '</div>';

        // Prompt
        if (testPrompt) {
            htmlContent += '<div class="modal-section">';
            htmlContent += '<div style="display:flex;justify-content:space-between;align-items:center;">';
            htmlContent += `<h4>${ICONS.messageSquare} テストプロンプト</h4>`;
            htmlContent += `<button class="copy-btn" data-copy="prompt" aria-label="プロンプトをコピー">${ICONS.copy} コピー</button>`;
            htmlContent += '</div>';
            htmlContent += `<pre class="modal-prompt" id="modal-prompt-text">${escapeHtml(testPrompt)}</pre>`;
            htmlContent += '</div>';
        }

        // Result
        htmlContent += '<div class="modal-section">';
        htmlContent += `<h4>${ICONS.barChart} 評価結果</h4>`;
        const passedClass = res.passed ? 'pass' : 'fail';
        const passedText = res.passed ? 'PASS' : 'FAIL';
        const passedIcon = res.passed ? ICONS.check : ICONS.x;
        const overrideNote = humanOverride !== null ? ' (手動変更済)' : '';
        htmlContent += `<div class="modal-row"><span class="modal-label">判定:</span><span class="modal-value ${passedClass}">${passedIcon} ${passedText}${overrideNote}</span></div>`;
        if (evalReason) {
            htmlContent += `<div class="modal-row"><span class="modal-label">評価理由:</span><span class="modal-value">${escapeHtml(evalReason)}</span></div>`;
        }
        htmlContent += '</div>';

        // Variants
        if (res.is_variant_test && res.variant_details) {
            htmlContent += '<div class="modal-section">';
            htmlContent += '<h4>📋 バリエーション詳細結果</h4>';
            htmlContent += '<div style="overflow-x:auto;">';
            htmlContent += '<table class="variant-table">';
            htmlContent += '<thead><tr><th>Q#</th><th>判定</th><th>プロンプト</th><th>レスポンス</th><th>期待値/理由</th></tr></thead>';
            htmlContent += '<tbody>';

            res.variant_details.forEach(v => {
                const rowClass = v.status === 'error' ? 'variant-row-error' : (v.passed ? 'variant-row-pass' : 'variant-row-fail');
                const vStatus = v.status === 'error' ? 'ERR' : (v.passed ? ICONS.check : ICONS.x);
                const vPrompt = v.prompt.length > 50 ? v.prompt.substring(0, 50) + '...' : v.prompt;
                const vResponse = v.response.length > 50 ? v.response.substring(0, 50) + '...' : v.response;

                htmlContent += `<tr class="${rowClass}">`;
                htmlContent += `<td>${v.variant_index + 1}</td>`;
                htmlContent += `<td><strong>${vStatus}</strong></td>`;
                htmlContent += `<td title="${escapeHtml(v.prompt)}">${escapeHtml(vPrompt)}</td>`;
                htmlContent += `<td title="${escapeHtml(v.response)}">${escapeHtml(vResponse)}</td>`;
                htmlContent += `<td><small>${escapeHtml(v.expected || '')}<br>${escapeHtml(v.eval_reason || '')}</small></td>`;
                htmlContent += '</tr>';
            });

            htmlContent += '</tbody></table>';
            htmlContent += '</div></div>';
        } else {
            // Response
            htmlContent += '<div class="modal-section">';
            htmlContent += '<div style="display:flex;justify-content:space-between;align-items:center;">';
            htmlContent += `<h4>${ICONS.messageCircle} モデルのレスポンス</h4>`;
            htmlContent += `<button class="copy-btn" data-copy="response" aria-label="レスポンスをコピー">${ICONS.copy} コピー</button>`;
            htmlContent += '</div>';
            htmlContent += `<pre class="modal-response" id="modal-response-text">${escapeHtml(res.full_response || res.reason || '(レスポンスなし)')}</pre>`;
            htmlContent += '</div>';
        }

        // Override
        if (typeof resultIndex === 'number' && currentJobId) {
            htmlContent += '<div class="modal-section modal-actions">';
            htmlContent += `<h4>${ICONS.edit} 手動で判定を変更</h4>`;
            htmlContent += '<div class="override-buttons">';
            htmlContent += `<button class="override-btn pass-btn" data-index="${resultIndex}" data-passed="true" ${res.passed ? 'disabled' : ''}>${ICONS.check} 合格にする</button>`;
            htmlContent += `<button class="override-btn fail-btn" data-index="${resultIndex}" data-passed="false" ${!res.passed ? 'disabled' : ''}>${ICONS.x} 不合格にする</button>`;
            htmlContent += '</div>';
            htmlContent += '</div>';
        }

        htmlContent += '</div>';

        modalContent.innerHTML = htmlContent;

        // Listeners
        modalContent.querySelectorAll('.override-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const index = parseInt(btn.dataset.index);
                const newPassed = btn.dataset.passed === 'true';
                await overrideResult(index, newPassed);
            });
        });

        modalContent.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const target = btn.dataset.copy;
                let text = '';
                if (target === 'prompt') {
                    text = testPrompt;
                } else if (target === 'response') {
                    text = res.full_response || '';
                }

                try {
                    await navigator.clipboard.writeText(text);
                    btn.textContent = '✓ コピー済';
                    btn.classList.add('copied');
                    setTimeout(() => {
                        btn.innerHTML = `${ICONS.copy} コピー`;
                        btn.classList.remove('copied');
                    }, 2000);
                } catch (err) {
                    console.error('Copy failed:', err);
                }
            });
        });

        modalOverlay.classList.remove('hidden');
        // Focus management: move focus to the modal close button or first interactive element
        // setTimeout ensures the DOM is updated and transition starts
        setTimeout(() => {
            if (modalClose) modalClose.focus();
        }, 50);
    }

    function closeModal() {
        modalOverlay.classList.add('hidden');
        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
    }

    function trapFocus(e) {
        const modal = document.querySelector('.modal');
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length === 0) {
            e.preventDefault();
            return;
        }

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) { // Shift + Tab
            if (document.activeElement === firstElement) {
                lastElement.focus();
                e.preventDefault();
            }
        } else { // Tab
            if (document.activeElement === lastElement) {
                firstElement.focus();
                e.preventDefault();
            }
        }
    }

    async function overrideResult(resultIndex, newPassed) {
        if (!currentJobId) return;

        try {
            const res = await fetch(`/api/bm/${currentJobId}/override`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ result_index: resultIndex, new_passed: newPassed })
            });

            const data = await res.json();

            if (data.success) {
                addLog('info', data.message);
                if (allResults[resultIndex]) {
                    allResults[resultIndex].passed = newPassed;
                    allResults[resultIndex].human_override = newPassed;
                }
                updateStats();
                modalOverlay.classList.add('hidden');
                refreshResultsDisplay();
            } else {
                addLog('error', data.error || '変更に失敗しました');
            }
        } catch (err) {
            addLog('error', `エラー: ${err.message}`);
        }
    }

    function updateStats() {
        const total = expectedTotal || (allResults.length + 1);
        // Note: expectedTotal comes from server, if 0 fallback to count.
        // Calculate progress bar width
        let pct = 0;
        if (expectedTotal > 0) {
            pct = Math.min(100, Math.round((allResults.length / expectedTotal) * 100));
        }
        statProgress.textContent = `${allResults.length} / ${expectedTotal || '?'}`;
        globalProgressBar.style.width = `${pct}%`;

        renderHeaderPassRates();
    }

    function refreshResultsDisplay() {
        resultsGrid.innerHTML = '';
        resultsTableBody.innerHTML = '';
        allResults.forEach((r, i) => {
            addResultCard(r, i);
            addResultRow(r, i);
        });
    }

    function renderSummary() {
        const container = document.getElementById('summary-content');

        const byModel = {};
        allResults.forEach(r => {
            if (!byModel[r.model]) byModel[r.model] = [];
            byModel[r.model].push(r);
        });

        const modelNames = Object.keys(byModel);
        const passRates = [];
        const avgTtfts = [];
        const avgE2es = [];

        const meta = currentSuiteMeta || (suiteInfo ? suiteInfo.meta : {}) || {};
        const passCriteria = getPassCriteria(meta);
        const categoryOrder = getCategoryOrder(byModel);

        let html = '';

        if (modelNames.length > 0 && typeof Chart !== 'undefined') {
            html += '<div class="summary-charts">';
            html += '<div class="chart-container chart-container-wide"><h4>カテゴリ別 合格率</h4><canvas id="chart-category-pass" class="chart-canvas"></canvas></div>';
            html += `<div class="chart-container"><h4>${ICONS.barChart} 合格率比較</h4><canvas id="chart-pass-rate" class="chart-canvas"></canvas></div>`;
            html += '<div class="chart-container"><h4>速度比較（平均レイテンシ）</h4><canvas id="chart-latency" class="chart-canvas"></canvas></div>';
            html += '</div>';
        }

        html += '<div class="summary-grid">';

        for (const [model, results] of Object.entries(byModel)) {
            const { passed, valid, rate } = computePassRate(results);
            const ttfts = results.filter(r => r.ttft_ms).map(r => r.ttft_ms);
            const e2es = results.filter(r => r.e2e_ms).map(r => r.e2e_ms);
            const avgTtft = ttfts.length > 0 ? Math.round(ttfts.reduce((a, b) => a + b, 0) / ttfts.length) : '-';
            const avgE2e = e2es.length > 0 ? Math.round(e2es.reduce((a, b) => a + b, 0) / e2es.length) : '-';

            const rateClass = rate >= 70 ? 'good' : rate >= 40 ? '' : 'bad';

            const catStats = computeCategoryStats(results, categoryOrder, passCriteria);
            const categoryPassed = catStats.passedCategories;
            const categoryTotal = catStats.totalCategories;
            const categoryRatioPct = categoryTotal > 0 ? Math.round((categoryPassed / categoryTotal) * 100) : 0;
            const overallPassed = catTotalAndRatioPass(catStats, passCriteria);
            const overallClass = overallPassed ? 'good' : 'bad';

            passRates.push(rate);
            avgTtfts.push(typeof avgTtft === 'number' ? avgTtft : 0);
            avgE2es.push(typeof avgE2e === 'number' ? avgE2e : 0);

            html += `
                <div class="summary-card">
                    <h4>Model</h4>
                    <div class="summary-model-name">${escapeHtml(model)}</div>
                    <div class="summary-stats">
                        <div class="summary-stat">
                            <div class="summary-stat-label">合格率</div>
                            <div class="summary-stat-value ${rateClass}">${rate}%</div>
                        </div>
                        <div class="summary-stat">
                            <div class="summary-stat-label">カテゴリ合格</div>
                            <div class="summary-stat-value ${overallClass}">${categoryPassed}/${categoryTotal} (${categoryRatioPct}%)</div>
                        </div>
                        <div class="summary-stat">
                            <div class="summary-stat-label">総合判定</div>
                            <div class="summary-stat-value ${overallClass}">${overallPassed ? 'PASS' : 'FAIL'}</div>
                        </div>
                        <div class="summary-stat">
                            <div class="summary-stat-label">テスト数</div>
                            <div class="summary-stat-value">${results.length}</div>
                        </div>
                        <div class="summary-stat">
                            <div class="summary-stat-label">平均 TTFT</div>
                            <div class="summary-stat-value">${avgTtft} ms</div>
                        </div>
                        <div class="summary-stat">
                            <div class="summary-stat-label">平均 E2E</div>
                            <div class="summary-stat-value">${avgE2e} ms</div>
                        </div>
                    </div>
                    ${renderCategoryBreakdown(model, catStats, passCriteria)}
                </div>
            `;
        }

        html += '</div>';
        container.innerHTML = html;

        if (modelNames.length > 0 && typeof Chart !== 'undefined') {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            const textColor = isDark ? '#eaeaea' : '#111111';
            const gridColor = isDark ? '#334155' : '#e0e0e0';

            Chart.defaults.color = textColor;
            Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';

            if (chartPassRate) { chartPassRate.destroy(); chartPassRate = null; }
            if (chartLatency) { chartLatency.destroy(); chartLatency = null; }
            if (chartCategoryPass) { chartCategoryPass.destroy(); chartCategoryPass = null; }

            const passRateCtx = document.getElementById('chart-pass-rate');
            if (passRateCtx) {
                chartPassRate = new Chart(passRateCtx, {
                    type: 'bar',
                    data: {
                        labels: modelNames.map(n => n.length > 20 ? n.substring(0, 17) + '...' : n),
                        datasets: [{
                            label: '合格率 (%)',
                            data: passRates,
                            backgroundColor: passRates.map(r => r >= 70 ? 'rgba(34, 197, 94, 0.8)' : r >= 40 ? 'rgba(245, 158, 11, 0.8)' : 'rgba(239, 68, 68, 0.8)'),
                            borderRadius: 4,
                            borderSkipped: false
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: { beginAtZero: true, max: 100, grid: { color: gridColor, borderDash: [2, 4] } },
                            x: { grid: { display: false } }
                        },
                        plugins: { legend: { display: false } }
                    }
                });
            }

            const latencyCtx = document.getElementById('chart-latency');
            if (latencyCtx) {
                chartLatency = new Chart(latencyCtx, {
                    type: 'bar',
                    data: {
                        labels: modelNames.map(n => n.length > 20 ? n.substring(0, 17) + '...' : n),
                        datasets: [
                            {
                                label: 'TTFT (ms)',
                                data: avgTtfts,
                                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                                borderRadius: 4
                            },
                            {
                                label: 'E2E (ms)',
                                data: avgE2es,
                                backgroundColor: 'rgba(168, 85, 247, 0.8)',
                                borderRadius: 4
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: { beginAtZero: true, grid: { color: gridColor, borderDash: [2, 4] } },
                            x: { grid: { display: false } }
                        }
                    }
                });
            }

            const categoryCtx = document.getElementById('chart-category-pass');
            if (categoryCtx) {
                const palette = [
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(14, 165, 233, 0.8)',
                ];

                const labels = categoryOrder.map(c => c.name);
                const datasets = modelNames.map((model, idx) => {
                    const stats = computeCategoryStats(byModel[model] || [], categoryOrder, passCriteria);
                    return {
                        label: model.length > 18 ? model.substring(0, 15) + '...' : model,
                        data: categoryOrder.map(c => {
                            const row = stats.byCategory[c.id];
                            return row && row.valid > 0 ? row.rate : null;
                        }),
                        backgroundColor: palette[idx % palette.length],
                        borderRadius: 4,
                        barPercentage: 0.8
                    };
                });

                chartCategoryPass = new Chart(categoryCtx, {
                    type: 'bar',
                    data: { labels, datasets },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: (labels.length > 8 ? 'y' : 'x'),
                        scales: (labels.length > 8 ? {
                            x: { beginAtZero: true, max: 100, grid: { color: gridColor } },
                            y: { grid: { display: false } }
                        } : {
                            y: { beginAtZero: true, max: 100, grid: { color: gridColor } },
                            x: { grid: { display: false } }
                        })
                    }
                });
            }
        }
    }

    // ... (helper functions remain mostly the same) ...
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function activateTab(tabName) {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        const btn = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
        const content = document.getElementById(`tab-${tabName}`);
        if (btn) btn.classList.add('active');
        if (content) content.classList.add('active');
    }

    function computePassRate(results) {
        const valid = results.filter(r => r.status === 'ok').length;
        const passed = results.filter(r => r.status === 'ok' && r.passed).length;
        const rate = valid > 0 ? Math.round((passed / valid) * 100) : 0;
        return { passed, valid, rate };
    }

    function renderHeaderPassRates() {
        const byModel = {};
        for (const r of allResults) {
            if (!byModel[r.model]) byModel[r.model] = [];
            byModel[r.model].push(r);
        }
        const models = Object.keys(byModel);
        if (models.length <= 1) {
            const only = models[0];
            if (!only) {
                statPassRate.textContent = '?';
                return;
            }
            const { rate } = computePassRate(byModel[only]);
            statPassRate.textContent = `${rate}%`;
            return;
        }

        const rows = models.map(m => {
            const { rate, valid } = computePassRate(byModel[m]);
            const cls = rate >= 70 ? 'good' : rate >= 40 ? '' : 'bad';
            const shortModel = m.length > 18 ? m.substring(0, 15) + '...' : m;
            return `
                <div class="passrate-row">
                    <span class="passrate-model" title="${escapeHtml(m)}">${escapeHtml(shortModel)}</span>
                    <span class="passrate-rate ${cls}">${rate}%</span>
                    <span class="passrate-valid">(${valid})</span>
                </div>
            `;
        }).join('');

        statPassRate.innerHTML = `<div class="passrate-multi">${rows}</div>`;
    }

    function getPassCriteria(meta) {
        const m = meta || {};
        const defaultCat = Number.isFinite(Number(m.category_threshold_default)) ? Number(m.category_threshold_default) : 0.7;
        const ratioThr = Number.isFinite(Number(m.category_pass_ratio_threshold)) ? Number(m.category_pass_ratio_threshold) : 0.7;
        const thresholds = (m.category_thresholds && typeof m.category_thresholds === 'object') ? m.category_thresholds : {};
        return { defaultCategoryThreshold: defaultCat, categoryRatioThreshold: ratioThr, categoryThresholds: thresholds };
    }

    function getCategoryOrder(byModel) {
        const map = new Map();

        if (suiteInfo && Array.isArray(suiteInfo.categories) && suiteInfo.categories.length > 0) {
            const norm = (p) => String(p || '').replace(/\\/g, '/').toLowerCase();
            const suitePathMatches = !currentSuitePath || !suiteInfo.suite_path || (norm(suiteInfo.suite_path) === norm(currentSuitePath));
            if (suitePathMatches) {
                for (const cat of suiteInfo.categories) {
                    if (cat && cat.id) map.set(cat.id, cat.name || cat.id);
                }
            }
        }

        for (const results of Object.values(byModel || {})) {
            for (const r of results) {
                const id = r.category_id || 'unknown';
                const name = r.category_name || id;
                if (!map.has(id)) map.set(id, name);
            }
        }

        return Array.from(map.entries()).map(([id, name]) => ({ id, name }));
    }

    function getCategoryThreshold(categoryId, passCriteria) {
        const thr = passCriteria.categoryThresholds ? passCriteria.categoryThresholds[categoryId] : undefined;
        const n = Number(thr);
        if (Number.isFinite(n)) return n;
        return passCriteria.defaultCategoryThreshold;
    }

    function computeCategoryStats(results, categoryOrder, passCriteria) {
        const byCategory = {};
        for (const c of categoryOrder) {
            byCategory[c.id] = { id: c.id, name: c.name, valid: 0, passed: 0, rate: 0, threshold: getCategoryThreshold(c.id, passCriteria) };
        }

        for (const r of results) {
            const id = r.category_id || 'unknown';
            if (!byCategory[id]) {
                byCategory[id] = { id, name: r.category_name || id, valid: 0, passed: 0, rate: 0, threshold: getCategoryThreshold(id, passCriteria) };
            }
            if (r.status !== 'ok') continue;
            byCategory[id].valid += 1;
            if (r.passed) byCategory[id].passed += 1;
        }

        let totalCategories = 0;
        let passedCategories = 0;
        for (const row of Object.values(byCategory)) {
            if (row.valid <= 0) continue;
            row.rate = Math.round((row.passed / row.valid) * 100);
            totalCategories += 1;
            if (row.rate >= Math.round(row.threshold * 100)) passedCategories += 1;
        }

        return { byCategory, totalCategories, passedCategories };
    }

    function catTotalAndRatioPass(catStats, passCriteria) {
        if (!catStats || catStats.totalCategories <= 0) return false;
        const ratio = catStats.passedCategories / catStats.totalCategories;
        return ratio >= passCriteria.categoryRatioThreshold;
    }

    function renderCategoryBreakdown(model, catStats, passCriteria) {
        const rows = Object.values(catStats.byCategory)
            .filter(r => r.valid > 0)
            .sort((a, b) => b.rate - a.rate)
            .map(r => {
                const thrPct = Math.round(r.threshold * 100);
                const pass = r.rate >= thrPct;
                return `
                    <tr class="${pass ? 'pass' : 'fail'}">
                        <td>${escapeHtml(r.name)}</td>
                        <td>${r.passed}/${r.valid}</td>
                        <td>${r.rate}%</td>
                        <td>${thrPct}%</td>
                        <td>${pass ? 'PASS' : 'FAIL'}</td>
                    </tr>
                `;
            })
            .join('');

        const ratioPct = catStats.totalCategories > 0 ? Math.round((catStats.passedCategories / catStats.totalCategories) * 100) : 0;
        const header = `カテゴリ内訳（総合PASS基準: ${Math.round(passCriteria.categoryRatioThreshold * 100)}%）`;

        return `
            <details class="summary-details">
                <summary>${ICONS.chevronRight} ${header} / ${catStats.passedCategories}/${catStats.totalCategories} (${ratioPct}%)</summary>
                <div class="summary-table-wrap">
                    <table class="summary-table" aria-label="${escapeHtml(model)} categories">
                        <thead>
                            <tr>
                                <th>カテゴリ</th>
                                <th>合格/有効</th>
                                <th>合格率</th>
                                <th>閾値</th>
                                <th>判定</th>
                            </tr>
                        </thead>
                        <tbody>${rows || '<tr><td colspan="5">（結果なし）</td></tr>'}</tbody>
                    </table>
                </div>
            </details>
        `;
    }

    // Stop button
    stopBtn.addEventListener('click', async () => {
        if (currentJobId) {
            try {
                await fetch(`/api/bm/${currentJobId}/cancel`, { method: 'POST' });
            } catch { }
        }
        stopPolling();
        addLog('warn', 'キャンセルしました（サーバー側は停止処理中の可能性があります）');
        renderSummary();
        activateTab('summary');
        resetUI();
    });
});
