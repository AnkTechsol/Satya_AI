# Main Owner Visual Specs & Dev Notes

## 1. CSS Size Tokens & Spacing
```css
:root {
    --card-radius: 16px;
    --card-padding-lg: 2rem;
    --card-padding-md: 1.25rem;
    --card-padding-sm: 1rem;
    --card-gap: 1.5rem;
    --transition-speed: 0.3s;
}

/* Card Base Styles */
.promo-card {
    border-radius: var(--card-radius);
    transition: all var(--transition-speed) ease;
    cursor: pointer;
    text-decoration: none;
    display: flex;
    flex-direction: column;
    border: 1px solid var(--border);
    overflow: hidden;
    position: relative;
}

.promo-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px var(--shadow-color);
}

.promo-card:active {
    transform: translateY(-2px);
}

/* 1. Hero Card (Large) */
.hero-card {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    padding: var(--card-padding-lg);
    color: white;
    min-height: 240px;
    justify-content: center;
}

.hero-card .card-headline {
    font-size: 1.75rem;
    font-weight: 800;
    margin-bottom: 0.75rem;
    color: white;
}

.hero-card .card-body {
    font-size: 1rem;
    opacity: 0.9;
    margin-bottom: 1.5rem;
    max-width: 80%;
}

/* 2. Compact Card (List/Side) */
.compact-card {
    background: var(--bg-card);
    padding: var(--card-padding-md);
    flex-direction: row;
    align-items: center;
    gap: 1rem;
}

.compact-card .card-icon {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
}

.compact-card .card-content {
    flex-grow: 1;
}

.compact-card .card-headline {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.compact-card .card-body {
    font-size: 0.85rem;
    color: var(--text-secondary);
}

/* 3. Mobile Tile */
.mobile-tile {
    background: var(--bg-card);
    padding: var(--card-padding-sm);
    text-align: center;
    aspect-ratio: 1 / 1;
    justify-content: space-between;
}

.mobile-tile .card-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 0.5rem;
}

.mobile-tile .card-headline {
    font-size: 0.95rem;
    font-weight: 700;
}

/* Accessibility: 4.5:1 Contrast for CTA */
.card-cta {
    display: inline-block;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.9rem;
    text-align: center;
    transition: background 0.2s;
}

.hero-card .card-cta {
    background: white;
    color: var(--primary);
}

.hero-card .card-cta:hover {
    background: var(--bg-card-hover);
}

.compact-card .card-cta, .mobile-tile .card-cta {
    background: var(--primary);
    color: white;
}
```

## 2. SVG Assets (Main Owner Icon)
```xml
<!-- Main Owner Identity Icon (SVG) -->
<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="32" fill="#6C5CE7" fill-opacity="0.1"/>
  <path d="M32 12C24.268 12 18 18.268 18 26C18 33.732 24.268 40 32 40C39.732 40 46 33.732 46 26C46 18.268 39.732 12 32 12ZM32 16C37.523 16 42 20.477 42 26C42 31.523 37.523 36 32 36C26.477 36 22 31.523 22 26C22 20.477 26.477 16 32 16ZM32 42C23.163 42 16 49.163 16 58H48C48 49.163 40.837 42 32 42Z" fill="#6C5CE7"/>
  <path d="M32 32L36 36L44 28" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

## 3. Analytics Integration Notes
**Analytics Event Names:**
- `main_owner_promo_view`: Triggered when a promo card enters the viewport.
- `main_owner_promo_click`: Triggered when a promo card or its CTA is clicked.
- `main_owner_setup_start`: Triggered when the user begins the setup guide.
- `main_owner_setup_complete`: Triggered when the 3rd step of setup is confirmed.

**Sample Payload:**
```json
{
  "event": "main_owner_promo_click",
  "properties": {
    "card_size": "hero",
    "variant": "A",
    "headline": "Master Your AI Fleet",
    "cta": "Set Main Owner",
    "location": "dashboard_top"
  }
}
```

## 4. Accessibility Check
- **Contrast:** Headline and CTA text maintain at least 4.5:1 ratio against their respective backgrounds (White on #6C5CE7 or #6C5CE7 on White).
- **Semantic HTML:** Cards use `<article>` or `<section>` tags. CTAs use `<button>` or `<a>` tags with descriptive `aria-label`.
- **Focus States:** `:focus-visible` outline included via default browser styles or custom `--primary` ring.
