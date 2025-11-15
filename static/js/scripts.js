/*!
 * Start Bootstrap - Clean Blog v6.0.9
 * https://startbootstrap.com/theme/clean-blog
 * Licensed under MIT
 */

// Navbar scroll behavior
window.addEventListener('DOMContentLoaded', () => {
  let scrollPos = 0;
  const mainNav = document.getElementById('mainNav');
  const headerHeight = mainNav.clientHeight;

  window.addEventListener('scroll', function () {
    const currentTop = document.body.getBoundingClientRect().top * -1;
    if (currentTop < scrollPos) {
      // Scrolling Up
      if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
        mainNav.classList.add('is-visible');
      } else {
        mainNav.classList.remove('is-visible', 'is-fixed');
      }
    } else {
      // Scrolling Down
      mainNav.classList.remove('is-visible');
      if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
        mainNav.classList.add('is-fixed');
      }
    }
    scrollPos = currentTop;
  });

  // Make navbar solid on scroll
  window.addEventListener('scroll', function () {
    if (window.scrollY > 50) {
      mainNav.classList.add('scrolled');
    } else {
      mainNav.classList.remove('scrolled');
    }
  });

  // Auto update copyright year
  const yearEl = document.getElementById('currentYear');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Hover effect for icons
  document.querySelectorAll('.fa-stack').forEach((el) => {
    el.addEventListener('mouseenter', () => (el.style.transform = 'scale(1.15)'));
    el.addEventListener('mouseleave', () => (el.style.transform = 'scale(1)'));
    el.style.transition = 'transform 0.3s ease';
  });
});

// Password visibility toggle (for all inputs with class password-toggle)
document.querySelectorAll('.password-toggle').forEach(button => {
  button.addEventListener('click', function() {
    const targetId = this.dataset.target;
    const targetInput = document.getElementById(targetId);
    const icon = this.querySelector('i');

    if (targetInput.type === "password") {
      targetInput.type = "text";
      icon.classList.remove("fa-eye");
      icon.classList.add("fa-eye-slash");
      this.setAttribute('aria-label', 'Hide password');
    } else {
      targetInput.type = "password";
      icon.classList.add("fa-eye");
      icon.classList.remove("fa-eye-slash");
      this.setAttribute('aria-label', 'Show password');
    }
    targetInput.focus();
  });
});

// Bootstrap form validation
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', function(event) {
    if (!this.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
    }
    this.classList.add('was-validated');
  }, false);
});

// File upload & preview
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  if (!validTypes.includes(file.type)) {
    alert('Please select a valid image file (JPG, PNG, GIF, or WEBP)');
    clearFileSelection();
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    alert('File size must be less than 5MB');
    clearFileSelection();
    return;
  }

  document.getElementById('fileName').textContent = file.name;
  document.getElementById('fileSize').textContent = formatFileSize(file.size);
  document.getElementById('fileInfo').classList.remove('d-none');
  document.getElementById('uploadBtn').disabled = false;

  // Preview image
  const reader = new FileReader();
  reader.onload = function() {
    document.getElementById('profilePreview').src = reader.result;
  };
  reader.readAsDataURL(file);
}

function clearFileSelection() {
  const fileInput = document.getElementById('picture');
  fileInput.value = '';
  document.getElementById('fileInfo').classList.add('d-none');
  document.getElementById('uploadBtn').disabled = true;

  // Reset preview image
  const originalSrc = fileInput.dataset.originalSrc || fileInput.dataset.defaultSrc;
  document.getElementById('profilePreview').src = originalSrc;
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Camera input
function openCamera() {
  const fileInput = document.getElementById('picture');
  fileInput.removeAttribute('capture');
  fileInput.setAttribute('capture', 'environment');
  fileInput.setAttribute('accept', 'image/*');
  fileInput.click();
}

// Drag & drop and click preview
document.addEventListener('DOMContentLoaded', function() {
  const profilePreview = document.getElementById('profilePreview');
  const fileInput = document.getElementById('picture');
  if (!profilePreview || !fileInput) return;

  // Store original src
  fileInput.dataset.originalSrc = profilePreview.src;

  // Drag over
  profilePreview.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.style.transform = 'scale(1.05)';
    this.style.transition = 'transform 0.2s ease';
  });
  profilePreview.addEventListener('dragleave', function(e) {
    e.preventDefault();
    this.style.transform = 'scale(1)';
  });
  profilePreview.addEventListener('drop', function(e) {
    e.preventDefault();
    this.style.transform = 'scale(1)';
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      handleFileSelect({ target: fileInput });
    }
  });

  // Click to select file
  profilePreview.addEventListener('click', function() {
    fileInput.click();
  });

  // Cursor and tooltip
  profilePreview.style.cursor = 'pointer';
  profilePreview.title = 'Click to choose a photo';
});
