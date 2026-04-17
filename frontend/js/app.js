const Toast = {
  container: null,
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  show(message, type = 'info', duration = 4000) {
    this.init();
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-icon">${icons[type]}</span><span class="toast-message">${message}</span>`;
    this.container.appendChild(toast);
    setTimeout(() => { toast.style.animation = 'slideInRight 0.3s ease reverse'; setTimeout(() => toast.remove(), 300); }, duration);
  },
  success: (msg) => Toast.show(msg, 'success'),
  error: (msg) => Toast.show(msg, 'error'),
  warning: (msg) => Toast.show(msg, 'warning'),
  info: (msg) => Toast.show(msg, 'info'),
};

function setLoading(btn, loading) {
  if (loading) { btn.classList.add('btn-loading'); btn.disabled = true; btn._originalText = btn.innerHTML; }
  else { btn.classList.remove('btn-loading'); btn.disabled = false; if (btn._originalText) btn.innerHTML = btn._originalText; }
}

function formatCurrency(amount) {
  return `₹${Number(amount).toLocaleString('en-IN', { minimumFractionDigits: 0 })}`;
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function statusBadge(status) {
  const map = { pending: { class: 'badge-pending', icon: '🕐', label: 'Pending' }, approved: { class: 'badge-approved', icon: '✅', label: 'Approved' }, rejected: { class: 'badge-rejected', icon: '❌', label: 'Rejected' } };
  const s = map[status] || map.pending;
  return `<span class="badge ${s.class}">${s.icon} ${s.label}</span>`;
}

document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => { navLinks.classList.toggle('open'); });
  }
  document.addEventListener('click', (e) => {
    if (navLinks && !navLinks.contains(e.target) && !hamburger?.contains(e.target)) navLinks.classList.remove('open');
  });
});

function renderCourseCard(course, isPurchased = false) {
  const thumbnailHTML = course.thumbnail_url
    ? `<div class="course-thumbnail"><img src="${course.thumbnail_url}" alt="${course.title}" onerror="this.style.display='none'"></div>`
    : `<div class="course-thumbnail-placeholder">📚</div>`;
  let actionBtn = isPurchased
    ? `<a href="/course_detail.html?id=${course.id}" class="btn btn-accent btn-sm" style="flex:1">📥 Access Course</a>`
    : `<a href="/course_detail.html?id=${course.id}" class="btn btn-ghost btn-sm">Details</a><a href="/payment.html?course_id=${course.id}" class="btn btn-primary btn-sm" style="flex:1">🛒 Buy Now</a>`;
  return `
    <div class="course-card animate-fadeInUp">
      ${thumbnailHTML}
      <div class="course-body">
        <div class="course-price-badge">${formatCurrency(course.price)}</div>
        <h3 class="course-title">${course.title}</h3>
        <p class="course-description">${course.description}</p>
        <div class="course-footer">${actionBtn}</div>
      </div>
    </div>`;
}

function copyToClipboard(text, label = 'Text') {
  navigator.clipboard.writeText(text).then(() => Toast.success(`${label} copied!`)).catch(() => Toast.error('Failed to copy'));
}
