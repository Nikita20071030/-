document.addEventListener('DOMContentLoaded', function() {

  let products = [];

  const elements = {
    productTable: document.querySelector('.products-table tbody'),
    addForm: document.getElementById('add-product-form'),
    navButtons: document.querySelectorAll('.nav-btn'),
    pages: document.querySelectorAll('.page'),
    alertsList: document.querySelector('.alerts-list'),
    reportsTable: document.querySelector('.reports-table tbody'),
    generateReportBtn: document.getElementById('generate-report'),
    photoUploadBtn: document.querySelector('.photo-upload-btn')
  };


  async function loadProducts() {
    try {
      const response = await fetch('http://localhost:5000/api/products');
      if (!response.ok) throw new Error("Ошибка загрузки");
      products = await response.json();
      renderProducts();
    } catch (error) {
      console.error("Ошибка:", error);
    }
  }


  async function addProduct(product) {
    try {
      const response = await fetch('http://localhost:5000/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(product)
      });
      if (!response.ok) throw new Error("Ошибка добавления");
      return await response.json();
    } catch (error) {
      console.error("Ошибка:", error);
      throw error;
    }
  }


  async function deleteProduct(productId) {
    try {
      const response = await fetch(`http://localhost:5000/api/products/${productId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error("Ошибка удаления");
      await loadProducts(); // Перезагружаем список
    } catch (error) {
      console.error("Ошибка:", error);
    }
  }


  function renderProducts() {
    if (!elements.productTable) return;
    elements.productTable.innerHTML = '';
    products.forEach(product => {
      const row = document.createElement('tr');
      row.dataset.id = product.id;
      row.innerHTML = `
        <td>${product.id}</td>
        <td>${product.name}</td>
        <td>${product.category}</td>
        <td>${product.quantity}</td>
        <td>${product.min_quantity || product.min}</td> <!-- Поддержка старого формата -->
        <td>${product.added_date || product.date}</td>
        <td>
          <button class="edit-btn" data-id="${product.id}">✏️</button>
          <button class="delete-btn" data-id="${product.id}">🗑️</button>
        </td>
      `;
      elements.productTable.appendChild(row);
    });


    document.querySelectorAll('.edit-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        editProduct(e.target.dataset.id);
      });
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (confirm(`Удалить товар ${e.target.dataset.id}?`)) {
          deleteProduct(e.target.dataset.id);
        }
      });
    });
  }


  function editProduct(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    document.getElementById('product-id').value = product.id;
    document.getElementById('product-name').value = product.name;
    document.getElementById('product-category').value = product.category;
    document.getElementById('product-quantity').value = product.quantity;
    document.getElementById('product-min').value = product.min_quantity || product.min;
    document.getElementById('product-date').value = product.added_date || product.date;
    showPage('add');
  }

 
  function showPage(pageId) {
    elements.pages.forEach(page => page.style.display = 'none');
    document.querySelector(`.${pageId}-page`).style.display = 'block';
    elements.navButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.page === pageId));
    if (pageId === 'products') loadProducts();
    if (pageId === 'alerts') renderAlerts();
    if (pageId === 'reports') renderReports();
  }


  if (elements.addForm) {
    elements.addForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const newProduct = {
        id: document.getElementById('product-id').value,
        name: document.getElementById('product-name').value,
        category: document.getElementById('product-category').value,
        quantity: parseInt(document.getElementById('product-quantity').value),
        min_quantity: parseInt(document.getElementById('product-min').value),
        added_date: document.getElementById('product-date').value || new Date().toISOString().split('T')[0]
      };

      try {
        await addProduct(newProduct);
        this.reset();
        showPage('products');
      } catch (error) {
        alert("Ошибка: товар с таким ID уже существует!");
      }
    });
  }




  loadPoducts(); // Первая загрузка данных
  showPage('products');
});
