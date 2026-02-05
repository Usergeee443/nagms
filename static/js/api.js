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

// API request helper
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (token) {
        // Token ni tozalash (agar bo'sh joylar bo'lsa)
        const cleanToken = token.trim();
        defaultOptions.headers['Authorization'] = `Bearer ${cleanToken}`;
        console.log('Token yuborilmoqda:', cleanToken.substring(0, 20) + '...');
    } else {
        console.warn('Token topilmadi!');
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
        
        // Response ni o'qishdan oldin statusni tekshirish
        let data;
        try {
            data = await response.json();
        } catch (e) {
            // Agar JSON emas bo'lsa
            data = { error: 'Server xatosi' };
        }
        
        if (!response.ok) {
            console.error('API Xatolik:', response.status, data);
            if (response.status === 401 || response.status === 422) {
                // Unauthorized or Invalid token - redirect to login
                removeAuthToken();
                if (window.location.pathname !== '/login.html') {
                    window.location.href = '/login.html';
                }
            }
            throw new Error(data.error || 'Xatolik yuz berdi');
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
            console.log('Token saqlandi:', data.access_token.substring(0, 20) + '...');
        }
        return data;
    },
    
    // Register funksiyasi o'chirildi - faqat admin foydalanuvchi mavjud
    
    getCurrentUser: async () => {
        return await apiRequest('/auth/me');
    }
};

// Dashboard API
const dashboardAPI = {
    getStats: async () => {
        return await apiRequest('/dashboard/stats');
    },
    
    getGrowthDynamics: async () => {
        return await apiRequest('/dashboard/growth-dynamics');
    },
    
    getTopProducts: async () => {
        return await apiRequest('/dashboard/top-products');
    },
    
    getTopCustomers: async () => {
        return await apiRequest('/dashboard/top-customers');
    },
    
    getDetailedStats: async () => {
        return await apiRequest('/dashboard/detailed-stats');
    }
};

// Goals API
const goalsAPI = {
    getAll: async () => {
        return await apiRequest('/goals');
    },
    
    getOne: async (id) => {
        return await apiRequest(`/goals/${id}`);
    },
    
    create: async (goalData) => {
        return await apiRequest('/goals', {
            method: 'POST',
            body: JSON.stringify(goalData)
        });
    },
    
    update: async (id, goalData) => {
        return await apiRequest(`/goals/${id}`, {
            method: 'PUT',
            body: JSON.stringify(goalData)
        });
    },
    
    delete: async (id) => {
        return await apiRequest(`/goals/${id}`, {
            method: 'DELETE'
        });
    },
    
    getPlans: async (goalId) => {
        return await apiRequest(`/goals/${goalId}/plans`);
    },
    
    createPlan: async (goalId, planData) => {
        return await apiRequest(`/goals/${goalId}/plans`, {
            method: 'POST',
            body: JSON.stringify(planData)
        });
    },
    
    updatePlan: async (planId, planData) => {
        return await apiRequest(`/goals/plans/${planId}`, {
            method: 'PUT',
            body: JSON.stringify(planData)
        });
    },
    
    deletePlan: async (planId) => {
        return await apiRequest(`/goals/plans/${planId}`, {
            method: 'DELETE'
        });
    }
};

// Products API
const productsAPI = {
    getAll: async () => {
        return await apiRequest('/products');
    },
    
    getOne: async (id) => {
        return await apiRequest(`/products/${id}`);
    },
    
    create: async (productData) => {
        return await apiRequest('/products', {
            method: 'POST',
            body: JSON.stringify(productData)
        });
    },
    
    update: async (id, productData) => {
        return await apiRequest(`/products/${id}`, {
            method: 'PUT',
            body: JSON.stringify(productData)
        });
    },
    
    delete: async (id) => {
        return await apiRequest(`/products/${id}`, {
            method: 'DELETE'
        });
    },
    
    getTopProfitable: async () => {
        return await apiRequest('/products/analysis/top-profitable');
    },
    
    getTopSelling: async () => {
        return await apiRequest('/products/analysis/top-selling');
    }
};

// Customers API
const customersAPI = {
    getAll: async () => {
        return await apiRequest('/customers');
    },
    
    getOne: async (id) => {
        return await apiRequest(`/customers/${id}`);
    },
    
    create: async (customerData) => {
        return await apiRequest('/customers', {
            method: 'POST',
            body: JSON.stringify(customerData)
        });
    },
    
    update: async (id, customerData) => {
        return await apiRequest(`/customers/${id}`, {
            method: 'PUT',
            body: JSON.stringify(customerData)
        });
    },
    
    delete: async (id) => {
        return await apiRequest(`/customers/${id}`, {
            method: 'DELETE'
        });
    },
    
    getMapData: async () => {
        return await apiRequest('/customers/map-data');
    }
};

// Sales API
const salesAPI = {
    getAll: async (startDate, endDate) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        const query = params.toString() ? `?${params.toString()}` : '';
        return await apiRequest(`/sales${query}`);
    },
    
    getOne: async (id) => {
        return await apiRequest(`/sales/${id}`);
    },
    
    create: async (saleData) => {
        return await apiRequest('/sales', {
            method: 'POST',
            body: JSON.stringify(saleData)
        });
    },
    
    update: async (id, saleData) => {
        return await apiRequest(`/sales/${id}`, {
            method: 'PUT',
            body: JSON.stringify(saleData)
        });
    },
    
    delete: async (id) => {
        return await apiRequest(`/sales/${id}`, {
            method: 'DELETE'
        });
    },
    
    getStatistics: async (period) => {
        return await apiRequest(`/sales/statistics?period=${period || 'month'}`);
    },
    
    getOnlineSales: async () => {
        return await apiRequest('/sales/online');
    },
    
    createOnlineSale: async (saleData) => {
        return await apiRequest('/sales/online', {
            method: 'POST',
            body: JSON.stringify(saleData)
        });
    },
    
    bulkImport: async (salesArray) => {
        return await apiRequest('/sales/bulk-import', {
            method: 'POST',
            body: JSON.stringify({ sales: salesArray })
        });
    }
};

// Config API
const configAPI = {
    getMapboxToken: async () => {
        return await apiRequest('/config/mapbox-token');
    }
};

// AI API
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
        return await apiRequest('/ai/recommendations');
    },
    
    getRisks: async () => {
        return await apiRequest('/ai/risks');
    },
    
    askQuestion: async (question) => {
        return await aiAPI.ask(question);
    }
};

