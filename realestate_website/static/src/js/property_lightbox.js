/** realestate_website/static/src/js/property_lightbox.js **/
odoo.define('realestate_website.property_lightbox', function (require) {
  'use strict';
  const domReady = require('web.dom_ready');

  // Helpers
  function byId(id)     { return document.getElementById(id); }
  function on(el, ev, cb, opts) { el && el.addEventListener(ev, cb, opts || false); }
  function hasClass(el, c) { return el && el.classList.contains(c); }

  // Bootstrap helpers
  function getModal(el)    { return window.bootstrap && el ? window.bootstrap.Modal.getOrCreateInstance(el) : null; }
  function getCarousel(el) { return window.bootstrap && el ? window.bootstrap.Carousel.getOrCreateInstance(el, { interval: false, ride: false }) : null; }

  domReady(function () {
    if (!window.bootstrap) return; // BS5 required

    /* ---------------- GALLERY ---------------- */
    const galleryModalEl    = byId('galleryModal');
    const galleryCarouselEl = byId('galleryCarousel');
    const galleryCounterEl  = byId('galleryCounter');

    // Delegate clicks from any .gallery-thumb
    on(document, 'click', function (e) {
      const thumb = e.target.closest('.gallery-thumb');
      if (!thumb) return;

      const index = parseInt(thumb.getAttribute('data-index') || '0', 10);
      if (!galleryModalEl || !galleryCarouselEl) return;

      const modal    = getModal(galleryModalEl);
      const carousel = getCarousel(galleryCarouselEl);
      if (!modal || !carousel) return;

      modal.show();
      // jump after modal shown (ensures layout is ready)
      const onShown = () => {
        try { carousel.to(index); } catch (_) {}
        galleryModalEl.removeEventListener('shown.bs.modal', onShown);
        updateGalleryCounter(index);
      };
      on(galleryModalEl, 'shown.bs.modal', onShown);
    });

    // Update counter on slide
    function updateGalleryCounter(activeIndex) {
      if (!galleryCounterEl) return;
      const total = galleryCarouselEl ? galleryCarouselEl.querySelectorAll('.carousel-item').length : 0;
      if (total > 0) galleryCounterEl.textContent = (activeIndex + 1) + '/' + total;
    }

    on(galleryCarouselEl, 'slid.bs.carousel', function (ev) {
      // ev.to is provided by BS5
      const idx = (typeof ev.to === 'number') ? ev.to
                 : Array.from(galleryCarouselEl.querySelectorAll('.carousel-item')).findIndex(i => hasClass(i, 'active'));
      if (idx >= 0) updateGalleryCounter(idx);
    });

    // Keyboard nav while gallery modal visible
    on(document, 'keydown', function (e) {
      if (!galleryModalEl || !hasClass(galleryModalEl, 'show')) return;
      const carousel = getCarousel(galleryCarouselEl);
      if (!carousel) return;
      if (e.key === 'ArrowLeft')  carousel.prev();
      if (e.key === 'ArrowRight') carousel.next();
      if (e.key === 'Escape')     getModal(galleryModalEl)?.hide();
    });

    /* ---------------- PLANS ---------------- */
    // Delegate clicks from any .plan-thumb
    on(document, 'click', function (e) {
      const thumb = e.target.closest('.plan-thumb');
      if (!thumb) return;

      const planId = thumb.getAttribute('data-plan');
      const index  = parseInt(thumb.getAttribute('data-index') || '0', 10);

      const modalEl    = byId('plan-modal-' + planId);
      const carouselEl = byId('planCarousel-' + planId);
      if (!modalEl || !carouselEl) return;

      const modal    = getModal(modalEl);
      const carousel = getCarousel(carouselEl);
      if (!modal || !carousel) return;

      modal.show();
      const onShown = () => {
        try { carousel.to(index); } catch (_) {}
        modalEl.removeEventListener('shown.bs.modal', onShown);
      };
      on(modalEl, 'shown.bs.modal', onShown);
    });
  });
});
