/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/

// Password visibility toggle script
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
})

        document.addEventListener('DOMContentLoaded', function() {
            const passwordInput = document.getElementById('password');
            if (!passwordInput) return;

            // Create toggle icon
            const toggle = document.createElement('span');
            toggle.innerHTML = '<i class="fas fa-eye"></i>';
            toggle.style.position = 'absolute';
            toggle.style.right = '15px';
            toggle.style.top = '50%';
            toggle.style.transform = 'translateY(-50%)';
            toggle.style.cursor = 'pointer';

            // Wrap field for positioning
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            passwordInput.parentNode.insertBefore(wrapper, passwordInput);
            wrapper.appendChild(passwordInput);
            wrapper.appendChild(toggle);

            // Toggle password visibility
            toggle.addEventListener('click', () => {
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);
                toggle.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
            });
        });

// Optional: script to make navbar solid when scrolling
  window.addEventListener("scroll", function() {
    const navbar = document.getElementById("mainNav");
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  });

    document.getElementById('currentYear').textContent = new Date().getFullYear();
    // Simple hover effect for icons
    document.querySelectorAll('.fa-stack').forEach(el => {
      el.addEventListener('mouseenter', () => el.style.transform = 'scale(1.15)');
      el.addEventListener('mouseleave', () => el.style.transform = 'scale(1)');
      el.style.transition = 'transform 0.3s ease';
    });

// Auto update copyright year
document.getElementById("currentYear").textContent = new Date().getFullYear();    