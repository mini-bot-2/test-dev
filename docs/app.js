(() => {
  const storageKey = "hello-world-theme";
  const root = document.documentElement;

  const setTheme = (theme) => {
    if (!theme) {
      root.removeAttribute("data-theme");
      return;
    }
    root.setAttribute("data-theme", theme);
  };

  const getStoredTheme = () => {
    try {
      return localStorage.getItem(storageKey);
    } catch {
      return null;
    }
  };

  const storeTheme = (theme) => {
    try {
      localStorage.setItem(storageKey, theme);
    } catch {
      // Ignore storage errors (private mode / disabled storage).
    }
  };

  const getEffectiveTheme = () => {
    const stored = getStoredTheme();
    if (stored === "light" || stored === "dark") return stored;
    return null;
  };

  const initMeta = () => {
    const year = document.getElementById("year");
    if (year) year.textContent = String(new Date().getFullYear());

    const renderedAt = document.getElementById("renderedAt");
    if (renderedAt) renderedAt.textContent = new Date().toLocaleString();
  };

  const initThemeToggle = () => {
    setTheme(getEffectiveTheme());

    const button = document.getElementById("toggleTheme");
    if (!button) return;

    button.addEventListener("click", () => {
      const current = root.getAttribute("data-theme");
      const next = current === "light" ? "dark" : "light";
      setTheme(next);
      storeTheme(next);
    });
  };

  const init = () => {
    initMeta();
    initThemeToggle();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();

