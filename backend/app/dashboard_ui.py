from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Person B - Frontend Dashboard"])

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>SecureBank — Analytics, Vector Search & Fraud Center</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-6">
  <div class="max-w-7xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex flex-wrap justify-between items-center border-b border-slate-800 pb-4">
      <div>
        <h1 class="text-3xl font-bold text-white">SecureBank Intelligence & Fraud Center</h1>
        <p class="text-slate-400 text-sm">Person B Module: MongoDB Audit & Aggregation • pgvector Semantic Search • Real-Time Fraud Engine</p>
      </div>
      <div class="flex gap-2 mt-3 sm:mt-0">
        <button onclick="simulateTx(1450, 'Food & Dining', 'Cafe Coffee Day Indiranagar')" class="bg-emerald-600 hover:bg-emerald-500 text-white text-sm px-3 py-2 rounded-lg font-medium">
          + Normal Spend (₹1,450)
        </button>
        <button onclick="simulateTx(85000, 'International Wire', 'Offshore Crypto Exchange Transfer')" class="bg-rose-600 hover:bg-rose-500 text-white text-sm px-3 py-2 rounded-lg font-medium">
          + Trigger Fraud Alert (₹85,000)
        </button>
        <button onclick="simulateFailedLogin()" class="bg-amber-600 hover:bg-amber-500 text-white text-sm px-3 py-2 rounded-lg font-medium">
          + Simulate Failed Login
        </button>
      </div>
    </div>

    <!-- 1. Smart Semantic Search (pgvector) -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 class="text-lg font-semibold text-blue-400 mb-2">1. Smart Semantic Search (PostgreSQL pgvector)</h2>
      <form onsubmit="runSearch(event)" class="flex gap-3">
        <input id="searchInput" type="text" placeholder="Search by meaning: e.g. 'morning coffee', 'airport cab ride', 'electricity bill', or 'stolen card FAQ'..."
          class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-100 focus:outline-none focus:border-blue-500" />
        <button type="submit" class="bg-blue-600 hover:bg-blue-500 px-6 py-2.5 rounded-lg font-semibold">Vector Search</button>
      </form>
      <div id="searchResults" class="mt-4 space-y-2"></div>
    </div>

    <!-- 2. Charts & 3. Real-Time Fraud Alerts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Spending Analytics Chart -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <h2 class="text-lg font-semibold text-emerald-400 mb-4">2. Spending Analytics (MongoDB Aggregation Pipeline)</h2>
        <canvas id="spendingChart" height="180"></canvas>
      </div>

      <!-- Real-Time Fraud Alerts Panel -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <h2 class="text-lg font-semibold text-rose-400 mb-4">3. Real-Time Fraud Alerts Panel (`fraud_alerts`)</h2>
        <div id="fraudList" class="space-y-3 max-h-72 overflow-y-auto pr-1"></div>
      </div>
    </div>

    <!-- Recent Login Events (`login_events`) -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 class="text-lg font-semibold text-amber-400 mb-3">4. Security Login Audit Trail (`login_events`)</h2>
      <div id="loginList" class="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm"></div>
    </div>
  </div>

  <script>
    let chartInstance = null;

    async function loadDashboard() {
      const res = await fetch('/api/person-b/analytics/spending');
      const data = await res.json();

      // Render Chart
      const labels = data.spendingByCategory.map(i => i.category);
      const values = data.spendingByCategory.map(i => i.totalSpent);
      const ctx = document.getElementById('spendingChart').getContext('2d');
      if (chartInstance) chartInstance.destroy();
      chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels.length ? labels : ['No Transactions Yet'],
          datasets: [{
            label: 'Total Volume (INR ₹)',
            data: values.length ? values : [0],
            backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
          }]
        },
        options: { plugins: { legend: { labels: { color: '#cbd5e1' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' } } } }
      });

      // Render Fraud Alerts
      const fraudContainer = document.getElementById('fraudList');
      if (!data.fraudAlerts || data.fraudAlerts.length === 0) {
        fraudContainer.innerHTML = '<p class="text-slate-500 text-sm">No active fraud alerts. Click "+ Trigger Fraud Alert" above to test.</p>';
      } else {
        fraudContainer.innerHTML = data.fraudAlerts.map(a => `
          <div class="p-3 rounded-lg bg-rose-950/50 border border-rose-800 flex justify-between items-start">
            <div>
              <span class="text-xs font-bold px-2 py-0.5 rounded bg-rose-600 text-white">${a.severity}</span>
              <span class="ml-2 font-semibold text-rose-200">${a.category} — ₹${a.amount.toLocaleString()}</span>
              <p class="text-xs text-slate-300 mt-1">${a.reason}</p>
            </div>
            <span class="text-xs text-slate-400">${a.status}</span>
          </div>
        `).join('');
      }

      // Render Login Events
      const loginContainer = document.getElementById('loginList');
      if (!data.loginEvents || data.loginEvents.length === 0) {
        loginContainer.innerHTML = '<p class="text-slate-500">No login events recorded yet.</p>';
      } else {
        loginContainer.innerHTML = data.loginEvents.map(l => `
          <div class="p-3 rounded bg-slate-950 border border-slate-800">
            <p class="font-medium text-slate-200">${l.email}</p>
            <p class="text-xs ${l.status === 'FAILED' ? 'text-rose-400 font-bold' : 'text-emerald-400'}">Status: ${l.status} • IP: ${l.ip_address}</p>
          </div>
        `).join('');
      }
    }

    async function simulateTx(amount, category, description) {
      await fetch('/api/person-b/fraud/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, amount, category, description })
      });
      loadDashboard();
    }

    async function simulateFailedLogin() {
      await fetch('/api/person-b/login-events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, email: 'customer@securebank.com', ip_address: '192.168.1.99', status: 'FAILED' })
      });
      loadDashboard();
    }

    async function runSearch(e) {
      e.preventDefault();
      const q = document.getElementById('searchInput').value || 'coffee';
      const res = await fetch('/api/person-b/semantic-search?q=' + encodeURIComponent(q));
      const data = await res.json();
      const box = document.getElementById('searchResults');
      box.innerHTML = data.results.map(r => `
        <div class="p-3 bg-slate-950 border border-slate-800 rounded-lg flex justify-between items-center">
          <div>
            <span class="text-xs font-bold px-2 py-0.5 rounded ${r.item_type === 'FAQ' ? 'bg-purple-700' : 'bg-blue-700'}">${r.item_type}</span>
            <span class="ml-2 font-semibold text-white">${r.title}</span>
            <span class="text-xs text-slate-400 ml-2">(${r.category})</span>
            <p class="text-xs text-slate-300 mt-1">${r.description}</p>
          </div>
          <div class="text-right">
            ${r.amount ? `<p class="font-bold text-emerald-400">₹${r.amount}</p>` : ''}
            <p class="text-xs text-blue-400">Similarity: ${(r.similarity * 100).toFixed(1)}%</p>
          </div>
        </div>
      `).join('');
    }

    loadDashboard();
  </script>
</body>
</html>
"""

@router.get("/dashboard", response_class=HTMLResponse)
def get_person_b_dashboard():
    return DASHBOARD_HTML