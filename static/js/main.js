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
