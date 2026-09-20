(() => {
  if (document.querySelector(".lab-workbench")) {
  let methodInstances = null;
  let methodIndex = 0;
  function connectMethod() {
    if (!methodInstances || window.innerWidth <= 1000) return;
    const root = document
      .querySelector(".lab-workbench")
      .getBoundingClientRect();
    const source = document.querySelector(".lab-json").getBoundingClientRect();
    const image = document
      .querySelector(".guitar-viewport")
      .getBoundingClientRect();
    const crop = document.querySelector(".bridge-zoom").getBoundingClientRect();
    const x1 = source.right - root.left + 2,
      x2 = image.left - root.left - 5;
    const y = source.top - root.top + source.height * 0.4;
    document
      .getElementById("scene-wire")
      .setAttribute("d", `M${x1} ${y}H${x2}`);
    const item = methodInstances[methodIndex];
    const a = image.right - root.left + 1,
      b = crop.left - root.left - 4;
    const y1 =
      image.top -
      root.top +
      ((item.crop[1] + item.crop[3] / 2) / 512) * image.height;
    const y2 = crop.top - root.top + crop.height * 0.4;
    const mid = (a + b) / 2;
    document
      .getElementById("pixel-wire")
      .setAttribute("d", `M${a} ${y1}C${mid} ${y1} ${mid} ${y2} ${b} ${y2}`);
  }
  new ResizeObserver(connectMethod).observe(
    document.querySelector(".lab-workbench"),
  );
  function renderMethod(index) {
    if (!methodInstances) return;
    methodIndex = index;
    const item = methodInstances[index];
    document
      .querySelectorAll("[data-method-sample]")
      .forEach((b) =>
        b.setAttribute(
          "aria-pressed",
          String(Number(b.dataset.methodSample) === index),
        ),
      );
    document
      .querySelectorAll("[data-method-count], [data-comparison-count]")
      .forEach((n) => (n.textContent = item.answer));
    document.getElementById("method-span").textContent = item.scene.string_span;
    document.getElementById("method-offset").textContent = item.scene.offset_x;
    const image = document.getElementById("method-image");
    image.src = item.image;
    image.alt = `Recorded guitar instance with ${item.answer} visible strings`;
    document
      .getElementById("method-crop-image")
      .setAttribute("href", item.image);
    document
      .getElementById("method-crop")
      .setAttribute("viewBox", item.crop.join(" "));
    const box = document.getElementById("method-bridge-box");
    ["x", "y", "width", "height"].forEach((key, i) =>
      box.setAttribute(key, item.crop[i]),
    );
    const [x, y, w, h] = item.crop;
    document
      .getElementById("method-bridge-leader")
      .setAttribute("d", `M${x + w} ${y + h / 2}H505`);
    const values = item.pixels[1].map(
      (rgb) => rgb.reduce((a, b) => a + b, 0) / 3,
    );
    document
      .getElementById("method-profile-line")
      .setAttribute(
        "points",
        values.map((v, i) => `${i * 4},${100 - (v / 255) * 80}`).join(" "),
      );
    const runs = document.getElementById("method-runs");
    runs.replaceChildren();
    for (let i = 0; i < values.length; i++) {
      if (values[i] >= 105) continue;
      const start = i;
      while (i + 1 < values.length && values[i + 1] < 105) i++;
      const mark = document.createElement("i");
      mark.style.left = `${(start / 86) * 100}%`;
      mark.style.width = `${((i - start + 1) / 86) * 100}%`;
      runs.append(mark);
    }
    runs.setAttribute(
      "aria-label",
      `${item.rowCounts[1]} dark runs in the displayed row`,
    );
    document.getElementById("method-row-counts").textContent =
      item.rowCounts.join(" · ");
    connectMethod();
  }
  fetch("data/method-pixels.json")
    .then((r) => {
      if (!r.ok) throw new Error("Method pixels unavailable");
      return r.json();
    })
    .then((data) => {
      methodInstances = data.instances;
      renderMethod(0);
    })
    .catch(() => {
      document
        .getElementById("method-profile")
        .setAttribute(
          "aria-label",
          "Brightness trace unavailable; original image and recorded answer shown.",
        );
    });
  document
    .querySelectorAll("[data-method-sample]")
    .forEach((button) =>
      button.addEventListener("click", () =>
        renderMethod(Number(button.dataset.methodSample)),
      ),
    );
  }
  let programLink = null;
  document.querySelectorAll(".instance-strip a").forEach((link) => {
    if (new URL(link.href).pathname !== location.pathname) return;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      programLink = link;
      history.pushState(null, "", link.hash);
      window.dispatchEvent(new HashChangeEvent("hashchange"));
    });
  });
  document.getElementById("question-dialog")?.addEventListener("close", () => {
    if (!programLink) return;
    const link = programLink;
    programLink = null;
    queueMicrotask(() => {
      if (document.getElementById("question-dialog").open) return;
      history.replaceState(null, "", "#programs");
      link.focus({ preventScroll: true });
    });
  });
  const tabs = [...document.querySelectorAll("[data-example]")];
  function select(index, focus = false) {
    tabs.forEach((tab, i) => {
      tab.setAttribute("aria-selected", String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
      document.getElementById(`program-example-${i}`).hidden = i !== index;
    });
    if (focus) tabs[index].focus();
  }
  tabs.forEach((tab, i) => {
    const panel = document.getElementById(`program-example-${i}`);
    panel.setAttribute("role", "tabpanel");
    panel.setAttribute("aria-labelledby", tab.id);
    tab.addEventListener("click", () => select(i));
    tab.addEventListener("keydown", (event) => {
      const next = {
        ArrowRight: (i + 1) % tabs.length,
        ArrowLeft: (i + tabs.length - 1) % tabs.length,
        Home: 0,
        End: tabs.length - 1,
      }[event.key];
      if (next !== undefined) {
        event.preventDefault();
        select(next, true);
      }
    });
  });
})();

// Additional recorded worlds share the forward/image/inverse reading order.
(() => {
  const tabs = [...document.querySelectorAll('[data-teaser]')];
  function select(index, focus=false) {
    tabs.forEach((t,i) => { t.setAttribute('aria-selected', String(i===index)); t.tabIndex=i===index?0:-1; document.getElementById(`teaser-panel-${i}`).hidden=i!==index; });
    if (focus) tabs[index].focus();
    window.dispatchEvent(new Event('resize'));
  }
  tabs.forEach((t,i) => {
    t.addEventListener('click',()=>select(i));
    t.addEventListener('keydown',e=>{
      const next={ArrowRight:(i+1)%tabs.length,ArrowLeft:(i+tabs.length-1)%tabs.length,Home:0,End:tabs.length-1}[e.key];
      if(next!==undefined){e.preventDefault();select(next,true);}
    });
  });
  document.querySelectorAll('.method-alt').forEach(panel=>{
    const answers=JSON.parse(panel.dataset.answers);
    panel.querySelectorAll('[data-teaser-sample]').forEach(b=>b.addEventListener('click',()=>{
      const index=Number(b.dataset.teaserSample);
      panel.querySelectorAll('[data-teaser-sample]').forEach(t=>t.setAttribute('aria-pressed',String(t===b)));
      panel.querySelectorAll('[data-teaser-slide]').forEach(s=>s.hidden=Number(s.dataset.teaserSlide)!==index);
      panel.querySelectorAll('[data-alt-answer], [data-alt-comparison]').forEach(a=>a.textContent=answers[index]);
      panel.querySelectorAll('[data-inverse-measurement]').forEach(m=>m.hidden=Number(m.dataset.inverseMeasurement)!==index);
    }));
  });
})();
