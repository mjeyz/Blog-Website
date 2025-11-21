/*!
 * Start Bootstrap - Clean Blog v6.0.9
 * https://startbootstrap.com/theme/clean-blog
 * Licensed under MIT
 */

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
        // Scrolling Up
        if (currentTop > 0 && this.mainNav.classList.contains('is-fixed')) {
          this.mainNav.classList.add('is-visible');
        } else {
          this.mainNav.classList.remove('is-visible', 'is-fixed');
        }
      } else {
        // Scrolling Down
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
    if (yearEl) {
      yearEl.textContent = new Date().getFullYear();
    }
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

  // Password visibility toggle
  setupPasswordToggles() {
    document.querySelectorAll('.password-toggle').forEach(button => {
      button.addEventListener('click', (e) => this.togglePasswordVisibility(e));
    });
  }

  togglePasswordVisibility(event) {
    const button = event.currentTarget;
    const targetId = button.dataset.target;
    const targetInput = document.getElementById(targetId);
    const icon = button.querySelector('i');

    if (!targetInput) return;

    if (targetInput.type === "password") {
      targetInput.type = "text";
      icon.classList.replace("fa-eye", "fa-eye-slash");
      button.setAttribute('aria-label', 'Hide password');
    } else {
      targetInput.type = "password";
      icon.classList.replace("fa-eye-slash", "fa-eye");
      button.setAttribute('aria-label', 'Show password');
    }
    targetInput.focus();
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

  // File upload & preview
  setupFileUpload() {
    const fileInput = document.getElementById('picture');
    const profilePreview = document.getElementById('profilePreview');

    if (!fileInput || !profilePreview) return;

    // Store original src
    fileInput.dataset.originalSrc = profilePreview.src;

    fileInput.addEventListener('change', (event) => this.handleFileSelect(event));

    this.setupImagePreview(profilePreview, fileInput);
  }

  handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      this.showAlert('Please select a valid image file (JPG, PNG, GIF, or WEBP)');
      this.clearFileSelection();
      return;
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      this.showAlert('File size must be less than 5MB');
      this.clearFileSelection();
      return;
    }

    this.updateFileInfo(file);
    this.previewImage(file);
  }

  showAlert(message) {
    // You can replace this with a more sophisticated notification system
    alert(message);
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
      if (profilePreview) {
        profilePreview.src = e.target.result;
      }
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

    // Reset preview image
    if (profilePreview && fileInput) {
      const originalSrc = fileInput.dataset.originalSrc;
      profilePreview.src = originalSrc;
    }
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Camera input
  openCamera() {
    const fileInput = document.getElementById('picture');
    if (!fileInput) return;

    fileInput.removeAttribute('capture');
    fileInput.setAttribute('capture', 'environment');
    fileInput.setAttribute('accept', 'image/*');
    fileInput.click();
  }

  // Drag & drop and click preview
  setupImagePreview(profilePreview, fileInput) {
    // Drag over
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

    // Click to select file
    profilePreview.addEventListener('click', () => {
      fileInput.click();
    });

    // Cursor and tooltip
    profilePreview.style.cursor = 'pointer';
    profilePreview.title = 'Click to choose a photo';
  }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new CleanBlogApp();
});