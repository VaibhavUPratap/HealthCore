const appt = document.getElementById("appointmentBtn");
if (appt) appt.addEventListener("click", () => alert("Thank you! Appointment feature coming soon 🚀"));

// Activate current nav link
document.querySelectorAll('.nav-links a').forEach(a => {
  if (a.getAttribute('href') === location.pathname) a.classList.add('active');
});

// Register basic service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/js/sw.js').catch(()=>{});
}

// Enhanced theme system with system detection
(function() {
  const root = document.documentElement;
  const key = 'theme';
  
  // Get system preference
  const getSystemTheme = () => window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  
  // Initialize theme
  function initTheme() {
    const saved = localStorage.getItem(key);
    const systemTheme = getSystemTheme();
    const theme = saved || systemTheme;
    
    console.log('Initializing theme:', theme, 'saved:', saved, 'system:', systemTheme);
    
    if (theme === 'dark') {
      root.classList.add('dark');
      root.setAttribute('data-theme', 'dark');
    } else {
      root.classList.remove('dark');
      root.setAttribute('data-theme', 'light');
    }
    
    updateThemeUI(theme === 'dark');
  }
  
  // Update theme UI elements
  function updateThemeUI(isDark) {
    const themeText = document.getElementById('themeText');
    const sunIcon = document.getElementById('sunIcon');
    const moonIcon = document.getElementById('moonIcon');
    
    console.log('Updating theme UI, isDark:', isDark);
    
    if (themeText) {
      themeText.textContent = isDark ? 'Light mode' : 'Dark mode';
    }
    if (sunIcon) {
      sunIcon.classList.toggle('hidden', !isDark);
      sunIcon.classList.toggle('block', isDark);
    }
    if (moonIcon) {
      moonIcon.classList.toggle('hidden', isDark);
      moonIcon.classList.toggle('block', !isDark);
    }
  }
  
  // Toggle theme
  function toggleTheme() {
    const isDark = root.classList.contains('dark');
    const newTheme = isDark ? 'light' : 'dark';
    
    console.log('Toggling theme from', isDark ? 'dark' : 'light', 'to', newTheme);
    
    root.classList.toggle('dark');
    root.setAttribute('data-theme', newTheme);
    localStorage.setItem(key, newTheme);
    updateThemeUI(!isDark);
    
    // Add a subtle animation effect
    root.style.transition = 'all 0.3s ease';
    setTimeout(() => {
      root.style.transition = '';
    }, 300);
  }
  
  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem(key)) {
      initTheme();
    }
  });
  
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    initTheme();
  }
  
  // Add click listener
  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('themeToggle');
    console.log('Theme toggle button found:', btn);
    if (btn) {
      btn.addEventListener('click', toggleTheme);
      console.log('Theme toggle listener added');
    }
  });
})();

// Enhanced UI Features
(function() {
  'use strict';
  
  // Enhanced loading states and animations
  function showLoadingState(element, text = 'Loading...') {
    const originalContent = element.innerHTML;
    element.innerHTML = `
      <div class="flex items-center justify-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        ${text}
      </div>
    `;
    return originalContent;
  }

  function hideLoadingState(element, originalContent) {
    element.innerHTML = originalContent;
  }

  // Enhanced notification system
  function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
    
    const colors = {
      success: 'bg-green-500 text-white',
      error: 'bg-red-500 text-white',
      warning: 'bg-yellow-500 text-black',
      info: 'bg-blue-500 text-white'
    };
    
    notification.className += ` ${colors[type]}`;
    notification.innerHTML = `
      <div class="flex items-center">
        <div class="flex-1">
          <p class="text-sm font-medium">${message}</p>
        </div>
        <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove
    setTimeout(() => {
      notification.classList.add('translate-x-full');
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, duration);
  }

  // Enhanced scroll animations
  function initScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
      observer.observe(el);
    });
  }

  // Enhanced button interactions
  function enhanceButtons() {
    document.querySelectorAll('button, .btn').forEach(button => {
      button.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.1)';
      });
      
      button.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '';
      });
    });
  }

  // Enhanced card hover effects
  function enhanceCards() {
    document.querySelectorAll('.card, .bg-card').forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-4px)';
        this.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.25)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '';
      });
    });
  }

  // Enhanced input focus effects
  function enhanceInputs() {
    document.querySelectorAll('input, textarea, select').forEach(input => {
      input.addEventListener('focus', function() {
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.3)';
      });
      
      input.addEventListener('blur', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '';
      });
    });
  }

  // Enhanced form validation with real-time feedback
  function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
      const value = input.value.trim();
      const isValidInput = value !== '';
      
      if (!isValidInput) {
        input.classList.add('border-red-500', 'bg-red-50');
        input.classList.remove('border-green-500', 'bg-green-50');
        isValid = false;
      } else {
        input.classList.remove('border-red-500', 'bg-red-50');
        input.classList.add('border-green-500', 'bg-green-50');
      }
    });
    
    return isValid;
  }

  // Initialize all enhancements when DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    initScrollAnimations();
    enhanceButtons();
    enhanceCards();
    enhanceInputs();
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  });

  // Enhanced error handling
  window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showNotification('An error occurred. Please refresh the page.', 'error');
  });

  // Enhanced network status monitoring
  window.addEventListener('online', function() {
    showNotification('Connection restored', 'success', 3000);
  });

  window.addEventListener('offline', function() {
    showNotification('Connection lost. Some features may not work.', 'warning', 10000);
  });

  // Make functions globally available
  window.showLoadingState = showLoadingState;
  window.hideLoadingState = hideLoadingState;
  window.showNotification = showNotification;
  window.validateForm = validateForm;
})();
