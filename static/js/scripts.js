/*! 
 * Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
 * Copyright 2013-2023 Start Bootstrap
 * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
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
});

// Password visibility toggle (icon appears only when user types)
document.addEventListener('DOMContentLoaded', function () {
  const passwordInput = document.getElementById('password');
  if (!passwordInput) return;

  // Create toggle icon (hidden by default)
  const toggle = document.createElement('span');
  toggle.innerHTML = '<i class="fas fa-eye"></i>';
  toggle.style.position = 'absolute';
  toggle.style.right = '15px';
  toggle.style.top = '50%';
  toggle.style.transform = 'translateY(-50%)';
  toggle.style.cursor = 'pointer';
  toggle.style.display = 'none'; // Hidden initially

  // Wrap field for positioning
  const wrapper = document.createElement('div');
  wrapper.style.position = 'relative';
  passwordInput.parentNode.insertBefore(wrapper, passwordInput);
  wrapper.appendChild(passwordInput);
  wrapper.appendChild(toggle);

  // Show/hide icon based on input
  passwordInput.addEventListener('input', () => {
    if (passwordInput.value.length > 0) {
      toggle.style.display = 'block';
    } else {
      toggle.style.display = 'none';
    }
  });

  // Toggle password visibility
  toggle.addEventListener('click', () => {
    const type =
      passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    toggle.innerHTML =
      type === 'password'
        ? '<i class="fas fa-eye"></i>'
        : '<i class="fas fa-eye-slash"></i>';
  });
});

// Make navbar solid on scroll
window.addEventListener('scroll', function () {
  const navbar = document.getElementById('mainNav');
  if (window.scrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// Auto update copyright year
document.getElementById('currentYear').textContent =
  new Date().getFullYear();

// Hover effect for icons
document.querySelectorAll('.fa-stack').forEach((el) => {
  el.addEventListener('mouseenter', () => (el.style.transform = 'scale(1.15)'));
  el.addEventListener('mouseleave', () => (el.style.transform = 'scale(1)'));
  el.style.transition = 'transform 0.3s ease';
});


// Toggle password visibility
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

        // Focus back on the input for better UX
        targetInput.focus();
    });
});


// Add Bootstrap validation on form submission
document.querySelector('form').addEventListener('submit', function(event) {
    if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
    }
    this.classList.add('was-validated');
}, false);


// Enhanced JS for file handling and camera
  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        alert('Please select a valid image file (JPG, PNG, GIF, or WEBP)');
        clearFileSelection();
        return;
      }

      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        clearFileSelection();
        return;
      }

      // Display file info
      document.getElementById('fileName').textContent = file.name;
      document.getElementById('fileSize').textContent = formatFileSize(file.size);
      document.getElementById('fileInfo').classList.remove('d-none');

      // Enable upload button
      document.getElementById('uploadBtn').disabled = false;

      // Preview image
      previewImage(event);
    }
  }

  function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function(){
      document.getElementById('profilePreview').src = reader.result;
    }
    if(event.target.files[0]){
      reader.readAsDataURL(event.target.files[0]);
    }
  }

  function clearFileSelection() {
    document.getElementById('picture').value = '';
    document.getElementById('fileInfo').classList.add('d-none');
    document.getElementById('uploadBtn').disabled = true;

    // Reset to original image
    const originalSrc = "{% if current_user.image_file %}{{ url_for('static', filename='profile_pics/' ~ current_user.image_file) }}{% else %}{{ url_for('static', filename='assets/img/default-profile.jpg') }}{% endif %}";
    document.getElementById('profilePreview').src = originalSrc;
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Camera functionality for mobile devices
  function openCamera() {
    // Reset file input to accept camera capture
    const fileInput = document.getElementById('picture');
    fileInput.removeAttribute('capture'); // Remove previous capture attribute
    fileInput.setAttribute('capture', 'environment'); // Use back camera if available
    fileInput.setAttribute('accept', 'image/*');

    // Trigger file input with camera preference
    fileInput.click();
  }

  // Drag and drop functionality
  document.addEventListener('DOMContentLoaded', function() {
    const profilePreview = document.getElementById('profilePreview');
    const fileInput = document.getElementById('picture');

    // Drag over effect
    profilePreview.addEventListener('dragover', function(e) {
      e.preventDefault();
      this.style.transform = 'scale(1.05)';
      this.style.transition = 'transform 0.2s ease';
    });

    // Drag leave effect
    profilePreview.addEventListener('dragleave', function(e) {
      e.preventDefault();
      this.style.transform = 'scale(1)';
    });

    // Drop functionality
    profilePreview.addEventListener('drop', function(e) {
      e.preventDefault();
      this.style.transform = 'scale(1)';

      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelect({ target: fileInput });
      }
    });

    // Make profile image clickable too
    profilePreview.addEventListener('click', function() {
      fileInput.click();
    });

    // Add hover effect to profile image
    profilePreview.style.cursor = 'pointer';
    profilePreview.title = 'Click to choose a photo';
  });
