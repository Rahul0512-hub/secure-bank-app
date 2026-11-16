from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Person B - Frontend Dashboard"])

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SecureBank — Analytics, Vector Search & Fraud Center</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-6">
  <div class="max-w-7xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex flex-wrap justify-between items-center border-b border-slate-800 pb-4 gap-4">
      <div>
        <div class="flex items-center gap-3">
          <h1 class="text-3xl font-bold text-white tracking-tight">SecureBank Intelligence Center</h1>
          <span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-900/60 text-blue-300 border border-blue-700">v1.0</span>
        </div>
        <p class="text-slate-400 text-sm mt-1">MongoDB Audit & Aggregation • pgvector Semantic Search • Real-Time Fraud Engine</p>
      </div>

      <!-- Live Health Status Indicators & Docs Link -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
          <span class="text-slate-400">PostgreSQL:</span>
          <span id="pgStatus" class="font-medium text-slate-400">Checking...</span>
        </div>
        <div class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
          <span class="text-slate-400">MongoDB:</span>
          <span id="mongoStatus" class="font-medium text-slate-400">Checking...</span>
        </div>
        <a href="/docs" target="_blank" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 font-medium">
          API Docs &rarr;
        </a>
      </div>
    </div>

    <!-- Interactive Simulation Controls -->
    <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3">
      <div class="text-sm">
        <span class="font-semibold text-slate-200">Interactive Simulation:</span>
        <span class="text-slate-400 ml-2">Trigger test transactions, high-value transfers, and security anomalies</span>
      </div>
      <div class="flex flex-wrap gap-2">
        <button onclick="simulateTx(1450, 'Food & Dining', 'Cafe Coffee Day Indiranagar')" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs sm:text-sm px-3.5 py-2 rounded-lg font-medium transition shadow">
          + Normal Spend (₹1,450)
        </button>
        <button onclick="simulateTx(85000, 'International Wire', 'Offshore Crypto Exchange Transfer')" class="bg-rose-600 hover:bg-rose-500 text-white text-xs sm:text-sm px-3.5 py-2 rounded-lg font-medium transition shadow">
          + Trigger Fraud Alert (₹85,000)
        </button>
        <button onclick="simulateFailedLogin()" class="bg-amber-600 hover:bg-amber-500 text-white text-xs sm:text-sm px-3.5 py-2 rounded-lg font-medium transition shadow">
          + Simulate Failed Login
        </button>
      </div>
    </div>

    <!-- Alert / Toast Banner -->
    <div id="toastBanner" class="hidden p-3.5 rounded-lg border text-sm transition"></div>

    <!-- 1. Smart Semantic Search (pgvector) -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div class="flex justify-between items-center mb-2">
        <h2 class="text-lg font-semibold text-blue-400">1. Smart Semantic Search (PostgreSQL pgvector)</h2>
        <span class="text-xs text-slate-500">HNSW Vector Index (Cosine &lt;=&gt;)</span>
      </div>
      <form onsubmit="runSearch(event)" class="flex gap-3">
        <input id="searchInput" type="text" placeholder="Search by meaning: e.g. 'morning coffee', 'airport cab ride', 'electricity bill', or 'stolen card FAQ'..."
          class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500" />
        <button type="submit" class="bg-blue-600 hover:bg-blue-500 px-6 py-2.5 rounded-lg font-semibold text-sm transition">Vector Search</button>
      </form>
      <div id="searchResults" class="mt-4 space-y-2">
        <p class="text-slate-500 text-sm">Type a search query above and press "Vector Search" to test pgvector semantic matching.</p>
      </div>
    </div>

    <!-- 2. Charts & 3. Real-Time Fraud Alerts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Spending Analytics Chart -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
        <div>
          <h2 class="text-lg font-semibold text-emerald-400 mb-1">2. Spending Analytics</h2>
          <p class="text-xs text-slate-400 mb-4">MongoDB Aggregation Pipeline (`$group`, `$sum`, `$sort`)</p>
        </div>
        <div class="relative min-h-[220px]">
          <canvas id="spendingChart" height="200"></canvas>
        </div>
      </div>

      <!-- Real-Time Fraud Alerts Panel -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col">
        <div>
          <h2 class="text-lg font-semibold text-rose-400 mb-1">3. Real-Time Fraud Alerts Panel</h2>
          <p class="text-xs text-slate-400 mb-4">Indexed Collection: `fraud_alerts`</p>
        </div>
        <div id="fraudList" class="space-y-3 max-h-72 overflow-y-auto pr-1 flex-1">
          <p class="text-slate-500 text-sm">Loading alerts...</p>
        </div>
      </div>
    </div>

    <!-- Recent Login Events (`login_events`) -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 class="text-lg font-semibold text-amber-400 mb-1">4. Security Login Audit Trail</h2>
      <p class="text-xs text-slate-400 mb-3">Audited Events Collection: `login_events` (Triggers brute-force alerts on 3+ consecutive failures)</p>
      <div id="loginList" class="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
        <p class="text-slate-500 text-sm col-span-3">Loading login trail...</p>
      </div>
    </div>
  </div>

  <script>
    let chartInstance = null;

    function showToast(message, type = 'info') {
      const banner = document.getElementById('toastBanner');
      banner.className = 'p-3.5 rounded-lg border text-sm transition';
      if (type === 'success') {
        banner.className += ' bg-emerald-950/60 border-emerald-700 text-emerald-200';
      } else if (type === 'error') {
        banner.className += ' bg-rose-950/60 border-rose-700 text-rose-200';
      } else if (type === 'warning') {
        banner.className += ' bg-amber-950/60 border-amber-700 text-amber-200';
      } else {
        banner.className += ' bg-blue-950/60 border-blue-700 text-blue-200';
      }
      banner.textContent = message;
      banner.classList.remove('hidden');
      setTimeout(() => { banner.classList.add('hidden'); }, 6000);
    }

    async function checkHealth() {
      try {
        const pgRes = await fetch('/health/postgres');
        const pgData = await pgRes.json();
        const pgEl = document.getElementById('pgStatus');
        if (pgData.status === 'healthy') {
          pgEl.textContent = '● Online';
          pgEl.className = 'font-semibold text-emerald-400';
        } else {
          pgEl.textContent = '○ Offline';
          pgEl.className = 'font-semibold text-amber-400';
        }
      } catch {
        const pgEl = document.getElementById('pgStatus');
        pgEl.textContent = '○ Disconnected';
        pgEl.className = 'font-semibold text-rose-400';
      }

      try {
        const mRes = await fetch('/health/mongodb');
        const mData = await mRes.json();
        const mEl = document.getElementById('mongoStatus');
        if (mData.status === 'healthy') {
          mEl.textContent = '● Online';
          mEl.className = 'font-semibold text-emerald-400';
        } else {
          mEl.textContent = '○ Offline';
          mEl.className = 'font-semibold text-amber-400';
        }
      } catch {
        const mEl = document.getElementById('mongoStatus');
        mEl.textContent = '○ Disconnected';
        mEl.className = 'font-semibold text-rose-400';
      }
    }

    async function loadDashboard() {
      await checkHealth();

      try {
        const res = await fetch('/api/person-b/analytics/spending');
        const data = await res.json();

        const spending = (data && Array.isArray(data.spendingByCategory)) ? data.spendingByCategory : [];
        const labels = spending.map(i => i.category);
        const values = spending.map(i => i.totalSpent);

        // Render Chart
        const ctx = document.getElementById('spendingChart').getContext('2d');
        if (chartInstance) chartInstance.destroy();
        chartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels.length ? labels : ['No Transactions Yet'],
            datasets: [{
              label: 'Total Volume (INR ₹)',
              data: values.length ? values : [0],
              backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6']
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#cbd5e1' } } },
            scales: {
              x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
              y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } }
            }
          }
        });

        // Render Fraud Alerts
        const fraudContainer = document.getElementById('fraudList');
        const alerts = (data && Array.isArray(data.fraudAlerts)) ? data.fraudAlerts : [];
        if (alerts.length === 0) {
          fraudContainer.innerHTML = '<p class="text-slate-500 text-sm">No active fraud alerts. Click "+ Trigger Fraud Alert" above to test real-time detection.</p>';
        } else {
          fraudContainer.innerHTML = alerts.map(a => `
            <div class="p-3 rounded-lg bg-rose-950/40 border border-rose-800/80 flex justify-between items-start gap-3">
              <div>
                <span class="text-xs font-bold px-2 py-0.5 rounded bg-rose-600 text-white">${a.severity}</span>
                <span class="ml-2 font-semibold text-rose-200">${a.category || 'Alert'} — ₹${(a.amount || 0).toLocaleString()}</span>
                <p class="text-xs text-slate-300 mt-1">${a.reason || 'Flagged by rules engine'}</p>
              </div>
              <span class="text-xs text-slate-400 font-mono">${a.status || 'OPEN'}</span>
            </div>
          `).join('');
        }

        // Render Login Events
        const loginContainer = document.getElementById('loginList');
        const logins = (data && Array.isArray(data.loginEvents)) ? data.loginEvents : [];
        if (logins.length === 0) {
          loginContainer.innerHTML = '<p class="text-slate-500 text-sm col-span-3">No login events recorded yet. Click "+ Simulate Failed Login" to test.</p>';
        } else {
          loginContainer.innerHTML = logins.map(l => `
            <div class="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <p class="font-medium text-slate-200 truncate">${l.email || 'user'}</p>
              <p class="text-xs mt-1 ${l.status === 'FAILED' ? 'text-rose-400 font-bold' : 'text-emerald-400'}">
                Status: ${l.status} • IP: ${l.ip_address || '127.0.0.1'}
              </p>
            </div>
          `).join('');
        }

        if (data && data.message) {
          showToast(data.message, 'warning');
        }
      } catch (err) {
        console.error("Dashboard load failed:", err);
        showToast("Notice: MongoDB is currently offline or unreachable. Live analytics will populate once MongoDB is running.", 'warning');
      }
    }

    async function simulateTx(amount, category, description) {
      try {
        const res = await fetch('/api/person-b/fraud/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 1, amount, category, description })
        });
        const data = await res.json();
        if (res.ok) {
          if (data.fraud_triggered) {
            showToast(`⚠️ Fraud Alert Generated: ${data.reason}`, 'warning');
          } else {
            showToast(`✓ Transaction of ₹${amount.toLocaleString()} processed successfully.`, 'success');
          }
        } else {
          showToast(`Simulation notice: ${data.detail || 'Service unavailable'}`, 'error');
        }
      } catch (err) {
        showToast(`Simulation network error: ${err.message}`, 'error');
      }
      loadDashboard();
    }

    async function simulateFailedLogin() {
      try {
        const res = await fetch('/api/person-b/login-events', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 1, email: 'customer@securebank.com', ip_address: '192.168.1.99', status: 'FAILED' })
        });
        const data = await res.json();
        if (res.ok) {
          showToast('Failed login event logged to MongoDB security audit trail.', 'info');
        } else {
          showToast(`Login log notice: ${data.detail || 'Service unavailable'}`, 'error');
        }
      } catch (err) {
        showToast(`Failed login network error: ${err.message}`, 'error');
      }
      loadDashboard();
    }

    async function runSearch(e) {
      e.preventDefault();
      const q = document.getElementById('searchInput').value.trim() || 'coffee';
      const box = document.getElementById('searchResults');
      box.innerHTML = '<p class="text-blue-400 text-sm">Searching vector embeddings...</p>';

      try {
        const res = await fetch('/api/person-b/semantic-search?q=' + encodeURIComponent(q));
        const data = await res.json();

        if (!res.ok) {
          box.innerHTML = `<div class="p-3 bg-amber-950/40 border border-amber-800 rounded-lg text-amber-300 text-sm">Semantic search notice: ${data.detail || 'PostgreSQL pgvector service is not reachable.'}</div>`;
          return;
        }

        const results = (data && Array.isArray(data.results)) ? data.results : [];
        if (results.length === 0) {
          box.innerHTML = '<p class="text-slate-400 text-sm">No matches found for this query.</p>';
          return;
        }

        box.innerHTML = results.map(r => `
          <div class="p-3 bg-slate-950 border border-slate-800 rounded-lg flex justify-between items-center gap-4">
            <div>
              <span class="text-xs font-bold px-2 py-0.5 rounded ${r.item_type === 'FAQ' ? 'bg-purple-700' : 'bg-blue-700'}">${r.item_type}</span>
              <span class="ml-2 font-semibold text-white">${r.title}</span>
              <span class="text-xs text-slate-400 ml-2">(${r.category})</span>
              <p class="text-xs text-slate-300 mt-1">${r.description}</p>
            </div>
            <div class="text-right whitespace-nowrap">
              ${r.amount ? `<p class="font-bold text-emerald-400">₹${r.amount.toLocaleString()}</p>` : ''}
              <p class="text-xs text-blue-400 font-mono">Similarity: ${(r.similarity * 100).toFixed(1)}%</p>
            </div>
          </div>
        `).join('');
      } catch (err) {
        box.innerHTML = `<div class="p-3 bg-rose-950/40 border border-rose-800 rounded-lg text-rose-300 text-sm">Search error: ${err.message}</div>`;
      }
    }

    loadDashboard();
  </script>
</body>
</html>
"""

@router.get("/dashboard", response_class=HTMLResponse)
def get_person_b_dashboard():
    return DASHBOARD_HTML
