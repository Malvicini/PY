/**
 * Modern Sidebar Resize & Responsive Manager
 * Handles desktop drag-resize and responsive overlay behavior
 */
function SidebarManager() {
  this.sidebar = document.getElementById('sidebar');
  this.main = document.getElementById('main');
  this.resizeGrip = document.getElementById('resize-grip');

  // State
  this.isResizing = false;
  this.isDesktop = false;
  this.currentWidth = 320; // Initial desktop width

  // Bind methods
  this.handleMouseDown = this.handleMouseDown.bind(this);
  this.handleMouseMove = this.handleMouseMove.bind(this);
  this.handleMouseUp = this.handleMouseUp.bind(this);
  this.handleWindowResize = this.handleWindowResize.bind(this);
  this.updateLayout = this.updateLayout.bind(this);

  // Initialize
  this.init();
}
  
SidebarManager.prototype.init = function() {
  // Set up event listeners
  if (this.resizeGrip) {
    this.resizeGrip.addEventListener('mousedown', this.handleMouseDown);
  }
  
  // Global mouse events for drag
  document.addEventListener('mousemove', this.handleMouseMove);
  document.addEventListener('mouseup', this.handleMouseUp);
  
  // Window events
  window.addEventListener('resize', this.handleWindowResize);
  window.addEventListener('load', this.updateLayout);
  
  // Initial layout
  this.updateLayout();
};
  
SidebarManager.prototype.updateLayout = function() {
  const width = window.innerWidth;
  const wasDesktop = this.isDesktop;
  
  // Determine responsive mode
  this.isDesktop = width > 1024;
  
  if (this.isDesktop) {
    // Desktop mode: resizable sidebar
    this.sidebar.classList.remove('mobile-overlay', 'mobile-hidden');
    this.sidebar.style.position = 'fixed';
    this.sidebar.style.width = this.currentWidth + 'px';
    this.main.style.marginLeft = this.currentWidth + 'px';
    
    // Enable resize grip
    if (this.resizeGrip) {
      this.resizeGrip.style.display = 'block';
    }
  } else {
    // Mobile/Tablet mode: overlay sidebar
    this.sidebar.classList.add('mobile-overlay');
    this.sidebar.classList.remove('mobile-hidden');
    this.sidebar.style.position = 'fixed';
    
    // Fixed width based on screen size
    const fixedWidth = width <= 768 ? 280 : 300;
    this.sidebar.style.width = fixedWidth + 'px';
    this.main.style.marginLeft = '0px';
    
    // Hide resize grip
    if (this.resizeGrip) {
      this.resizeGrip.style.display = 'none';
    }
  }
  
  // Force layout recalculation to prevent glitches
  this.forceLayoutRecalc();
};
  
SidebarManager.prototype.handleMouseDown = function(e) {
  if (!this.isDesktop || !this.resizeGrip) return;
  
  this.isResizing = true;
  e.preventDefault();
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
};

SidebarManager.prototype.handleMouseMove = function(e) {
  if (!this.isResizing || !this.isDesktop) return;
  
  const newWidth = Math.max(180, Math.min(800, e.clientX));
  this.currentWidth = newWidth;
  
  // Update sidebar width
  this.sidebar.style.width = newWidth + 'px';
  
  // Update main margin
  this.main.style.marginLeft = newWidth + 'px';
  
  // Prevent layout thrashing
  e.preventDefault();
};

SidebarManager.prototype.handleMouseUp = function() {
  if (!this.isResizing) return;
  
  this.isResizing = false;
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  
  // Final layout sync
  this.forceLayoutRecalc();
};
  
SidebarManager.prototype.handleWindowResize = function() {
  // Debounce resize events
  clearTimeout(this.resizeTimeout);
  this.resizeTimeout = setTimeout(() => {
    this.updateLayout();
  }, 100);
};

SidebarManager.prototype.forceLayoutRecalc = function() {
  // Force browser to recalculate layout
  if (this.sidebar && this.main) {
    this.sidebar.offsetWidth; // Trigger reflow
    this.main.offsetWidth;
  }
};

// Public method to programmatically set width (desktop only)
SidebarManager.prototype.setWidth = function(width) {
  if (!this.isDesktop) return;
  
  this.currentWidth = Math.max(180, Math.min(800, width));
  this.sidebar.style.width = this.currentWidth + 'px';
  this.main.style.marginLeft = this.currentWidth + 'px';
  this.forceLayoutRecalc();
};

// Public method to get current width
SidebarManager.prototype.getWidth = function() {
  return this.currentWidth;
};

// Cleanup method
SidebarManager.prototype.destroy = function() {
  if (this.resizeGrip) {
    this.resizeGrip.removeEventListener('mousedown', this.handleMouseDown);
  }
  document.removeEventListener('mousemove', this.handleMouseMove);
  document.removeEventListener('mouseup', this.handleMouseUp);
  window.removeEventListener('resize', this.handleWindowResize);
  window.removeEventListener('load', this.updateLayout);
};

// Export for use in other scripts (optional)
// window.SidebarManager = SidebarManager;