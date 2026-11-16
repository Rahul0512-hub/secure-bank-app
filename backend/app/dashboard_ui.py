from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Frontend Banking Portal"])

# ==============================================================================
# 1. DEDICATED LOGIN PAGE (/login)
# ==============================================================================
LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sign In — SecureBank Enterprise</title>
  <title>SecureBank — Analytics, Vector Search & Fraud Center</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #070b14; color: #f1f5f9; }
    .glass-card { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(51, 65, 85, 0.6); }

    /* Custom Sleek Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #090d16; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
    * { scrollbar-width: thin; scrollbar-color: #334155 #090d16; }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">

  <!-- Subtle Background Glows -->
  <div class="absolute -top-32 -left-32 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
  <div class="absolute -bottom-32 -right-32 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

  <!-- Toast Container -->
  <div id="toastContainer" class="fixed top-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none"></div>

  <!-- Login Card Container -->
  <div class="glass-card w-full max-w-md rounded-3xl p-8 shadow-2xl space-y-6 relative z-10">
    
    <!-- Bank Logo & Header -->
    <div class="text-center space-y-2">
      <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/20">
        <svg class="w-8 h-8 text-slate-950" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2L2 7v3c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5zm-1 9V8h2v3h-2zm0 4v-2h2v2h-2z"/>
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-white tracking-tight">Secure<span class="text-emerald-400">Bank</span></h1>
      <p class="text-xs text-slate-400">Sign in to access your secure banking environment</p>
    </div>

    <!-- Auth Tabs (Login / Register) -->
    <div class="flex rounded-xl bg-slate-950 p-1 border border-slate-800 text-xs font-semibold">
      <button id="tabLoginBtn" onclick="switchAuthMode('login')" class="flex-1 py-2 rounded-lg bg-emerald-500 text-slate-950 font-bold transition">Sign In</button>
      <button id="tabRegBtn" onclick="switchAuthMode('register')" class="flex-1 py-2 rounded-lg text-slate-400 hover:text-white transition">New Registration</button>
    </div>

    <!-- Login Form -->
    <form id="loginForm" onsubmit="handleLogin(event)" class="space-y-4">
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1.5">Username</label>
        <input id="loginUser" type="text" placeholder="Enter username" required
          class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition" />
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
        <input id="loginPass" type="password" placeholder="••••••••••••" required
          class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition" />
      </div>

      <button type="submit" id="submitBtn" class="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-emerald-500/20">
        Authorize & Sign In
      </button>
    </form>

    <!-- Registration Form (Hidden by default) -->
    <form id="regForm" onsubmit="handleRegister(event)" class="space-y-3 hidden">
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Desired Username</label>
        <input id="regUser" type="text" placeholder="e.g. rahul_verma" minlength="3" required
          class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
        <input id="regEmail" type="email" placeholder="rahul@example.com" required
          class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Phone Number</label>
        <input id="regPhone" type="text" placeholder="+91 98765 00000"
          class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition" />
      </div>
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Password</label>
        <input id="regPass" type="password" placeholder="min 8 characters" minlength="8" required
          class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition" />
      </div>
      <button type="submit" class="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-emerald-500/20">
        Register Customer Account
      </button>
    </form>

    <!-- Quick Demo Fill Buttons -->
    <div class="pt-4 border-t border-slate-800 space-y-2.5">
      <p class="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-400 text-center">Quick Demo Credentials:</p>
      
      <div class="grid grid-cols-2 gap-2 text-xs">
        <button type="button" onclick="fillCreds('priya_sharma', 'CustomerPass@123')" class="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-500 text-left transition">
          <span class="font-bold text-white block">👤 Priya Sharma</span>
          <span class="text-[10px] text-emerald-400 font-mono">Customer (₹7.5L)</span>
        </button>

        <button type="button" onclick="fillCreds('arun_kumar', 'CustomerPass@123')" class="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-blue-500 text-left transition">
          <span class="font-bold text-white block">👤 Arun Kumar</span>
          <span class="text-[10px] text-blue-400 font-mono">Customer (₹85K)</span>
        </button>
      </div>

      <button type="button" onclick="fillCreds('admin', 'AdminPassword@123')" class="w-full p-2.5 rounded-xl bg-purple-950/40 border border-purple-800/60 hover:border-purple-500 text-left transition flex justify-between items-center text-xs">
        <div>
          <span class="font-bold text-white block">🏦 Bank Administrator</span>
          <span class="text-[10px] text-purple-300 font-mono">Risk Office & Underwriting Authority</span>
        </div>
        <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-900 text-purple-200">Admin</span>
      </button>
    </div>

  </div>

  <script>
    function showToast(title, msg, type = 'error') {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      const colors = {
        success: 'bg-emerald-950 border-emerald-700 text-emerald-200',
        error: 'bg-rose-950 border-rose-700 text-rose-200',
      };
      toast.className = `p-3.5 rounded-xl border ${colors[type] || colors.error} shadow-xl backdrop-blur-md text-xs pointer-events-auto`;
      toast.innerHTML = `<p class="font-bold">${title}</p><p class="mt-0.5 text-slate-300">${msg}</p>`;
      container.appendChild(toast);
      setTimeout(() => toast.remove(), 4000);
    }

    function switchAuthMode(mode) {
      if (mode === 'login') {
        document.getElementById('loginForm').classList.remove('hidden');
        document.getElementById('regForm').classList.add('hidden');
        document.getElementById('tabLoginBtn').className = 'flex-1 py-2 rounded-lg bg-emerald-500 text-slate-950 font-bold transition';
        document.getElementById('tabRegBtn').className = 'flex-1 py-2 rounded-lg text-slate-400 hover:text-white transition';
      } else {
        document.getElementById('loginForm').classList.add('hidden');
        document.getElementById('regForm').classList.remove('hidden');
        document.getElementById('tabRegBtn').className = 'flex-1 py-2 rounded-lg bg-emerald-500 text-slate-950 font-bold transition';
        document.getElementById('tabLoginBtn').className = 'flex-1 py-2 rounded-lg text-slate-400 hover:text-white transition';
      }
    }

    function fillCreds(u, p) {
      switchAuthMode('login');
      document.getElementById('loginUser').value = u;
      document.getElementById('loginPass').value = p;
    }

    async function handleLogin(e) {
      e.preventDefault();
      const u = document.getElementById('loginUser').value.trim();
      const p = document.getElementById('loginPass').value;
      const btn = document.getElementById('submitBtn');
      btn.innerText = 'Authenticating...';
      btn.disabled = true;

      try {
        const res = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: u, password: p })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Invalid username or password');

        localStorage.setItem('sb_token', data.access_token);
        localStorage.setItem('sb_user', JSON.stringify(data.user));

        if (data.user.role === 'Admin') {
          window.location.href = '/admin';
        } else {
          window.location.href = '/customer';
        }
      } catch (err) {
        showToast('Authentication Failed', err.message, 'error');
        btn.innerText = 'Authorize & Sign In';
        btn.disabled = false;
      }
    }

    async function handleRegister(e) {
      e.preventDefault();
      try {
        const payload = {
          username: document.getElementById('regUser').value.trim(),
          email: document.getElementById('regEmail').value.trim(),
          phone: document.getElementById('regPhone').value.trim() || null,
          password: document.getElementById('regPass').value,
          initial_deposit: 5000.0,
        };
        const res = await fetch('/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Registration failed');

        showToast('Registration Success', 'Account created! Signing you in...', 'success');
        // Auto login
        const loginRes = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: payload.username, password: payload.password })
        });
        const loginData = await loginRes.json();
        localStorage.setItem('sb_token', loginData.access_token);
        localStorage.setItem('sb_user', JSON.stringify(loginData.user));
        window.location.href = '/customer';
      } catch (err) {
        showToast('Registration Error', err.message, 'error');
      }
    }

    // Auto redirect if already signed in
    window.addEventListener('DOMContentLoaded', () => {
      const token = localStorage.getItem('sb_token');
      const userStr = localStorage.getItem('sb_user');
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          if (user.role === 'Admin') window.location.href = '/admin';
          else window.location.href = '/customer';
        } catch (e) {}
      }
      fillCreds('priya_sharma', 'CustomerPass@123');
    });
  </script>
</body>
</html>
"""

# ==============================================================================
# 2. DEDICATED CUSTOMER BANKING PAGE (/customer)
# ==============================================================================
CUSTOMER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Customer Banking Portal — SecureBank</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #070b14; color: #f1f5f9; }
    .glass-panel { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(14px); border: 1px solid rgba(51, 65, 85, 0.6); }
    .glass-card { background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(71, 85, 105, 0.4); }

    /* Custom Sleek Dark Scrollbar - Prevents browser default overlap */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #090d16;
      border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb {
      background: #334155;
      border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #475569;
    }
    * {
      scrollbar-width: thin;
      scrollbar-color: #334155 #090d16;
    }

    /* Print media styling: Only print the clean statement sheet */
    @media print {
      body {
        background: #ffffff !important;
        color: #0f172a !important;
      }
      header, main, #toastContainer, #newAccountModal, #applyLoanModal, .no-print {
        display: none !important;
      }
      #printableStatementArea {
        display: block !important;
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        background: #ffffff !important;
        color: #0f172a !important;
        padding: 0 !important;
        margin: 0 !important;
      }
    }
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- Top Navbar -->
  <header class="sticky top-0 z-40 bg-slate-950/95 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3.5">
    <div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
      
      <!-- Brand -->
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <svg class="w-5 h-5 text-slate-950" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L2 7v3c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5zm-1 9V8h2v3h-2zm0 4v-2h2v2h-2z"/>
          </svg>
        </div>
        <div>
          <span class="text-lg font-bold text-white">Secure<span class="text-emerald-400">Bank</span></span>
          <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono ml-2">Customer Portal</span>
        </div>
      </div>

      <!-- User Greeting & Logout -->
      <div class="flex items-center gap-3">
        <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
          <span id="navUsername" class="font-bold text-slate-200">Customer</span>
          <span class="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300">Customer</span>
        </div>
        <button onclick="logout()" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition">
          Sign Out
        </button>
      </div>

    </div>
  </header>

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none"></div>

  <!-- Main Content -->
  <main class="flex-1 max-w-7xl mx-auto w-full p-4 lg:p-8 space-y-8">
    
    <!-- Hero Summary Bar -->
    <div class="rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40 border border-slate-800 p-6 shadow-xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">Welcome, <span id="heroName" class="text-emerald-400">Customer</span></h1>
        <p class="text-xs text-slate-400 mt-1">Primary Retail Banking • Protected by PostgreSQL Least-Privilege Isolation</p>
      </div>
      <div class="flex items-center gap-6 bg-slate-950/80 border border-slate-800 rounded-2xl p-4">
        <div>
          <span class="text-[11px] font-semibold uppercase text-slate-400 block">Total Net Balance</span>
          <span id="heroTotalBalance" class="text-2xl font-black text-white font-mono">₹0.00</span>
        </div>
        <button onclick="openNewAccountModal()" class="px-3 py-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-bold transition">
          + Open Account
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

    <!-- 1. Account Cards -->
    <div>
      <h2 class="text-base font-bold text-white mb-3 flex items-center gap-2">
        <span>My Accounts</span>
        <span class="text-xs font-normal text-slate-400">(Encrypted in PostgreSQL `accounts` table)</span>
      </h2>
      <div id="accountsList" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <!-- Populated via JS -->
      </div>
    </div>

    <!-- 2. Transfer Studio & AI Semantic Search -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- Transfer Studio (7 cols) -->
      <div class="lg:col-span-7 glass-panel rounded-2xl p-6 shadow-xl space-y-5">
        <div class="border-b border-slate-800 pb-3">
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>
            Instant Fund Transfer
          </h2>
          <p class="text-xs text-slate-400">Atomic execution via PostgreSQL stored procedure <code class="text-emerald-300">transfer_funds</code></p>
        </div>

        <form onsubmit="handleTransfer(event)" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Debit From Account</label>
              <select id="transferSource" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2.5 text-xs text-slate-100 focus:border-emerald-500 focus:outline-none"></select>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Send To Beneficiary</label>
              <select id="transferDest" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2.5 text-xs text-slate-100 focus:border-emerald-500 focus:outline-none"></select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Amount (INR ₹)</label>
            <div class="relative">
              <span class="absolute left-3.5 top-2.5 text-slate-400 font-mono text-base font-semibold">₹</span>
              <input id="transferAmount" type="number" step="0.01" min="1" max="500000" placeholder="0.00" required
                oninput="checkAmountWarning(this.value)"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl pl-8 pr-4 py-2.5 text-slate-100 font-mono font-semibold text-base focus:border-emerald-500 focus:outline-none" />
            </div>
            <!-- Quick Chips -->
            <div class="flex flex-wrap gap-2 mt-2">
              <button type="button" onclick="setAmount(1000)" class="px-2 py-0.5 text-xs rounded-lg bg-slate-800 text-slate-300 font-mono">₹1,000</button>
              <button type="button" onclick="setAmount(5000)" class="px-2 py-0.5 text-xs rounded-lg bg-slate-800 text-slate-300 font-mono">₹5,000</button>
              <button type="button" onclick="setAmount(15000)" class="px-2 py-0.5 text-xs rounded-lg bg-slate-800 text-slate-300 font-mono">₹15,000</button>
              <button type="button" onclick="setAmount(50000)" class="px-2 py-0.5 text-xs rounded-lg bg-slate-800 text-amber-300 font-mono">₹50,000 (Alert Trigger)</button>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Category</label>
              <select id="transferCategory" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 focus:outline-none">
                <option value="Transfer">Inter-Account Transfer</option>
                <option value="Food & Dining">Food & Dining</option>
                <option value="Bills & Utilities">Bills & Utilities</option>
                <option value="Travel">Travel & Lodging</option>
                <option value="Investments">Investments</option>
                <option value="International Wire">International Wire (High Risk)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Description / Memo</label>
              <input id="transferDesc" type="text" placeholder="e.g. Monthly rent, groceries"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 focus:outline-none" />
            </div>
          </div>

          <!-- Dynamic Warning -->
          <div id="riskWarning" class="hidden p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs">
            ⚠️ <strong>Risk Alert:</strong> Transfers ≥ ₹50,000 trigger velocity anomaly scoring and are replicated to MongoDB Fraud Center.
          </div>

          <button type="submit" class="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-emerald-500/20">
            Confirm & Send Transfer
          </button>
        </form>
      </div>

      <!-- AI Semantic Search (5 cols) -->
      <div class="lg:col-span-5 glass-panel rounded-2xl p-6 shadow-xl space-y-4 flex flex-col">
        <div class="border-b border-slate-800 pb-3">
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            AI Semantic Statement Search
          </h2>
          <p class="text-xs text-slate-400">PostgreSQL 16 <code class="text-cyan-300">pgvector</code> HNSW Cosine Similarity</p>
        </div>

        <form onsubmit="handleSearch(event)" class="flex gap-2">
          <input id="searchInput" type="text" placeholder="Search by meaning: e.g. 'coffee', 'cab', 'lost card'..."
            class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-cyan-500 focus:outline-none" />
          <button type="submit" class="px-3.5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition">Search</button>
        </form>

        <div class="flex flex-wrap gap-1 text-[11px]">
          <button onclick="runQuickSearch('Starbucks Indiranagar coffee')" class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 hover:border-cyan-600 text-slate-300">Coffee</button>
          <button onclick="runQuickSearch('Airport cab ride')" class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 hover:border-cyan-600 text-slate-300">Airport Taxi</button>
          <button onclick="runQuickSearch('BESCOM Electricity Bill')" class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 hover:border-cyan-600 text-slate-300">Bills</button>
          <button onclick="runQuickSearch('How to block a stolen card')" class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 hover:border-cyan-600 text-slate-300">Lost Card FAQ</button>
        </div>

        <div id="searchResults" class="flex-1 overflow-y-auto max-h-72 space-y-2 pr-2.5"></div>
      </div>

    </div>

    <!-- 3. Transaction History Table -->
    <div class="glass-panel rounded-2xl p-6 shadow-xl space-y-4">
      <div class="flex flex-wrap justify-between items-center border-b border-slate-800 pb-3 gap-3">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
            Transaction Statement
          </h2>
          <p class="text-xs text-slate-400">PostgreSQL ACID Transaction Ledger • Audited Dual-Engine Outbox</p>
        </div>
        <div class="flex items-center gap-2">
          <button id="pdfDownloadBtn" onclick="generateTransactionPDF()" class="px-3.5 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            Generate Statement PDF
          </button>
          <button onclick="printOnlyStatement()" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition flex items-center gap-1.5">
            <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
            Print Statement
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800">
            <tr>
              <th class="py-2.5 px-3">TX ID</th>
              <th class="py-2.5 px-3">Date</th>
              <th class="py-2.5 px-3">Direction</th>
              <th class="py-2.5 px-3">Description</th>
              <th class="py-2.5 px-3 text-right">Amount</th>
              <th class="py-2.5 px-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody id="txListBody" class="divide-y divide-slate-800 font-mono"></tbody>
        </table>
      </div>
    </div>

    <!-- 4. Loans & Interactive EMI Simulator -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- EMI Calculator (7 cols) -->
      <div class="lg:col-span-7 glass-panel rounded-2xl p-6 shadow-xl space-y-5">
        <div class="border-b border-slate-800 pb-3 flex justify-between items-center">
          <div>
            <h2 class="text-base font-bold text-white">Loan & EMI Calculator</h2>
            <p class="text-xs text-slate-400">Simulate monthly amortization</p>
          </div>
          <button onclick="openApplyLoanModal()" class="px-3 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold transition">
            + Apply for Loan
          </button>
        </div>

        <div class="space-y-3 text-xs">
          <div>
            <div class="flex justify-between mb-1">
              <span class="text-slate-400">Principal</span>
              <span id="pVal" class="text-white font-bold font-mono">₹5,00,000</span>
            </div>
            <input type="range" id="pSlider" min="50000" max="5000000" step="25000" value="500000" oninput="recalcEMI()" class="w-full accent-amber-500 bg-slate-900 rounded-lg cursor-pointer" />
          </div>

          <div>
            <div class="flex justify-between mb-1">
              <span class="text-slate-400">Interest Rate</span>
              <span id="rVal" class="text-white font-bold font-mono">8.50%</span>
            </div>
            <input type="range" id="rSlider" min="5.0" max="18.0" step="0.25" value="8.50" oninput="recalcEMI()" class="w-full accent-amber-500 bg-slate-900 rounded-lg cursor-pointer" />
          </div>

          <div>
            <div class="flex justify-between mb-1">
              <span class="text-slate-400">Tenure</span>
              <span id="tVal" class="text-white font-bold font-mono">36 Months</span>
            </div>
            <input type="range" id="tSlider" min="6" max="120" step="6" value="36" oninput="recalcEMI()" class="w-full accent-amber-500 bg-slate-900 rounded-lg cursor-pointer" />
          </div>

          <div class="grid grid-cols-3 gap-3 pt-2 text-center">
            <div class="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
              <span class="text-[10px] text-slate-400 uppercase block font-semibold">Monthly EMI</span>
              <span id="resEMI" class="text-base font-bold text-amber-400 font-mono">₹15,783</span>
            </div>
            <div class="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
              <span class="text-[10px] text-slate-400 uppercase block font-semibold">Total Interest</span>
              <span id="resInterest" class="text-base font-bold text-slate-200 font-mono">₹68,188</span>
            </div>
            <div class="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
              <span class="text-[10px] text-slate-400 uppercase block font-semibold">Total Payable</span>
              <span id="resTotal" class="text-base font-bold text-emerald-400 font-mono">₹5,68,188</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Loans (5 cols) -->
      <div class="lg:col-span-5 glass-panel rounded-2xl p-6 shadow-xl space-y-4">
        <div class="border-b border-slate-800 pb-3">
          <h2 class="text-base font-bold text-white">My Active Credit Facilities</h2>
          <p class="text-xs text-slate-400">PostgreSQL `loans` table</p>
        </div>
        <div id="customerLoansList" class="space-y-2.5 overflow-y-auto max-h-64"></div>
      </div>

    </div>

    <!-- Official Transaction Statement Container (Rendered to PDF & Pure Print) -->
    <div id="printableStatementArea" class="hidden">
      <div id="statementSheet" style="background:#ffffff; color:#0f172a; padding:36px; font-family:'Plus Jakarta Sans', Arial, sans-serif; max-width:850px; margin:0 auto; box-sizing:border-box; border-radius:12px; box-shadow:0 10px 25px rgba(0,0,0,0.05);">
        
        <!-- Statement Header -->
        <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom:2px solid #0f172a; padding-bottom:18px; margin-bottom:20px;">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <div style="width:30px; height:30px; border-radius:6px; background:#059669; display:flex; align-items:center; justify-content:center; color:#ffffff; font-weight:800; font-size:16px;">S</div>
              <h1 style="font-size:22px; font-weight:800; color:#0f172a; margin:0; letter-spacing:-0.5px;">SECURE<span style="color:#059669;">BANK</span></h1>
            </div>
            <p style="font-size:11px; font-weight:600; color:#475569; margin:4px 0 0 0;">Official Account Transaction Statement</p>
            <p style="font-size:10px; color:#64748b; margin:2px 0 0 0;">Dual-Engine Core Banking System • Reserve Bank of India FinTech Reg. #SB-2026-X1</p>
          </div>
          <div style="text-align:right;">
            <span style="display:inline-block; font-size:10px; font-weight:700; text-transform:uppercase; background:#ecfdf5; color:#047857; border:1px solid #6ee7b7; padding:3px 8px; border-radius:4px; font-family:monospace;">OFFICIAL STATEMENT</span>
            <p style="font-size:10px; color:#64748b; margin:6px 0 2px 0;">Generated Date:</p>
            <p style="font-size:11px; font-weight:700; color:#0f172a; margin:0;" id="stmtGenDate"></p>
          </div>
        </div>

        <!-- Account Holder & Balance Overview Card -->
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:14px 18px; margin-bottom:24px;">
          <div>
            <p style="font-size:9.5px; font-weight:700; text-transform:uppercase; color:#64748b; margin:0 0 4px 0; letter-spacing:0.5px;">Account Holder</p>
            <p style="font-size:14px; font-weight:800; color:#0f172a; margin:0;" id="stmtHolderName">Priya Sharma</p>
            <p style="font-size:11px; color:#475569; margin:2px 0 0 0;" id="stmtHolderEmail">priya@example.com</p>
            <p style="font-size:10px; font-family:monospace; color:#64748b; margin:2px 0 0 0;" id="stmtHolderId">Customer ID: #1</p>
          </div>
          <div style="text-align:right;">
            <p style="font-size:9.5px; font-weight:700; text-transform:uppercase; color:#64748b; margin:0 0 4px 0; letter-spacing:0.5px;">Consolidated Net Balance</p>
            <p style="font-size:18px; font-weight:900; color:#059669; font-family:monospace; margin:0;" id="stmtNetBalance">₹0.00</p>
            <p style="font-size:10px; color:#475569; margin:2px 0 0 0;" id="stmtActiveAccountsCount">Accounts: 1 Active</p>
            <p style="font-size:10px; font-family:monospace; color:#64748b; margin:2px 0 0 0;">Currency: INR (₹)</p>
          </div>
        </div>

        <!-- Detailed Transaction Ledger -->
        <div style="margin-bottom:24px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <p style="font-size:11px; font-weight:700; text-transform:uppercase; color:#0f172a; margin:0; letter-spacing:0.5px;">Transaction Ledger</p>
            <span style="font-size:10px; color:#64748b; font-family:monospace;">PostgreSQL ACID Table: `transactions`</span>
          </div>
          <table style="width:100%; border-collapse:collapse; font-size:10.5px;">
            <thead>
              <tr style="background:#0f172a; color:#ffffff;">
                <th style="padding:8px 10px; text-align:left; font-weight:600; border-top-left-radius:4px;">TX ID</th>
                <th style="padding:8px 10px; text-align:left; font-weight:600;">Date</th>
                <th style="padding:8px 10px; text-align:left; font-weight:600;">Type</th>
                <th style="padding:8px 10px; text-align:left; font-weight:600;">Description</th>
                <th style="padding:8px 10px; text-align:right; font-weight:600;">Amount (₹)</th>
                <th style="padding:8px 10px; text-align:center; font-weight:600; border-top-right-radius:4px;">Status</th>
              </tr>
            </thead>
            <tbody id="stmtRows" style="font-family:'JetBrains Mono', Courier, monospace;">
              <!-- Transaction rows populated dynamically -->
            </tbody>
          </table>
        </div>

        <!-- Security Seal & Disclaimer Footer -->
        <div style="border-top:1px dashed #cbd5e1; padding-top:14px; margin-top:20px; font-size:9.5px; color:#64748b; line-height:1.5;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
            <div>
              <p style="margin:0; font-weight:700; color:#334155;">Security & Audit Verification:</p>
              <p style="margin:1px 0 0 0; font-family:monospace; font-size:9px;" id="stmtAuditHash">HASH: 8f3c7e91...d2a10b • ACID Verified</p>
            </div>
            <div style="text-align:right;">
              <p style="margin:0; font-weight:700; color:#334155;">SecureBank Operations Hub</p>
              <p style="margin:1px 0 0 0;">Tech Core, MG Road, Bengaluru, KA 560001</p>
            </div>
          </div>
          <p style="margin:0; color:#94a3b8; font-style:italic;">
            Note: This is an authentic computer-generated account statement issued directly from the SecureBank database cluster. It does not require a physical signature.
          </p>
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
    </div>

  </main>

  <!-- Modals -->
  <div id="newAccountModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm hidden p-4">
    <div class="glass-panel w-full max-w-sm rounded-2xl p-6 shadow-2xl space-y-4 border border-slate-700">
      <div class="flex justify-between items-center border-b border-slate-800 pb-2">
        <h3 class="text-sm font-bold text-white">Open Bank Account</h3>
        <button onclick="closeNewAccountModal()" class="text-slate-400 hover:text-white">✕</button>
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
      <form onsubmit="handleOpenAccount(event)" class="space-y-3 text-xs">
        <div>
          <label class="block text-slate-400 mb-1">Account Type</label>
          <select id="newAccountType" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white">
            <option value="Savings">Savings Account</option>
            <option value="Checking">Checking Account</option>
            <option value="Investment">Investment Account</option>
          </select>
        </div>
        <div>
          <label class="block text-slate-400 mb-1">Initial Deposit (₹)</label>
          <input id="newAccountDeposit" type="number" step="0.01" min="0" value="5000" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono" />
        </div>
        <button type="submit" class="w-full py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase">Open Account</button>
      </form>
    </div>
  </div>

  <div id="applyLoanModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm hidden p-4">
    <div class="glass-panel w-full max-w-md rounded-2xl p-6 shadow-2xl space-y-4 border border-slate-700">
      <div class="flex justify-between items-center border-b border-slate-800 pb-2">
        <h3 class="text-sm font-bold text-white">Loan Application Form</h3>
        <button onclick="closeApplyLoanModal()" class="text-slate-400 hover:text-white">✕</button>
      </div>
      <form onsubmit="handleApplyLoan(event)" class="space-y-3 text-xs">
        <div>
          <label class="block text-slate-400 mb-1">Principal Amount (₹)</label>
          <input id="applyLoanAmount" type="number" step="1000" min="10000" max="5000000" value="350000" required class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-slate-400 mb-1">Tenure (Months)</label>
            <input id="applyLoanTenure" type="number" min="6" max="120" value="24" required class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono" />
          </div>
          <div>
            <label class="block text-slate-400 mb-1">Annual Rate (%)</label>
            <input type="text" value="8.50%" readonly class="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-400 font-mono" />
          </div>
        </div>
        <button type="submit" class="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs uppercase">Submit Loan Application</button>
      </form>
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
    let authToken = localStorage.getItem('sb_token') || null;
    let currentUser = null;
    let myAccounts = [];

    function showToast(title, msg, type = 'success') {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      const colors = {
        success: 'bg-emerald-950 border-emerald-700 text-emerald-200',
        error: 'bg-rose-950 border-rose-700 text-rose-200',
        warning: 'bg-amber-950 border-amber-700 text-amber-200',
      };
      toast.className = `p-3.5 rounded-xl border ${colors[type] || colors.success} shadow-xl backdrop-blur-md text-xs pointer-events-auto`;
      toast.innerHTML = `<p class="font-bold">${title}</p><p class="mt-0.5 text-slate-300">${msg}</p>`;
      container.appendChild(toast);
      setTimeout(() => toast.remove(), 4000);
    }

    function logout() {
      localStorage.removeItem('sb_token');
      localStorage.removeItem('sb_user');
      window.location.href = '/login';
    }

    function openNewAccountModal() { document.getElementById('newAccountModal').classList.remove('hidden'); }
    function closeNewAccountModal() { document.getElementById('newAccountModal').classList.add('hidden'); }
    function openApplyLoanModal() { document.getElementById('applyLoanModal').classList.remove('hidden'); }
    function closeApplyLoanModal() { document.getElementById('applyLoanModal').classList.add('hidden'); }

    function setAmount(amt) {
      document.getElementById('transferAmount').value = amt;
      checkAmountWarning(amt);
    }

    function checkAmountWarning(amt) {
      const val = parseFloat(amt) || 0;
      const b = document.getElementById('riskWarning');
      if (val >= 50000) b.classList.remove('hidden');
      else b.classList.add('hidden');
    }

    function recalcEMI() {
      const p = parseFloat(document.getElementById('pSlider').value);
      const r = parseFloat(document.getElementById('rSlider').value);
      const n = parseInt(document.getElementById('tSlider').value);

      document.getElementById('pVal').innerText = '₹' + p.toLocaleString();
      document.getElementById('rVal').innerText = r.toFixed(2) + '%';
      document.getElementById('tVal').innerText = n + ' Months';

      const mr = (r / 100) / 12;
      const factor = Math.pow(1 + mr, n);
      const emi = p * mr * factor / (factor - 1);
      const total = emi * n;

      document.getElementById('resEMI').innerText = '₹' + Math.round(emi).toLocaleString();
      document.getElementById('resInterest').innerText = '₹' + Math.round(total - p).toLocaleString();
      document.getElementById('resTotal').innerText = '₹' + Math.round(total).toLocaleString();
    }

    async function loadCustomerPortal() {
      const token = localStorage.getItem('sb_token');
      const userStr = localStorage.getItem('sb_user');

      if (!token || !userStr) {
        window.location.href = '/login';
        return;
      }

      currentUser = JSON.parse(userStr);
      if (currentUser.role === 'Admin') {
        window.location.href = '/admin';
        return;
      }

      document.getElementById('navUsername').innerText = currentUser.username;
      document.getElementById('heroName').innerText = currentUser.username;

      try {
        // Accounts
        const accRes = await fetch('/accounts/me', { headers: { 'Authorization': `Bearer ${token}` } });
        if (accRes.ok) {
          const accData = await accRes.json();
          myAccounts = accData.accounts || [];
          renderAccounts(myAccounts);
          await loadRecipients(myAccounts);
        }

        // Transactions
        const txRes = await fetch('/transactions/me', { headers: { 'Authorization': `Bearer ${token}` } });
        if (txRes.ok) {
          const txData = await txRes.json();
          renderTransactions(txData.transactions || []);
        }

        // Loans
        const lRes = await fetch('/loans/me', { headers: { 'Authorization': `Bearer ${token}` } });
        if (lRes.ok) {
          const lData = await lRes.json();
          renderLoans(lData.loans || []);
        }

        // Initial search
        runQuickSearch('Starbucks Coffee Indiranagar');
      } catch (err) {
        console.error(err);
      }
    }

    function renderAccounts(accs) {
      const container = document.getElementById('accountsList');
      let total = 0;
      accs.forEach(a => total += parseFloat(a.balance));
      document.getElementById('heroTotalBalance').innerText = '₹' + total.toLocaleString('en-IN', { minimumFractionDigits: 2 });

      container.innerHTML = accs.map(a => `
        <div class="glass-card rounded-2xl p-5 shadow-lg flex flex-col justify-between">
          <div class="flex justify-between items-start mb-3">
            <div>
              <span class="text-xs uppercase text-slate-400 font-mono">${a.account_type}</span>
              <p class="text-xs font-mono text-emerald-400 mt-0.5">${a.account_number}</p>
            </div>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${a.status === 'Active' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}">
              ${a.status}
            </span>
          </div>
          <div>
            <span class="text-[10px] text-slate-400 uppercase block font-semibold">Balance</span>
            <span class="text-2xl font-black text-white font-mono">₹${parseFloat(a.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-800 text-xs flex justify-between">
            <span class="text-slate-500 font-mono">Currency: ${a.currency}</span>
            <button onclick="document.getElementById('transferSource').value = ${a.account_id}" class="text-emerald-400 hover:text-emerald-300 font-semibold">Select Source</button>
          </div>
        </div>
      `).join('');

      document.getElementById('transferSource').innerHTML = accs.map(a => `
        <option value="${a.account_id}">${a.account_type} (${a.account_number}) — ₹${parseFloat(a.balance).toLocaleString()}</option>
      `).join('');
    }

    async function loadRecipients(accs) {
      const token = localStorage.getItem('sb_token');
      try {
        const res = await fetch('/accounts/recipients', { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) {
          const data = await res.json();
          document.getElementById('transferDest').innerHTML = (data.recipients || []).map(r => `
            <option value="${r.account_id}">${r.owner_username} — ${r.account_type} (${r.account_number})</option>
          `).join('');
        }
      } catch (e) {}
    }

    let currentTransactionsList = [];

    function renderTransactions(txs) {
      currentTransactionsList = txs || [];
      const tbody = document.getElementById('txListBody');
      if (!txs.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-slate-500">No transactions recorded.</td></tr>`;
        return;
      }
      tbody.innerHTML = txs.map(t => {
        const isDebit = myAccounts.some(a => a.account_id === t.source_account_id);
        return `
          <tr class="hover:bg-slate-900/40">
            <td class="py-2.5 px-3 font-bold text-slate-300">#${t.transaction_id}</td>
            <td class="py-2.5 px-3 text-slate-400">${new Date(t.created_at).toLocaleDateString()}</td>
            <td class="py-2.5 px-3">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isDebit ? 'bg-rose-950 text-rose-300' : 'bg-emerald-950 text-emerald-300'}">
                ${isDebit ? 'DEBIT ➔ ' + t.destination_account_id : 'CREDIT ⬅ ' + t.source_account_id}
              </span>
            </td>
            <td class="py-2.5 px-3 text-slate-200">${t.description || 'Transfer'}</td>
            <td class="py-2.5 px-3 text-right font-bold ${isDebit ? 'text-rose-400' : 'text-emerald-400'}">
              ${isDebit ? '- ₹' : '+ ₹'}${parseFloat(t.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </td>
            <td class="py-2.5 px-3 text-center">
              <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 font-bold">${t.status}</span>
            </td>
          </tr>
        `;
      }).join('');
    }

    function populateStatementSheet() {
      const now = new Date();
      document.getElementById('stmtGenDate').innerText = now.toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short'
      });

      if (currentUser) {
        document.getElementById('stmtHolderName').innerText = currentUser.username.toUpperCase().replace('_', ' ');
        document.getElementById('stmtHolderEmail').innerText = currentUser.email || `${currentUser.username}@securebank.local`;
        document.getElementById('stmtHolderId').innerText = `Customer ID: #${currentUser.user_id} (${currentUser.role})`;
      }

      let totalBal = 0;
      myAccounts.forEach(a => totalBal += parseFloat(a.balance));
      document.getElementById('stmtNetBalance').innerText = '₹' + totalBal.toLocaleString('en-IN', { minimumFractionDigits: 2 });
      document.getElementById('stmtActiveAccountsCount').innerText = `Accounts: ${myAccounts.length} (${myAccounts.map(a => a.account_number).join(', ')})`;

      const randHex = Array.from(crypto.getRandomValues(new Uint8Array(12))).map(b => b.toString(16).padStart(2, '0')).join('');
      document.getElementById('stmtAuditHash').innerText = `SHA256:${randHex}...e3 • PostgreSQL 16 ACID Engine`;

      const tbody = document.getElementById('stmtRows');
      if (!currentTransactionsList.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="padding:16px; text-align:center; color:#94a3b8; border-bottom:1px solid #e2e8f0;">No transactions recorded in statement period.</td></tr>`;
        return;
      }

      tbody.innerHTML = currentTransactionsList.map((t, idx) => {
        const isDebit = myAccounts.some(a => a.account_id === t.source_account_id);
        const bg = idx % 2 === 0 ? '#ffffff' : '#f8fafc';
        const typeLabel = isDebit ? 'DEBIT' : 'CREDIT';
        const typeColor = isDebit ? '#b91c1c' : '#047857';
        const typeBg = isDebit ? '#fef2f2' : '#ecfdf5';
        const amtColor = isDebit ? '#dc2626' : '#059669';
        const sign = isDebit ? '-' : '+';

        return `
          <tr style="background:${bg}; border-bottom:1px solid #e2e8f0;">
            <td style="padding:8px 10px; font-weight:700; color:#334155;">#${t.transaction_id}</td>
            <td style="padding:8px 10px; color:#475569;">${new Date(t.created_at).toLocaleDateString('en-IN')}</td>
            <td style="padding:8px 10px;">
              <span style="font-size:9.5px; font-weight:700; padding:2px 6px; border-radius:3px; background:${typeBg}; color:${typeColor};">
                ${typeLabel}
              </span>
            </td>
            <td style="padding:8px 10px; color:#0f172a; font-family:'Plus Jakarta Sans', Arial, sans-serif;">
              ${t.description || 'Inter-Account Transfer'}
            </td>
            <td style="padding:8px 10px; text-align:right; font-weight:700; color:${amtColor};">
              ${sign} ₹${parseFloat(t.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </td>
            <td style="padding:8px 10px; text-align:center;">
              <span style="font-size:9px; font-weight:700; padding:2px 6px; border-radius:3px; background:#f1f5f9; color:#475569;">
                ${t.status}
              </span>
            </td>
          </tr>
        `;
      }).join('');
    }

    async function generateTransactionPDF() {
      const btn = document.getElementById('pdfDownloadBtn');
      const originalHtml = btn.innerHTML;
      btn.innerHTML = `<svg class="w-4 h-4 animate-spin inline-block mr-1" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> Generating PDF...`;
      btn.disabled = true;

      try {
        populateStatementSheet();
        const area = document.getElementById('printableStatementArea');
        area.classList.remove('hidden');

        const filename = `SecureBank_Statement_${currentUser ? currentUser.username : 'Account'}_${new Date().toISOString().slice(0,10)}.pdf`;

        if (window.html2pdf) {
          const opt = {
            margin:       [8, 8, 8, 8],
            filename:     filename,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true, logging: false },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
          };
          await html2pdf().set(opt).from(document.getElementById('statementSheet')).save();
          showToast('Statement Downloaded', `Successfully generated ${filename}`, 'success');
        } else {
          window.print();
        }
      } catch (err) {
        console.error('PDF generation error:', err);
        showToast('PDF Export', 'Printing statement directly...', 'warning');
        window.print();
      } finally {
        document.getElementById('printableStatementArea').classList.add('hidden');
        btn.innerHTML = originalHtml;
        btn.disabled = false;
      }
    }

    function printOnlyStatement() {
      populateStatementSheet();
      const area = document.getElementById('printableStatementArea');
      area.classList.remove('hidden');
      window.print();
      setTimeout(() => {
        area.classList.add('hidden');
      }, 1000);
    }

    function renderLoans(loans) {
      const c = document.getElementById('customerLoansList');
      if (!loans.length) {
        c.innerHTML = `<p class="text-xs text-slate-500 py-3 text-center">No active loans.</p>`;
        return;
      }
      c.innerHTML = loans.map(l => `
        <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center text-xs">
          <div>
            <span class="font-bold text-white">Loan #${l.loan_id}</span>
            <span class="text-[10px] ml-2 px-2 py-0.5 rounded font-bold ${l.status === 'Active' ? 'bg-emerald-950 text-emerald-300' : 'bg-amber-950 text-amber-300'}">${l.status}</span>
            <p class="text-[10px] text-slate-400 mt-0.5 font-mono">Rate: ${l.interest_rate} • ${l.tenure_months}m</p>
          </div>
          <div class="text-right font-mono">
            <span class="text-amber-400 font-bold block">₹${parseFloat(l.loan_amount).toLocaleString()}</span>
            <span class="text-[10px] text-slate-400">EMI: ₹${parseFloat(l.monthly_emi).toLocaleString()}/mo</span>
          </div>
        </div>
      `).join('');
    }

    async function handleTransfer(e) {
      e.preventDefault();
      const token = localStorage.getItem('sb_token');
      const src = parseInt(document.getElementById('transferSource').value);
      const dest = parseInt(document.getElementById('transferDest').value);
      const amount = parseFloat(document.getElementById('transferAmount').value);
      const category = document.getElementById('transferCategory').value;
      const description = document.getElementById('transferDesc').value || `${category} payment`;

      if (src === dest) {
        showToast('Transfer Error', 'Source and destination accounts must be distinct.', 'error');
        return;
      }

      try {
        const res = await fetch('/transactions/transfer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({
            source_account_id: src,
            destination_account_id: dest,
            amount: amount,
            category: category,
            description: `[${category}] ${description}`
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Transfer failed');

        let msg = `Transfer #${data.transaction_id} completed.`;
        if (data.fraud_alert && data.fraud_alert.triggered) {
          showToast('Transfer Flagged', msg + ' Flagged for compliance review.', 'warning');
        } else {
          showToast('Transfer Completed', msg, 'success');
        }

        document.getElementById('transferAmount').value = '';
        document.getElementById('transferDesc').value = '';
        checkAmountWarning(0);
        await loadCustomerPortal();
      } catch (err) {
        showToast('Transfer Failed', err.message, 'error');
      }
    }

    async function handleSearch(e) {
      e.preventDefault();
      runQuickSearch(document.getElementById('searchInput').value.trim());
    }

    async function runQuickSearch(q) {
      if (!q) return;
      document.getElementById('searchInput').value = q;
      const box = document.getElementById('searchResults');
      box.innerHTML = `<p class="text-xs text-slate-500 py-2 text-center">Searching pgvector...</p>`;

      try {
        const res = await fetch('/api/person-b/semantic-search?q=' + encodeURIComponent(q));
        const data = await res.json();
        box.innerHTML = (data.results || []).map(r => `
          <div class="p-3 rounded-xl bg-slate-950/90 border border-slate-800 text-xs flex justify-between items-center gap-3 hover:border-cyan-500/40 transition">
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${r.item_type === 'FAQ' ? 'bg-purple-950 text-purple-300 border border-purple-800/50' : 'bg-cyan-950 text-cyan-300 border border-cyan-800/50'}">${r.item_type}</span>
                <span class="font-semibold text-white truncate">${r.title}</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">${r.description}</p>
            </div>
            <div class="shrink-0 text-right font-mono flex flex-col items-end gap-1">
              ${r.amount ? `<span class="text-emerald-400 font-bold text-xs">₹${r.amount.toLocaleString()}</span>` : ''}
              <span class="text-[10px] text-cyan-400 bg-cyan-950/70 border border-cyan-800/40 px-2 py-0.5 rounded-full font-semibold whitespace-nowrap">${(r.similarity * 100).toFixed(1)}% match</span>
            </div>
          </div>
        `).join('') || '<p class="text-xs text-slate-500 py-4 text-center">No matching records found.</p>';
      } catch (e) {
        box.innerHTML = `<p class="text-xs text-rose-400 py-2 text-center">${e.message}</p>`;
      }
    }

    async function handleOpenAccount(e) {
      e.preventDefault();
      const token = localStorage.getItem('sb_token');
      try {
        const res = await fetch('/accounts/open', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({
            account_type: document.getElementById('newAccountType').value,
            initial_balance: parseFloat(document.getElementById('newAccountDeposit').value) || 0,
            currency: 'INR'
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Failed');
        showToast('Success', 'Account opened successfully!', 'success');
        closeNewAccountModal();
        await loadCustomerPortal();
      } catch (err) {
        showToast('Error', err.message, 'error');
      }
    }

    async function handleApplyLoan(e) {
      e.preventDefault();
      const token = localStorage.getItem('sb_token');
      try {
        const res = await fetch('/loans/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({
            loan_amount: parseFloat(document.getElementById('applyLoanAmount').value),
            interest_rate: 8.5,
            tenure_months: parseInt(document.getElementById('applyLoanTenure').value)
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Failed');
        showToast('Loan Submitted', 'Loan request submitted for underwriting!', 'success');
        closeApplyLoanModal();
        await loadCustomerPortal();
      } catch (err) {
        showToast('Error', err.message, 'error');
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      recalcEMI();
      loadCustomerPortal();
    });
  </script>
</body>
</html>
"""

# ==============================================================================
# 3. DEDICATED BANK ADMIN & FRAUD PORTAL (/admin)
# ==============================================================================
ADMIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bank Management & Risk Center — SecureBank</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #070b14; color: #f1f5f9; }
    .glass-panel { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(14px); border: 1px solid rgba(51, 65, 85, 0.6); }

    /* Custom Sleek Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #090d16; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
    * { scrollbar-width: thin; scrollbar-color: #334155 #090d16; }
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- Top Navbar -->
  <header class="sticky top-0 z-40 bg-slate-950/95 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3.5">
    <div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
      
      <!-- Brand -->
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
        </div>
        <div>
          <span class="text-lg font-bold text-white">Secure<span class="text-purple-400">Bank</span></span>
          <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/30 font-mono ml-2">Staff & Risk Center</span>
        </div>
      </div>

      <!-- Officer & Logout -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <div class="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></div>
          <span class="font-bold text-slate-200">Officer: admin</span>
          <span class="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-purple-950 text-purple-300 font-bold">Admin</span>
        </div>
        <button onclick="logout()" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition">
          Sign Out
        </button>
      </div>

    </div>
  </header>

  <!-- Toast Container -->
  <div id="toastContainer" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none"></div>

  <!-- Main Admin Portal -->
  <main class="flex-1 max-w-7xl mx-auto w-full p-4 lg:p-8 space-y-8">
    
    <!-- Executive KPI Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-emerald-500 shadow-lg">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Total Deposits (AUM)</span>
        <span id="kpiAUM" class="text-2xl font-bold text-white font-mono mt-1 block">₹0.00</span>
        <span class="text-[10px] text-emerald-400 font-mono mt-1 block">PostgreSQL Core</span>
      </div>
      <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-blue-500 shadow-lg">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Active Accounts</span>
        <span id="kpiAccounts" class="text-2xl font-bold text-white font-mono mt-1 block">0</span>
        <span class="text-[10px] text-blue-400 font-mono mt-1 block">Custody Units</span>
      </div>
      <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-purple-500 shadow-lg">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Ledger Transfers</span>
        <span id="kpiTransfers" class="text-2xl font-bold text-white font-mono mt-1 block">0</span>
        <span class="text-[10px] text-purple-400 font-mono mt-1 block">ACID Ledger Rows</span>
      </div>
      <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-rose-500 shadow-lg">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Open Fraud Alerts</span>
        <span id="kpiAlerts" class="text-2xl font-bold text-rose-400 font-mono mt-1 block">0</span>
        <span class="text-[10px] text-rose-400 font-mono mt-1 block">MongoDB Real-Time</span>
      </div>
      <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-amber-500 shadow-lg">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Pending Outbox</span>
        <span id="kpiOutbox" class="text-2xl font-bold text-amber-400 font-mono mt-1 block">0</span>
        <button onclick="triggerSync()" class="text-[10px] font-bold text-amber-300 hover:text-white uppercase font-mono mt-1 block underline">Sync Outbox Now →</button>
      </div>
    </div>

    <!-- Loan Underwriting Queue -->
    <div class="glass-panel rounded-2xl p-6 shadow-xl space-y-4">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            Customer Loan Applications & Underwriting Queue
          </h2>
          <p class="text-xs text-slate-400">Execute credit decisions via stored procedure <code class="text-amber-300">public.update_loan_status</code></p>
        </div>
        <button onclick="loadAdminPortal()" class="px-3 py-1 rounded-lg bg-slate-800 text-xs text-slate-300 hover:bg-slate-700">Refresh</button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800">
            <tr>
              <th class="py-2.5 px-3">Loan ID</th>
              <th class="py-2.5 px-3">Customer User ID</th>
              <th class="py-2.5 px-3">Principal Amount</th>
              <th class="py-2.5 px-3">Interest Rate</th>
              <th class="py-2.5 px-3">Est. Monthly EMI</th>
              <th class="py-2.5 px-3">Status</th>
              <th class="py-2.5 px-3 text-right">Officer Decision</th>
            </tr>
          </thead>
          <tbody id="loanTableBody" class="divide-y divide-slate-800 font-mono"></tbody>
        </table>
      </div>
    </div>

    <!-- Real-Time Fraud Alerts Queue & MongoDB Analytics -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      
      <!-- Fraud Alerts Queue -->
      <div class="glass-panel rounded-2xl p-6 shadow-xl space-y-4 flex flex-col">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <svg class="w-5 h-5 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              Real-Time Fraud Alerts Queue
            </h2>
            <p class="text-xs text-slate-400">MongoDB `fraud_alerts` collection with velocity rules</p>
          </div>
          <button onclick="simulateFraud()" class="px-2.5 py-1 rounded bg-rose-950 border border-rose-800 text-[10px] text-rose-300 font-bold hover:bg-rose-900">+ Simulate Test Alert</button>
        </div>
        <div id="fraudList" class="space-y-3 overflow-y-auto max-h-72 flex-1 pr-1"></div>
      </div>

      <!-- MongoDB Aggregation Spending Chart -->
      <div class="glass-panel rounded-2xl p-6 shadow-xl space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"/></svg>
              Spending Analytics (MongoDB Aggregation)
            </h2>
            <p class="text-xs text-slate-400">Pipeline: `$group` ➔ `$sum` ➔ `$sort`</p>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">Live Mongo Data</span>
        </div>
        <div class="h-72 relative">
          <canvas id="adminSpendingChart"></canvas>
        </div>
      </div>

    </div>

    <!-- Account Freeze Controls & Login Audit Trail -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      
      <!-- Account Freeze Supervision -->
      <div class="glass-panel rounded-2xl p-6 shadow-xl space-y-4">
        <div class="border-b border-slate-800 pb-3">
          <h2 class="text-base font-bold text-white">Customer Account Compliance & Freeze Controls</h2>
          <p class="text-xs text-slate-400">Restricted stored procedure <code class="text-purple-300">public.set_account_status</code></p>
        </div>
        <div id="adminAccountsList" class="space-y-2.5 overflow-y-auto max-h-72 pr-1"></div>
      </div>

      <!-- Security Login Trail -->
      <div class="glass-panel rounded-2xl p-6 shadow-xl space-y-4">
        <div class="border-b border-slate-800 pb-3">
          <h2 class="text-base font-bold text-white">Authentication & Brute-Force Surveillance</h2>
          <p class="text-xs text-slate-400">MongoDB `login_events` audit trail</p>
        </div>
        <div id="loginEventsList" class="space-y-2 overflow-y-auto max-h-72 pr-1"></div>
      </div>

    </div>

  </main>

  <script>
    let chartInstance = null;

    function showToast(title, msg, type = 'success') {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      toast.className = `p-3.5 rounded-xl border bg-slate-900 border-slate-700 text-slate-200 shadow-xl backdrop-blur-md text-xs pointer-events-auto`;
      toast.innerHTML = `<p class="font-bold text-white">${title}</p><p class="mt-0.5 text-slate-300">${msg}</p>`;
      container.appendChild(toast);
      setTimeout(() => toast.remove(), 4000);
    }

    function logout() {
      localStorage.removeItem('sb_token');
      localStorage.removeItem('sb_user');
      window.location.href = '/login';
    }

    async function loadAdminPortal() {
      const token = localStorage.getItem('sb_token');
      const userStr = localStorage.getItem('sb_user');

      if (!token || !userStr) {
        window.location.href = '/login';
        return;
      }

      const user = JSON.parse(userStr);
      if (user.role !== 'Admin') {
        window.location.href = '/customer';
        return;
      }

      try {
        // 1. KPIs
        const sumRes = await fetch('/api/person-b/system-summary');
        if (sumRes.ok) {
          const s = await sumRes.json();
          document.getElementById('kpiAUM').innerText = '₹' + s.total_deposits.toLocaleString('en-IN', { minimumFractionDigits: 2 });
          document.getElementById('kpiAccounts').innerText = s.active_accounts;
          document.getElementById('kpiTransfers').innerText = s.total_transactions;
          document.getElementById('kpiAlerts').innerText = s.open_fraud_alerts;
          document.getElementById('kpiOutbox').innerText = s.pending_outbox;
        }

        // 2. Loans
        const loansRes = await fetch('/loans/admin/all', { headers: { 'Authorization': `Bearer ${token}` } });
        if (loansRes.ok) {
          const lData = await loansRes.json();
          renderLoansTable(lData.loans || []);
        }

        // 3. Analytics & Fraud & Logins
        const spendRes = await fetch('/api/person-b/analytics/spending');
        if (spendRes.ok) {
          const sData = await spendRes.json();
          renderChart(sData.spendingByCategory || []);
          renderFraud(sData.fraudAlerts || []);
          renderLogins(sData.loginEvents || []);
        }

        // 4. Accounts List
        const accsRes = await fetch('/accounts/admin/all', { headers: { 'Authorization': `Bearer ${token}` } });
        if (accsRes.ok) {
          const aData = await accsRes.json();
          renderAccountsList(aData.accounts || []);
        }
      } catch (err) {
        console.error(err);
      }
    }

    function renderLoansTable(loans) {
      const tbody = document.getElementById('loanTableBody');
      if (!loans.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-slate-500">No loan applications found.</td></tr>`;
        return;
      }
      tbody.innerHTML = loans.map(l => {
        const isPending = l.status === 'Pending';
        return `
          <tr class="hover:bg-slate-900/60">
            <td class="py-2.5 px-3 font-bold text-slate-300">#${l.loan_id}</td>
            <td class="py-2.5 px-3 text-slate-400">User #${l.user_id}</td>
            <td class="py-2.5 px-3 font-bold text-amber-400">₹${parseFloat(l.loan_amount).toLocaleString()}</td>
            <td class="py-2.5 px-3 text-slate-300">${l.interest_rate}</td>
            <td class="py-2.5 px-3 text-emerald-400">₹${parseFloat(l.monthly_emi).toLocaleString()}/mo</td>
            <td class="py-2.5 px-3">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${l.status === 'Active' ? 'bg-emerald-950 text-emerald-300' : l.status === 'Approved' ? 'bg-blue-950 text-blue-300' : 'bg-amber-950 text-amber-300'}">${l.status}</span>
            </td>
            <td class="py-2.5 px-3 text-right">
              ${isPending ? `
                <button onclick="decideLoan(${l.loan_id}, 'Approved')" class="px-2 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[10px] mr-1">Approve</button>
                <button onclick="decideLoan(${l.loan_id}, 'Rejected')" class="px-2 py-1 rounded bg-rose-600 hover:bg-rose-500 text-white font-bold text-[10px]">Reject</button>
              ` : `<span class="text-[10px] text-slate-500 font-sans">Resolved</span>`}
            </td>
          </tr>
        `;
      }).join('');
    }

    async function decideLoan(id, decision) {
      const token = localStorage.getItem('sb_token');
      try {
        const res = await fetch(`/loans/${id}/status`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ status: decision })
        });
        if (res.ok) {
          showToast('Underwriting Complete', `Loan #${id} marked as ${decision}.`, 'success');
          await loadAdminPortal();
        }
      } catch (e) {
        showToast('Error', e.message);
      }
    }

    function renderChart(spending) {
      const originalLabels = spending.map(i => {
        let cat = (i.category || 'General').trim();
        return cat.replace(/^\[(.*?)\]/, '$1').trim();
      });
      const values = spending.map(i => i.totalSpent);
      const ctx = document.getElementById('adminSpendingChart').getContext('2d');
      if (chartInstance) chartInstance.destroy();

      chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: originalLabels.length ? originalLabels : ['No Data'],
          datasets: [{
            label: 'Total Spend (₹)',
            data: values.length ? values : [0],
            backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4'],
            borderRadius: 8,
            barPercentage: 0.55,
            maxBarThickness: 56,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#090d16',
              borderColor: '#334155',
              borderWidth: 1,
              titleFont: { size: 12, family: "'Plus Jakarta Sans', sans-serif", weight: '700' },
              bodyFont: { size: 12, family: "'JetBrains Mono', monospace" },
              padding: 10,
              callbacks: {
                title: function(items) {
                  return originalLabels[items[0].dataIndex] || '';
                },
                label: function(item) {
                  return '  Total: ₹' + Number(item.raw).toLocaleString('en-IN', { minimumFractionDigits: 2 });
                }
              }
            }
          },
          scales: {
            x: {
              ticks: {
                color: '#cbd5e1',
                font: { size: 11, family: "'Plus Jakarta Sans', sans-serif", weight: '600' },
                maxRotation: 20,
                minRotation: 0,
                autoSkip: false,
                callback: function(val, index) {
                  const lbl = originalLabels[index] || '';
                  return lbl.length > 15 ? lbl.slice(0, 13) + '…' : lbl;
                }
              },
              grid: { display: false }
            },
            y: {
              ticks: {
                color: '#94a3b8',
                font: { size: 10, family: "'JetBrains Mono', monospace" },
                callback: function(val) {
                  return '₹' + (val >= 1000 ? (val / 1000).toFixed(0) + 'k' : val);
                }
              },
              grid: { color: 'rgba(51, 65, 85, 0.4)' }
            }
          }
        }
      });
    }

    function renderFraud(alerts) {
      const c = document.getElementById('fraudList');
      if (!alerts.length) {
        c.innerHTML = `<p class="text-xs text-slate-500 py-4 text-center">No open alerts.</p>`;
        return;
      }
      c.innerHTML = alerts.map(a => `
        <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-start text-xs">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${a.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-300' : 'bg-amber-950 text-amber-300'}">${a.severity}</span>
              <span class="font-bold text-white">${a.category}</span>
              ${a.amount ? `<span class="font-mono text-rose-400 font-bold">₹${a.amount.toLocaleString()}</span>` : ''}
            </div>
            <p class="text-slate-300 mt-1">${a.reason}</p>
          </div>
          <div>
            ${a.status !== 'RESOLVED' ? `
              <button onclick="resolveAlert('${a.id}')" class="px-2 py-1 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 text-[10px] font-bold hover:bg-emerald-900">Resolve</button>
            ` : '<span class="text-[10px] text-emerald-400 font-bold font-mono">Resolved</span>'}
          </div>
        </div>
      `).join('');
    }

    async function resolveAlert(id) {
      try {
        const res = await fetch(`/api/person-b/fraud/alerts/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'RESOLVED' })
        });
        if (res.ok) {
          showToast('Alert Resolved', 'Marked alert as resolved.');
          await loadAdminPortal();
        }
      } catch (e) {
        showToast('Error', e.message);
      }
    }

    function renderAccountsList(accounts) {
      const c = document.getElementById('adminAccountsList');
      c.innerHTML = accounts.map(a => {
        const isFrozen = a.status === 'Frozen';
        return `
          <div class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center text-xs">
            <div>
              <span class="font-bold text-white font-mono">${a.raw_account_number || a.account_number}</span>
              <span class="text-slate-400 ml-1">(${a.account_type})</span>
              <span class="block text-emerald-400 font-mono font-semibold">₹${parseFloat(a.balance).toLocaleString()}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isFrozen ? 'bg-rose-950 text-rose-300' : 'bg-emerald-950 text-emerald-300'}">${a.status}</span>
              <button onclick="toggleFreeze(${a.account_id}, '${isFrozen ? 'Active' : 'Frozen'}')" class="px-2 py-1 rounded bg-slate-800 text-slate-200 text-[10px] font-bold hover:bg-slate-700">
                ${isFrozen ? 'Unfreeze' : 'Freeze'}
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    async function toggleFreeze(id, status) {
      const token = localStorage.getItem('sb_token');
      try {
        const res = await fetch(`/accounts/${id}/status`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ status: status })
        });
        if (res.ok) {
          showToast('Updated', `Account status set to ${status}.`);
          await loadAdminPortal();
        }
      } catch (e) {
        showToast('Error', e.message);
      }
    }

    function renderLogins(logins) {
      const c = document.getElementById('loginEventsList');
      c.innerHTML = logins.map(l => `
        <div class="p-2 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center text-xs">
          <div>
            <span class="text-slate-200 font-medium">${l.email}</span>
            <span class="text-[10px] text-slate-400 ml-2 font-mono">${l.ip_address}</span>
          </div>
          <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${l.status === 'FAILED' ? 'bg-rose-950 text-rose-300' : 'bg-emerald-950 text-emerald-300'}">${l.status}</span>
        </div>
      `).join('');
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

    async function loadDashboard(suppressToast = false) {
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

        if (!suppressToast && data && data.message) {
          showToast(data.message, 'warning');
        }
      } catch (err) {
        console.error("Dashboard load failed:", err);
        if (!suppressToast) {
          showToast("Notice: MongoDB is currently offline or unreachable. Live analytics will populate once MongoDB is running.", 'warning');
        }
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
      loadDashboard(true);
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
      loadDashboard(true);
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

    async function triggerSync() {
      try {
        const res = await fetch('/api/person-b/outbox/sync', { method: 'POST' });
        const d = await res.json();
        showToast('Outbox Synced', `Delivered ${d.delivered_count} events to MongoDB.`);
        await loadAdminPortal();
      } catch (e) {
        showToast('Error', e.message);
      }
    }

    async function simulateFraud() {
      try {
        await fetch('/api/person-b/fraud/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 2, amount: 85000, category: 'International Wire', description: 'Offshore Crypto Exchange' })
        });
        showToast('Simulation', 'Triggered test high-risk alert.');
        await loadAdminPortal();
      } catch (e) {
        showToast('Error', e.message);
      }
    }

    window.addEventListener('DOMContentLoaded', loadAdminPortal);
  </script>
</body>
</html>
"""

# ==============================================================================
# 4. CENTRAL GATEWAY / DISPATCHER (/dashboard)
# ==============================================================================
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SecureBank Enterprise Core</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #070b14; color: #f1f5f9; }
    .glass-card { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(14px); border: 1px solid rgba(51, 65, 85, 0.6); }
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between p-4 sm:p-8">

  <header class="max-w-6xl mx-auto w-full flex justify-between items-center py-4 border-b border-slate-800">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
        <svg class="w-6 h-6 text-slate-950" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2L2 7v3c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5zm-1 9V8h2v3h-2zm0 4v-2h2v2h-2z"/>
        </svg>
      </div>
      <div>
        <h1 class="text-xl font-bold text-white tracking-tight">Secure<span class="text-emerald-400">Bank</span> Enterprise Core</h1>
        <p class="text-xs text-slate-400">PostgreSQL ACID Core • MongoDB Outbox Replicator • pgvector</p>
      </div>
    </div>
    <a href="/login" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition">
      Go to Login Page →
    </a>
  </header>

  <main class="max-w-5xl mx-auto w-full my-auto py-10 space-y-8">
    <div class="text-center space-y-2">
      <span class="text-xs font-mono font-bold text-emerald-400 uppercase tracking-widest px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">Dedicated Role Portals</span>
      <h2 class="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">Access Your Banking Environment</h2>
      <p class="text-sm text-slate-400 max-w-lg mx-auto">Select a dedicated portal below or sign in with your credentials.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- Customer Portal Card -->
      <div class="glass-card rounded-3xl p-6 sm:p-8 space-y-5 border-2 border-emerald-500/20 hover:border-emerald-500/50 transition">
        <div class="flex justify-between items-center">
          <span class="text-xs font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">Customer Role</span>
          <svg class="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
        </div>
        <div>
          <h3 class="text-xl font-bold text-white">Customer Banking Portal</h3>
          <p class="text-xs text-slate-400 mt-1">Multi-account balances, instant fund transfers, pgvector statement search, and loan calculator.</p>
        </div>
        <div class="pt-2">
          <a href="/customer" class="block w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase tracking-wider text-center transition shadow-lg">
            Open Customer Portal →
          </a>
        </div>
      </div>

      <!-- Admin Portal Card -->
      <div class="glass-card rounded-3xl p-6 sm:p-8 space-y-5 border-2 border-purple-500/20 hover:border-purple-500/50 transition">
        <div class="flex justify-between items-center">
          <span class="text-xs font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/30">Bank Staff / Admin</span>
          <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
        </div>
        <div>
          <h3 class="text-xl font-bold text-white">Admin & Fraud Intelligence Center</h3>
          <p class="text-xs text-slate-400 mt-1">Executive AUM metrics, loan approvals, account freeze controls, real-time fraud queue, and outbox sync.</p>
        </div>
        <div class="pt-2">
          <a href="/admin" class="block w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs uppercase tracking-wider text-center transition shadow-lg">
            Open Admin Center →
          </a>
        </div>
      </div>

    </div>
  </main>

  <footer class="max-w-6xl mx-auto w-full text-center py-4 border-t border-slate-900 text-xs text-slate-500 font-mono">
    SecureBank Enterprise • Dual-Engine Architecture
  </footer>

  <script>
    window.addEventListener('DOMContentLoaded', () => {
      const token = localStorage.getItem('sb_token');
      const userStr = localStorage.getItem('sb_user');
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          if (user.role === 'Admin') window.location.href = '/admin';
          else window.location.href = '/customer';
        } catch (e) {}
      }
    });
  </script>
</body>
</html>
"""

# ==============================================================================
# ROUTE HANDLERS
# ==============================================================================
@router.get("/login", response_class=HTMLResponse)
def get_login_page():
    """Dedicated Clean Login & Registration Page."""
    return LOGIN_HTML

@router.get("/customer", response_class=HTMLResponse)
def get_customer_page():
    """Dedicated Customer Banking Portal."""
    return CUSTOMER_HTML

@router.get("/admin", response_class=HTMLResponse)
def get_admin_page():
    """Dedicated Bank Admin & Fraud Intelligence Portal."""
    return ADMIN_HTML

@router.get("/dashboard", response_class=HTMLResponse)
def get_banking_dashboard():
    """Gateway Portal that routes to Customer or Admin."""
def get_person_b_dashboard():
    return DASHBOARD_HTML
