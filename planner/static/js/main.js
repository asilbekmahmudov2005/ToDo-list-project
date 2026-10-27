document.addEventListener('DOMContentLoaded', () => {
  // 1. Dark Mode / Light Mode
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const themeIcon = document.getElementById('theme-icon');
  
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeIcon) return;
    if (theme === 'dark') {
      themeIcon.className = 'fa-solid fa-sun';
    } else {
      themeIcon.className = 'fa-solid fa-moon';
    }
  }

  // 2. Mobile Sidebar Toggle
  const menuToggle = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebar-overlay');

  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      if (sidebarOverlay) sidebarOverlay.classList.toggle('active');
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      sidebarOverlay.classList.remove('active');
    });
  }

  // 3. Task Status Toggle (Bajarildi/Bajarilmadi)
  document.querySelectorAll('.task-check-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const actionUrl = form.action;
      const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
      const taskItem = form.closest('.task-item');
      const checkBtn = form.querySelector('.task-check-btn');

      try {
        const response = await fetch(actionUrl, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.is_completed) {
            taskItem.classList.add('completed');
            checkBtn.classList.add('checked');
            checkBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
          } else {
            taskItem.classList.remove('completed');
            checkBtn.classList.remove('checked');
            checkBtn.innerHTML = '';
          }

          // Dashboard statistikasini yangilash agar sahifada mavjud bo'lsa
          const totalStat = document.getElementById('stat-total-today');
          const completedStat = document.getElementById('stat-completed-today');
          const pendingStat = document.getElementById('stat-pending-today');
          const percentStat = document.getElementById('stat-progress-percent');
          const progressBar = document.getElementById('dashboard-progress-bar');

          if (completedStat && data.completed_today !== undefined) {
            completedStat.innerText = data.completed_today;
          }
          if (pendingStat && data.pending_today !== undefined) {
            pendingStat.innerText = data.pending_today;
          }
          if (percentStat && data.progress_percentage !== undefined) {
            percentStat.innerText = data.progress_percentage + '%';
          }
          if (progressBar && data.progress_percentage !== undefined) {
            progressBar.style.width = data.progress_percentage + '%';
          }
        }
      } catch (err) {
        console.error("Vazifa holatini o‘zgartirishda xatolik:", err);
        form.submit(); // fallback
      }
    });
  });

  // 4. Modal Oynalar (Yangi vazifa & Tahrirlash)
  const taskModal = document.getElementById('task-modal');
  const taskModalTitle = document.getElementById('task-modal-title');
  const taskForm = document.getElementById('task-form');
  const openCreateBtns = document.querySelectorAll('.open-create-task-modal');
  const closeModalBtns = document.querySelectorAll('.close-modal-btn');

  // Yangi vazifa ochish
  openCreateBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (!taskModal) return;
      taskModalTitle.innerText = "Yangi vazifa yaratish";
      taskForm.action = "/tasks/create/";
      taskForm.reset();

      // Agar tugmada data-date bo'lsa (taqvimdan bosilganda)
      const targetDate = btn.getAttribute('data-date');
      if (targetDate) {
        const dateInput = taskForm.querySelector('[name=date]');
        if (dateInput) dateInput.value = targetDate;
      }

      taskModal.classList.add('active');
    });
  });

  // Tahrirlash modalini ochish
  document.querySelectorAll('.open-edit-task-modal').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const taskId = btn.getAttribute('data-id');
      if (!taskId || !taskModal) return;

      try {
        const response = await fetch(`/tasks/${taskId}/json/`, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (response.ok) {
          const task = await response.json();
          taskModalTitle.innerText = "Vazifani tahrirlash";
          taskForm.action = `/tasks/${task.id}/update/`;

          taskForm.querySelector('[name=title]').value = task.title || '';
          taskForm.querySelector('[name=description]').value = task.description || '';
          taskForm.querySelector('[name=date]').value = task.date || '';
          taskForm.querySelector('[name=start_time]').value = task.start_time || '';
          taskForm.querySelector('[name=end_time]').value = task.end_time || '';
          taskForm.querySelector('[name=duration]').value = task.duration || '';
          taskForm.querySelector('[name=priority]').value = task.priority || 'medium';
          taskForm.querySelector('[name=category]').value = task.category || 'personal';
          
          const completedCheckbox = taskForm.querySelector('[name=is_completed]');
          if (completedCheckbox) {
            completedCheckbox.checked = task.is_completed;
          }

          taskModal.classList.add('active');
        }
      } catch (err) {
        console.error("Vazifa maʼlumotlarini yuklashda xatolik:", err);
      }
    });
  });

  // Modalni yopish
  closeModalBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (taskModal) taskModal.classList.remove('active');
      const deleteModal = document.getElementById('delete-modal');
      if (deleteModal) deleteModal.classList.remove('active');
    });
  });

  // Modal tashqarisiga bosganda yopish
  window.addEventListener('click', (e) => {
    if (taskModal && e.target === taskModal) {
      taskModal.classList.remove('active');
    }
    const deleteModal = document.getElementById('delete-modal');
    if (deleteModal && e.target === deleteModal) {
      deleteModal.classList.remove('active');
    }
  });

  // 5. O'chirishni xavfsiz tasdiqlash modali
  const deleteModal = document.getElementById('delete-modal');
  const deleteForm = document.getElementById('delete-task-form');
  const deleteTitleSpan = document.getElementById('delete-task-title');

  document.querySelectorAll('.open-delete-modal').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const taskId = btn.getAttribute('data-id');
      const taskTitle = btn.getAttribute('data-title');
      if (deleteModal && deleteForm) {
        deleteForm.action = `/tasks/${taskId}/delete/`;
        if (deleteTitleSpan) deleteTitleSpan.innerText = taskTitle;
        deleteModal.classList.add('active');
      }
    });
  });
});
