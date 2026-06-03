/* ==================== sjzs Interactive Legal Map ==================== */
(function(global) {
  'use strict';

  var defaults = {
    imageUrl: '/assets/sjzs-map.png',
    apiBase: '/api/config-data',
    category: 'public_law_service',
    minScale: 0.1,
    maxScale: 5,
    zoomStep: 0.9,
    dragDeadZone: 5
  };

  var state = {
    container: null,
    opts: {},
    scale: 1,
    translateX: 0,
    translateY: 0,
    markers: [],
    isDragging: false,
    isMarkerDragging: false,
    dragStartX: 0,
    dragStartY: 0,
    dragOrigX: 0,
    dragOrigY: 0,
    editMode: false,
    overlayOpen: false,
    initialized: false,
    imageLoaded: false,
    activePopup: null,
    cells: null // reference to 24 committees data
  };

  // ── SVG pin icon ──
  var PIN_SVG = '<svg width="28" height="36" viewBox="0 0 28 36" xmlns="http://www.w3.org/2000/svg">' +
    '<path d="M14 0C6.268 0 0 6.268 0 14c0 10.5 14 22 14 22s14-11.5 14-22C28 6.268 21.732 0 14 0z" fill="#4F6EF7"/>' +
    '<circle cx="14" cy="14" r="5" fill="#fff"/>' +
    '</svg>';

  var PIN_SVG_SELECTED = '<svg width="28" height="36" viewBox="0 0 28 36" xmlns="http://www.w3.org/2000/svg">' +
    '<path d="M14 0C6.268 0 0 6.268 0 14c0 10.5 14 22 14 22s14-11.5 14-22C28 6.268 21.732 0 14 0z" fill="#ef4444"/>' +
    '<circle cx="14" cy="14" r="5" fill="#fff"/>' +
    '</svg>';

  var PIN_SVG_GOLD = '<svg width="28" height="36" viewBox="0 0 28 36" xmlns="http://www.w3.org/2000/svg">' +
    '<path d="M14 0C6.268 0 0 6.268 0 14c0 10.5 14 22 14 22s14-11.5 14-22C28 6.268 21.732 0 14 0z" fill="#F59E0B"/>' +
    '<circle cx="14" cy="14" r="5" fill="#fff"/>' +
    '</svg>';

  function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  // ── Toast notification ──
  function showToast(text, type) {
    var existing = document.querySelector('.sjzs-toast');
    if (existing) existing.remove();

    var el = document.createElement('div');
    el.className = 'sjzs-toast ' + (type || 'success');
    el.textContent = text;
    document.body.appendChild(el);
    setTimeout(function () { el.remove(); }, 2500);
  }

  // ── Get image natural display size within container ──
  function getImageRect() {
    var img = state.container && state.container.querySelector('.sjzs-map-area img');
    if (!img) return { w: 1600, h: 2853 };
    // The image is displayed at its natural size initially
    // Use offsetWidth/Height of the map-area which matches img size
    var area = state.container.querySelector('.sjzs-map-area');
    if (area) {
      return { w: area.offsetWidth, h: area.offsetHeight };
    }
    return { w: img.naturalWidth || 1600, h: img.naturalHeight || 2853 };
  }

  // ── Update transform on map-area ──
  function updateTransform() {
    var area = state.container.querySelector('.sjzs-map-area');
    if (!area) return;
    area.style.transform = 'scale(' + state.scale + ') translate(' + state.translateX + 'px, ' + state.translateY + 'px)';
  }

  // ================================================================
  //  ZOOM
  // ================================================================
  function onWheel(e) {
    e.preventDefault();
    var rect = state.container.querySelector('.sjzs-map-canvas').getBoundingClientRect();
    var mx = e.clientX - rect.left;
    var my = e.clientY - rect.top;

    var oldScale = state.scale;
    var factor = e.deltaY > 0 ? state.opts.zoomStep : (1 / state.opts.zoomStep);
    var newScale = Math.max(state.opts.minScale, Math.min(state.opts.maxScale, oldScale * factor));
    if (newScale === oldScale) return;

    // Zoom centered on mouse position
    var area = state.container.querySelector('.sjzs-map-area');
    var areaRect = area.getBoundingClientRect();
    var areaLeft = areaRect.left - rect.left;
    var areaTop = areaRect.top - rect.top;

    // Point on the map under the mouse, in unscaled coordinates
    var px = (mx - areaLeft) / oldScale;
    var py = (my - areaTop) / oldScale;

    state.scale = newScale;
    state.translateX = mx / newScale - px;
    state.translateY = my / newScale - py;

    updateTransform();
  }

  // ================================================================
  //  PAN (drag)
  // ================================================================
  function onMouseDown(e) {
    if (e.button !== 0) return;
    if (state.editMode) return; // don't pan in edit mode
    if (state.isMarkerDragging) return;

    var area = state.container.querySelector('.sjzs-map-area');
    state.isDragging = false;
    state.dragStartX = e.clientX;
    state.dragStartY = e.clientY;
    state.dragOrigX = state.translateX;
    state.dragOrigY = state.translateY;
    area.classList.add('dragging');
  }

  function onMouseMove(e) {
    if (state.isMarkerDragging) return;

    if (state.container.querySelector('.sjzs-map-area.dragging')) {
      var dx = e.clientX - state.dragStartX;
      var dy = e.clientY - state.dragStartY;
      if (!state.isDragging && (Math.abs(dx) > state.opts.dragDeadZone || Math.abs(dy) > state.opts.dragDeadZone)) {
        state.isDragging = true;
      }
      if (state.isDragging) {
        state.translateX = state.dragOrigX + dx / state.scale;
        state.translateY = state.dragOrigY + dy / state.scale;
        updateTransform();
      }
    }
  }

  function onMouseUp() {
    var area = state.container.querySelector('.sjzs-map-area');
    if (area) area.classList.remove('dragging');
    state.isDragging = false;
  }

  // ================================================================
  //  TOUCH SUPPORT (multi-touch pinch zoom + pan)
  // ================================================================
  var touches = [];

  function onTouchStart(e) {
    if (e.touches.length === 1 && !state.editMode) {
      var t = e.touches[0];
      state.dragStartX = t.clientX;
      state.dragStartY = t.clientY;
      state.dragOrigX = state.translateX;
      state.dragOrigY = state.translateY;
      state.isDragging = false;
    } else if (e.touches.length === 2) {
      touches = [e.touches[0], e.touches[1]];
    }
  }

  function onTouchMove(e) {
    if (state.editMode) return;
    if (e.touches.length === 1 && !state.isMarkerDragging) {
      var t = e.touches[0];
      var dx = t.clientX - state.dragStartX;
      var dy = t.clientY - state.dragStartY;
      if (!state.isDragging && (Math.abs(dx) > state.opts.dragDeadZone || Math.abs(dy) > state.opts.dragDeadZone)) {
        state.isDragging = true;
      }
      if (state.isDragging) {
        state.translateX = state.dragOrigX + dx / state.scale;
        state.translateY = state.dragOrigY + dy / state.scale;
        updateTransform();
      }
    } else if (e.touches.length === 2) {
      e.preventDefault();
      var t0 = e.touches[0], t1 = e.touches[1];
      var p0 = touches[0], p1 = touches[1];
      var oldDist = Math.hypot(p0.clientX - p1.clientX, p0.clientY - p1.clientY);
      var newDist = Math.hypot(t0.clientX - t1.clientX, t0.clientY - t1.clientY);
      if (oldDist > 0) {
        var factor = newDist / oldDist;
        var newScale = Math.max(state.opts.minScale, Math.min(state.opts.maxScale, state.scale * factor));
        if (newScale !== state.scale) {
          var canvas = state.container.querySelector('.sjzs-map-canvas');
          var rect = canvas.getBoundingClientRect();
          var cx = (t0.clientX + t1.clientX) / 2 - rect.left;
          var cy = (t0.clientY + t1.clientY) / 2 - rect.top;
          var area = state.container.querySelector('.sjzs-map-area');
          var areaRect = area.getBoundingClientRect();
          var px = (cx - (areaRect.left - rect.left)) / state.scale;
          var py = (cy - (areaRect.top - rect.top)) / state.scale;
          state.scale = newScale;
          state.translateX = cx / newScale - px;
          state.translateY = cy / newScale - py;
          updateTransform();
        }
      }
      touches = [t0, t1];
    }
  }

  function onTouchEnd() {
    state.isDragging = false;
  }

  // ================================================================
  //  OVERLAY
  // ================================================================
  function openOverlay() {
    var overlay = document.getElementById('sjzs-overlay');
    if (!overlay) return;
    overlay.classList.add('active');
    state.overlayOpen = true;
    document.body.style.overflow = 'hidden';
    // Background click to close
    overlay.addEventListener('click', onOverlayClick);

    if (!state.initialized) {
      initMap(state.opts.containerId, state.opts);
    }
    // Fit markers to view on open
    setTimeout(fitToMarkers, 400);
  }

  function closeOverlay() {
    var overlay = document.getElementById('sjzs-overlay');
    if (!overlay) return;
    overlay.classList.remove('active');
    state.overlayOpen = false;
    document.body.style.overflow = '';
    overlay.removeEventListener('click', onOverlayClick);
    closePopup();
    resetView();
  }

  function onKeyDown(e) {
    if (e.key === 'Escape' && state.overlayOpen) {
      closeOverlay();
    }
  }

  function onOverlayClick(e) {
    if (e.target === e.currentTarget) {
      closeOverlay();
    }
  }

  // ── Reset zoom/pan ──
  function resetView() {
    state.scale = 1;
    state.translateX = 0;
    state.translateY = 0;
    updateTransform();
  }

  // ── Fit markers to visible area ──
  function fitToMarkers() {
    if (!state.markers || state.markers.length === 0) return;
    var canvas = state.container.querySelector('.sjzs-map-canvas');
    if (!canvas) return;

    var cw = canvas.clientWidth;
    var ch = canvas.clientHeight;
    if (cw === 0 || ch === 0) return;

    // Find bounding box of all markers (percentage coordinates)
    var minX = 100, maxX = 0, minY = 100, maxY = 0;
    for (var i = 0; i < state.markers.length; i++) {
      var m = state.markers[i];
      var x = parseFloat(m.position_x);
      var y = parseFloat(m.position_y);
      if (!isNaN(x) && !isNaN(y)) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }

    var margin = 15; // percentage margin
    minX = Math.max(0, minX - margin);
    maxX = Math.min(100, maxX + margin);
    minY = Math.max(0, minY - margin);
    maxY = Math.min(100, maxY + margin);

    var imgW = 1600, imgH = 2853;
    var markerW = ((maxX - minX) / 100) * imgW;
    var markerH = ((maxY - minY) / 100) * imgH;

    var scaleX = cw / markerW;
    var scaleY = ch / markerH;
    var fitScale = Math.min(scaleX, scaleY, 2); // cap at 2x
    fitScale = Math.max(state.opts.minScale, Math.min(state.opts.maxScale, fitScale));

    // Center the bounding box
    var centerX = ((minX + maxX) / 200) * imgW;
    var centerY = ((minY + maxY) / 200) * imgH;

    // Calculate translate so center of markers is at center of canvas
    state.scale = fitScale;
    state.translateX = (cw / 2) / fitScale - centerX;
    state.translateY = (ch / 2) / fitScale - centerY;
    updateTransform();
  }

  // ── Fit map height to viewport ──
  function fitToHeight() {
    var canvas = state.container.querySelector('.sjzs-map-canvas');
    var img = state.container.querySelector('.sjzs-map-area img');
    if (!canvas || !img) return;
    var ch = canvas.clientHeight;
    var ih = img.naturalHeight || 2853;
    var fitScale = Math.min(ch / ih, 1);
    fitScale = Math.max(state.opts.minScale, fitScale);
    state.scale = fitScale;
    state.translateX = 0;
    state.translateY = 0;
    updateTransform();
  }

  // ================================================================
  //  POPUP
  // ================================================================
  function closePopup() {
    if (state.activePopup) {
      state.activePopup.remove();
      state.activePopup = null;
    }
  }

  function showPopup(marker) {
    closePopup();

    var data = marker.data || {};

    // Normalize field names: try both abbreviated and full versions
    var fields = {
      name: data.station_name || data.name || marker.name || '',
      phone: data.phone || '',
      address: data.address || '',
      lawyer: data.lawyer || '',
      lawyerPhone: data.lawyer_phone || '',
      hours: data.hours || ''
    };

    var bodyHtml = '';
    if (fields.address) {
      bodyHtml += '<div class="sjzs-popup-row"><i class="fas fa-map-marker-alt"></i><span><span class="sjzs-popup-label">地址：</span>' + escapeHtml(fields.address) + '</span></div>';
    }
    if (fields.phone) {
      bodyHtml += '<div class="sjzs-popup-row"><i class="fas fa-phone"></i><span><span class="sjzs-popup-label">电话：</span>' + escapeHtml(fields.phone) + '</span></div>';
    }
    if (fields.lawyer) {
      var lawyerStr = escapeHtml(fields.lawyer);
      if (fields.lawyerPhone) lawyerStr += ' (' + escapeHtml(fields.lawyerPhone) + ')';
      bodyHtml += '<div class="sjzs-popup-row"><i class="fas fa-gavel"></i><span><span class="sjzs-popup-label">法律顾问：</span>' + lawyerStr + '</span></div>';
    }
    if (fields.hours) {
      bodyHtml += '<div class="sjzs-popup-row"><i class="fas fa-clock"></i><span><span class="sjzs-popup-label">值班时间：</span>' + escapeHtml(fields.hours) + '</span></div>';
    }

    var popup = document.createElement('div');
    popup.className = 'sjzs-popup';
    popup.innerHTML =
      '<div class="sjzs-popup-header">' +
        '<h3>' + escapeHtml(fields.name) + '</h3>' +
        '<button class="sjzs-popup-close" onclick="SJZS_MAP.closePopup()"><i class="fas fa-times"></i></button>' +
      '</div>' +
      '<div class="sjzs-popup-body">' + (bodyHtml || '<div style="color:#999;font-size:13px;">暂无详细信息</div>') + '</div>';

    // Position popup near the marker
    var canvas = state.container.querySelector('.sjzs-map-canvas');
    canvas.appendChild(popup);
    state.activePopup = popup;

    // Find marker element position
    var markerEl = state.container.querySelector('.sjzs-marker[data-name="' + marker.name.replace(/"/g, '&quot;') + '"]');
    if (markerEl) {
      var mRect = markerEl.getBoundingClientRect();
      var cRect = canvas.getBoundingClientRect();
      var popupW = popup.offsetWidth;
      var popupH = popup.offsetHeight;

      // Default: above and right of marker
      var left = mRect.left - cRect.left + 16;
      var top = mRect.top - cRect.top - popupH - 8;

      // Collision detection
      if (top < 4) top = mRect.top - cRect.top + 20; // below if no space above
      if (left + popupW > cRect.width - 4) left = cRect.width - popupW - 4;
      if (left < 4) left = 4;

      popup.style.left = left + 'px';
      popup.style.top = top + 'px';
    } else {
      popup.style.left = '50%';
      popup.style.top = '50%';
      popup.style.transform = 'translate(-50%, -50%)';
    }

    // Click outside popup closes it
    setTimeout(function () {
      function onClickOutside(ev) {
        if (!popup.contains(ev.target) && !ev.target.closest('.sjzs-marker')) {
          closePopup();
          document.removeEventListener('click', onClickOutside);
        }
      }
      document.addEventListener('click', onClickOutside);
    }, 10);
  }

  // ================================================================
  //  MARKERS
  // ================================================================
  function loadMarkers() {
    closePopup();
    var loadingEl = state.container.querySelector('.sjzs-loading');
    var errorEl = state.container.querySelector('.sjzs-error');
    if (loadingEl) loadingEl.style.display = 'flex';
    if (errorEl) errorEl.style.display = 'none';

    fetch(state.opts.apiBase + '/list/' + state.opts.category)
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) {
        // API returns {success, data: {items: [...], total: N}}
        state.markers = (data.data && data.data.items) || data.data || data || [];
        if (loadingEl) loadingEl.style.display = 'none';
        renderMarkers();
        fitToHeight();
      })
      .catch(function (err) {
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) {
          errorEl.style.display = 'flex';
          errorEl.innerHTML =
            '<i class="fas fa-exclamation-triangle"></i>' +
            '<span>加载地图数据失败：' + escapeHtml(err.message) + '</span>' +
            '<button onclick="SJZS_MAP.loadMarkers()">重试</button>';
        }
      });
  }

  function renderMarkers() {
    var wrapper = state.container.querySelector('.sjzs-markers-wrapper');
    if (!wrapper) return;
    wrapper.innerHTML = '';

    for (var i = 0; i < state.markers.length; i++) {
      var m = state.markers[i];
      var px = m.position_x;
      var py = m.position_y;
      if (px == null || py == null) continue;

      var el = document.createElement('div');
      el.className = 'sjzs-marker';
      el.setAttribute('data-name', m.name);
      el.style.left = px + '%';
      el.style.top = py + '%';

      var isGov = m.data && m.data.type === 'governance_center';
      el.innerHTML =
        (isGov ? PIN_SVG_GOLD : PIN_SVG) +
        '<div class="sjzs-marker-label">' + escapeHtml(m.name) + '</div>';

      // Click to show popup
      el.addEventListener('click', function (ev) {
        var name = ev.currentTarget.getAttribute('data-name');
        for (var j = 0; j < state.markers.length; j++) {
          if (state.markers[j].name === name) {
            showPopup(state.markers[j]);
            break;
          }
        }
      });

      wrapper.appendChild(el);
    }
  }

  // ================================================================
  //  MARKER DRAG (edit mode)
  // ================================================================
  function enableMarkerDrag() {
    var markers = state.container.querySelectorAll('.sjzs-marker');
    for (var i = 0; i < markers.length; i++) {
      markers[i].classList.add('draggable');
      markers[i].addEventListener('mousedown', onMarkerDragStart);
      markers[i].addEventListener('touchstart', onMarkerTouchStart, { passive: true });
    }
  }

  function disableMarkerDrag() {
    var markers = state.container.querySelectorAll('.sjzs-marker');
    for (var i = 0; i < markers.length; i++) {
      markers[i].classList.remove('draggable');
      markers[i].removeEventListener('mousedown', onMarkerDragStart);
      markers[i].removeEventListener('touchstart', onMarkerTouchStart);
    }
  }

  var dragMarker = null;
  var dragMarkerOffX = 0;
  var dragMarkerOffY = 0;

  function onMarkerDragStart(e) {
    e.stopPropagation();
    if (e.button !== 0) return;
    state.isMarkerDragging = true;

    dragMarker = e.currentTarget;
    dragMarker.classList.add('dragging');

    var area = state.container.querySelector('.sjzs-map-area');
    var areaRect = area.getBoundingClientRect();
    var canvas = state.container.querySelector('.sjzs-map-canvas');
    var canRect = canvas.getBoundingClientRect();

    // Mouse position in unscaled map coordinates
    var mx = (e.clientX - canRect.left) / state.scale - state.translateX;
    var my = (e.clientY - canRect.top) / state.scale - state.translateY;

    // Marker current position in unscaled map coords
    var imgW = 1600, imgH = 2853;
    var mPctX = parseFloat(dragMarker.style.left);
    var mPctY = parseFloat(dragMarker.style.top);
    var mMapX = (mPctX / 100) * imgW;
    var mMapY = (mPctY / 100) * imgH;

    dragMarkerOffX = mMapX - mx;
    dragMarkerOffY = mMapY - my;

    document.addEventListener('mousemove', onMarkerDragMove);
    document.addEventListener('mouseup', onMarkerDragEnd);
  }

  function onMarkerDragMove(e) {
    if (!dragMarker) return;
    var canvas = state.container.querySelector('.sjzs-map-canvas');
    var canRect = canvas.getBoundingClientRect();
    var imgW = 1600, imgH = 2853;

    var mx = (e.clientX - canRect.left) / state.scale - state.translateX;
    var my = (e.clientY - canRect.top) / state.scale - state.translateY;

    var mapX = mx + dragMarkerOffX;
    var mapY = my + dragMarkerOffY;

    var pctX = Math.max(0, Math.min(100, (mapX / imgW) * 100));
    var pctY = Math.max(0, Math.min(100, (mapY / imgH) * 100));

    dragMarker.style.left = pctX + '%';
    dragMarker.style.top = pctY + '%';
  }

  function onMarkerDragEnd() {
    if (dragMarker) dragMarker.classList.remove('dragging');
    dragMarker = null;
    state.isMarkerDragging = false;
    document.removeEventListener('mousemove', onMarkerDragMove);
    document.removeEventListener('mouseup', onMarkerDragEnd);
  }

  function onMarkerTouchStart(e) {
    if (e.touches.length !== 1) return;
    e.stopPropagation();
    state.isMarkerDragging = true;

    dragMarker = e.currentTarget;
    dragMarker.classList.add('dragging');

    var canvas = state.container.querySelector('.sjzs-map-canvas');
    var canRect = canvas.getBoundingClientRect();
    var imgW = 1600, imgH = 2853;
    var t = e.touches[0];

    var mx = (t.clientX - canRect.left) / state.scale - state.translateX;
    var my = (t.clientY - canRect.top) / state.scale - state.translateY;

    var mPctX = parseFloat(dragMarker.style.left);
    var mPctY = parseFloat(dragMarker.style.top);
    var mMapX = (mPctX / 100) * imgW;
    var mMapY = (mPctY / 100) * imgH;

    dragMarkerOffX = mMapX - mx;
    dragMarkerOffY = mMapY - my;

    document.addEventListener('touchmove', onMarkerTouchMove, { passive: false });
    document.addEventListener('touchend', onMarkerTouchEnd);
  }

  function onMarkerTouchMove(e) {
    e.preventDefault();
    if (!dragMarker || e.touches.length !== 1) return;
    var canvas = state.container.querySelector('.sjzs-map-canvas');
    var canRect = canvas.getBoundingClientRect();
    var imgW = 1600, imgH = 2853;
    var t = e.touches[0];

    var mx = (t.clientX - canRect.left) / state.scale - state.translateX;
    var my = (t.clientY - canRect.top) / state.scale - state.translateY;

    var mapX = mx + dragMarkerOffX;
    var mapY = my + dragMarkerOffY;

    var pctX = Math.max(0, Math.min(100, (mapX / imgW) * 100));
    var pctY = Math.max(0, Math.min(100, (mapY / imgH) * 100));

    dragMarker.style.left = pctX + '%';
    dragMarker.style.top = pctY + '%';
  }

  function onMarkerTouchEnd() {
    if (dragMarker) dragMarker.classList.remove('dragging');
    dragMarker = null;
    state.isMarkerDragging = false;
    document.removeEventListener('touchmove', onMarkerTouchMove);
    document.removeEventListener('touchend', onMarkerTouchEnd);
  }

  // ================================================================
  //  EDIT MODE
  // ================================================================
  function toggleEditMode() {
    state.editMode = !state.editMode;
    var toolbar = state.container.querySelector('.sjzs-toolbar');
    var editBtn = toolbar && toolbar.querySelector('.sjzs-edit-btn');

    if (state.editMode) {
      if (toolbar) toolbar.classList.add('editing');
      if (editBtn) editBtn.classList.add('active');
      enableMarkerDrag();
      showToast('拖拽标记点调整位置，完成后点击"保存位置"');
    } else {
      if (toolbar) toolbar.classList.remove('editing');
      if (editBtn) editBtn.classList.remove('active');
      disableMarkerDrag();
    }
  }

  function savePositions() {
    var markers = state.container.querySelectorAll('.sjzs-marker');
    var items = [];

    for (var i = 0; i < markers.length; i++) {
      var el = markers[i];
      var name = el.getAttribute('data-name');
      var px = parseFloat(el.style.left);
      var py = parseFloat(el.style.top);
      items.push({ name: name, position_x: px, position_y: py });
    }

    fetch(state.opts.apiBase + '/batch-update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: state.opts.category, items: items })
    })
    .then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    })
    .then(function () {
      showToast('位置已保存', 'success');
      // Update local state
      for (var i = 0; i < items.length; i++) {
        for (var j = 0; j < state.markers.length; j++) {
          if (state.markers[j].name === items[i].name) {
            state.markers[j].position_x = items[i].position_x;
            state.markers[j].position_y = items[i].position_y;
            break;
          }
        }
      }
      toggleEditMode(); // exit edit mode
    })
    .catch(function (err) {
      showToast('保存失败：' + err.message, 'error');
    });
  }

  function resetPositions() {
    // Reload from server
    loadMarkers();
    if (state.editMode) toggleEditMode();
    showToast('已重置标记点位置', 'success');
  }

  // ================================================================
  //  INIT
  // ================================================================
  function initMap(containerId, options) {
    state.container = document.getElementById(containerId);
    if (!state.container) {
      console.error('SJZS Map: container not found:', containerId);
      return;
    }
    state.opts = {};
    for (var k in defaults) state.opts[k] = defaults[k];
    if (options) {
      for (var k in options) state.opts[k] = options[k];
    }

    // Reset state
    state.scale = 1;
    state.translateX = 0;
    state.translateY = 0;
    state.markers = [];
    state.initialized = true;
    state.imageLoaded = false;

    // Build DOM
    state.container.innerHTML =
      '<div class="sjzs-map-canvas">' +
        '<div class="sjzs-loading" style="display:flex;">' +
          '<div class="sjzs-spinner"></div><span>加载地图...</span>' +
        '</div>' +
        '<div class="sjzs-error" style="display:none;"></div>' +
        '<div class="sjzs-map-area">' +
          '<img src="' + escapeHtml(state.opts.imageUrl) + '" alt="法治地图" />' +
          '<div class="sjzs-markers-wrapper"></div>' +
        '</div>' +
      '</div>' +
      '<div class="sjzs-toolbar">' +
        '<button class="sjzs-zoom-in" title="放大"><i class="fas fa-plus"></i></button>' +
        '<button class="sjzs-zoom-out" title="缩小"><i class="fas fa-minus"></i></button>' +
        '<button class="sjzs-edit-btn" title="编辑模式"><i class="fas fa-pen"></i></button>' +
        '<button class="sjzs-save-btn" title="保存位置"><i class="fas fa-save"></i></button>' +
        '<button class="sjzs-reset-btn" title="重置"><i class="fas fa-undo"></i></button>' +
        '<button class="sjzs-fit-btn" title="适合全部"><i class="fas fa-expand"></i></button>' +
      '</div>';

    // ── Bind events ──
    var canvas = state.container.querySelector('.sjzs-map-canvas');
    canvas.addEventListener('wheel', onWheel, { passive: false });
    canvas.addEventListener('mousedown', onMouseDown);
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);

    // Touch
    canvas.addEventListener('touchstart', onTouchStart, { passive: true });
    canvas.addEventListener('touchmove', onTouchMove, { passive: false });
    canvas.addEventListener('touchend', onTouchEnd);

    // Toolbar buttons
    state.container.querySelector('.sjzs-zoom-in').addEventListener('click', function () {
      var canvas = state.container.querySelector('.sjzs-map-canvas');
      var rect = canvas.getBoundingClientRect();
      var mx = rect.width / 2;
      var my = rect.height / 2;
      var oldS = state.scale;
      var newS = Math.min(state.opts.maxScale, oldS * (1 / state.opts.zoomStep));
      if (newS === oldS) return;
      // zoom centered on viewport center
      var px = (mx / oldS) - state.translateX;
      var py = (my / oldS) - state.translateY;
      state.scale = newS;
      state.translateX = (mx / newS) - px;
      state.translateY = (my / newS) - py;
      updateTransform();
    });

    state.container.querySelector('.sjzs-zoom-out').addEventListener('click', function () {
      var oldS = state.scale;
      var newS = Math.max(state.opts.minScale, oldS * state.opts.zoomStep);
      if (newS === oldS) return;
      state.scale = newS;
      updateTransform();
    });

    state.container.querySelector('.sjzs-edit-btn').addEventListener('click', toggleEditMode);
    state.container.querySelector('.sjzs-save-btn').addEventListener('click', savePositions);
    state.container.querySelector('.sjzs-reset-btn').addEventListener('click', resetPositions);
    state.container.querySelector('.sjzs-fit-btn').addEventListener('click', fitToMarkers);

    // ── Image load ──
    var img = state.container.querySelector('.sjzs-map-area img');
    if (img.complete) {
      state.imageLoaded = true;
      loadMarkers();
    } else {
      img.addEventListener('load', function () {
        state.imageLoaded = true;
        loadMarkers();
      });
      img.addEventListener('error', function () {
        var loadingEl = state.container.querySelector('.sjzs-loading');
        if (loadingEl) loadingEl.style.display = 'none';
        var errorEl = state.container.querySelector('.sjzs-error');
        if (errorEl) {
          errorEl.style.display = 'flex';
          errorEl.innerHTML =
            '<i class="fas fa-exclamation-triangle"></i>' +
            '<span>地图图片加载失败</span>' +
            '<button onclick="SJZS_MAP.initMap(\'' + containerId + '\', ' + JSON.stringify(options || {}) + ')">重试</button>';
        }
      });
    }
  }

  // ── Cleanup ──
  function destroy() {
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
    document.removeEventListener('keydown', onKeyDown);
    if (state.container) {
      state.container.innerHTML = '';
    }
    state.initialized = false;
  }

  // ================================================================
  //  EXPORT
  // ================================================================
  var SJZS_MAP = {
    init: initMap,
    openOverlay: openOverlay,
    closeOverlay: closeOverlay,
    closePopup: closePopup,
    loadMarkers: loadMarkers,
    toggleEditMode: toggleEditMode,
    savePositions: savePositions,
    resetPositions: resetPositions,
    fitToMarkers: fitToMarkers,
    destroy: destroy
  };

  global.SJZS_MAP = SJZS_MAP;

  // ── Global key listener ──
  document.addEventListener('keydown', onKeyDown);

})(window);
