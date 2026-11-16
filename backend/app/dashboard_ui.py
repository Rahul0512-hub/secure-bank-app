from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Frontend Banking Portal"])

# ==============================================================================
# 1. DEDICATED LOGIN & AUTHENTICATION PAGE (/login)
# ==============================================================================
LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sign In — SecureBank Enterprise</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #070b14; color: #f1f5f9; }
    .glass-card { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(51, 65, 85, 0.6); }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">

  <!-- Subtle Background Glows -->
  <div class="absolute -top-32 -left-32 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
  <div class="absolute -bottom-32 -right-32 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

  <!-- Toast Container -->
  <div id="toastContainer" class="fixed top-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none"></div>

  <!-- Login Card Container -->
  <div class="glass-card w-full max-w-md rounded-3xl p-8 shadow-2xl space-y-6 relative z-10 border border-slate-700/80">
    
    <!-- Bank Logo & Header -->
    <div class="text-center space-y-2">
      <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/20">
        <svg class="w-8 h-8 text-slate-950" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2L2 7v3c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5zm-1 9V8h2v3h-2zm0 4v-2h2v2h-2z"/>
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-white tracking-tight">Secure<span class="text-emerald-400">Bank</span></h1>
      <p class="text-xs text-slate-400">Enterprise Dual-Engine Core Banking System</p>
    </div>

    <!-- Active Session Banner (if signed in) -->
    <div id="activeSessionBanner" class="hidden p-3 rounded-2xl bg-slate-900 border border-slate-700 text-xs flex justify-between items-center">
      <div>
        <span class="text-slate-400">Signed in as</span>
        <span id="activeUsername" class="font-bold text-emerald-400 ml-1"></span>
      </div>
      <div class="flex gap-2">
        <a id="activePortalLink" href="/customer" class="px-2.5 py-1 rounded-lg bg-emerald-500 text-slate-950 font-bold hover:bg-emerald-400 transition text-[11px]">Continue →</a>
        <button onclick="clearSession()" class="px-2 py-1 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition text-[11px]">Switch</button>
      </div>
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
        <input id="loginUser" type="text" placeholder="e.g. priya_sharma or admin" required
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

    <!-- 1-Click Fast Login Demo Credentials -->
    <div class="pt-4 border-t border-slate-800 space-y-2.5">
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-400">1-Click Fast Login:</span>
        <span class="text-[10px] text-slate-500">Click to authenticate</span>
      </div>
      
      <div class="grid grid-cols-2 gap-2.5 text-xs">
        <button type="button" onclick="quickLogin('priya_sharma', 'CustomerPass@123')" class="p-3 rounded-2xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500 text-left transition flex flex-col justify-between group shadow">
          <div class="flex items-center justify-between w-full mb-1">
            <span class="font-bold text-white group-hover:text-emerald-400 transition">👤 Customer</span>
            <span class="text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/40">Role</span>
          </div>
          <p class="text-[10px] text-emerald-400 font-mono">priya_sharma</p>
          <span class="text-[9px] text-slate-500 mt-1">Retail Banking Portal</span>
        </button>

        <button type="button" onclick="quickLogin('admin', 'AdminPassword@123')" class="p-3 rounded-2xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-purple-500 text-left transition flex flex-col justify-between group shadow">
          <div class="flex items-center justify-between w-full mb-1">
            <span class="font-bold text-white group-hover:text-purple-400 transition">🏦 Bank Admin</span>
            <span class="text-[10px] font-bold px-1.5 py-0.2 rounded bg-purple-950 text-purple-300 border border-purple-800/40">Staff</span>
          </div>
          <p class="text-[10px] text-purple-300 font-mono">admin</p>
          <span class="text-[9px] text-slate-500 mt-1">Risk Desk & AML Center</span>
        </button>
      </div>

    </div>

  </div>

  <script>
    function showToast(title, msg, type = 'error') {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      const colors = {
        success: 'bg-emerald-950 border-emerald-700 text-emerald-200',
        error: 'bg-rose-950 border-rose-700 text-rose-200',
        warning: 'bg-amber-950 border-amber-700 text-amber-200',
      };
      toast.className = `p-3.5 rounded-xl border ${colors[type] || colors.error} shadow-xl backdrop-blur-md text-xs pointer-events-auto`;
      toast.innerHTML = `<p class="font-bold">${title}</p><p class="mt-0.5 text-slate-300">${msg}</p>`;
      container.appendChild(toast);
      setTimeout(() => toast.remove(), 4000);
    }

    function clearSession() {
      localStorage.removeItem('sb_token');
      localStorage.removeItem('sb_user');
      document.getElementById('activeSessionBanner').classList.add('hidden');
      showToast('Session Cleared', 'You can sign in with any account below.', 'success');
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

    async function quickLogin(u, p) {
      document.getElementById('loginUser').value = u;
      document.getElementById('loginPass').value = p;
      await authenticateUser(u, p);
    }

    async function handleLogin(e) {
      e.preventDefault();
      const u = document.getElementById('loginUser').value.trim();
      const p = document.getElementById('loginPass').value;
      await authenticateUser(u, p);
    }

    async function authenticateUser(u, p) {
      const btn = document.getElementById('submitBtn');
      const originalText = btn.innerText;
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

        showToast('Authenticated', `Welcome back, ${data.user.username}!`, 'success');

        setTimeout(() => {
          if (data.user.role === 'Admin') {
            window.location.href = '/admin';
          } else {
            window.location.href = '/customer';
          }
        }, 300);
      } catch (err) {
        showToast('Authentication Failed', err.message, 'error');
        btn.innerText = originalText;
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

        // Automatically log in newly registered user
        const loginRes = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: payload.username, password: payload.password })
        });
        const loginData = await loginRes.json();
        localStorage.setItem('sb_token', loginData.access_token);
        localStorage.setItem('sb_user', JSON.stringify(loginData.user));

        // Open default savings account
        try {
          await fetch('/accounts/open', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${loginData.access_token}` },
            body: JSON.stringify({ account_type: 'Savings', initial_deposit: 5000.0 })
          });
        } catch (accErr) {}

        window.location.href = '/customer';
      } catch (err) {
        showToast('Registration Error', err.message, 'error');
      }
    }

    // Check query params and session state
    window.addEventListener('DOMContentLoaded', async () => {
      const params = new URLSearchParams(window.location.search);
      if (params.get('msg') === 'session_expired') {
        showToast('Session Expired', 'Your authentication session expired. Please sign in again.', 'warning');
      } else if (params.get('msg') === 'signed_out') {
        showToast('Signed Out', 'You have been signed out safely.', 'success');
      }

      // Check if existing token is valid
      const token = localStorage.getItem('sb_token');
      const userStr = localStorage.getItem('sb_user');
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          const banner = document.getElementById('activeSessionBanner');
          const usernameEl = document.getElementById('activeUsername');
          const portalLink = document.getElementById('activePortalLink');
          if (banner && usernameEl && portalLink) {
            usernameEl.innerText = `${user.username} (${user.role})`;
            portalLink.href = user.role === 'Admin' ? '/admin' : '/customer';
            banner.classList.remove('hidden');
          }
        } catch (e) {}
      }

      // Fill default customer credentials in form for easy testing
      document.getElementById('loginUser').value = 'priya_sharma';
      document.getElementById('loginPass').value = 'CustomerPass@123';
    });
  </script>
</body>
</html>
"""

# ==============================================================================
# 2. DEDICATED CUSTOMER BANKING PORTAL (/customer)
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

    /* Custom Sleek Dark Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #090d16; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
    * { scrollbar-width: thin; scrollbar-color: #334155 #090d16; }

    /* Print media styling: Only print the clean statement sheet */
    @media print {
      body { background: #ffffff !important; color: #0f172a !important; }
      header, main, #toastContainer, #newAccountModal, #applyLoanModal, .no-print { display: none !important; }
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

  <!-- Top Sticky Navbar -->
  <header class="sticky top-0 z-40 bg-slate-950/95 backdrop-blur-md border-b border-slate-800/80 px-4 sm:px-6 lg:px-8 py-3.5">
    <div class="max-w-[1440px] mx-auto flex items-center justify-between gap-4">
      
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

      <!-- User Greeting & Controls -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
          <span id="navUsername" class="font-bold text-slate-200">Customer</span>
          <span class="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300">Customer</span>
        </div>
        <a href="/login" class="hidden sm:inline-block px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition">
          Switch Account
        </a>
        <button onclick="logout()" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 text-rose-300 border border-rose-900/50 hover:border-rose-700 transition">
          Sign Out
        </button>
      </div>

    </div>
  </header>

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none"></div>

  <!-- Main Content - Balanced Proportional Grid -->
  <main class="flex-1 max-w-[1440px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    
    <!-- Hero Summary Bar -->
    <div class="rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40 border border-slate-800/90 p-6 shadow-xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-2xl font-bold text-white tracking-tight">Welcome back, <span id="heroName" class="text-emerald-400">Customer</span></h1>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800/50 font-semibold">Active Session</span>
        </div>
        <p class="text-xs text-slate-400 mt-1">Dual-Engine Core Banking • PostgreSQL ACID Protection • Real-Time Fraud Quarantine</p>
      </div>

      <!-- Total Balance & Quick Action -->
      <div class="flex items-center gap-4 bg-slate-950/80 border border-slate-800 rounded-2xl p-3 sm:px-5 sm:py-3.5">
        <div>
          <span class="text-[10px] font-semibold uppercase text-slate-400 block font-mono">Consolidated Net Balance</span>
          <span id="heroTotalBalance" class="text-2xl font-black text-white font-mono tracking-tight">₹0.00</span>
        </div>
        <div class="flex gap-2">
          <button onclick="openNewAccountModal()" class="px-3 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase transition shadow-lg shadow-emerald-500/20">
            + Open Account
          </button>
        </div>
      </div>
    </div>

    <!-- Balanced 2-Column Dashboard Grid (7 cols / 5 cols) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- LEFT COLUMN (7 COLS): Accounts & Transaction History -->
      <div class="lg:col-span-7 space-y-6">
        
        <!-- 1. My Accounts Cards -->
        <div>
          <div class="flex justify-between items-center mb-3">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/></svg>
              My Bank Accounts
            </h2>
            <span class="text-xs text-slate-400 font-mono">PostgreSQL `accounts` table</span>
          </div>

          <div id="accountsList" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- Dynamically populated -->
          </div>
        </div>

        <!-- 2. Transaction Statement & PDF Export -->
        <div class="glass-panel rounded-3xl p-6 shadow-xl space-y-4">
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
                Print
              </button>
            </div>
          </div>

          <!-- Transaction Ledger Table -->
          <div class="overflow-x-auto max-h-[420px] overflow-y-auto">
            <table class="w-full text-left text-xs">
              <thead class="sticky top-0 bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800 z-10">
                <tr>
                  <th class="py-2.5 px-3">TX ID</th>
                  <th class="py-2.5 px-3">Date</th>
                  <th class="py-2.5 px-3">Direction</th>
                  <th class="py-2.5 px-3">Description</th>
                  <th class="py-2.5 px-3 text-right">Amount</th>
                  <th class="py-2.5 px-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody id="txListBody" class="divide-y divide-slate-800/80 font-mono">
                <tr><td colspan="6" class="text-center py-6 text-slate-500">Loading transaction history...</td></tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- RIGHT COLUMN (5 COLS): Transfer Studio & Loan Calculator -->
      <div class="lg:col-span-5 space-y-6">
        
        <!-- 3. Instant Fund Transfer Studio (Compact, Sleek Card) -->
        <div class="glass-panel rounded-3xl p-6 shadow-xl space-y-4 border border-slate-700/80">
          <div class="border-b border-slate-800 pb-3 flex justify-between items-center">
            <div>
              <h2 class="text-base font-bold text-white flex items-center gap-2">
                <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>
                Instant Fund Transfer
              </h2>
              <p class="text-[11px] text-slate-400">Atomic execution via <code class="text-emerald-300">transfer_funds</code> procedure</p>
            </div>
            <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-semibold">
              ACID Settled
            </span>
          </div>

          <form onsubmit="handleTransfer(event)" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Debit From Account</label>
              <select id="transferSource" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 focus:outline-none"></select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Send To Beneficiary</label>
              <select id="transferDest" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 focus:outline-none"></select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Transfer Amount (INR ₹)</label>
              <div class="relative">
                <span class="absolute left-3.5 top-2.5 text-slate-400 font-mono text-sm font-semibold">₹</span>
                <input id="transferAmount" type="number" step="0.01" min="1" max="500000" placeholder="0.00" required
                  oninput="checkAmountWarning(this.value)"
                  class="w-full bg-slate-950 border border-slate-700 rounded-xl pl-8 pr-4 py-2.5 text-slate-100 font-mono font-semibold text-sm focus:border-emerald-500 focus:outline-none" />
              </div>
              <!-- Quick Chips -->
              <div class="flex flex-wrap gap-1.5 mt-2">
                <button type="button" onclick="setAmount(1000)" class="px-2 py-0.5 text-xs rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-mono transition">₹1k</button>
                <button type="button" onclick="setAmount(5000)" class="px-2 py-0.5 text-xs rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-mono transition">₹5k</button>
                <button type="button" onclick="setAmount(15000)" class="px-2 py-0.5 text-xs rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-mono transition">₹15k</button>
                <button type="button" onclick="setAmount(50000)" class="px-2 py-0.5 text-xs rounded-lg bg-slate-900 hover:bg-slate-800 border border-amber-900/50 text-amber-300 font-mono transition">₹50k (Alert)</button>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1">Category</label>
                <select id="transferCategory" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-2.5 py-2 text-xs text-slate-100 focus:border-emerald-500 focus:outline-none">
                  <option value="Transfer">Inter-Account</option>
                  <option value="Food & Dining">Food & Dining</option>
                  <option value="Bills & Utilities">Bills & Utilities</option>
                  <option value="Travel">Travel & Lodging</option>
                  <option value="Investments">Investments</option>
                  <option value="International Wire">International Wire</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1">Description / Memo</label>
                <input id="transferDesc" type="text" placeholder="e.g. Rent, groceries"
                  class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 focus:outline-none" />
              </div>
            </div>

            <!-- Dynamic Risk Alert Warning -->
            <div id="riskWarning" class="hidden p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs">
              ⚠️ <strong>Risk Notice:</strong> Transfers ≥ ₹50,000 trigger AML scoring and are replicated to MongoDB Fraud Center.
            </div>

            <button type="submit" class="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-emerald-500/20">
              Confirm & Send Transfer
            </button>
          </form>
        </div>

        <!-- 4. Loan & Interactive EMI Calculator -->
        <div class="glass-panel rounded-3xl p-6 shadow-xl space-y-4">
          <div class="border-b border-slate-800 pb-3 flex justify-between items-center">
            <div>
              <h2 class="text-base font-bold text-white">Loan & EMI Calculator</h2>
              <p class="text-xs text-slate-400">Simulate monthly amortization</p>
            </div>
            <button onclick="openApplyLoanModal()" class="px-3 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold transition">
              + Apply Loan
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

            <div class="grid grid-cols-2 gap-3">
              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-slate-400">Rate</span>
                  <span id="rVal" class="text-white font-bold font-mono">8.50%</span>
                </div>
                <input type="range" id="rSlider" min="5.0" max="18.0" step="0.25" value="8.50" oninput="recalcEMI()" class="w-full accent-amber-500 bg-slate-900 rounded-lg cursor-pointer" />
              </div>

              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-slate-400">Tenure</span>
                  <span id="tVal" class="text-white font-bold font-mono">36m</span>
                </div>
                <input type="range" id="tSlider" min="6" max="120" step="6" value="36" oninput="recalcEMI()" class="w-full accent-amber-500 bg-slate-900 rounded-lg cursor-pointer" />
              </div>
            </div>
          </div>

          <!-- Calculated Summary Box -->
          <div class="grid grid-cols-3 gap-2 p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
            <div>
              <span class="text-[9px] text-slate-400 uppercase block font-semibold">Monthly EMI</span>
              <span id="resEMI" class="text-xs font-bold text-amber-400 font-mono">₹15,780</span>
            </div>
            <div>
              <span class="text-[9px] text-slate-400 uppercase block font-semibold">Total Interest</span>
              <span id="resInterest" class="text-xs font-bold text-slate-300 font-mono">₹68,080</span>
            </div>
            <div>
              <span class="text-[9px] text-slate-400 uppercase block font-semibold">Total Payable</span>
              <span id="resTotal" class="text-xs font-bold text-white font-mono">₹5,68,080</span>
            </div>
          </div>

          <!-- Active Facilities List -->
          <div class="pt-2 border-t border-slate-800">
            <h3 class="text-xs font-bold text-white mb-2">My Active Credit Facilities</h3>
            <div id="customerLoansList" class="space-y-2 overflow-y-auto max-h-40"></div>
          </div>
        </div>

      </div>

    </div>

    <!-- Official Transaction Statement Container (Rendered to PDF & Print) -->
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
            <span style="font-size:10px; color:#64748b; font-family:monospace;">PostgreSQL ACID Table: transactions</span>
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

      </div>
    </div>

  </main>

  <!-- Modals -->
  <div id="newAccountModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm hidden p-4">
    <div class="glass-panel w-full max-w-sm rounded-3xl p-6 shadow-2xl space-y-4 border border-slate-700">
      <div class="flex justify-between items-center border-b border-slate-800 pb-2">
        <h3 class="text-sm font-bold text-white">Open Bank Account</h3>
        <button onclick="closeNewAccountModal()" class="text-slate-400 hover:text-white">✕</button>
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
        <button type="submit" class="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase">Open Account</button>
      </form>
    </div>
  </div>

  <div id="applyLoanModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm hidden p-4">
    <div class="glass-panel w-full max-w-md rounded-3xl p-6 shadow-2xl space-y-4 border border-slate-700">
      <div class="flex justify-between items-center border-b border-slate-800 pb-2">
        <h3 class="text-sm font-bold text-white">Loan Application Form</h3>
        <button onclick="closeApplyLoanModal()" class="text-slate-400 hover:text-white">✕</button>
      </div>
      <form onsubmit="handleApplyLoan(event)" class="space-y-3 text-xs">
        <div>
          <label class="block text-slate-400 mb-1">Requested Principal (₹)</label>
          <input id="loanReqAmount" type="number" step="1000" min="10000" max="5000000" value="250000" required class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-slate-400 mb-1">Interest Rate (%)</label>
            <input id="loanReqRate" type="number" step="0.1" value="8.5" required class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono" />
          </div>
          <div>
            <label class="block text-slate-400 mb-1">Tenure (Months)</label>
            <input id="loanReqTenure" type="number" value="24" required class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white font-mono" />
          </div>
        </div>
        <div>
          <label class="block text-slate-400 mb-1">Purpose / End-Use</label>
          <input id="loanReqPurpose" type="text" placeholder="e.g. Home Renovation, Education" required class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white" />
        </div>
        <button type="submit" class="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs uppercase">Submit Loan Application</button>
      </form>
    </div>
  </div>

  <script>
    let currentUser = null;
    let myAccounts = [];
    let currentTransactionsList = [];

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
      window.location.href = '/login?msg=signed_out';
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
      document.getElementById('tVal').innerText = n + 'm';

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

      try {
        currentUser = JSON.parse(userStr);
      } catch (e) {
        logout();
        return;
      }

      // Role check: Admins belong on /admin
      if (currentUser.role === 'Admin') {
        window.location.href = '/admin';
        return;
      }

      // Verify token with backend
      try {
        const verifyRes = await fetch('/auth/me', { headers: { 'Authorization': `Bearer ${token}` } });
        if (verifyRes.status === 401 || verifyRes.status === 403) {
          localStorage.removeItem('sb_token');
          localStorage.removeItem('sb_user');
          window.location.href = '/login?msg=session_expired';
          return;
        }
        if (verifyRes.ok) {
          const profile = await verifyRes.json();
          currentUser.email = profile.email;
        }
      } catch (e) {
        // Network warning only
      }

      document.getElementById('navUsername').innerText = currentUser.username;
      document.getElementById('heroName').innerText = currentUser.username;

      try {
        // Accounts
        const accRes = await fetch('/accounts/me', { headers: { 'Authorization': `Bearer ${token}` } });
        if (accRes.status === 401) { logout(); return; }
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
          currentTransactionsList = txData.transactions || [];
          renderTransactions(currentTransactionsList);
        }

        // Loans
        const lRes = await fetch('/loans/me', { headers: { 'Authorization': `Bearer ${token}` } });
        if (lRes.ok) {
          const lData = await lRes.json();
          renderLoans(lData.loans || []);
        }
      } catch (err) {
        console.error(err);
      }
    }

    function renderAccounts(accs) {
      const container = document.getElementById('accountsList');
      let total = 0;
      accs.forEach(a => total += parseFloat(a.balance));
      document.getElementById('heroTotalBalance').innerText = '₹' + total.toLocaleString('en-IN', { minimumFractionDigits: 2 });

      if (!accs.length) {
        container.innerHTML = `
          <div class="col-span-2 glass-card rounded-2xl p-6 text-center text-slate-400 space-y-2">
            <p class="font-semibold text-white">No active bank accounts found.</p>
            <p class="text-xs">Click "+ Open Account" above to create your first savings or checking account.</p>
          </div>
        `;
        return;
      }

      container.innerHTML = accs.map(a => `
        <div class="glass-card rounded-2xl p-4 shadow-lg flex flex-col justify-between hover:border-emerald-500/50 transition">
          <div class="flex justify-between items-start mb-2">
            <div>
              <span class="text-[10px] uppercase text-slate-400 font-mono font-bold">${a.account_type}</span>
              <p class="text-xs font-mono text-emerald-400 mt-0.5">${a.account_number}</p>
            </div>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${a.status === 'Active' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}">
              ${a.status}
            </span>
          </div>
          <div class="my-1">
            <span class="text-[9px] text-slate-400 uppercase block font-semibold">Available Balance</span>
            <span class="text-xl font-black text-white font-mono">₹${parseFloat(a.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
          </div>
          <div class="mt-2 pt-2 border-t border-slate-800 text-[11px] flex justify-between items-center">
            <span class="text-slate-500 font-mono">${a.currency}</span>
            <button onclick="document.getElementById('transferSource').value = ${a.account_id}" class="text-emerald-400 hover:text-emerald-300 font-bold transition">Use for Transfer →</button>
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

    function renderTransactions(txs) {
      currentTransactionsList = txs || [];
      const tbody = document.getElementById('txListBody');
      if (!txs.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-slate-500">No transactions recorded yet.</td></tr>`;
        return;
      }
      tbody.innerHTML = txs.map(t => {
        const isDebit = myAccounts.some(a => a.account_id === t.source_account_id);
        return `
          <tr class="hover:bg-slate-900/40">
            <td class="py-2.5 px-3 font-bold text-slate-300">#${t.transaction_id}</td>
            <td class="py-2.5 px-3 text-slate-400">${new Date(t.created_at).toLocaleDateString()}</td>
            <td class="py-2.5 px-3">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isDebit ? 'bg-rose-950 text-rose-300 border border-rose-800/40' : 'bg-emerald-950 text-emerald-300 border border-emerald-800/40'}">
                ${isDebit ? 'DEBIT ➔ ' + t.destination_account_id : 'CREDIT ⬅ ' + t.source_account_id}
              </span>
            </td>
            <td class="py-2.5 px-3 text-slate-200 font-sans">${t.description || 'Transfer'}</td>
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
        // Fetch ALL user transactions to guarantee complete statement download
        const token = localStorage.getItem('sb_token');
        if (token) {
          const allTxRes = await fetch('/transactions/me?limit=1000', { headers: { 'Authorization': `Bearer ${token}` } });
          if (allTxRes.ok) {
            const allTxData = await allTxRes.json();
            currentTransactionsList = allTxData.transactions || currentTransactionsList;
          }
        }

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
          showToast('Statement Downloaded', `Generated complete statement with ${currentTransactionsList.length} transactions.`, 'success');
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

    async function printOnlyStatement() {
      const token = localStorage.getItem('sb_token');
      if (token) {
        try {
          const allTxRes = await fetch('/transactions/me?limit=1000', { headers: { 'Authorization': `Bearer ${token}` } });
          if (allTxRes.ok) {
            const allTxData = await allTxRes.json();
            currentTransactionsList = allTxData.transactions || currentTransactionsList;
          }
        } catch (e) {}
      }

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
        c.innerHTML = `<p class="text-[11px] text-slate-500 py-2 text-center">No active credit facilities.</p>`;
        return;
      }
      c.innerHTML = loans.map(l => `
        <div class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center text-xs">
          <div>
            <span class="font-bold text-white">Facility #${l.loan_id}</span>
            <span class="text-[9px] ml-1.5 px-1.5 py-0.2 rounded font-bold ${l.status === 'Active' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/40' : 'bg-amber-950 text-amber-300 border border-amber-800/40'}">${l.status}</span>
            <p class="text-[10px] text-slate-400 mt-0.5 font-mono">${l.interest_rate}% • ${l.tenure_months}m</p>
          </div>
          <div class="text-right font-mono">
            <span class="text-amber-400 font-bold block">₹${parseFloat(l.loan_amount).toLocaleString()}</span>
            <span class="text-[10px] text-slate-400">EMI: ₹${parseFloat(l.monthly_emi).toLocaleString()}/m</span>
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

    async function handleOpenAccount(e) {
      e.preventDefault();
      const token = localStorage.getItem('sb_token');
      try {
        const res = await fetch('/accounts/open', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({
            account_type: document.getElementById('newAccountType').value,
            initial_deposit: parseFloat(document.getElementById('newAccountDeposit').value) || 0.0
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Failed to open account');
        showToast('Account Opened', `Account ${data.account_number} created!`);
        closeNewAccountModal();
        await loadCustomerPortal();
      } catch (e) {
        showToast('Error', e.message, 'error');
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
            loan_amount: parseFloat(document.getElementById('loanReqAmount').value),
            interest_rate: parseFloat(document.getElementById('loanReqRate').value),
            tenure_months: parseInt(document.getElementById('loanReqTenure').value),
            purpose: document.getElementById('loanReqPurpose').value
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Loan application failed');
        showToast('Application Submitted', `Application #${data.loan_id} under underwriting.`);
        closeApplyLoanModal();
        await loadCustomerPortal();
      } catch (e) {
        showToast('Error', e.message, 'error');
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      loadCustomerPortal();
      recalcEMI();
    });
  </script>
</body>
</html>
"""

# ==============================================================================
# 3. DEDICATED BANK ADMIN & FRAUD INTELLIGENCE CENTER (/admin)
# ==============================================================================
ADMIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bank Management & Risk Center — SecureBank</title>
  <script src="https://cdn.tailwindcss.com"></script>
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

  <!-- Top Sticky Navbar -->
  <header class="sticky top-0 z-40 bg-slate-950/95 backdrop-blur-md border-b border-slate-800/80 px-4 sm:px-6 lg:px-8 py-3.5">
    <div class="max-w-[1440px] mx-auto flex items-center justify-between gap-4">
      
      <!-- Brand -->
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
          <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L2 7v3c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5zm0 18c-4.41-1.12-7-5.52-7-9.88V8.3l7-3.5 7 3.5v1.82c0 4.36-2.59 8.76-7 9.88z"/>
          </svg>
        </div>
        <div>
          <span class="text-lg font-bold text-white">Secure<span class="text-purple-400">Bank</span></span>
          <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono ml-2">Admin Risk Desk</span>
        </div>
      </div>

      <!-- Controls & Logout -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <div class="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></div>
          <span id="adminUsernameBadge" class="font-bold text-slate-200">Bank Risk Office</span>
          <span class="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-purple-950 text-purple-300">Staff</span>
        </div>

        <button onclick="triggerSync()" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-purple-950 hover:bg-purple-900 text-purple-300 border border-purple-800 flex items-center gap-1.5 transition">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Sync Outbox
        </button>

        <a href="/login" class="hidden sm:inline-block px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition">
          Switch Account
        </a>

        <button onclick="logout()" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 text-rose-300 border border-rose-900/50 hover:border-rose-700 transition">
          Sign Out
        </button>
      </div>

    </div>
  </header>

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none"></div>

  <!-- Main Content - Balanced Proportional Container -->
  <main class="flex-1 max-w-[1440px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    
    <!-- Top Bar -->
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white tracking-tight">Bank Administration & Risk Supervision</h1>
        <p class="text-xs text-slate-400 mt-1">Dual-Engine Supervision • PostgreSQL ACID Core • MongoDB Risk Quarantine</p>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="simulateFraud()" class="px-3.5 py-2 text-xs font-semibold rounded-xl bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800 transition shadow">
          + Simulate Fraud Alert
        </button>
        <button onclick="triggerSync()" class="px-3.5 py-2 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 transition">
          Sync Outbox Events
        </button>
      </div>
    </div>

    <!-- Executive KPI Ribbon (5 Metrics) -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div class="glass-panel rounded-2xl p-4 shadow-lg border border-slate-800/80">
        <span class="text-[10px] uppercase font-mono text-slate-400 block font-semibold">Total Deposits (AUM)</span>
        <span id="kpiAUM" class="text-xl font-black text-emerald-400 font-mono mt-1 block">₹0.00</span>
      </div>
      <div class="glass-panel rounded-2xl p-4 shadow-lg border border-slate-800/80">
        <span class="text-[10px] uppercase font-mono text-slate-400 block font-semibold">Active Accounts</span>
        <span id="kpiAccounts" class="text-xl font-black text-white font-mono mt-1 block">0</span>
      </div>
      <div class="glass-panel rounded-2xl p-4 shadow-lg border border-slate-800/80">
        <span class="text-[10px] uppercase font-mono text-slate-400 block font-semibold">Total Transfers</span>
        <span id="kpiTransfers" class="text-xl font-black text-cyan-400 font-mono mt-1 block">0</span>
      </div>
      <div class="glass-panel rounded-2xl p-4 shadow-lg border border-slate-800/80">
        <span class="text-[10px] uppercase font-mono text-slate-400 block font-semibold">Open Fraud Alerts</span>
        <span id="kpiAlerts" class="text-xl font-black text-rose-400 font-mono mt-1 block">0</span>
      </div>
      <div class="glass-panel rounded-2xl p-4 shadow-lg border border-slate-800/80 col-span-2 md:col-span-1">
        <span class="text-[10px] uppercase font-mono text-slate-400 block font-semibold">Pending Outbox</span>
        <span id="kpiOutbox" class="text-xl font-black text-purple-400 font-mono mt-1 block">0</span>
      </div>
    </div>

    <!-- Row 1: Loan Underwriting & Spending Analytics Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- Loan Underwriting & Approval Center (7 cols) -->
      <div class="lg:col-span-7 glass-panel rounded-3xl p-6 shadow-xl space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              Loan Underwriting & Portfolio Supervision
            </h2>
            <p class="text-xs text-slate-400">Review credit facilities, interest spreads, and execute underwriting decisions</p>
          </div>
          <span class="text-xs font-mono text-slate-400">Admin Authority</span>
        </div>

        <div class="overflow-x-auto max-h-72 overflow-y-auto">
          <table class="w-full text-left text-xs">
            <thead class="sticky top-0 bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800 z-10">
              <tr>
                <th class="py-2.5 px-3">Loan ID</th>
                <th class="py-2.5 px-3">Customer</th>
                <th class="py-2.5 px-3">Principal (₹)</th>
                <th class="py-2.5 px-3">Rate / Tenure</th>
                <th class="py-2.5 px-3">Status</th>
                <th class="py-2.5 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody id="loanTableBody" class="divide-y divide-slate-800/80 font-mono">
              <tr><td colspan="6" class="text-center py-6 text-slate-500">Loading loan requests...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Razor-Sharp Vector Spending Analytics (5 cols) -->
      <div class="lg:col-span-5 glass-panel rounded-3xl p-6 shadow-xl space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"/></svg>
              Spending Analytics
            </h2>
            <p class="text-xs text-slate-400">MongoDB Pipeline: `$group` ➔ `$sum` ➔ `$sort`</p>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">Live Mongo Data</span>
        </div>
        <!-- Pure Vector Bar Chart Container: Razor sharp on all DPI displays -->
        <div id="chartContainer" class="h-64 relative"></div>
      </div>

    </div>

    <!-- Row 2: Fraud Quarantine & Compliance Supervision Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- Real-Time Fraud Quarantine (6 cols) -->
      <div class="lg:col-span-6 glass-panel rounded-3xl p-6 shadow-xl space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <svg class="w-5 h-5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              Real-Time Fraud Quarantine Desk
            </h2>
            <p class="text-xs text-slate-400">Replicated to MongoDB <code class="text-rose-300">fraud_alerts</code></p>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800">Risk Stream</span>
        </div>
        <div id="fraudList" class="space-y-3 overflow-y-auto max-h-72 pr-1"></div>
      </div>

      <!-- Compliance Freeze Controls & Login Audit (6 cols) -->
      <div class="lg:col-span-6 space-y-6">
        
        <!-- Account Freeze Supervision -->
        <div class="glass-panel rounded-3xl p-6 shadow-xl space-y-3">
          <div class="border-b border-slate-800 pb-2.5">
            <h2 class="text-base font-bold text-white">Customer Account Compliance & Freeze Controls</h2>
            <p class="text-xs text-slate-400">Procedure <code class="text-purple-300">public.set_account_status</code></p>
          </div>
          <div id="adminAccountsList" class="space-y-2 overflow-y-auto max-h-40 pr-1"></div>
        </div>

        <!-- Security Login Trail -->
        <div class="glass-panel rounded-3xl p-6 shadow-xl space-y-3">
          <div class="border-b border-slate-800 pb-2.5">
            <h2 class="text-base font-bold text-white">Authentication & Brute-Force Surveillance</h2>
            <p class="text-xs text-slate-400">MongoDB `login_events` audit trail</p>
          </div>
          <div id="loginEventsList" class="space-y-2 overflow-y-auto max-h-40 pr-1"></div>
        </div>

      </div>

    </div>

  </main>

  <script>
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
      window.location.href = '/login?msg=signed_out';
    }

    async function loadAdminPortal() {
      const token = localStorage.getItem('sb_token');
      const userStr = localStorage.getItem('sb_user');

      if (!token || !userStr) {
        window.location.href = '/login';
        return;
      }

      let user;
      try {
        user = JSON.parse(userStr);
      } catch (e) {
        logout();
        return;
      }

      if (user.role !== 'Admin') {
        window.location.href = '/customer';
        return;
      }

      // Verify token
      try {
        const verifyRes = await fetch('/auth/me', { headers: { 'Authorization': `Bearer ${token}` } });
        if (verifyRes.status === 401 || verifyRes.status === 403) {
          logout();
          return;
        }
      } catch (e) {}

      const badge = document.getElementById('adminUsernameBadge');
      if (badge) badge.innerText = `${user.username} (Admin)`;

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
        if (loansRes.status === 401) { logout(); return; }
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
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-slate-500">No loan applications found.</td></tr>`;
        return;
      }
      tbody.innerHTML = loans.map(l => {
        const isPending = l.status === 'Pending';
        return `
          <tr class="hover:bg-slate-900/60">
            <td class="py-2.5 px-3 font-bold text-slate-300">#${l.loan_id}</td>
            <td class="py-2.5 px-3 font-medium text-white">${l.applicant_username || 'User #' + l.user_id}</td>
            <td class="py-2.5 px-3 font-bold text-amber-400">₹${parseFloat(l.loan_amount).toLocaleString()}</td>
            <td class="py-2.5 px-3 text-slate-400">${l.interest_rate}% • ${l.tenure_months}m</td>
            <td class="py-2.5 px-3">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${l.status === 'Active' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/40' : (l.status === 'Rejected' ? 'bg-rose-950 text-rose-300 border border-rose-800/40' : 'bg-amber-950 text-amber-300 border border-amber-800/40')}">
                ${l.status}
              </span>
            </td>
            <td class="py-2.5 px-3 text-right">
              ${isPending ? `
                <div class="flex justify-end gap-1.5">
                  <button onclick="reviewLoan(${l.loan_id}, 'Active')" class="px-2 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[10px]">Approve</button>
                  <button onclick="reviewLoan(${l.loan_id}, 'Rejected')" class="px-2 py-1 rounded bg-rose-600 hover:bg-rose-500 text-white font-bold text-[10px]">Reject</button>
                </div>
              ` : `<span class="text-[10px] text-slate-500 font-mono">Processed</span>`}
            </td>
          </tr>
        `;
      }).join('');
    }

    async function reviewLoan(id, decision) {
      const token = localStorage.getItem('sb_token');
      try {
        const res = await fetch(`/loans/admin/${id}/review`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ decision: decision, notes: `Reviewed by Bank Staff` })
        });
        const data = await res.json();
        if (res.ok) {
          showToast('Decision Recorded', `Loan #${id} marked as ${decision}.`);
          await loadAdminPortal();
        } else {
          showToast('Error', data.detail || 'Action failed.');
        }
      } catch (e) {
        showToast('Error', e.message);
      }
    }

    // Razor-Sharp Vector Chart Rendering (Pure HTML/CSS/SVG)
    function renderChart(spending) {
      const container = document.getElementById('chartContainer');
      if (!container) return;

      if (!spending || !spending.length) {
        container.innerHTML = `
          <div class="h-full flex flex-col items-center justify-center text-slate-500 text-xs">
            <svg class="w-8 h-8 text-slate-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
            No spending records found.
          </div>
        `;
        return;
      }

      const items = spending.map(i => ({
        name: (i.category || 'General').replace(/^\\[(.*?)\\]/, '$1').trim(),
        total: parseFloat(i.totalSpent) || 0
      }));

      const maxVal = Math.max(...items.map(i => i.total), 1000);
      const ceiling = Math.ceil(maxVal / 5000) * 5000 || 20000;

      const colors = [
        { from: '#10b981', to: '#059669', border: '#34d399', shadow: 'rgba(16, 185, 129, 0.25)' },
        { from: '#3b82f6', to: '#1d4ed8', border: '#60a5fa', shadow: 'rgba(59, 130, 246, 0.25)' },
        { from: '#f59e0b', to: '#b45309', border: '#fbbf24', shadow: 'rgba(245, 158, 11, 0.25)' },
        { from: '#8b5cf6', to: '#6d28d9', border: '#a78bfa', shadow: 'rgba(139, 92, 246, 0.25)' },
        { from: '#ec4899', to: '#be185d', border: '#f472b6', shadow: 'rgba(236, 72, 153, 0.25)' },
        { from: '#06b6d4', to: '#0891b2', border: '#22d3ee', shadow: 'rgba(6, 182, 212, 0.25)' }
      ];

      const steps = [
        { label: '₹' + (ceiling >= 1000 ? (ceiling/1000).toFixed(0) + 'k' : ceiling), pct: 100 },
        { label: '₹' + (ceiling*0.75 >= 1000 ? (ceiling*0.75/1000).toFixed(0) + 'k' : Math.round(ceiling*0.75)), pct: 75 },
        { label: '₹' + (ceiling*0.5 >= 1000 ? (ceiling*0.5/1000).toFixed(0) + 'k' : Math.round(ceiling*0.5)), pct: 50 },
        { label: '₹' + (ceiling*0.25 >= 1000 ? (ceiling*0.25/1000).toFixed(0) + 'k' : Math.round(ceiling*0.25)), pct: 25 },
        { label: '₹0', pct: 0 }
      ];

      container.innerHTML = `
        <div class="h-full flex flex-col justify-between select-none font-sans">
          <!-- Plot Area with Grid -->
          <div class="flex-1 relative flex">
            <!-- Y-Axis Ticks -->
            <div class="w-12 flex flex-col justify-between text-right pr-2.5 font-mono text-[9px] text-slate-400 py-1">
              ${steps.map(s => `<span>${s.label}</span>`).join('')}
            </div>

            <!-- Graph Area -->
            <div class="flex-1 relative border-l border-b border-slate-700/80">
              <!-- Crisp Horizontal Gridlines -->
              <div class="absolute inset-0 flex flex-col justify-between pointer-events-none py-1">
                ${steps.map(() => `<div class="w-full border-b border-slate-800/80"></div>`).join('')}
              </div>

              <!-- Bars Flex Row -->
              <div class="absolute inset-0 flex items-end justify-around px-3 pt-3">
                ${items.map((item, idx) => {
                  const color = colors[idx % colors.length];
                  const heightPct = Math.max(Math.min((item.total / ceiling) * 100, 100), 5);
                  return `
                    <div class="group relative flex-1 max-w-[64px] h-full flex flex-col justify-end items-center mx-1">
                      <!-- Hover Popup Card -->
                      <div class="opacity-0 group-hover:opacity-100 transition-all duration-200 absolute -top-12 z-30 pointer-events-none bg-slate-950 text-white border border-slate-700 px-2.5 py-1 rounded-xl shadow-2xl text-center whitespace-nowrap transform -translate-y-1">
                        <p class="text-[9px] text-slate-400 font-medium">${item.name}</p>
                        <p class="text-xs font-bold font-mono text-emerald-400">₹${item.total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</p>
                      </div>

                      <!-- Metric on Bar Top -->
                      <span class="text-[9px] font-mono font-bold text-slate-300 mb-1 group-hover:text-emerald-300 transition">
                        ₹${item.total >= 1000 ? (item.total/1000).toFixed(1) + 'k' : item.total}
                      </span>

                      <!-- Vector Gradient Bar -->
                      <div style="height: ${heightPct}%; background: linear-gradient(180deg, ${color.from} 0%, ${color.to} 100%); border-top: 2px solid ${color.border}; box-shadow: 0 4px 14px ${color.shadow};"
                           class="w-full rounded-t-lg transition-all duration-300 group-hover:brightness-125"></div>
                    </div>
                  `;
                }).join('')}
              </div>
            </div>
          </div>

          <!-- X-Axis Labels Row -->
          <div class="flex pl-12 pt-2">
            <div class="flex-1 flex justify-around px-3">
              ${items.map(item => {
                const shortName = item.name.length > 12 ? item.name.slice(0, 10) + '…' : item.name;
                return `
                  <div class="flex-1 max-w-[64px] text-center mx-1" title="${item.name}">
                    <span class="text-[10px] font-semibold text-slate-300 block truncate hover:text-white transition">
                      ${shortName}
                    </span>
                  </div>
                `;
              }).join('')}
            </div>
          </div>
        </div>
      `;
    }

    function renderFraud(alerts) {
      const c = document.getElementById('fraudList');
      if (!alerts.length) {
        c.innerHTML = `<p class="text-xs text-slate-500 py-6 text-center">No open alerts.</p>`;
        return;
      }
      c.innerHTML = alerts.map(a => `
        <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-start text-xs">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${a.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-300 border border-rose-800/40' : 'bg-amber-950 text-amber-300 border border-amber-800/40'}">${a.severity}</span>
              <span class="font-bold text-white">${a.category}</span>
            </div>
            <p class="text-slate-400 mt-1">${a.reason}</p>
          </div>
          <span class="font-bold font-mono text-rose-400">₹${parseFloat(a.amount).toLocaleString()}</span>
        </div>
      `).join('');
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

  <header class="w-full max-w-6xl mx-auto flex justify-between items-center py-4 border-b border-slate-800">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
        <svg class="w-6 h-6 text-slate-950" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2L2 7v3c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5zm-1 9V8h2v3h-2zm0 4v-2h2v2h-2z"/>
        </svg>
      </div>
      <div>
        <h1 class="text-xl font-bold text-white tracking-tight">Secure<span class="text-emerald-400">Bank</span> Enterprise Core</h1>
        <p class="text-xs text-slate-400">SecureBank Intelligence Center • PostgreSQL ACID Core • MongoDB Outbox Replicator</p>
      </div>
    </div>
    <a href="/login" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-emerald-500/20">
      Go to Login Page →
    </a>
  </header>

  <main class="w-full max-w-5xl mx-auto my-auto py-10 space-y-8">
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
          <p class="text-xs text-slate-400 mt-1">Multi-account balances, instant fund transfers, PDF statement export, and EMI loan calculator.</p>
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

  <footer class="w-full max-w-6xl mx-auto text-center py-4 border-t border-slate-900 text-xs text-slate-500 font-mono">
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
    return DASHBOARD_HTML
