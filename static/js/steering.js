(() => {
  document.querySelectorAll("[data-category]").forEach((button) => {
    button.addEventListener("click", () => {
      document
        .querySelectorAll("[data-category]")
        .forEach((b) => b.setAttribute("aria-pressed", String(b === button)));
      document
        .querySelectorAll(".category-panel")
        .forEach(
          (panel) =>
            (panel.hidden = panel.id !== `category-${button.dataset.category}`),
        );
    });
  });
  const grid = document.getElementById("probe-grid");
  const mask = document.getElementById("probe-mask");
  for (let i = 0; i < 64; i++) {
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute(
      "aria-label",
      `Mask row ${Math.floor(i / 8) + 1}, column ${(i % 8) + 1}`,
    );
    button.addEventListener("click", () => {
      const x = i % 8,
        y = Math.floor(i / 8);
      mask.hidden = false;
      mask.style.left = `${(x - 0.25) * 12.5}%`;
      mask.style.top = `${(y - 0.25) * 12.5}%`;
      mask.style.width = "18.75%";
      mask.style.height = "18.75%";
      document.getElementById("probe-status").textContent =
        `Illustrated mask: row ${y + 1}, column ${x + 1}. The replacement extends beyond the selected square.`;
    });
    grid.append(button);
  }
  document.getElementById("reset-mask").addEventListener("click", () => {
    mask.hidden = true;
    document.getElementById("probe-status").textContent =
      "Select a square to illustrate the region replaced.";
  });
})();
