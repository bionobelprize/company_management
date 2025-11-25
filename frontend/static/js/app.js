/**
 * 生物公司进销存管理系统 - 前端JavaScript
 */

const API_BASE_URL = '/api';
let currentPage = 'dashboard';
let currentEditId = null;
let authToken = null;

// Page titles mapping
const pageTitles = {
    'dashboard': '仪表盘',
    'products': '产品管理',
    'inventory': '库存管理',
    'purchases': '采购管理',
    'sales': '销售管理',
    'partners': '合作伙伴管理'
};

// Product types
const productTypes = [
    { value: '蛋白', label: '蛋白' },
    { value: '抗原', label: '抗原' },
    { value: '抗体', label: '抗体' },
    { value: '合成服务', label: '合成服务' },
    { value: '试剂', label: '试剂' },
    { value: '其他', label: '其他' }
];

// Partner types
const partnerTypes = [
    { value: '供应商', label: '供应商' },
    { value: '客户', label: '客户' },
    { value: '供应商/客户', label: '供应商/客户' }
];

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
});

// Authentication initialization
function initAuth() {
    authToken = localStorage.getItem('authToken');
    
    if (authToken) {
        // Verify token is still valid
        verifyAuth();
    } else {
        showLoginPage();
    }
    
    // Setup login form
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', handleLogin);
    
    // Setup logout button
    const logoutBtn = document.getElementById('logout-btn');
    logoutBtn.addEventListener('click', handleLogout);
}

// Verify authentication
async function verifyAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            showMainApp(user);
        } else {
            // Token is invalid, show login
            localStorage.removeItem('authToken');
            authToken = null;
            showLoginPage();
        }
    } catch (error) {
        console.error('Auth verification failed:', error);
        showLoginPage();
    }
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    try {
        // First, try to initialize admin if no users exist (ignore 400 error if admin already exists)
        try {
            const initResponse = await fetch(`${API_BASE_URL}/auth/init-admin`, {
                method: 'POST'
            });
            // Only log unexpected errors (not 400 which means admin already exists)
            if (!initResponse.ok && initResponse.status !== 400) {
                console.warn('Unexpected error initializing admin:', initResponse.status);
            }
        } catch (initError) {
            console.warn('Failed to initialize admin:', initError.message);
        }
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            
            // Get user info
            const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (userResponse.ok) {
                const user = await userResponse.json();
                showMainApp(user);
            }
        } else {
            const error = await response.json();
            errorDiv.textContent = error.detail || '登录失败';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Login failed:', error);
        errorDiv.textContent = '网络错误，请重试';
        errorDiv.style.display = 'block';
    }
}

// Handle logout
function handleLogout() {
    localStorage.removeItem('authToken');
    authToken = null;
    showLoginPage();
}

// Show login page
function showLoginPage() {
    document.getElementById('login-container').style.display = 'flex';
    document.getElementById('app-container').style.display = 'none';
    document.getElementById('login-username').value = '';
    document.getElementById('login-password').value = '';
    document.getElementById('login-error').style.display = 'none';
}

// Show main application
function showMainApp(user) {
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('app-container').style.display = 'flex';
    document.getElementById('current-user').textContent = user.full_name || user.username;
    
    initNavigation();
    loadDashboard();
}

// Navigation initialization
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const addBtn = document.getElementById('add-btn');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            switchPage(page);
        });
    });
    
    addBtn.addEventListener('click', () => {
        openAddModal();
    });
}

// Switch page
function switchPage(page) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === page) {
            item.classList.add('active');
        }
    });
    
    // Update page display
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    document.getElementById(`${page}-page`).classList.add('active');
    
    // Update title
    document.getElementById('page-title').textContent = pageTitles[page];
    
    // Show/hide add button
    const addBtn = document.getElementById('add-btn');
    addBtn.style.display = page === 'dashboard' ? 'none' : 'block';
    
    currentPage = page;
    
    // Load page data
    loadPageData(page);
}

// Load page data
function loadPageData(page) {
    switch (page) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'products':
            loadProducts();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'purchases':
            loadPurchases();
            break;
        case 'sales':
            loadSales();
            break;
        case 'partners':
            loadPartners();
            break;
    }
}

// API request helper
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    // Add auth token if available
    if (authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        // Handle authentication errors
        if (response.status === 401) {
            handleLogout();
            throw new Error('登录已过期，请重新登录');
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }
        if (response.status === 204) {
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Load dashboard data
async function loadDashboard() {
    try {
        const [products, inventory, purchases, sales] = await Promise.all([
            apiRequest('/products/').catch(() => []),
            apiRequest('/inventory/').catch(() => []),
            apiRequest('/purchases/').catch(() => []),
            apiRequest('/sales/').catch(() => [])
        ]);
        
        document.getElementById('stat-products').textContent = products.length;
        document.getElementById('stat-inventory').textContent = inventory.length;
        document.getElementById('stat-purchases').textContent = purchases.length;
        document.getElementById('stat-sales').textContent = sales.length;
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

// Load products
async function loadProducts() {
    const tbody = document.getElementById('products-table-body');
    tbody.innerHTML = '<tr><td colspan="7" class="loading">加载中...</td></tr>';
    
    try {
        const products = await apiRequest('/products/');
        
        if (products.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty">暂无数据</td></tr>';
            return;
        }
        
        tbody.innerHTML = products.map(product => `
            <tr>
                <td>${escapeHtml(product.product_code)}</td>
                <td>${escapeHtml(product.name)}</td>
                <td>${escapeHtml(product.product_type)}</td>
                <td>${escapeHtml(product.specification || '-')}</td>
                <td>${escapeHtml(product.unit)}</td>
                <td>${escapeHtml(product.storage_conditions || '-')}</td>
                <td class="action-btns">
                    <button class="btn btn-sm btn-primary" onclick="editProduct('${product.id}')">编辑</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteProduct('${product.id}')">删除</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty">加载失败</td></tr>';
    }
}

// Load inventory
async function loadInventory() {
    const tbody = document.getElementById('inventory-table-body');
    tbody.innerHTML = '<tr><td colspan="8" class="loading">加载中...</td></tr>';
    
    try {
        const inventory = await apiRequest('/inventory/');
        
        if (inventory.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="empty">暂无数据</td></tr>';
            return;
        }
        
        tbody.innerHTML = inventory.map(item => `
            <tr>
                <td>${escapeHtml(item.product_code || '-')}</td>
                <td>${escapeHtml(item.product_name || '-')}</td>
                <td>${escapeHtml(item.warehouse)}</td>
                <td>${escapeHtml(item.batch_number || '-')}</td>
                <td>${item.quantity}</td>
                <td>¥${item.unit_price.toFixed(2)}</td>
                <td>${escapeHtml(item.location || '-')}</td>
                <td class="action-btns">
                    <button class="btn btn-sm btn-success" onclick="inventoryIn('${item.id}')">入库</button>
                    <button class="btn btn-sm btn-secondary" onclick="inventoryOut('${item.id}')">出库</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty">加载失败</td></tr>';
    }
}

// Load purchases
async function loadPurchases() {
    const tbody = document.getElementById('purchases-table-body');
    tbody.innerHTML = '<tr><td colspan="7" class="loading">加载中...</td></tr>';
    
    try {
        const purchases = await apiRequest('/purchases/');
        
        if (purchases.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty">暂无数据</td></tr>';
            return;
        }
        
        tbody.innerHTML = purchases.map(order => `
            <tr>
                <td>${escapeHtml(order.order_number)}</td>
                <td>${escapeHtml(order.supplier_name || '-')}</td>
                <td>¥${order.total_amount.toFixed(2)}</td>
                <td><span class="status-badge ${getStatusClass(order.status)}">${escapeHtml(order.status)}</span></td>
                <td>${formatDate(order.order_date)}</td>
                <td>${formatDate(order.expected_date)}</td>
                <td class="action-btns">
                    <button class="btn btn-sm btn-primary" onclick="viewPurchase('${order.id}')">查看</button>
                    <button class="btn btn-sm btn-danger" onclick="deletePurchase('${order.id}')">删除</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty">加载失败</td></tr>';
    }
}

// Load sales
async function loadSales() {
    const tbody = document.getElementById('sales-table-body');
    tbody.innerHTML = '<tr><td colspan="7" class="loading">加载中...</td></tr>';
    
    try {
        const sales = await apiRequest('/sales/');
        
        if (sales.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty">暂无数据</td></tr>';
            return;
        }
        
        tbody.innerHTML = sales.map(order => `
            <tr>
                <td>${escapeHtml(order.order_number)}</td>
                <td>${escapeHtml(order.customer_name || '-')}</td>
                <td>¥${order.total_amount.toFixed(2)}</td>
                <td><span class="status-badge ${getStatusClass(order.status)}">${escapeHtml(order.status)}</span></td>
                <td>${formatDate(order.order_date)}</td>
                <td>${formatDate(order.expected_date)}</td>
                <td class="action-btns">
                    <button class="btn btn-sm btn-primary" onclick="viewSale('${order.id}')">查看</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteSale('${order.id}')">删除</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty">加载失败</td></tr>';
    }
}

// Load partners
async function loadPartners() {
    const tbody = document.getElementById('partners-table-body');
    tbody.innerHTML = '<tr><td colspan="8" class="loading">加载中...</td></tr>';
    
    try {
        const partners = await apiRequest('/partners/');
        
        if (partners.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="empty">暂无数据</td></tr>';
            return;
        }
        
        tbody.innerHTML = partners.map(partner => `
            <tr>
                <td>${escapeHtml(partner.partner_code)}</td>
                <td>${escapeHtml(partner.name)}</td>
                <td>${escapeHtml(partner.partner_type)}</td>
                <td>${escapeHtml(partner.contact_person || '-')}</td>
                <td>${escapeHtml(partner.phone || '-')}</td>
                <td>${escapeHtml(partner.email || '-')}</td>
                <td><span class="status-badge ${partner.is_active ? 'active' : 'inactive'}">${partner.is_active ? '启用' : '禁用'}</span></td>
                <td class="action-btns">
                    <button class="btn btn-sm btn-primary" onclick="editPartner('${partner.id}')">编辑</button>
                    <button class="btn btn-sm btn-danger" onclick="deletePartner('${partner.id}')">删除</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty">加载失败</td></tr>';
    }
}

// Open add modal
function openAddModal() {
    currentEditId = null;
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const saveBtn = document.getElementById('modal-save-btn');
    
    modalTitle.textContent = `新增${pageTitles[currentPage].replace('管理', '')}`;
    modalBody.innerHTML = getFormHtml(currentPage);
    
    saveBtn.onclick = () => saveItem();
    
    modal.classList.add('active');
}

// Open edit modal
async function openEditModal(id, type) {
    currentEditId = id;
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const saveBtn = document.getElementById('modal-save-btn');
    
    modalTitle.textContent = `编辑${pageTitles[type].replace('管理', '')}`;
    modalBody.innerHTML = getFormHtml(type);
    
    // Load existing data
    try {
        const data = await apiRequest(`/${type}/${id}`);
        populateForm(type, data);
    } catch (error) {
        alert('加载数据失败');
        closeModal();
        return;
    }
    
    saveBtn.onclick = () => saveItem();
    
    modal.classList.add('active');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('modal');
    modal.classList.remove('active');
    currentEditId = null;
}

// Get form HTML based on page type
function getFormHtml(page) {
    switch (page) {
        case 'products':
            return `
                <div class="form-row">
                    <div class="form-group">
                        <label>产品编号 *</label>
                        <input type="text" id="form-product_code" required>
                    </div>
                    <div class="form-group">
                        <label>产品名称 *</label>
                        <input type="text" id="form-name" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>产品类型 *</label>
                        <select id="form-product_type" required>
                            ${productTypes.map(t => `<option value="${t.value}">${t.label}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>规格</label>
                        <input type="text" id="form-specification">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>单位</label>
                        <input type="text" id="form-unit" value="个">
                    </div>
                    <div class="form-group">
                        <label>储存条件</label>
                        <input type="text" id="form-storage_conditions">
                    </div>
                </div>
                <div class="form-group">
                    <label>产品描述</label>
                    <textarea id="form-description"></textarea>
                </div>
            `;
        case 'inventory':
            return `
                <div class="form-group">
                    <label>产品ID *</label>
                    <input type="text" id="form-product_id" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>仓库</label>
                        <input type="text" id="form-warehouse" value="主仓库">
                    </div>
                    <div class="form-group">
                        <label>批次号</label>
                        <input type="text" id="form-batch_number">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>数量</label>
                        <input type="number" id="form-quantity" value="0">
                    </div>
                    <div class="form-group">
                        <label>单价</label>
                        <input type="number" id="form-unit_price" step="0.01" value="0">
                    </div>
                </div>
                <div class="form-group">
                    <label>货位</label>
                    <input type="text" id="form-location">
                </div>
            `;
        case 'partners':
            return `
                <div class="form-row">
                    <div class="form-group">
                        <label>编号 *</label>
                        <input type="text" id="form-partner_code" required>
                    </div>
                    <div class="form-group">
                        <label>名称 *</label>
                        <input type="text" id="form-name" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>类型 *</label>
                        <select id="form-partner_type" required>
                            ${partnerTypes.map(t => `<option value="${t.value}">${t.label}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>联系人</label>
                        <input type="text" id="form-contact_person">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>电话</label>
                        <input type="text" id="form-phone">
                    </div>
                    <div class="form-group">
                        <label>邮箱</label>
                        <input type="email" id="form-email">
                    </div>
                </div>
                <div class="form-group">
                    <label>地址</label>
                    <textarea id="form-address"></textarea>
                </div>
                <div class="form-group">
                    <label>备注</label>
                    <textarea id="form-remark"></textarea>
                </div>
            `;
        default:
            return '<p>暂不支持此操作</p>';
    }
}

// Populate form with existing data
function populateForm(type, data) {
    switch (type) {
        case 'products':
            document.getElementById('form-product_code').value = data.product_code || '';
            document.getElementById('form-name').value = data.name || '';
            document.getElementById('form-product_type').value = data.product_type || '';
            document.getElementById('form-specification').value = data.specification || '';
            document.getElementById('form-unit').value = data.unit || '';
            document.getElementById('form-storage_conditions').value = data.storage_conditions || '';
            document.getElementById('form-description').value = data.description || '';
            break;
        case 'inventory':
            document.getElementById('form-product_id').value = data.product_id || '';
            document.getElementById('form-warehouse').value = data.warehouse || '';
            document.getElementById('form-batch_number').value = data.batch_number || '';
            document.getElementById('form-quantity').value = data.quantity || 0;
            document.getElementById('form-unit_price').value = data.unit_price || 0;
            document.getElementById('form-location').value = data.location || '';
            break;
        case 'partners':
            document.getElementById('form-partner_code').value = data.partner_code || '';
            document.getElementById('form-name').value = data.name || '';
            document.getElementById('form-partner_type').value = data.partner_type || '';
            document.getElementById('form-contact_person').value = data.contact_person || '';
            document.getElementById('form-phone').value = data.phone || '';
            document.getElementById('form-email').value = data.email || '';
            document.getElementById('form-address').value = data.address || '';
            document.getElementById('form-remark').value = data.remark || '';
            break;
    }
}

// Save item
async function saveItem() {
    const data = getFormData(currentPage);
    
    try {
        if (currentEditId) {
            await apiRequest(`/${currentPage}/${currentEditId}`, 'PUT', data);
            alert('更新成功');
        } else {
            await apiRequest(`/${currentPage}/`, 'POST', data);
            alert('创建成功');
        }
        closeModal();
        loadPageData(currentPage);
    } catch (error) {
        alert('操作失败: ' + error.message);
    }
}

// Get form data
function getFormData(page) {
    switch (page) {
        case 'products':
            return {
                product_code: document.getElementById('form-product_code').value,
                name: document.getElementById('form-name').value,
                product_type: document.getElementById('form-product_type').value,
                specification: document.getElementById('form-specification').value || null,
                unit: document.getElementById('form-unit').value || '个',
                storage_conditions: document.getElementById('form-storage_conditions').value || null,
                description: document.getElementById('form-description').value || null
            };
        case 'inventory':
            return {
                product_id: document.getElementById('form-product_id').value,
                warehouse: document.getElementById('form-warehouse').value || '主仓库',
                batch_number: document.getElementById('form-batch_number').value || null,
                quantity: parseInt(document.getElementById('form-quantity').value) || 0,
                unit_price: parseFloat(document.getElementById('form-unit_price').value) || 0,
                location: document.getElementById('form-location').value || null
            };
        case 'partners':
            return {
                partner_code: document.getElementById('form-partner_code').value,
                name: document.getElementById('form-name').value,
                partner_type: document.getElementById('form-partner_type').value,
                contact_person: document.getElementById('form-contact_person').value || null,
                phone: document.getElementById('form-phone').value || null,
                email: document.getElementById('form-email').value || null,
                address: document.getElementById('form-address').value || null,
                remark: document.getElementById('form-remark').value || null
            };
        default:
            return {};
    }
}

// Edit handlers
function editProduct(id) {
    openEditModal(id, 'products');
}

function editPartner(id) {
    openEditModal(id, 'partners');
}

// Delete handlers
async function deleteProduct(id) {
    if (!confirm('确定要删除此产品吗？')) return;
    
    try {
        await apiRequest(`/products/${id}`, 'DELETE');
        alert('删除成功');
        loadProducts();
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

async function deletePartner(id) {
    if (!confirm('确定要删除此合作伙伴吗？')) return;
    
    try {
        await apiRequest(`/partners/${id}`, 'DELETE');
        alert('删除成功');
        loadPartners();
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

async function deletePurchase(id) {
    if (!confirm('确定要删除此采购订单吗？')) return;
    
    try {
        await apiRequest(`/purchases/${id}`, 'DELETE');
        alert('删除成功');
        loadPurchases();
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

async function deleteSale(id) {
    if (!confirm('确定要删除此销售订单吗？')) return;
    
    try {
        await apiRequest(`/sales/${id}`, 'DELETE');
        alert('删除成功');
        loadSales();
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

// View order details
function viewPurchase(id) {
    alert('查看采购订单详情: ' + id);
}

function viewSale(id) {
    alert('查看销售订单详情: ' + id);
}

// Inventory operations
function inventoryIn(id) {
    const quantity = prompt('请输入入库数量：');
    if (quantity && parseInt(quantity) > 0) {
        alert(`入库操作：库存ID=${id}, 数量=${quantity}`);
    }
}

function inventoryOut(id) {
    const quantity = prompt('请输入出库数量：');
    if (quantity && parseInt(quantity) > 0) {
        alert(`出库操作：库存ID=${id}, 数量=${quantity}`);
    }
}

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

function getStatusClass(status) {
    const statusMap = {
        '草稿': 'draft',
        '待审核': 'pending',
        '已审核': 'approved',
        '已完成': 'completed',
        '已取消': 'cancelled'
    };
    return statusMap[status] || 'draft';
}
