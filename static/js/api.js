// API utility functions

const API_BASE_URL = '/api';

// Token management
let authToken = localStorage.getItem('authToken');

function setAuthToken(token) {
    authToken = token;
    localStorage.setItem('authToken', token);
}

function getAuthToken() {
    return authToken || localStorage.getItem('authToken');
}

function removeAuthToken() {
    authToken = null;
    localStorage.removeItem('authToken');
}

/**
 * Keshli API so'rov — GET uchun keshdan oladi, POST/PUT/DELETE keshni tozalaydi
 * @param {string} endpoint
 * @param {object} options — fetch options
 * @param {object} cacheOpts — { key, invalidate }
 */
async function apiRequest(endpoint, options = {}, cacheOpts = {}) {
    const token = getAuthToken();
    const url = `${API_BASE_URL}${endpoint}`;
    const method = (options.method || 'GET').toUpperCase();
    const cacheKey = cacheOpts.key || endpoint;
    
    // GET so'rovlar uchun kesh tekshirish
    if (method === 'GET' && typeof cacheGet === 'function') {
        const cached = cacheGet(cacheKey);
        if (cached !== null) {
            return cached;
        }
    }
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (token) {
        const cleanToken = token.trim();
        defaultOptions.headers['Authorization'] = `Bearer ${cleanToken}`;
    }
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {})
        }
    };
    
    try {
        const response = await fetch(url, finalOptions);
        
        let data;
        try {
            data = await response.json();
        } catch (e) {
            data = { error: 'Server xatosi' };
        }
        
        if (!response.ok) {
            console.error('API Xatolik:', response.status, data);
            if (response.status === 401 || response.status === 422) {
                removeAuthToken();
                if (typeof cacheClear === 'function') cacheClear();
                if (window.location.pathname !== '/login.html') {
                    window.location.href = '/login.html';
                }
            }
            throw new Error(data.error || 'Xatolik yuz berdi');
        }
        
        // GET natijasini keshlash
        if (method === 'GET' && typeof cacheSet === 'function') {
            cacheSet(cacheKey, data);
        }
        
        // POST/PUT/DELETE bo'lsa tegishli keshlarni tozalash
        if (method !== 'GET' && typeof cacheInvalidate === 'function') {
            if (cacheOpts.invalidate) {
                cacheInvalidate(cacheOpts.invalidate);
            }
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth API
const authAPI = {
    login: async (username, password) => {
        // Login uchun token talab qilinmaydi
        const url = `${API_BASE_URL}/auth/login`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Xatolik yuz berdi');
        }
        
        // Token ni saqlash
        if (data.access_token) {
            setAuthToken(data.access_token);
        }
        return data;
    },
    
    // Register funksiyasi o'chirildi - faqat admin foydalanuvchi mavjud
    
    getCurrentUser: async () => {
        return await apiRequest('/auth/me');
    }
};

// Dashboard API (keshlanadi)
const dashboardAPI = {
    getStats: async () => {
        return await apiRequest('/dashboard/stats', {}, { key: 'dash_stats' });
    },
    
    getGrowthDynamics: async (params = {}) => {
        const q = new URLSearchParams();
        if (params.period === 'all') q.append('period', 'all');
        else if (params.year) q.append('year', params.year);
        const query = q.toString() ? '?' + q.toString() : '';
        const key = 'dash_growth_' + (params.period || params.year || 'cur');
        return await apiRequest('/dashboard/growth-dynamics' + query, {}, { key });
    },
    
    getTopProducts: async () => {
        return await apiRequest('/dashboard/top-products', {}, { key: 'dash_top_prod' });
    },
    
    getTopCustomers: async () => {
        return await apiRequest('/dashboard/top-customers', {}, { key: 'dash_top_cust' });
    },
    
    getDetailedStats: async () => {
        return await apiRequest('/dashboard/detailed-stats', {}, { key: 'dash_detailed' });
    },
    
    getMonthlyStats: async (year, month) => {
        const key = `dash_monthly_${year}_${month}`;
        return await apiRequest(`/dashboard/monthly-stats?year=${year}&month=${month}`, {}, { key });
    }
};


// Products API (keshlanadi)
const productsAPI = {
    getAll: async () => {
        return await apiRequest('/products', {}, { key: 'products_all' });
    },
    
    getOne: async (id) => {
        return await apiRequest(`/products/${id}`, {}, { key: `product_${id}` });
    },
    
    create: async (productData) => {
        return await apiRequest('/products', {
            method: 'POST',
            body: JSON.stringify(productData)
        }, { invalidate: ['products', 'dash'] });
    },
    
    update: async (id, productData) => {
        return await apiRequest(`/products/${id}`, {
            method: 'PUT',
            body: JSON.stringify(productData)
        }, { invalidate: ['products', 'dash'] });
    },
    
    delete: async (id) => {
        return await apiRequest(`/products/${id}`, {
            method: 'DELETE'
        }, { invalidate: ['products', 'dash'] });
    },
    
    getTopProfitable: async () => {
        return await apiRequest('/products/analysis/top-profitable', {}, { key: 'prod_top_profit' });
    },
    
    getTopSelling: async () => {
        return await apiRequest('/products/analysis/top-selling', {}, { key: 'prod_top_sell' });
    }
};

// Customers API (keshlanadi)
const customersAPI = {
    getAll: async () => {
        return await apiRequest('/customers', {}, { key: 'customers_all' });
    },
    
    getOne: async (id) => {
        return await apiRequest(`/customers/${id}`, {}, { key: `customer_${id}` });
    },
    
    create: async (customerData) => {
        return await apiRequest('/customers', {
            method: 'POST',
            body: JSON.stringify(customerData)
        }, { invalidate: ['customers', 'dash'] });
    },
    
    update: async (id, customerData) => {
        return await apiRequest(`/customers/${id}`, {
            method: 'PUT',
            body: JSON.stringify(customerData)
        }, { invalidate: ['customers', 'dash'] });
    },
    
    delete: async (id) => {
        return await apiRequest(`/customers/${id}`, {
            method: 'DELETE'
        }, { invalidate: ['customers', 'dash'] });
    },
    
    getMapData: async () => {
        return await apiRequest('/customers/map-data', {}, { key: 'customers_map' });
    }
};

// Sales API (keshlanadi)
const salesAPI = {
    getAll: async (startDate, endDate) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        const query = params.toString() ? `?${params.toString()}` : '';
        const key = 'sales_' + (startDate || '') + '_' + (endDate || '');
        return await apiRequest(`/sales${query}`, {}, { key });
    },
    
    getOne: async (id) => {
        return await apiRequest(`/sales/${id}`, {}, { key: `sale_${id}` });
    },
    
    create: async (saleData) => {
        return await apiRequest('/sales', {
            method: 'POST',
            body: JSON.stringify(saleData)
        }, { invalidate: ['sales', 'dash', 'products', 'customers'] });
    },
    
    update: async (id, saleData) => {
        return await apiRequest(`/sales/${id}`, {
            method: 'PUT',
            body: JSON.stringify(saleData)
        }, { invalidate: ['sales', 'dash', 'products', 'customers'] });
    },
    
    delete: async (id) => {
        return await apiRequest(`/sales/${id}`, {
            method: 'DELETE'
        }, { invalidate: ['sales', 'dash', 'products', 'customers'] });
    },
    
    getStatistics: async (period) => {
        const key = 'sales_stats_' + (period || 'month');
        return await apiRequest(`/sales/statistics?period=${period || 'month'}`, {}, { key });
    },
    
    getOnlineSales: async () => {
        return await apiRequest('/sales/online', {}, { key: 'sales_online' });
    },
    
    createOnlineSale: async (saleData) => {
        return await apiRequest('/sales/online', {
            method: 'POST',
            body: JSON.stringify(saleData)
        }, { invalidate: ['sales', 'dash'] });
    },
    
    bulkImport: async (salesArray) => {
        return await apiRequest('/sales/bulk-import', {
            method: 'POST',
            body: JSON.stringify({ sales: salesArray })
        }, { invalidate: ['sales', 'dash', 'products', 'customers'] });
    }
};

// Config API (token keshlanadi)
const configAPI = {
    getMapboxToken: async () => {
        return await apiRequest('/config/mapbox-token', {}, { key: 'config_mapbox' });
    }
};

// Regions API (keshlanadi)
const regionsAPI = {
    getAll: async () => {
        return await apiRequest('/regions', {}, { key: 'regions_all' });
    },
    
    getOne: async (id) => {
        return await apiRequest(`/regions/${id}`, {}, { key: `region_${id}` });
    },
    
    create: async (data) => {
        return await apiRequest('/regions', {
            method: 'POST',
            body: JSON.stringify(data)
        }, { invalidate: ['regions', 'shops'] });
    },
    
    update: async (id, data) => {
        return await apiRequest(`/regions/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }, { invalidate: ['regions', 'shops'] });
    },
    
    delete: async (id) => {
        return await apiRequest(`/regions/${id}`, {
            method: 'DELETE'
        }, { invalidate: ['regions', 'shops'] });
    },
    
    getMapData: async () => {
        return await apiRequest('/regions/map-data', {}, { key: 'regions_map' });
    }
};

// Shops API (keshlanadi)
const shopsAPI = {
    getAll: async () => {
        return await apiRequest('/shops', {}, { key: 'shops_all' });
    },
    
    getOne: async (id) => {
        return await apiRequest(`/shops/${id}`, {}, { key: `shop_${id}` });
    },
    
    create: async (data) => {
        return await apiRequest('/shops', {
            method: 'POST',
            body: JSON.stringify(data)
        }, { invalidate: ['shops', 'regions'] });
    },
    
    update: async (id, data) => {
        return await apiRequest(`/shops/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }, { invalidate: ['shops', 'regions'] });
    },
    
    delete: async (id) => {
        return await apiRequest(`/shops/${id}`, {
            method: 'DELETE'
        }, { invalidate: ['shops', 'regions'] });
    }
};

// AI API (tavsiyalar keshlanadi, savollar keshlanmaydi)
const aiAPI = {
    ask: async (question) => {
        return await apiRequest('/ai/ask', {
            method: 'POST',
            body: JSON.stringify({ question })
        });
    },
    
    generateReport: async (type) => {
        return await apiRequest('/ai/report', {
            method: 'POST',
            body: JSON.stringify({ type })
        });
    },
    
    getRecommendations: async () => {
        return await apiRequest('/ai/recommendations', {}, { key: 'ai_recommendations' });
    },
    
    getRisks: async () => {
        return await apiRequest('/ai/risks', {}, { key: 'ai_risks' });
    },
    
    askQuestion: async (question) => {
        return await aiAPI.ask(question);
    }
};

