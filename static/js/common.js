// Common functions for all pages

function getSidebarHTML(currentPage = '') {
    const pages = [
        { id: 'dashboard', name: 'Dashboard', icon: '📊', url: '/dashboard.html' },
        { id: 'goals', name: 'Maqsadlar & Rejalar', icon: '🎯', url: '/goals.html' },
        { id: 'products', name: 'Mahsulotlar', icon: '📦', url: '/products.html' },
        { id: 'suppliers', name: 'Ta\'minotchilar', icon: '🚚', url: '/suppliers.html' },
        { id: 'shops', name: 'Do\'konlar', icon: '🏪', url: '/shops.html' },
        { id: 'regions', name: 'Hududlar & Xarita', icon: '🗺️', url: '/regions.html' },
        { id: 'sales', name: 'Savdo', icon: '💰', url: '/sales.html' },
        { id: 'ai', name: 'AI Tahlil', icon: '🤖', url: '/ai.html' }
    ];
    
    let navHTML = '';
    pages.forEach(page => {
        const activeClass = page.id === currentPage ? 'bg-gray-700' : 'hover:bg-gray-700';
        navHTML += `
            <a href="${page.url}" class="block px-4 py-2 rounded ${activeClass} flex items-center">
                <span class="mr-2">${page.icon}</span> ${page.name}
            </a>
        `;
    });
    
    return `
        <div id="sidebar" class="fixed left-0 top-0 h-full w-64 bg-gray-800 text-white sidebar-transition z-50">
            <div class="p-6">
                <h1 class="text-2xl font-bold mb-8">NGMS</h1>
                <nav class="space-y-2">
                    ${navHTML}
                </nav>
            </div>
            <div class="absolute bottom-0 w-full p-4 border-t border-gray-700">
                <button onclick="logout()" class="w-full px-4 py-2 bg-red-600 rounded hover:bg-red-700">
                    Chiqish
                </button>
            </div>
        </div>
    `;
}

function logout() {
    removeAuthToken();
    window.location.href = '/login.html';
}

function checkAuth() {
    if (!getAuthToken()) {
        window.location.href = '/login.html';
    }
}

function formatNumber(num) {
    return new Intl.NumberFormat('uz-UZ').format(num);
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('uz-UZ');
}

function showModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner mx-auto"></div>';
    }
}

function showError(message) {
    alert(message);
}

function showSuccess(message) {
    alert(message);
}

