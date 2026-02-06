(function(){
/* ── SVG Icons ── */
var I = {
    dashboard:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
    products:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><path d="M3.27 6.96L12 12.01l8.73-5.05"/><path d="M12 22.08V12"/></svg>',
    customers:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
    sales:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
    maps:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    regions:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>',
    shops:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    ai:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/></svg>',
    logout:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
    chevron:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>',
    plus:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    more:'<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>'
};

/* ── Nav items ── */
var items = [
    {h:'/dashboard.html', i:'dashboard', l:'Dashboard',  bn:true},
    {h:'/products.html',  i:'products',  l:'Mahsulotlar', bn:false},
    {h:'/customers.html', i:'customers', l:'Mijozlar',   bn:true},
    {h:'/sales.html',     i:'sales',     l:'Savdo',      bn:true},
    {h:'/maps.html',      i:'maps',      l:'Xaritalar',  bn:false},
    {h:'/regions.html',   i:'regions',   l:'Hududlar',   bn:false},
    {h:'/shops.html',     i:'shops',     l:"Do'konlar",  bn:false},
    {h:'/ai.html',        i:'ai',        l:'AI Tahlil',  bn:false}
];

var path = location.pathname;
if(path==='/'||path==='/index.html') path='/dashboard.html';

/* Auth check */
if(typeof getAuthToken==='function' && !getAuthToken() && !path.includes('login')){
    location.href='/login.html'; return;
}
if(path.includes('login')) return; /* login sahifada nav kerak emas */

/* Collapsed state */
if(localStorage.getItem('ngms_sb')==='c') document.documentElement.classList.add('collapsed');

/* ── Build Sidebar ── */
var sideNav = items.map(function(it){
    var ac = path===it.h?' active':'';
    return '<a href="'+it.h+'" class="nav-item'+ac+'" data-tip="'+it.l+'"><span class="nav-icon">'+I[it.i]+'</span><span class="nav-label">'+it.l+'</span></a>';
}).join('');

var sidebar = '<aside class="sidebar" id="sidebar">'
    +'<div class="sidebar-header"><span class="sidebar-logo">NGMS</span>'
    +'<button class="collapse-btn" id="collapseBtn" onclick="window._nav.collapse()"><span class="collapse-icon">'+I.chevron+'</span></button></div>'
    +'<nav class="sidebar-nav">'+sideNav+'</nav>'
    +'<div class="sidebar-footer"><a class="nav-item" data-tip="Chiqish" onclick="window._nav.logout()" style="cursor:pointer"><span class="nav-icon">'+I.logout+'</span><span class="nav-label">Chiqish</span></a></div>'
    +'</aside>';

/* ── Build Bottom Nav ── */
var bnItems = items.filter(function(x){return x.bn});
var bnSales = path==='/sales.html';

function bnItem(it){
    var ac = path===it.h?' active':'';
    return '<a href="'+it.h+'" class="bnav-item'+ac+'">'+I[it.i]+'<span>'+it.l+'</span></a>';
}
var moreActive = !items.some(function(x){return x.bn && path===x.h});

var bottomNav = '<nav class="bottom-nav" id="bottomNav">'
    + bnItem(bnItems[0])
    + bnItem(bnItems[1])
    + '<a class="bnav-fab" id="fabAdd" onclick="window._nav.fab(event)">'+I.plus+'</a>'
    + bnItem(bnItems[2])
    + '<a class="bnav-item'+(moreActive?' active':'')+'" onclick="window._nav.openMore(event)">'+I.more+'<span>Yana</span></a>'
    + '</nav>';

/* ── Build More Menu ── */
var moreItems = items.filter(function(x){return !x.bn});
var moreNav = moreItems.map(function(it){
    var ac = path===it.h?' active':'';
    return '<a href="'+it.h+'" class="more-item'+ac+'"><span class="more-icon">'+I[it.i]+'</span><span>'+it.l+'</span></a>';
}).join('');

var moreMenu = '<div class="more-menu" id="moreMenu"><div class="more-overlay" onclick="window._nav.closeMore()"></div>'
    +'<div class="more-sheet"><div class="more-handle"></div>'
    +moreNav
    +'<div class="more-divider"></div>'
    +'<a class="more-item more-item-danger" onclick="window._nav.logout()" style="cursor:pointer"><span class="more-icon">'+I.logout+'</span><span>Chiqish</span></a>'
    +'</div></div>';

/* ── Inject ── */
document.body.insertAdjacentHTML('afterbegin', sidebar);
document.body.insertAdjacentHTML('beforeend', bottomNav + moreMenu);

/* ── API ── */
window._nav = {
    collapse: function(){
        document.documentElement.classList.toggle('collapsed');
        localStorage.setItem('ngms_sb', document.documentElement.classList.contains('collapsed')?'c':'e');
    },
    logout: function(){
        if(typeof cacheClear==='function') cacheClear(); // Keshni tozalash
        if(typeof removeAuthToken==='function') removeAuthToken();
        else localStorage.removeItem('authToken');
        location.href='/login.html';
    },
    openMore: function(e){ if(e)e.preventDefault(); document.getElementById('moreMenu').classList.add('active'); },
    closeMore: function(){ document.getElementById('moreMenu').classList.remove('active'); },
    fab: function(e){
        if(e)e.preventDefault();
        if(path==='/sales.html'){
            /* Sales sahifada modal ochish */
            var m = document.getElementById('quickSaleModal');
            if(m) m.classList.add('active');
            else{ var f=document.getElementById('quickSaleForm'); if(f) f.scrollIntoView({behavior:'smooth'}); }
        } else {
            location.href='/sales.html#add';
        }
    }
};

/* Global compat */
window.logout = window._nav.logout;
window.toggleSidebar = window._nav.collapse;
})();
