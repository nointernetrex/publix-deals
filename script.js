// SquatchyStack.com - Deal Hunter Scripts

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('search-input');
    const searchClear = document.getElementById('search-clear');
    const filterChips = document.querySelectorAll('.filter-chip:not(.clear-filter)');
    const clearFilterBtn = document.querySelector('.filter-chip.clear-filter');
    const dealRows = document.querySelectorAll('.deal-row');
    const sections = document.querySelectorAll('.deals-section');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const nav = document.getElementById('main-nav');

    let activeFilter = null;

    // Mobile menu toggle
    if (mobileMenuBtn && nav) {
        mobileMenuBtn.addEventListener('click', function() {
            nav.classList.toggle('open');
            const isOpen = nav.classList.contains('open');
            mobileMenuBtn.setAttribute('aria-expanded', isOpen);
        });
    }

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();

            // Show/hide clear button
            if (searchClear) {
                searchClear.classList.toggle('visible', query.length > 0);
            }

            filterDeals();
        });
    }

    // Search clear button
    if (searchClear) {
        searchClear.addEventListener('click', function() {
            searchInput.value = '';
            searchClear.classList.remove('visible');
            filterDeals();
            searchInput.focus();
        });
    }

    // Filter chips
    filterChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const filter = this.dataset.filter;

            // Toggle active state
            if (activeFilter === filter) {
                activeFilter = null;
                this.classList.remove('active');
            } else {
                filterChips.forEach(c => c.classList.remove('active'));
                this.classList.add('active');
                activeFilter = filter;
            }

            filterDeals();
        });
    });

    // Clear filters
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', function() {
            activeFilter = null;
            filterChips.forEach(c => c.classList.remove('active'));
            searchInput.value = '';
            if (searchClear) searchClear.classList.remove('visible');
            filterDeals();
        });
    }

    // Filter deals function
    function filterDeals() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

        dealRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const type = row.dataset.type;

            const matchesSearch = !query || text.includes(query);
            const matchesFilter = !activeFilter || type === activeFilter;

            row.style.display = matchesSearch && matchesFilter ? '' : 'none';
        });

        // Update section visibility and counts
        sections.forEach(section => {
            const visibleRows = section.querySelectorAll('.deal-row[style=""], .deal-row:not([style])');
            const visibleCount = Array.from(section.querySelectorAll('.deal-row'))
                .filter(row => row.style.display !== 'none').length;

            const countEl = section.querySelector('.section-count');
            if (countEl) {
                countEl.textContent = visibleCount + ' deals';
            }

            // Hide section if no visible deals
            const dealsList = section.querySelector('.deals-list');
            if (dealsList) {
                const hasVisible = Array.from(dealsList.querySelectorAll('.deal-row'))
                    .some(row => row.style.display !== 'none');
                section.style.display = hasVisible ? '' : 'none';
            }
        });

        // Show no results message
        updateNoResults();
    }

    // No results message
    function updateNoResults() {
        let noResultsEl = document.getElementById('no-results');
        const anyVisible = Array.from(dealRows).some(row => row.style.display !== 'none');

        if (!anyVisible) {
            if (!noResultsEl) {
                noResultsEl = document.createElement('div');
                noResultsEl.id = 'no-results';
                noResultsEl.className = 'no-results';
                noResultsEl.innerHTML = `
                    <div class="no-results-icon">🔍</div>
                    <h3>No deals found</h3>
                    <p>Try adjusting your search or filters</p>
                `;
                document.querySelector('.main-content').appendChild(noResultsEl);
            }
            noResultsEl.style.display = '';
        } else if (noResultsEl) {
            noResultsEl.style.display = 'none';
        }
    }

    // Copy to clipboard functionality
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const dealRow = this.closest('.deal-row');
            const dealText = dealRow.dataset.copyText || dealRow.querySelector('.deal-content').textContent.trim();

            try {
                await navigator.clipboard.writeText(dealText);

                const originalText = this.textContent;
                this.textContent = 'Copied!';
                this.classList.add('copied');

                setTimeout(() => {
                    this.textContent = originalText;
                    this.classList.remove('copied');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });

    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = target.offsetTop - headerHeight - 20;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                if (nav) nav.classList.remove('open');
            }
        });
    });

    // Keyboard navigation for chips
    filterChips.forEach(chip => {
        chip.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
});
