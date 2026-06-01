# Design Tokens & Tailwind Color Mapping

## CSS Variables (Source of Truth)

All colors are defined in `src/app/globals.css` as RGB triplet CSS variables (not hex or hsl). This enables:
- Opacity support: `rgb(var(--color-primary) / 0.5)` → 50% opacity
- Dynamic theme switching: `.dark` class overrides all variables
- Tailwind integration: Variables mapped to Tailwind colors

### Light Mode (`:root`)

```css
:root {
  /* Core colors */
  --color-background: 106 90 205;           /* slateblue (gradient start) */
  --color-background-end: 138 43 226;       /* blueviolet (gradient end) */
  --color-foreground: 255 255 255;          /* white */
  --color-card: 255 255 255;                /* white */
  --color-card-foreground: 17 24 39;        /* gray-900 */
  --color-border: 229 231 235;              /* gray-200 */
  --color-input: 243 244 246;               /* gray-100 */
  --color-input-foreground: 17 24 39;       /* gray-900 */
  
  /* Primary (purple) */
  --color-primary: 109 40 217;              /* purple-600 */
  --color-primary-foreground: 255 255 255;  /* white */
  --color-primary-hover: 91 33 182;         /* purple-700 */
  --color-primary-gradient-start: 139 92 246;  /* purple-500 */
  --color-primary-gradient-end: 109 40 217;    /* purple-600 */
  
  /* Secondary & muted */
  --color-secondary: 243 244 246;           /* gray-100 */
  --color-secondary-foreground: 17 24 39;   /* gray-900 */
  --color-muted: 243 244 246;               /* gray-100 */
  --color-muted-foreground: 107 114 128;    /* gray-500 */
  --color-accent: 243 244 246;              /* gray-100 */
  --color-accent-foreground: 17 24 39;      /* gray-900 */
  
  /* Status colors */
  --color-destructive: 239 68 68;           /* red-500 */
  --color-destructive-foreground: 255 255 255;  /* white */
  --color-error: 254 242 242;               /* red-50 */
  --color-error-foreground: 153 27 27;      /* red-800 */
  --color-success: 240 253 244;             /* green-50 */
  --color-success-foreground: 22 101 52;    /* green-800 */
  
  /* UI ring (focus) */
  --color-ring: 109 40 217;                 /* purple-600 */
  --color-shadow: 0 0 0;                    /* transparent */
  
  /* Toggle background (light purple) */
  --color-toggle-bg: 139 92 246;            /* purple-500 */
}
```

**Light Theme Palette:**
- **Background**: Purple gradient (slateblue → blueviolet) creates eye-catching intro
- **Surface**: Pure white (card, input)
- **Text**: Dark gray-900 on light surfaces
- **Primary**: Purple-600 with hover state (purple-700)
- **Accent**: Light gray (secondary actions)
- **Status**: Red (destructive/error), Green (success)

### Dark Mode (`.dark`)

```css
.dark {
  /* Core colors */
  --color-background: 40 44 52;             /* dark blue-gray #282c34 */
  --color-background-end: 40 44 52;         /* same (no gradient in dark) */
  --color-foreground: 255 255 255;          /* white */
  --color-card: 54 58 69;                   /* slightly lighter #363a45 */
  --color-card-foreground: 255 255 255;     /* white */
  --color-border: 55 65 81;                 /* gray-700 */
  --color-input: 54 58 69;                  /* dark gray */
  --color-input-foreground: 255 255 255;    /* white */
  
  /* Primary (bright purple) */
  --color-primary: 139 92 246;              /* purple-500 (brighter in dark) */
  --color-primary-foreground: 255 255 255;  /* white */
  --color-primary-hover: 124 58 237;        /* purple-600 */
  --color-primary-gradient-start: 139 92 246;  /* purple-500 */
  --color-primary-gradient-end: 109 40 217;    /* purple-600 */
  
  /* Secondary & muted */
  --color-secondary: 55 65 81;              /* gray-700 */
  --color-secondary-foreground: 249 250 251;    /* gray-50 */
  --color-muted: 54 58 69;                  /* dark gray */
  --color-muted-foreground: 156 163 175;    /* gray-400 */
  --color-accent: 55 65 81;                 /* gray-700 */
  --color-accent-foreground: 249 250 251;   /* gray-50 */
  
  /* Status colors */
  --color-destructive: 239 68 68;           /* red-500 */
  --color-destructive-foreground: 255 255 255;  /* white */
  --color-error: 127 29 29;                 /* red-900 */
  --color-error-foreground: 254 202 202;    /* red-300 */
  --color-success: 20 83 45;                /* green-900 */
  --color-success-foreground: 187 247 208;  /* green-300 */
  
  /* UI ring & toggle */
  --color-ring: 139 92 246;                 /* purple-500 */
  --color-toggle-bg: 54 58 69;              /* dark gray */
}
```

**Dark Theme Palette:**
- **Background**: Solid dark blue-gray (no gradient, keeps it readable)
- **Surface**: Slightly lighter dark gray (good contrast for cards)
- **Text**: White on dark surfaces
- **Primary**: Bright purple-500 (more prominent in dark mode)
- **Accent**: Medium gray (secondary actions)
- **Status**: Same red/green (works on dark)

## Tailwind Color Config

`tailwind.config.js` maps CSS variables to Tailwind utilities:

```javascript
theme: {
  extend: {
    colors: {
      background: "rgb(var(--color-background) / <alpha-value>)",
      foreground: "rgb(var(--color-foreground) / <alpha-value>)",
      
      card: {
        DEFAULT: "rgb(var(--color-card) / <alpha-value>)",
        foreground: "rgb(var(--color-card-foreground) / <alpha-value>)",
      },
      
      border: "rgb(var(--color-border) / <alpha-value>)",
      
      input: {
        DEFAULT: "rgb(var(--color-input) / <alpha-value>)",
        foreground: "rgb(var(--color-input-foreground) / <alpha-value>)",
      },
      
      primary: {
        DEFAULT: "rgb(var(--color-primary) / <alpha-value>)",
        foreground: "rgb(var(--color-primary-foreground) / <alpha-value>)",
        hover: "rgb(var(--color-primary-hover) / <alpha-value>)",
      },
      
      secondary: {
        DEFAULT: "rgb(var(--color-secondary) / <alpha-value>)",
        foreground: "rgb(var(--color-secondary-foreground) / <alpha-value>)",
      },
      
      muted: {
        DEFAULT: "rgb(var(--color-muted) / <alpha-value>)",
        foreground: "rgb(var(--color-muted-foreground) / <alpha-value>)",
      },
      
      accent: {
        DEFAULT: "rgb(var(--color-accent) / <alpha-value>)",
        foreground: "rgb(var(--color-accent-foreground) / <alpha-value>)",
      },
      
      destructive: {
        DEFAULT: "rgb(var(--color-destructive) / <alpha-value>)",
        foreground: "rgb(var(--color-destructive-foreground) / <alpha-value>)",
      },
      
      error: {
        DEFAULT: "rgb(var(--color-error) / <alpha-value>)",
        foreground: "rgb(var(--color-error-foreground) / <alpha-value>)",
      },
      
      success: {
        DEFAULT: "rgb(var(--color-success) / <alpha-value>)",
        foreground: "rgb(var(--color-success-foreground) / <alpha-value>)",
      },
      
      ring: "rgb(var(--color-ring) / <alpha-value>)",
    },
  },
}
```

## How to Use Colors in Components

### ✅ Correct Usage (Using Tailwind Tokens)

```tsx
// Background colors
<div className="bg-background">
<div className="bg-card">
<div className="bg-primary">
<div className="bg-error">

// Text colors
<p className="text-foreground">
<p className="text-card-foreground">
<p className="text-muted-foreground">
<p className="text-destructive">

// Border colors
<div className="border border-border">
<div className="border-b border-accent">

// Input styling
<input className="bg-input text-input-foreground">

// With opacity
<div className="bg-primary/50">
<div className="text-foreground/80">

// Hover states
<button className="hover:bg-primary-hover">
<button className="hover:text-destructive/80">

// Multiple states
<div className="bg-card text-card-foreground border border-border">
```

### ❌ Hardcoded Colors (Never Use)

```tsx
// ✗ Don't use arbitrary hex/rgb
<div className="bg-blue-600">
<div className="bg-[#6D28D9]">
<div className="text-[rgb(109,40,217)]">

// ✗ Don't use Tailwind's default colors
<button className="bg-blue-500 hover:bg-blue-600">
<div className="text-red-700">

// These break the theme system!
```

## Common Component Patterns

### Buttons

```tsx
// Primary button
<button className="bg-primary text-primary-foreground hover:bg-primary-hover px-4 py-2 rounded transition-colors">
  Send
</button>

// Secondary button
<button className="bg-secondary text-secondary-foreground hover:opacity-80 px-3 py-2 rounded">
  Cancel
</button>

// Destructive button
<button className="text-destructive hover:text-destructive/80">
  Logout
</button>

// With gradient
<button className="btn-gradient text-white px-4 py-2 rounded">
  Gradient Button
</button>
```

### Cards

```tsx
// Message bubble (user)
<div className="bg-primary text-primary-foreground rounded-lg px-4 py-2">
  {message}
</div>

// Message bubble (assistant)
<div className="bg-card text-card-foreground border border-border rounded-lg px-4 py-2">
  {message}
</div>

// Card container
<div className="bg-card border border-border rounded-lg p-4">
  <h3 className="text-card-foreground font-semibold">
    Title
  </h3>
</div>
```

### Forms

```tsx
// Input field
<input
  className="w-full bg-input text-input-foreground border border-border rounded px-3 py-2 placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
  placeholder="Enter secret..."
/>

// Error message
<p className="text-error text-error-foreground text-sm mt-1">
  Login failed
</p>

// Success message
<p className="text-success text-success-foreground text-sm mt-1">
  Message sent
</p>
```

### Status Indicators

```tsx
// Loading spinner
<div className="bg-muted rounded-lg px-4 py-2">
  <div className="flex space-x-1">
    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
  </div>
</div>

// Error banner
<div className="bg-error text-error-foreground border-t border-border px-4 py-2">
  {error}
</div>

// Success banner
<div className="bg-success text-success-foreground px-4 py-2">
  Message sent!
</div>
```

## Spacing Scale

No custom spacing config; uses Tailwind defaults:
- `p-2` = 0.5rem (8px)
- `p-3` = 0.75rem (12px)
- `p-4` = 1rem (16px)
- `gap-2` = 0.5rem (8px)
- `gap-3` = 0.75rem (12px)
- `gap-4` = 1rem (16px)

```tsx
// Compact: p-2, gap-2
<div className="flex gap-2 p-2">

// Normal: p-3, gap-3
<div className="flex gap-3 p-3">

// Loose: p-4, gap-4
<div className="flex gap-4 p-4">
```

## Typography

No custom font config; uses Tailwind defaults:
- `text-xs` = 0.75rem (12px) — labels, footnotes
- `text-sm` = 0.875rem (14px) — secondary text
- `text-base` = 1rem (16px) — body text
- `text-lg` = 1.125rem (18px) — emphasized
- `text-xl` = 1.25rem (20px) — subheading
- `text-2xl` = 1.5rem (24px) — heading
- `text-3xl` = 1.875rem (30px) — main heading

**Weight:**
- `font-normal` = 400 (body)
- `font-semibold` = 600 (headings, labels)
- `font-bold` = 700 (emphasis)

```tsx
// Main heading
<h1 className="text-3xl font-bold text-foreground">Illuresight</h1>

// Subheading
<h2 className="text-xl font-semibold text-card-foreground">Chat History</h2>

// Body text
<p className="text-base text-foreground">Message content</p>

// Secondary text
<p className="text-sm text-muted-foreground">Timestamp</p>

// Label
<label className="text-xs font-semibold text-card-foreground">Secret Key</label>
```

## Responsive Design

`darkMode: "class"` in Tailwind config — apply dark mode via `<html class="dark">`.

**Breakpoints (Tailwind defaults):**
- `sm` = 640px
- `md` = 768px
- `lg` = 1024px
- `xl` = 1280px

```tsx
// Mobile-first: stack on mobile, row on sm+
<div className="flex flex-col sm:flex-row gap-2 sm:gap-4">

// Text size responsive
<h1 className="text-xl sm:text-2xl md:text-3xl">

// Padding responsive
<div className="px-3 sm:px-4 md:px-6">

// Hide on mobile
<div className="hidden sm:block">Desktop only</div>

// Show on mobile only
<div className="sm:hidden">Mobile only</div>
```

## Custom CSS in globals.css

### Utility Classes

```css
/* Gradient button */
.btn-gradient {
  background: linear-gradient(
    to right,
    rgb(var(--color-primary-gradient-start)),
    rgb(var(--color-primary-gradient-end))
  );
}

.btn-gradient:hover {
  opacity: 0.9;
}

/* Animated gradient text */
@keyframes gradient-shift { ... }
.animate-gradient {
  animation: gradient-shift 3s ease infinite;
}

/* Touch optimizations */
.touch-manipulation {
  touch-action: manipulation;
}

/* Safe area for notch devices */
.safe-area-inset {
  padding: env(safe-area-inset-*);
}
.safe-area-inset-bottom {
  padding-bottom: calc(env(safe-area-inset-bottom) + 0.75rem);
}
```

## Mobile/PWA Considerations

### Min Touch Target
```tsx
// Buttons should be at least 44x44px (mobile tap target)
<button className="min-h-[44px] min-w-[44px] touch-manipulation">
```

### Input Font Size
```tsx
// Prevent iOS Safari auto-zoom on input focus
<input className="text-base" />  <!-- 16px -->
```

### Safe Area
```tsx
// Respect notch on iOS
<div className="safe-area-inset">
  Content (respects notch)
</div>
```

## Color Accessibility

- **Contrast**: All text passes WCAG AA (4.5:1 for normal text)
- **Status**: Don't rely on color alone (use icons + text)
- **Colorblind**: Purple + red are distinct; avoid pure red/green pairs
- **Dark mode**: High contrast maintained on dark background

### Recommended Combinations

```tsx
// ✓ Good contrast
<div className="bg-primary text-primary-foreground">
<div className="bg-card text-card-foreground">
<div className="bg-destructive text-destructive-foreground">

// ✓ Readable on both light & dark
<button className="text-primary hover:opacity-80">
<button className="border border-border">

// ✗ Avoid low contrast
<div className="text-muted-foreground/50">  <!-- Too faint -->
<div className="bg-card text-muted">         <!-- Gray on gray -->
```
