class CleanBlogApp {
  constructor() { 
    this.mainNav = document.getElementById('mainNav');
    this.scrollPos = 0;
    this.init();
  }

  init() {
    this.setupNavbarScroll();
    this.setupNavbarSolid();
    this.autoUpdateCopyright();
    this.setupIconHoverEffects();
    this.setupPasswordToggles();
    this.setupFormValidation();
    this.setupFileUpload();
  }

  // Navbar scroll behavior
  setupNavbarScroll() {
    if (!this.mainNav) return;

    const headerHeight = this.mainNav.clientHeight;

    window.addEventListener('scroll', () => {
      const currentTop = Math.abs(document.body.getBoundingClientRect().top);

      if (currentTop < this.scrollPos) {
        if (currentTop > 0 && this.mainNav.classList.contains('is-fixed')) {
          this.mainNav.classList.add('is-visible');
        } else {
          this.mainNav.classList.remove('is-visible', 'is-fixed');
        }
      } else {
        this.mainNav.classList.remove('is-visible');
        if (currentTop > headerHeight && !this.mainNav.classList.contains('is-fixed')) {
          this.mainNav.classList.add('is-fixed');
        }
      }
      this.scrollPos = currentTop;
    });
  }

  // Make navbar solid on scroll
  setupNavbarSolid() {
    if (!this.mainNav) return;

    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        this.mainNav.classList.add('scrolled');
      } else {
        this.mainNav.classList.remove('scrolled');
      }
    });
  }

  // Auto update copyright year
  autoUpdateCopyright() {
    const yearEl = document.getElementById('currentYear');
    if (yearEl) yearEl.textContent = new Date().getFullYear();
  }

  // Hover effect for icons
  setupIconHoverEffects() {
    document.querySelectorAll('.fa-stack').forEach((el) => {
      el.addEventListener('mouseenter', () => this.scaleElement(el, 1.15));
      el.addEventListener('mouseleave', () => this.scaleElement(el, 1));
      el.style.transition = 'transform 0.3s ease';
    });
  }

  scaleElement(element, scale) {
    element.style.transform = `scale(${scale})`;
  }

  // Password toggle visibility
  setupPasswordToggles() {
    const pwdField = document.querySelector('input[type="password"]');
    if (!pwdField) return;

    // Create toggle button
    const toggleBtn = document.createElement('span');
    toggleBtn.className = 'position-absolute cursor-pointer password-toggle';
    toggleBtn.style.right = '15px';
    toggleBtn.style.top = '75%';
    toggleBtn.style.transform = 'translateY(-50%)';
    toggleBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';

    // Attach to parent
    pwdField.parentElement.style.position = 'relative';
    pwdField.parentElement.appendChild(toggleBtn);

    // Toggle visibility
    toggleBtn.addEventListener('click', () => {
      const isPassword = pwdField.type === 'password';
      pwdField.type = isPassword ? 'text' : 'password';

      toggleBtn.innerHTML = isPassword
        ? '<i class="bi bi-eye"></i>'
        : '<i class="bi bi-eye-slash"></i>';
    });
  }

  // Bootstrap form validation
  setupFormValidation() {
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', (event) => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  }

  // File upload logic
  setupFileUpload() {
    const fileInput = document.getElementById('picture');
    const profilePreview = document.getElementById('profilePreview');

    if (!fileInput || !profilePreview) return;

    // Store original image source
    fileInput.dataset.originalSrc = profilePreview.src;

    // Setup event listeners
    fileInput.addEventListener('change', (event) => this.handleFileSelect(event));
    this.setupImagePreview(profilePreview, fileInput);

    // Add loading state to form submission
    const form = fileInput.closest('form');
    if (form) {
      form.addEventListener('submit', (e) => {
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadText = document.getElementById('uploadText');
        const uploadSpinner = document.getElementById('uploadSpinner');

        if (uploadBtn) {
          uploadBtn.disabled = true;
          if (uploadText) uploadText.textContent = 'Uploading...';
          if (uploadSpinner) uploadSpinner.classList.remove('d-none');
        }
      });
    }
  }

  handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file
    if (!this.validateFile(file)) {
      return;
    }

    // Update UI and preview
    this.updateFileInfo(file);
    this.previewImage(file);

    // Show success message
    this.showAlert('File selected successfully. Click "Upload Photo" to save.', 'success');
  }

  validateFile(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

    if (!validTypes.includes(file.type)) {
      this.showAlert('Please select a valid image file (JPG, PNG, GIF, or WEBP)', 'danger');
      this.clearFileSelection();
      return false;
    }

    if (file.size > 5 * 1024 * 1024) {
      this.showAlert('File size must be less than 5MB', 'danger');
      this.clearFileSelection();
      return false;
    }

    return true;
  }

  showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.custom-alert');
    existingAlerts.forEach(alert => alert.remove());

    // Create new alert
    const alert = document.createElement('div');
    alert.className = `custom-alert alert alert-${type} alert-dismissible fade show rounded-3 shadow-sm`;
    alert.innerHTML = `
      <div class="d-flex align-items-center">
        <i class="bi bi-${type === 'success' ? 'check-circle-fill' :
                         type === 'danger' ? 'exclamation-triangle-fill' :
                         'info-circle-fill'} me-2"></i>
        <span class="fw-medium">${message}</span>
      </div>
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Add styles
    Object.assign(alert.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: '1060',
      minWidth: '300px'
    });

    document.body.appendChild(alert);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (alert.parentNode) {
        alert.remove();
      }
    }, 5000);
  }

  updateFileInfo(file) {
    const fileNameEl = document.getElementById('fileName');
    const fileSizeEl = document.getElementById('fileSize');
    const fileInfoEl = document.getElementById('fileInfo');
    const uploadBtn = document.getElementById('uploadBtn');

    if (fileNameEl) fileNameEl.textContent = file.name;
    if (fileSizeEl) fileSizeEl.textContent = this.formatFileSize(file.size);
    if (fileInfoEl) fileInfoEl.classList.remove('d-none');
    if (uploadBtn) uploadBtn.disabled = false;
  }

  previewImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const profilePreview = document.getElementById('profilePreview');
      if (profilePreview) profilePreview.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  clearFileSelection() {
    const fileInput = document.getElementById('picture');
    const fileInfoEl = document.getElementById('fileInfo');
    const uploadBtn = document.getElementById('uploadBtn');
    const profilePreview = document.getElementById('profilePreview');

    if (fileInput) fileInput.value = '';
    if (fileInfoEl) fileInfoEl.classList.add('d-none');
    if (uploadBtn) uploadBtn.disabled = true;

    if (profilePreview && fileInput) {
      profilePreview.src = fileInput.dataset.originalSrc || profilePreview.src;
    }
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  setupImagePreview(profilePreview, fileInput) {
    profilePreview.addEventListener('dragover', (e) => {
      e.preventDefault();
      this.scaleElement(profilePreview, 1.05);
    });

    profilePreview.addEventListener('dragleave', (e) => {
      e.preventDefault();
      this.scaleElement(profilePreview, 1);
    });

    profilePreview.addEventListener('drop', (e) => {
      e.preventDefault();
      this.scaleElement(profilePreview, 1);
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        this.handleFileSelect({ target: fileInput });
      }
    });

    profilePreview.addEventListener('click', () => fileInput.click());

    profilePreview.style.cursor = 'pointer';
    profilePreview.title = 'Click to choose a photo';
  }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  new CleanBlogApp();
});