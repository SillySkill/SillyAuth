/**
 * Mobile Menu JavaScript
 * Handles mobile navigation menu functionality
 */

(function() {
  'use strict';

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    createMobileMenuToggle();
    createMobileOverlay();
    initMobileMenuEvents();
    initSidebarToggle();
    initFiltersPanel();
    handleResize();
  }

  /**
   * Create mobile menu toggle button
   */
  function createMobileMenuToggle() {
    const navbarContent = document.querySelector('.navbar-content');
    if (!navbarContent) return;

    // Check if toggle already exists
    if (navbarContent.querySelector('.mobile-menu-toggle')) return;

    const toggle = document.createElement('button');
    toggle.className = 'mobile-menu-toggle';
    toggle.setAttribute('aria-label', 'Toggle navigation menu');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.innerHTML = '<i class="fas fa-bars"></i>';

    // Insert toggle before nav actions
    const navActions = navbarContent.querySelector('.nav-actions');
    if (navActions) {
      navbarContent.insertBefore(toggle, navActions);
    } else {
      navbarContent.appendChild(toggle);
    }

    // Store reference
    window.mobileMenuToggle = toggle;
  }

  /**
   * Create mobile menu overlay
   */
  function createMobileOverlay() {
    // Check if overlay already exists
    if (document.querySelector('.mobile-menu-overlay')) return;

    const overlay = document.createElement('div');
    overlay.className = 'mobile-menu-overlay';
    document.body.appendChild(overlay);

    // Store reference
    window.mobileMenuOverlay = overlay;
  }

  /**
   * Initialize mobile menu events
   */
  function initMobileMenuEvents() {
    const toggle = window.mobileMenuToggle;
    const navLinks = document.querySelector('.nav-links');
    const overlay = window.mobileMenuOverlay;

    if (!toggle || !navLinks) return;

    // Toggle menu on button click
    toggle.addEventListener('click', function(e) {
      e.stopPropagation();
      toggleMenu();
    });

    // Close menu on overlay click
    if (overlay) {
      overlay.addEventListener('click', closeMenu);
    }

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
      if (navLinks.classList.contains('active') &&
          !navLinks.contains(e.target) &&
          !toggle.contains(e.target)) {
        closeMenu();
      }
    });

    // Close menu on window resize if opened
    window.addEventListener('resize', function() {
      if (window.innerWidth > 768 && navLinks.classList.contains('active')) {
        closeMenu();
      }
    });

    // Close menu on link click
    const links = navLinks.querySelectorAll('.nav-link');
    links.forEach(function(link) {
      link.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
          closeMenu();
        }
      });
    });
  }

  /**
   * Toggle mobile menu open/closed
   */
  function toggleMenu() {
    const navLinks = document.querySelector('.nav-links');
    const toggle = window.mobileMenuToggle;
    const overlay = window.mobileMenuOverlay;

    if (!navLinks) return;

    const isOpen = navLinks.classList.toggle('active');

    // Update ARIA attribute
    if (toggle) {
      toggle.setAttribute('aria-expanded', isOpen);
    }

    // Update overlay
    if (overlay) {
      overlay.classList.toggle('active', isOpen);
    }

    // Update icon
    if (toggle) {
      const icon = toggle.querySelector('i');
      if (icon) {
        icon.className = isOpen ? 'fas fa-times' : 'fas fa-bars';
      }
    }

    // Prevent body scroll when menu is open
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }

  /**
   * Close mobile menu
   */
  function closeMenu() {
    const navLinks = document.querySelector('.nav-links');
    const toggle = window.mobileMenuToggle;
    const overlay = window.mobileMenuOverlay;

    if (navLinks) {
      navLinks.classList.remove('active');
    }

    if (toggle) {
      toggle.setAttribute('aria-expanded', 'false');
      const icon = toggle.querySelector('i');
      if (icon) {
        icon.className = 'fas fa-bars';
      }
    }

    if (overlay) {
      overlay.classList.remove('active');
    }

    // Restore body scroll
    document.body.style.overflow = '';
  }

  /**
   * Initialize sidebar toggle for dashboard pages
   */
  function initSidebarToggle() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    if (!sidebar || !mainContent) return;

    // Create sidebar toggle button
    const topBar = document.querySelector('.top-bar');
    if (!topBar) return;

    // Check if toggle already exists
    if (topBar.querySelector('.sidebar-toggle')) return;

    const toggle = document.createElement('button');
    toggle.className = 'btn-icon sidebar-toggle';
    toggle.setAttribute('aria-label', 'Toggle sidebar');
    toggle.innerHTML = '<i class="fas fa-bars"></i>';

    // Insert at the beginning of top bar
    topBar.insertBefore(toggle, topBar.firstChild);

    // Create sidebar overlay
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'sidebar-overlay';
      document.body.appendChild(overlay);
    }

    // Toggle sidebar
    toggle.addEventListener('click', function() {
      sidebar.classList.toggle('active');
      overlay.classList.toggle('active');
      document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
    });

    // Close sidebar on overlay click
    overlay.addEventListener('click', function() {
      sidebar.classList.remove('active');
      overlay.classList.remove('active');
      document.body.style.overflow = '';
    });

    // Close sidebar on window resize if opened
    window.addEventListener('resize', function() {
      if (window.innerWidth > 768 && sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  /**
   * Initialize filters panel for listing pages
   */
  function initFiltersPanel() {
    const pageWithSidebar = document.querySelector('.page-with-sidebar, [style*="grid-template-columns: 280px"]');
    if (!pageWithSidebar) return;

    const sidebar = pageWithSidebar.querySelector('aside, [style*="sticky"]');
    if (!sidebar) return;

    // Check if filters toggle already exists
    if (document.querySelector('.filters-toggle-btn')) return;

    const container = pageWithSidebar.querySelector('.container');
    if (!container) return;

    // Create filters toggle button
    const toggle = document.createElement('button');
    toggle.className = 'btn btn-secondary filters-toggle-btn';
    toggle.innerHTML = '<i class="fas fa-filter"></i> 筛选';
    toggle.style.display = 'none';
    toggle.style.marginBottom = 'var(--space-md)';
    toggle.style.width = '100%';

    // Insert before the grid
    const grid = pageWithSidebar.querySelector('[style*="grid-template-columns"]');
    if (grid) {
      grid.parentNode.insertBefore(toggle, grid);
    }

    // Make sidebar responsive
    sidebar.classList.add('filters-panel');

    // Toggle filters panel
    toggle.addEventListener('click', function() {
      sidebar.classList.toggle('active');
    });

    // Show toggle button on mobile
    window.addEventListener('resize', function() {
      if (window.innerWidth <= 768) {
        toggle.style.display = 'flex';
      } else {
        toggle.style.display = 'none';
        sidebar.classList.remove('active');
      }
    });

    // Check on load
    if (window.innerWidth <= 768) {
      toggle.style.display = 'flex';
    }
  }

  /**
   * Handle window resize
   */
  function handleResize() {
    let resizeTimer;
    window.addEventListener('resize', function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function() {
        // Close mobile menu on resize to desktop
        if (window.innerWidth > 768) {
          const navLinks = document.querySelector('.nav-links');
          const toggle = window.mobileMenuToggle;
          const overlay = window.mobileMenuOverlay;

          if (navLinks) navLinks.classList.remove('active');
          if (toggle) toggle.setAttribute('aria-expanded', 'false');
          if (overlay) overlay.classList.remove('active');
          document.body.style.overflow = '';
        }

        // Close sidebar on resize to desktop
        if (window.innerWidth > 768) {
          const sidebar = document.querySelector('.sidebar');
          const sidebarOverlay = document.querySelector('.sidebar-overlay');

          if (sidebar) sidebar.classList.remove('active');
          if (sidebarOverlay) sidebarOverlay.classList.remove('active');
        }
      }, 250);
    });
  }

  /**
   * Expose public API
   */
  window.MobileMenu = {
    toggle: toggleMenu,
    close: closeMenu,
    isOpen: function() {
      const navLinks = document.querySelector('.nav-links');
      return navLinks ? navLinks.classList.contains('active') : false;
    }
  };

})();
