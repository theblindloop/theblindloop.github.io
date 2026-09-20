(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const number = (n) => n.toLocaleString("en-US");
  const preview = document.body.classList.contains("homepage");
  const BATCH_SIZE = preview ? 6 : 48;
  const CACHE_SIZE = 32;
  const cache = new Map();
  const state = {
    worlds: [],
    filtered: [],
    selected: null,
    detail: null,
    sample: 0,
    choice: null,
    visible: 0,
    request: 0,
  };
  let requestController = null;
  const filters = [
    "question-search",
    "experiment-filter",
    "profile-filter",
    "generator-filter",
  ];
  const activeSample = () => state.detail.samples[state.sample];
  const selectedHash = () =>
    `world=${encodeURIComponent(state.selected.id)}&sample=${state.sample + 1}`;
  const setHash = () => history.replaceState(null, "", `#${selectedHash()}`);
  const questionSet = () =>
    state.filtered.includes(state.selected) ? state.filtered : state.worlds;

  function updateChoiceStatus() {
    const status = $("choice-status");
    delete status.dataset.match;
    if (state.choice === null) {
      status.textContent = "";
      return;
    }
    if ($("recorded-answer").hidden) {
      status.textContent =
        "Answer selected. Reveal the recorded answer to compare.";
    } else {
      const matches = state.choice === String(activeSample().answer);
      status.dataset.match = String(matches);
      status.textContent = matches
        ? "Your choice matches the recorded answer."
        : "Your choice differs from the recorded answer.";
    }
  }

  function resetAnswer() {
    state.choice = null;
    $("recorded-answer").hidden = true;
    $("reveal-answer").setAttribute("aria-expanded", "false");
    $("reveal-answer").textContent = "Reveal recorded answer";
    $("copy-status").textContent = "";
    updateChoiceStatus();
  }

  function renderSample() {
    const sample = activeSample();
    $("question-image").src = sample.image;
    $("question-image").alt =
      `Recorded instance ${state.sample + 1} of ${state.selected.title}. Original question follows.`;
    $("question-text").textContent = sample.question;
    $("answer-text").textContent = sample.answer;
    $("sample-label").textContent =
      `Instance ${state.sample + 1} of ${state.detail.samples.length}`;
    $("sample-buttons").replaceChildren();
    state.detail.samples.forEach((_, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = index + 1;
      button.setAttribute("aria-label", `Show instance ${index + 1}`);
      button.setAttribute("aria-pressed", String(index === state.sample));
      button.addEventListener("click", () => {
        state.sample = index;
        renderSample();
        setHash();
        $("sample-buttons").children[index].focus({ preventScroll: true });
      });
      $("sample-buttons").append(button);
    });
    resetAnswer();
    $("option-buttons").replaceChildren();
    $("quiz-options").hidden = !sample.options?.length;
    (sample.options || []).forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = String(option);
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => {
        state.choice = String(option);
        [...$("option-buttons").children].forEach((b) =>
          b.setAttribute("aria-pressed", String(b === button)),
        );
        if ($("recorded-answer").hidden)
          $("reveal-answer").textContent = "Check my answer";
        updateChoiceStatus();
      });
      $("option-buttons").append(button);
    });
  }

  async function fetchDetail(world, signal) {
    if (cache.has(world.id)) {
      const detail = cache.get(world.id);
      cache.delete(world.id);
      cache.set(world.id, detail);
      return detail;
    }
    const response = await fetch(world.detail, { signal });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const detail = await response.json();
    if (
      detail.id !== world.id ||
      !Array.isArray(detail.samples) ||
      detail.samples.length !== world.sampleCount
    )
      throw new Error("Invalid question record");
    cache.set(world.id, detail);
    if (cache.size > CACHE_SIZE) cache.delete(cache.keys().next().value);
    return detail;
  }

  async function openWorld(world, index = 0, updateURL = true) {
    requestController?.abort();
    requestController = new AbortController();
    const request = ++state.request;
    state.selected = world;
    state.detail = null;
    state.sample = Math.max(
      0,
      Math.min(world.sampleCount - 1, Number.isInteger(index) ? index : 0),
    );
    $("world-title").textContent = world.title;
    $("question-dialog").setAttribute("aria-label", world.title);
    $("question-viewer").hidden = true;
    $("quiz-loading").hidden = false;
    $("quiz-error").hidden = true;
    const collection = questionSet();
    $("quiz-position").textContent =
      `Question ${number(collection.indexOf(world) + 1)} of ${number(collection.length)}`;
    $("previous-question").disabled = collection.length < 2;
    $("next-question").disabled = collection.length < 2;
    if (updateURL) setHash();
    document
      .querySelectorAll(".world-card")
      .forEach((card) =>
        card.setAttribute(
          "aria-pressed",
          String(card.dataset.worldId === world.id),
        ),
      );
    if (!$("question-dialog").open) $("question-dialog").showModal();
    $("question-dialog").scrollTop = 0;
    try {
      const detail = await fetchDetail(world, requestController.signal);
      if (request !== state.request || !$("question-dialog").open) return;
      state.detail = detail;
      $("world-experiment").textContent = detail.experimentLabel;
      $("world-profile").textContent = detail.profile || "Feedback-guided";
      $("world-generator").textContent = `Generated by ${detail.generator}`;
      $("generator-source").href = detail.programs.generator.path;
      $("inverse-source").href = detail.programs.inverse.path;
      $("record-id").textContent = `Source record: ${detail.recordId}`;
      document.querySelector(".source-details").open = false;
      renderSample();
      $("question-viewer").hidden = false;
    } catch (error) {
      if (request === state.request && error.name !== "AbortError")
        $("quiz-error").hidden = false;
    } finally {
      if (request === state.request) $("quiz-loading").hidden = true;
    }
  }

  function worldCard(world) {
    const button = document.createElement("button");
    button.className = "world-card";
    button.type = "button";
    button.dataset.worldId = world.id;
    button.setAttribute(
      "aria-pressed",
      String(state.selected?.id === world.id),
    );
    button.setAttribute(
      "aria-label",
      `Try ${world.title}, ${world.experimentLabel}`,
    );
    const image = document.createElement("img");
    image.src = world.image;
    image.alt = "";
    image.loading = "lazy";
    image.decoding = "async";
    const title = document.createElement("span");
    title.className = "card-title";
    title.textContent = world.title;
    const type = document.createElement("span");
    type.className = "card-type";
    type.textContent = `${world.profile || "Model-feedback"} · ${world.generator}`;
    const question = document.createElement("span");
    question.className = "card-question";
    question.textContent = world.question;
    const open = document.createElement("span");
    open.className = "card-open";
    const label = document.createElement("span");
    label.textContent = "Try this question";
    const count = document.createElement("span");
    count.textContent = `${world.sampleCount} instances ↗`;
    open.append(label, count);
    button.append(image, title, type, question, open);
    button.addEventListener("click", () => openWorld(world));
    return button;
  }

  function loadMore() {
    const next = Math.min(state.filtered.length, state.visible + BATCH_SIZE);
    const fragment = document.createDocumentFragment();
    state.filtered
      .slice(state.visible, next)
      .forEach((world) => fragment.append(worldCard(world)));
    $("world-grid").append(fragment);
    state.visible = next;
    $("gallery-progress").textContent = state.filtered.length
      ? `Showing ${number(state.visible)} of ${number(state.filtered.length)} worlds`
      : "";
    $("load-more").hidden = state.visible >= state.filtered.length;
    $("gallery-sentinel").hidden = !state.filtered.length;
  }

  function applyFilters() {
    const query = $("question-search").value.trim().toLowerCase();
    const experiment = $("experiment-filter").value;
    const profile = $("profile-filter").value;
    const generator = $("generator-filter").value;
    state.filtered = state.worlds.filter(
      (world) =>
        (!experiment || world.experiment === experiment) &&
        (!profile ||
          (profile === "none" ? !world.profile : world.profile === profile)) &&
        (!generator || world.generator === generator) &&
        (!query || world.searchText.includes(query)),
    );
    if (preview) state.filtered = state.filtered.slice(0, 6);
    $("filter-count").textContent =
      `${number(state.filtered.length)} of ${number(state.worlds.length)} worlds`;
    $("no-results").hidden = state.filtered.length > 0;
    $("world-grid").replaceChildren();
    state.visible = 0;
    loadMore();
  }

  function resetFilters() {
    filters.forEach((id) => {
      $(id).value = "";
    });
    applyFilters();
  }

  function readHash() {
    if (!location.hash.startsWith("#world=")) {
      if ($("image-dialog").open) $("image-dialog").close();
      if ($("question-dialog").open) $("question-dialog").close();
      return;
    }
    const params = new URLSearchParams(location.hash.slice(1));
    const world = state.worlds.find((w) => w.id === params.get("world"));
    if (world) openWorld(world, Number(params.get("sample") || 1) - 1, false);
  }

  function options(id, values) {
    values.forEach(([value, text]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      $(id).append(option);
    });
  }

  async function load() {
    $("explorer-loading").hidden = false;
    $("explorer-error").hidden = true;
    try {
      const response = await fetch("data/questions.json");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (
        data.schemaVersion !== 2 ||
        !Array.isArray(data.worlds) ||
        !data.worlds.length
      )
        throw new Error("Invalid catalog");
      state.worlds = data.worlds;
      state.worlds.forEach((world) => {
        world.searchText =
          `${world.title} ${world.question} ${(world.additionalQuestions || []).join(" ")} ${world.profile || ""} ${world.generator}`.toLowerCase();
      });
      ["experiment-filter", "profile-filter", "generator-filter"].forEach(
        (id) => {
          while ($(id).options.length > 1) $(id).remove(1);
        },
      );
      options("experiment-filter", [
        ...new Map(state.worlds.map((w) => [w.experiment, w.experimentLabel])),
      ]);
      options(
        "profile-filter",
        [...new Set(state.worlds.map((w) => w.profile).filter(Boolean))]
          .sort()
          .map((p) => [p, p])
          .concat([["none", "No profile (model feedback)"]]),
      );
      options(
        "generator-filter",
        [...new Set(state.worlds.map((w) => w.generator))]
          .sort()
          .map((m) => [m, m]),
      );
      $("world-total").textContent = number(state.worlds.length);
      $("explorer").hidden = false;
      applyFilters();
      readHash();
    } catch (error) {
      $("explorer-error").hidden = false;
      $("explorer").hidden = true;
      console.error("Unable to load question records:", error.message);
    } finally {
      $("explorer-loading").hidden = true;
    }
  }

  filters.forEach((id) =>
    $(id).addEventListener(
      id === "question-search" ? "input" : "change",
      applyFilters,
    ),
  );
  $("reset-filters").addEventListener("click", resetFilters);
  $("retry-load").addEventListener("click", load);
  $("load-more").addEventListener("click", loadMore);
  if (!preview && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        // Paper-section navigation must remain stable rather than growing the gallery under its target.
        const viewingPaper =
          location.hash &&
          location.hash !== "#questions" &&
          !location.hash.startsWith("#world=");
        if (
          entries.some((entry) => entry.isIntersecting) &&
          !viewingPaper &&
          !$("question-dialog").open &&
          state.visible < state.filtered.length
        )
          loadMore();
      },
      { rootMargin: "350px" },
    );
    observer.observe($("gallery-sentinel"));
  }
  $("retry-question").addEventListener("click", () =>
    openWorld(state.selected, state.sample, false),
  );
  $("next-sample").addEventListener("click", () => {
    if (!state.detail) return;
    state.sample = (state.sample + 1) % state.detail.samples.length;
    renderSample();
    setHash();
  });
  $("reveal-answer").addEventListener("click", () => {
    if (!state.detail) return;
    const reveal = $("recorded-answer").hidden;
    $("recorded-answer").hidden = !reveal;
    $("reveal-answer").setAttribute("aria-expanded", String(reveal));
    $("reveal-answer").textContent = reveal
      ? "Hide recorded answer"
      : state.choice === null
        ? "Reveal recorded answer"
        : "Check my answer";
    updateChoiceStatus();
  });
  $("copy-link").addEventListener("click", async () => {
    const url = new URL(location.href);
    url.hash = selectedHash();
    try {
      await navigator.clipboard.writeText(url.href);
      $("copy-status").textContent = "Link copied to this world and instance.";
    } catch {
      $("copy-status").textContent = `Copy this link: ${url.href}`;
    }
  });
  ["previous-question", "next-question"].forEach((id, i) =>
    $(id).addEventListener("click", () => {
      const collection = questionSet();
      const index =
        (collection.indexOf(state.selected) +
          (i ? 1 : -1) +
          collection.length) %
        collection.length;
      openWorld(collection[index]);
    }),
  );
  $("close-question").addEventListener("click", () =>
    $("question-dialog").close(),
  );
  $("question-dialog").addEventListener("close", () => {
    if ($("question-dialog").open) return;
    state.request++;
    requestController?.abort();
    if (location.hash.startsWith("#world="))
      history.replaceState(null, "", "#questions");
  });
  $("enlarge-image").addEventListener("click", () => {
    if (!state.detail) return;
    $("dialog-title").textContent =
      `${state.selected.title} · instance ${state.sample + 1}`;
    $("dialog-image").src = activeSample().image;
    $("dialog-image").alt = $("question-image").alt;
    $("dialog-question").textContent = activeSample().question;
    $("image-dialog").showModal();
  });
  $("close-dialog").addEventListener("click", () => $("image-dialog").close());
  ["question-dialog", "image-dialog"].forEach((id) =>
    $(id).addEventListener("click", (event) => {
      if (event.target !== $(id)) return;
      const box = $(id).getBoundingClientRect();
      if (
        event.clientX < box.left ||
        event.clientX > box.right ||
        event.clientY < box.top ||
        event.clientY > box.bottom
      )
        $(id).close();
    }),
  );
  window.addEventListener("hashchange", readHash);
  load();
})();
