/**
 * NGMS Utility funksiyalari
 */

// O'zbek oy nomlari
var OY_NOMLARI = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun', 'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'];
var OY_QISQA = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'];

/**
 * Sonni formatlash (1234567 -> 1 234 567)
 */
function fmt(n) {
    return new Intl.NumberFormat('uz-UZ').format(n || 0);
}

/**
 * Pul formatlab chiqarish (1234567 -> 1 234 567 so'm)
 */
function fmtC(n) {
    return fmt(n) + " so'm";
}

/**
 * Sana formatlash: 2-Fevral, 2026
 * @param {string|Date} d - sana
 * @param {boolean} showYear - yilni ko'rsatish (default: true)
 * @returns {string}
 */
function fmtD(d, showYear) {
    if (!d) return '-';
    var date = typeof d === 'string' ? new Date(d) : d;
    if (isNaN(date.getTime())) return '-';
    
    var day = date.getDate();
    var month = OY_NOMLARI[date.getMonth()];
    var year = date.getFullYear();
    
    if (showYear === false) {
        return day + '-' + month;
    }
    return day + '-' + month + ', ' + year;
}

/**
 * Qisqa sana formati: 2-Fev
 */
function fmtDShort(d) {
    if (!d) return '-';
    var date = typeof d === 'string' ? new Date(d) : d;
    if (isNaN(date.getTime())) return '-';
    
    var day = date.getDate();
    var month = OY_QISQA[date.getMonth()];
    return day + '-' + month;
}

/**
 * Oy va yil formati: Fevral 2026
 */
function fmtMonth(year, month) {
    return OY_NOMLARI[month - 1] + ' ' + year;
}

/**
 * Toast xabar ko'rsatish
 */
function showToast(message, type) {
    var el = document.createElement('div');
    el.className = 'toast toast-' + (type || 'info');
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(function() { el.remove(); }, 3000);
}
