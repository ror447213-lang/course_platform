function requireAuth() {
  if (!TokenManager.isLoggedIn()) { window.location.href = '/login.html'; return false; }
  return true;
}

function requireAdmin() {
  if (!TokenManager.isLoggedIn()) { window.location.href = '/login.html'; return false; }
  if (!TokenManager.isAdmin()) { window.location.href = '/dashboard.html'; return false; }
  return true;
}

function redirectIfLoggedIn() {
  if (TokenManager.isLoggedIn()) {
    if (TokenManager.isAdmin()) window.location.href = '/admin/dashboard.html';
    else window.location.href = '/dashboard.html';
    return true;
  }
  return false;
}

function logout() {
  TokenManager.remove();
  TokenManager.removeUser();
  window.location.href = '/index.html';
}

function updateNavigation() {
  const user = TokenManager.getUser();
  const navAuth = document.getElementById('navAuth');
  if (!navAuth) return;
  if (user) {
    navAuth.innerHTML = `
      <li><a href="${user.role === 'admin' ? '/admin/dashboard.html' : '/dashboard.html'}">
        ${user.role === 'admin' ? '⚙️ Admin' : '👤 ' + user.name.split(' ')[0]}
      </a></li>
      <li><a href="#" class="btn-nav" onclick="logout()">Logout</a></li>`;
  } else {
    navAuth.innerHTML = `
      <li><a href="/login.html">Login</a></li>
      <li><a href="/register.html" class="btn-nav">Get Started</a></li>`;
  }
}
