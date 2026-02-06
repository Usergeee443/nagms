/**
 * NGMS API Cache — sahifalar orasida ma'lumotlarni saqlash
 * sessionStorage orqali 5 daqiqagacha keshlab turadi
 */
(function(){
var CACHE_TTL = 5 * 60 * 1000; // 5 daqiqa
var CACHE_KEY = 'ngms_cache';

function _getCache() {
    try {
        var raw = sessionStorage.getItem(CACHE_KEY);
        return raw ? JSON.parse(raw) : {};
    } catch(e) { return {}; }
}

function _setCache(cache) {
    try {
        sessionStorage.setItem(CACHE_KEY, JSON.stringify(cache));
    } catch(e) {}
}

/**
 * Keshdan olish
 * @param {string} key — endpoint yoki unikal kalit
 * @returns {any|null} — kesh mavjud va yangi bo'lsa qaytaradi, aks holda null
 */
window.cacheGet = function(key) {
    var cache = _getCache();
    var entry = cache[key];
    if (!entry) return null;
    var now = Date.now();
    if (now - entry.ts > CACHE_TTL) {
        // Muddati o'tgan
        delete cache[key];
        _setCache(cache);
        return null;
    }
    return entry.data;
};

/**
 * Keshga saqlash
 * @param {string} key
 * @param {any} data
 */
window.cacheSet = function(key, data) {
    var cache = _getCache();
    cache[key] = { ts: Date.now(), data: data };
    _setCache(cache);
};

/**
 * Keshni tozalash (ixtiyoriy kalit bo'yicha yoki butunlay)
 * @param {string} [key]
 */
window.cacheClear = function(key) {
    if (key) {
        var cache = _getCache();
        delete cache[key];
        _setCache(cache);
    } else {
        sessionStorage.removeItem(CACHE_KEY);
    }
};

/**
 * Ma'lumot o'zgarganda tegishli keshni tozalash
 * Masalan: savdo qo'shilganda dashboard keshini tozalash
 */
window.cacheInvalidate = function(patterns) {
    if (!patterns) return;
    var cache = _getCache();
    var arr = Array.isArray(patterns) ? patterns : [patterns];
    var changed = false;
    arr.forEach(function(pat) {
        Object.keys(cache).forEach(function(k) {
            if (k.indexOf(pat) !== -1) {
                delete cache[k];
                changed = true;
            }
        });
    });
    if (changed) _setCache(cache);
};
})();
