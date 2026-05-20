/**
 * Cuber Progress — Frontend Application
 * Handles: navigation, data fetching, filtering, toggling, Chart.js rendering
 */

// ── State ─────────────────────────────────────────────
let currentView = 'dashboard';
let filters = { category: 'all', status: 'all', sub_group: 'all' };
let currentPage = 1;
let totalPages = 1;
let searchTimeout = null;
let monthlyChart = null;

// ── Loader ────────────────────────────────────────────
function showLoader(text = 'Loading...') {
    const loader = document.getElementById('loader');
    loader.querySelector('.loader-text').textContent = text;
    loader.classList.remove('hidden');
}
function hideLoader() {
    document.getElementById('loader').classList.add('hidden');
}

// ── View Switching ────────────────────────────────────
function switchView(view) {
    currentView = view;
    document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
    document.getElementById(`view-${view}`).classList.add('active');
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById(`nav-${view}`).classList.add('active');

    if (view === 'dashboard') loadDashboard();
    else loadCases();
}

// ── Dashboard ─────────────────────────────────────────
async function loadDashboard() {
    showLoader('Memuat statistik...');
    try {
        const [statsRes, monthlyRes] = await Promise.all([
            fetch('/api/stats'), fetch('/api/stats/monthly')
        ]);
        const stats = await statsRes.json();
        const monthly = await monthlyRes.json();

        // Summary cards
        document.getElementById('stat-total-pct').textContent = stats.percentage + '%';
        document.getElementById('stat-total-count').textContent = stats.memorized;
        document.getElementById('stat-total-all').textContent = stats.total;
        document.getElementById('bar-total').style.width = stats.percentage + '%';

        const catMap = { f2l: 'F2L', zbls: 'ZBLS', zbll: 'ZBLL' };
        for (const [key, cat] of Object.entries(catMap)) {
            const c = stats.categories[cat] || { total: 0, memorized: 0, percentage: 0 };
            document.getElementById(`stat-${key}-pct`).textContent = c.percentage + '%';
            document.getElementById(`stat-${key}-count`).textContent = c.memorized;
            document.getElementById(`stat-${key}-all`).textContent = c.total;
            document.getElementById(`bar-${key}`).style.width = c.percentage + '%';
        }

        // Sidebar quick stats
        document.getElementById('qs-total').textContent = stats.total;
        document.getElementById('qs-memorized').textContent = stats.memorized;
        document.getElementById('qs-percent').textContent = stats.percentage + '%';

        // Sub-group details
        for (const [key, cat] of Object.entries(catMap)) {
            const container = document.getElementById(`sg-${key}`);
            const groups = stats.sub_groups[cat] || [];
            container.innerHTML = groups.map(g => `
                <div>
                    <div class="flex justify-between text-slate-600 mb-1">
                        <span class="truncate mr-2">${g.name}</span>
                        <span class="font-medium text-slate-800 whitespace-nowrap">${g.memorized}/${g.total}</span>
                    </div>
                    <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div class="progress-fill h-full rounded-full ${key === 'f2l' ? 'bg-emerald-500' : key === 'zbls' ? 'bg-violet-500' : 'bg-amber-500'}" style="width:${g.percentage}%"></div>
                    </div>
                </div>
            `).join('');
        }

        // Monthly chart
        renderChart(monthly);
    } catch (e) {
        console.error('Dashboard error:', e);
    } finally {
        hideLoader();
    }
}

function renderChart(data) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    if (monthlyChart) monthlyChart.destroy();

    const months = data.total.map(d => d.month);
    const emptyMonths = months.length === 0;

    // If no data yet, show placeholder
    const labels = emptyMonths ? ['Start'] : months;
    const totalData = emptyMonths ? [0] : data.total.map(d => d.count);

    const datasets = [{
        label: 'Total',
        data: totalData,
        borderColor: '#1e40af',
        backgroundColor: 'rgba(30,64,175,0.08)',
        fill: true,
        tension: 0.4,
        borderWidth: 2.5,
        pointRadius: 4,
        pointBackgroundColor: '#1e40af',
    }];

    const catColors = { F2L: '#10b981', ZBLS: '#8b5cf6', ZBLL: '#f59e0b' };
    for (const [cat, color] of Object.entries(catColors)) {
        const catData = data.by_category[cat] || [];
        if (catData.length > 0) {
            datasets.push({
                label: cat,
                data: labels.map(m => {
                    const found = catData.find(d => d.month === m);
                    return found ? found.count : 0;
                }),
                borderColor: color,
                backgroundColor: 'transparent',
                borderWidth: 2,
                tension: 0.4,
                pointRadius: 3,
                borderDash: [5, 3],
            });
        }
    }

    monthlyChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { usePointStyle: true, padding: 16 } },
            },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 5 }, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } },
            },
        },
    });
}

// ── Cases / Tracker ───────────────────────────────────
async function loadCases() {
    showLoader('Memuat algoritma...');
    try {
        const params = new URLSearchParams();
        if (filters.category !== 'all') params.set('category', filters.category);
        if (filters.status !== 'all') params.set('status', filters.status);
        if (filters.sub_group !== 'all') params.set('sub_group', filters.sub_group);
        const search = document.getElementById('searchInput')?.value;
        if (search) params.set('search', search);
        params.set('page', currentPage);
        params.set('per_page', 30);

        const res = await fetch(`/api/cases?${params}`);
        const data = await res.json();
        totalPages = data.pages;

        document.getElementById('results-info').textContent =
            `Menampilkan ${data.cases.length} dari ${data.total} cases`;
        document.getElementById('page-info').textContent =
            data.pages > 0 ? `${data.page} / ${data.pages}` : '';
        document.getElementById('btn-prev').disabled = data.page <= 1;
        document.getElementById('btn-next').disabled = data.page >= data.pages;

        renderCases(data.cases);
        loadSubGroupFilter();
    } catch (e) {
        console.error('Cases error:', e);
        document.getElementById('cases-grid').innerHTML =
            '<p class="text-red-500 col-span-full text-center py-8">Gagal memuat data</p>';
    } finally {
        hideLoader();
    }
}

function renderCases(cases) {
    const grid = document.getElementById('cases-grid');
    if (cases.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full text-center py-16 text-slate-400">
                <svg class="w-12 h-12 mx-auto mb-3 text-slate-300" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/></svg>
                <p class="font-medium">Tidak ada case ditemukan</p>
                <p class="text-sm mt-1">Coba ubah filter atau kata kunci pencarian</p>
            </div>`;
        return;
    }

    grid.innerHTML = cases.map(c => {
        const selectedAlg = c.algorithms.find(a => a.is_selected) || c.algorithms[0];
        const hasMultiple = c.algorithms.length > 1;
        const catBadge = c.category === 'F2L' ? 'bg-emerald-50 text-emerald-700'
            : c.category === 'ZBLS' ? 'bg-violet-50 text-violet-700' : 'bg-amber-50 text-amber-700';

        return `
        <div class="case-card bg-white border border-slate-200 rounded-xl p-5 shadow-sm" id="case-${c.id}">
            <div class="flex gap-4">
                <div class="flex-shrink-0">
                    <img src="${c.image_url}" alt="${c.case_name}" class="w-20 h-20 object-contain rounded-lg bg-slate-50 border border-slate-100 p-1"
                         onerror="this.src='/static/images/placeholder.svg'">
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-xs px-2 py-0.5 rounded-full font-medium ${catBadge}">${c.category}</span>
                        ${c.status ? '<span class="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-medium">Hafal</span>' : ''}
                    </div>
                    <h4 class="font-semibold text-slate-800 text-sm truncate">${c.case_name}</h4>
                    <p class="text-xs text-slate-400 truncate">${c.sub_group || ''}</p>
                </div>
            </div>

            <!-- Algorithm display -->
            <div class="mt-3">
                ${hasMultiple ? `
                <div class="flex items-center gap-1 mb-2">
                    <span class="text-xs text-slate-400">Pilih algoritma:</span>
                    <select onchange="selectAlgorithm(${c.id}, this.value)" class="text-xs border border-slate-200 rounded px-2 py-1 bg-white">
                        ${c.algorithms.map(a => `<option value="${a.id}" ${a.is_selected ? 'selected' : ''}>${a.label}</option>`).join('')}
                    </select>
                </div>` : ''}
                <div class="font-mono text-sm bg-slate-50 text-slate-800 p-3 rounded-lg border border-slate-100 break-all" id="alg-display-${c.id}">
                    ${selectedAlg ? selectedAlg.notation : '-'}
                </div>
            </div>

            <!-- Toggle buttons -->
            <div class="flex gap-2 mt-4">
                <button onclick="toggleStatus(${c.id})"
                    class="flex-1 px-4 py-2 rounded-lg text-sm font-medium text-center transition-all ${
                        c.status
                            ? 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
                            : 'bg-white text-slate-600 border border-slate-200 hover:bg-red-50 hover:text-red-600 hover:border-red-200'
                    }">
                    ${c.status ? 'Tandai Belum' : 'Belum Hafal'}
                </button>
                <button onclick="toggleStatus(${c.id})"
                    class="flex-1 px-4 py-2 rounded-lg text-sm font-medium text-center transition-all ${
                        c.status
                            ? 'bg-blue-600 text-white shadow-sm shadow-blue-200'
                            : 'bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-600 hover:text-white'
                    }">
                    ${c.status ? 'Sudah Hafal ✓' : 'Sudah Hafal'}
                </button>
            </div>
            ${c.date_learned ? `<p class="text-xs text-slate-400 mt-2 text-right">Dihafal: ${new Date(c.date_learned).toLocaleDateString('id-ID')}</p>` : ''}
        </div>`;
    }).join('');
}

// ── Toggle Status ─────────────────────────────────────
async function toggleStatus(id) {
    try {
        const res = await fetch(`/api/cases/${id}/toggle`, { method: 'PUT' });
        if (!res.ok) throw new Error('Toggle failed');
        const updated = await res.json();

        // Re-render just this card
        const card = document.getElementById(`case-${id}`);
        if (card) {
            const temp = document.createElement('div');
            temp.innerHTML = renderSingleCase(updated);
            card.replaceWith(temp.firstElementChild);
        }

        // Update sidebar stats
        loadSidebarStats();
    } catch (e) {
        console.error('Toggle error:', e);
    }
}

function renderSingleCase(c) {
    const selectedAlg = c.algorithms.find(a => a.is_selected) || c.algorithms[0];
    const hasMultiple = c.algorithms.length > 1;
    const catBadge = c.category === 'F2L' ? 'bg-emerald-50 text-emerald-700'
        : c.category === 'ZBLS' ? 'bg-violet-50 text-violet-700' : 'bg-amber-50 text-amber-700';

    return `
    <div class="case-card bg-white border border-slate-200 rounded-xl p-5 shadow-sm" id="case-${c.id}">
        <div class="flex gap-4">
            <div class="flex-shrink-0">
                <img src="${c.image_url}" alt="${c.case_name}" class="w-20 h-20 object-contain rounded-lg bg-slate-50 border border-slate-100 p-1"
                     onerror="this.src='/static/images/placeholder.svg'">
            </div>
            <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                    <span class="text-xs px-2 py-0.5 rounded-full font-medium ${catBadge}">${c.category}</span>
                    ${c.status ? '<span class="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-medium">Hafal</span>' : ''}
                </div>
                <h4 class="font-semibold text-slate-800 text-sm truncate">${c.case_name}</h4>
                <p class="text-xs text-slate-400 truncate">${c.sub_group || ''}</p>
            </div>
        </div>
        <div class="mt-3">
            ${hasMultiple ? `
            <div class="flex items-center gap-1 mb-2">
                <span class="text-xs text-slate-400">Pilih algoritma:</span>
                <select onchange="selectAlgorithm(${c.id}, this.value)" class="text-xs border border-slate-200 rounded px-2 py-1 bg-white">
                    ${c.algorithms.map(a => `<option value="${a.id}" ${a.is_selected ? 'selected' : ''}>${a.label}</option>`).join('')}
                </select>
            </div>` : ''}
            <div class="font-mono text-sm bg-slate-50 text-slate-800 p-3 rounded-lg border border-slate-100 break-all" id="alg-display-${c.id}">
                ${selectedAlg ? selectedAlg.notation : '-'}
            </div>
        </div>
        <div class="flex gap-2 mt-4">
            <button onclick="toggleStatus(${c.id})"
                class="flex-1 px-4 py-2 rounded-lg text-sm font-medium text-center transition-all ${
                    c.status
                        ? 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
                        : 'bg-white text-slate-600 border border-slate-200 hover:bg-red-50 hover:text-red-600 hover:border-red-200'
                }">
                ${c.status ? 'Tandai Belum' : 'Belum Hafal'}
            </button>
            <button onclick="toggleStatus(${c.id})"
                class="flex-1 px-4 py-2 rounded-lg text-sm font-medium text-center transition-all ${
                    c.status
                        ? 'bg-blue-600 text-white shadow-sm shadow-blue-200'
                        : 'bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-600 hover:text-white'
                }">
                ${c.status ? 'Sudah Hafal ✓' : 'Sudah Hafal'}
            </button>
        </div>
        ${c.date_learned ? `<p class="text-xs text-slate-400 mt-2 text-right">Dihafal: ${new Date(c.date_learned).toLocaleDateString('id-ID')}</p>` : ''}
    </div>`;
}

// ── Select Algorithm ──────────────────────────────────
async function selectAlgorithm(caseId, algId) {
    try {
        const res = await fetch(`/api/cases/${caseId}/select-algorithm/${algId}`, { method: 'PUT' });
        if (!res.ok) throw new Error('Select failed');
        const updated = await res.json();
        const selectedAlg = updated.algorithms.find(a => a.is_selected) || updated.algorithms[0];
        const display = document.getElementById(`alg-display-${caseId}`);
        if (display) display.textContent = selectedAlg ? selectedAlg.notation : '-';
    } catch (e) {
        console.error('Select algorithm error:', e);
    }
}

// ── Filters ───────────────────────────────────────────
function setFilter(type, value) {
    filters[type] = value;
    currentPage = 1;

    // Update tab visuals
    if (type === 'category' || type === 'status') {
        document.querySelectorAll(`.filter-tab[data-group="${type}"]`).forEach(btn => {
            btn.classList.remove('active');
        });
        // Find the clicked button by matching its onclick value
        document.querySelectorAll(`.filter-tab[data-group="${type}"]`).forEach(btn => {
            const onclick = btn.getAttribute('onclick');
            if (onclick && onclick.includes(`'${value}'`)) {
                btn.classList.add('active');
            }
        });
    }

    if (type === 'category') {
        // Reset sub_group filter when category changes
        filters.sub_group = 'all';
        document.getElementById('subGroupFilter').value = 'all';
        loadSubGroupFilter();
    }

    loadCases();
}

async function loadSubGroupFilter() {
    try {
        const params = filters.category !== 'all' ? `?category=${filters.category}` : '';
        const res = await fetch(`/api/sub-groups${params}`);
        const data = await res.json();
        const select = document.getElementById('subGroupFilter');
        const current = select.value;
        select.innerHTML = '<option value="all">Semua Sub-Group</option>';
        for (const [cat, groups] of Object.entries(data)) {
            for (const g of groups) {
                const opt = document.createElement('option');
                opt.value = g;
                opt.textContent = `${cat}: ${g}`;
                if (g === current) opt.selected = true;
                select.appendChild(opt);
            }
        }
    } catch (e) { console.error(e); }
}

// ── Pagination ────────────────────────────────────────
function prevPage() { if (currentPage > 1) { currentPage--; loadCases(); } }
function nextPage() { if (currentPage < totalPages) { currentPage++; loadCases(); } }

// ── Sidebar Stats (lightweight refresh) ───────────────
async function loadSidebarStats() {
    try {
        const res = await fetch('/api/stats');
        const stats = await res.json();
        document.getElementById('qs-total').textContent = stats.total;
        document.getElementById('qs-memorized').textContent = stats.memorized;
        document.getElementById('qs-percent').textContent = stats.percentage + '%';
    } catch (e) { /* silent */ }
}

// ── Search debounce ───────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentPage = 1;
                loadCases();
            }, 400);
        });
    }

    // Initial load
    loadDashboard();
});
