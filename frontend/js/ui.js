// ─── Toast notification ─────────────────────────────────────────
export function toast(msg, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = msg;
    container.appendChild(el);
    setTimeout(() => el.remove(), 3200);
}

// ─── Date/time helpers ─────────────────────────────────────────
export function formatDate(iso) {
    if (!iso) return '—';
    return new Intl.DateTimeFormat('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit', hour12: true,
    }).format(new Date(iso));
}

export function formatDateShort(iso) {
    if (!iso) return '—';
    return new Intl.DateTimeFormat('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
    }).format(new Date(iso));
}

// ─── Seat progress bar color ────────────────────────────────────
export function seatColor(available, total) {
    if (total === 0) return 'red';
    const ratio = available / total;
    if (ratio > 0.5) return 'green';
    if (ratio > 0.2) return 'yellow';
    return 'red';
}

// ─── Category chip color ─────────────────────────────────────────
export function categoryChip(cat) {
    return `<span class="chip chip-accent">${cat}</span>`;
}

// ─── Seat chip ───────────────────────────────────────────────────
export function seatChip(available, total) {
    const cls = available === 0 ? 'chip-danger' : available <= total * 0.2 ? 'chip-warning' : 'chip-success';
    const label = available === 0 ? 'Full' : `${available} / ${total} seats`;
    return `<span class="chip ${cls}">${label}</span>`;
}

// ─── Build event card HTML ───────────────────────────────────────
export function buildEventCard(ev, registeredIds = new Set()) {
    const fill = ev.total_seats ? Math.round((ev.available_seats / ev.total_seats) * 100) : 0;
    const color = seatColor(ev.available_seats, ev.total_seats);
    const isReg = registeredIds.has(ev.id);
    return `
    <div class="card event-card" onclick="window.location='/event-detail.html?id=${ev.id}'">
      <div class="event-meta">
        ${categoryChip(ev.category)}
        ${seatChip(ev.available_seats, ev.total_seats)}
        ${!ev.is_active ? '<span class="chip chip-muted">Inactive</span>' : ''}
        ${isReg ? '<span class="chip chip-accent">✓ Registered</span>' : ''}
      </div>
      <div class="event-title">${ev.title}</div>
      ${ev.clubs ? `<div class="text-muted" style="font-size:0.82rem">🏫 ${ev.clubs.name}</div>` : ''}
      <div class="event-desc">${ev.description || 'No description provided.'}</div>
      <div class="flex gap-1 items-center mt-1" style="font-size:0.82rem">
        <span class="text-muted">📅 ${formatDate(ev.event_date)}</span>
        ${ev.venue ? `<span class="text-muted" style="margin-left:auto">📍 ${ev.venue}</span>` : ''}
      </div>
      <div class="seat-bar mt-1">
        <div class="seat-bar-fill ${color}" style="width:${fill}%"></div>
      </div>
    </div>`;
}

// ─── Nav update based on auth state ────────────────────────────
import { getUser, isLoggedIn, isAdmin, clearAuth } from './api.js';

export function updateNav() {
    const u = getUser();
    const navAuth = document.getElementById('nav-auth');
    if (!navAuth) return;
    if (isLoggedIn() && u) {
        const dashLink = isAdmin() ? '/admin-dashboard.html' : '/events.html';
        const dashLabel = isAdmin() ? '⚙️ Dashboard' : '📋 Events';
        navAuth.innerHTML = `
      ${isAdmin() ? '<a href="/create-event.html" class="btn btn-primary btn-sm">+ Create Event</a>' : ''}
      <a href="${dashLink}">${dashLabel}</a>
      <a href="/profile.html">👤 Profile</a>
      <button onclick="handleLogout()">Logout</button>`;
    } else {
        navAuth.innerHTML = `
      <button onclick="openModal('login-modal')">Login</button>
      <button class="btn btn-secondary btn-sm" onclick="openModal('signup-modal')">Sign Up</button>
      <a href="/admin-login.html" class="btn btn-primary btn-sm">Create Event</a>`;
    }
}

window.handleLogout = function () {
    clearAuth();
    window.location.href = '/';
};

// ─── Modal helpers ──────────────────────────────────────────────
window.openModal = function (id) {
    document.getElementById(id)?.classList.add('open');
};

window.closeModal = function (id) {
    document.getElementById(id)?.classList.remove('open');
};

// ─── Password visibility toggle ────────────────────────────────
window.togglePassword = function (inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁️';
    }
};

// ─── Calendar renderer ─────────────────────────────────────────
export function renderCalendar(container, year, month, eventDates, onDayClick) {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startWeekday = firstDay.getDay();
    const totalDays = lastDay.getDate();
    const today = new Date();

    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];

    // Build set of dates with events for quick lookup
    const eventDaySet = new Set();
    const eventsByDay = {};
    (eventDates || []).forEach(ev => {
        const d = new Date(ev.event_date);
        if (d.getFullYear() === year && d.getMonth() === month) {
            const day = d.getDate();
            eventDaySet.add(day);
            if (!eventsByDay[day]) eventsByDay[day] = [];
            eventsByDay[day].push(ev);
        }
    });

    let html = `
    <div class="calendar-header">
      <button class="calendar-nav" onclick="calendarNav(-1)">‹</button>
      <h4>${monthNames[month]} ${year}</h4>
      <button class="calendar-nav" onclick="calendarNav(1)">›</button>
    </div>
    <div class="calendar-grid">
      ${'Sun Mon Tue Wed Thu Fri Sat'.split(' ').map(d => `<div class="calendar-day-header">${d}</div>`).join('')}
    `;

    // Empty cells before first day
    for (let i = 0; i < startWeekday; i++) html += '<div class="calendar-day other-month"></div>';

    for (let day = 1; day <= totalDays; day++) {
        const isToday = today.getFullYear() === year && today.getMonth() === month && today.getDate() === day;
        const hasEvent = eventDaySet.has(day);
        const classes = ['calendar-day'];
        if (isToday) classes.push('today');
        if (hasEvent) classes.push('has-event');

        const clickAttr = hasEvent ? `onclick="calendarDayClick(${day})"` : '';
        html += `<div class="${classes.join(' ')}" ${clickAttr}>${day}</div>`;
    }

    html += '</div>';
    container.innerHTML = html;

    // Expose day click handler to window
    window._calendarEventsByDay = eventsByDay;
    window.calendarDayClick = (day) => {
        if (onDayClick && eventsByDay[day]) onDayClick(day, eventsByDay[day]);
    };
}
