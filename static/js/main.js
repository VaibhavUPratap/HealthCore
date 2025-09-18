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
