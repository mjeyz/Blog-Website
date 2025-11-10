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
