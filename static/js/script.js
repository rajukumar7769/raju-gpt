// const toggleSidebarButton = document.getElementById('toggle-sidebar');
// const sidebar = document.getElementById('sidebar');
// const mainContent = document.getElementById('main-content');
// const inputContainer = document.getElementById('input-container');

// toggleSidebarButton.addEventListener('click', () => {
//   sidebar.classList.toggle('collapsed');
//   if (sidebar.classList.contains('collapsed')) {
//     mainContent.style.marginLeft = '0';
//     inputContainer.style.left = '16px';
//     inputContainer.style.width = 'calc(100% - 32px)';
//   } else {
//     mainContent.style.marginLeft = 'var(--sidebar-width)';
//     inputContainer.style.left = 'var(--sidebar-width)';
//     inputContainer.style.width = 'calc(100% - var(--sidebar-width) - 32px)';
//   }
// });

// const toggleModeButton = document.getElementById('toggle-mode');
// const modeIcon = document.getElementById('mode-icon');

// toggleModeButton.addEventListener('click', () => {
//   const body = document.body;
//   if (body.classList.contains('dark-mode')) {
//     body.classList.remove('dark-mode');
//     body.classList.add('light-mode');
//     modeIcon.classList.remove('fa-moon');
//     modeIcon.classList.add('fa-sun');
//     toggleModeButton.innerHTML = '<i id="mode-icon" class="fas fa-sun"></i> Light Mode';
//   } else {
//     body.classList.remove('light-mode');
//     body.classList.add('dark-mode');
//     modeIcon.classList.remove('fa-sun');
//     modeIcon.classList.add('fa-moon');
//     toggleModeButton.innerHTML = '<i id="mode-icon" class="fas fa-moon"></i> Dark Mode';
//   }
// });
