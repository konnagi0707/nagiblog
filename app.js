const state = {
  posts: [],
  filteredPosts: [],
  activeTag: "all",
  keyword: "",
  activeId: null,
  loadingState: "loading",
  errorMessage: "",
};

const postListEl = document.getElementById("post-list");
const postDetailEl = document.getElementById("post-detail");
const tagSelectEl = document.getElementById("tag-select");
const keywordInputEl = document.getElementById("keyword-input");
const listStatusEl = document.getElementById("list-status");

function normalizeKeyword(input) {
  return String(input ?? "").trim().toLowerCase();
}

function parseHashPostId(hashValue) {
  const raw = String(hashValue ?? "").replace("#", "").trim();
  if (raw === "") return null;

  const postId = Number(raw);
  if (!Number.isInteger(postId) || postId < 0) return null;

  return postId;
}

function getHashPostId() {
  return parseHashPostId(window.location.hash);
}

function setHash(postId) {
  if (postId === null || Number.isNaN(postId)) return;

  const nextHash = `#${postId}`;
  if (window.location.hash !== nextHash) {
    history.replaceState(null, "", nextHash);
  }
}

function clearHash() {
  if (window.location.hash !== "") {
    history.replaceState(null, "", window.location.pathname + window.location.search);
  }
}

function filterPosts(posts, activeTag, keyword) {
  const normalizedKeyword = normalizeKeyword(keyword);

  return posts.filter((post) => {
    const matchesTag = activeTag === "all" || post.tags.includes(activeTag);
    if (!matchesTag) return false;

    if (normalizedKeyword === "") return true;

    const searchableText = `${post.title} ${post.content}`.toLowerCase();
    return searchableText.includes(normalizedKeyword);
  });
}

function resolveActiveId(filteredPosts, preferredId, hashId) {
  const visibleIds = new Set(filteredPosts.map((post) => post.id));

  if (hashId !== null && visibleIds.has(hashId)) {
    return hashId;
  }

  if (preferredId !== null && visibleIds.has(preferredId)) {
    return preferredId;
  }

  return filteredPosts.length ? filteredPosts[0].id : null;
}

function renderTagOptions(posts) {
  tagSelectEl.innerHTML = '<option value="all">全部</option>';

  const tags = new Set();
  posts.forEach((post) => post.tags.forEach((tag) => tags.add(tag)));

  [...tags]
    .sort((a, b) => a.localeCompare(b, "zh"))
    .forEach((tag) => {
      const option = document.createElement("option");
      option.value = tag;
      option.textContent = tag;
      tagSelectEl.appendChild(option);
    });
}

function renderStatus() {
  listStatusEl.className = "status-message";

  if (state.loadingState === "loading") {
    listStatusEl.classList.add("info");
    listStatusEl.textContent = "正在加载文章...";
    return;
  }

  if (state.loadingState === "error") {
    listStatusEl.classList.add("error");
    listStatusEl.textContent = state.errorMessage || "数据加载失败，请稍后重试。";
    return;
  }

  if (state.posts.length === 0) {
    listStatusEl.classList.add("info");
    listStatusEl.textContent = "暂无文章数据。";
    return;
  }

  if (state.filteredPosts.length === 0) {
    listStatusEl.classList.add("info");
    listStatusEl.textContent = "当前筛选条件下没有匹配文章。";
    return;
  }

  listStatusEl.classList.add("info");
  listStatusEl.textContent = `共 ${state.filteredPosts.length} 篇文章`;
}

function renderList() {
  postListEl.innerHTML = "";

  if (state.loadingState !== "ready" || state.filteredPosts.length === 0) {
    return;
  }

  state.filteredPosts.forEach((post) => {
    const li = document.createElement("li");
    const button = document.createElement("button");

    if (post.id === state.activeId) {
      button.classList.add("active");
    }

    const dateEl = document.createElement("span");
    dateEl.className = "post-date";
    dateEl.textContent = post.date;

    const titleEl = document.createElement("strong");
    titleEl.textContent = post.title;

    button.append(dateEl, titleEl);
    button.addEventListener("click", () => {
      state.activeId = post.id;
      setHash(post.id);
      renderList();
      renderDetail();
      renderStatus();
    });

    li.appendChild(button);
    postListEl.appendChild(li);
  });
}

function renderDetail() {
  if (state.loadingState === "loading") {
    postDetailEl.innerHTML = '<p class="empty">正在加载文章...</p>';
    return;
  }

  if (state.loadingState === "error") {
    postDetailEl.innerHTML = `<p class="empty error">${
      state.errorMessage || "数据加载失败，请稍后重试。"
    }</p>`;
    return;
  }

  const post = state.filteredPosts.find((item) => item.id === state.activeId);

  if (!post) {
    const emptyText =
      state.posts.length === 0
        ? "暂无文章数据。"
        : "当前筛选条件下没有可展示内容。";
    postDetailEl.innerHTML = `<p class="empty">${emptyText}</p>`;
    return;
  }

  postDetailEl.innerHTML = "";

  const titleEl = document.createElement("h2");
  titleEl.textContent = post.title;

  const dateEl = document.createElement("p");
  dateEl.className = "post-date";
  dateEl.textContent = post.date;

  const tagsWrapEl = document.createElement("div");
  tagsWrapEl.className = "tags";
  post.tags.forEach((tag) => {
    const tagEl = document.createElement("span");
    tagEl.className = "tag";
    tagEl.textContent = tag;
    tagsWrapEl.appendChild(tagEl);
  });

  const contentEl = document.createElement("p");
  contentEl.textContent = post.content;

  const sourceWrapEl = document.createElement("p");
  const sourceLinkEl = document.createElement("a");
  sourceLinkEl.href = post.sourceUrl;
  sourceLinkEl.target = "_blank";
  sourceLinkEl.rel = "noreferrer";
  sourceLinkEl.textContent = "查看原文";
  sourceWrapEl.appendChild(sourceLinkEl);

  postDetailEl.append(titleEl, dateEl, tagsWrapEl, contentEl, sourceWrapEl);
}

function syncHashWithActive({ force = false } = {}) {
  if (state.activeId === null) {
    clearHash();
    return;
  }

  if (!force && window.location.hash === "") {
    return;
  }

  setHash(state.activeId);
}

function applyFilter({ preferHash = false, forceHashSync = false } = {}) {
  state.filteredPosts = filterPosts(state.posts, state.activeTag, state.keyword);

  const hasHash = preferHash && window.location.hash !== "";
  const hashId = hasHash ? getHashPostId() : null;
  const preferredId = hasHash ? null : state.activeId;
  state.activeId = resolveActiveId(state.filteredPosts, preferredId, hashId);

  if (forceHashSync) {
    syncHashWithActive({ force: true });
  }

  renderList();
  renderStatus();
  renderDetail();
}

async function init() {
  state.loadingState = "loading";
  state.errorMessage = "";
  renderStatus();
  renderDetail();

  try {
    const response = await fetch("data/posts.json");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const posts = await response.json();
    if (!Array.isArray(posts)) {
      throw new Error("数据格式错误：posts.json 不是数组");
    }

    state.posts = [...posts].sort((a, b) => new Date(b.date) - new Date(a.date));
    state.loadingState = "ready";

    renderTagOptions(state.posts);

    const hadHash = window.location.hash !== "";
    applyFilter({
      preferHash: true,
      forceHashSync: hadHash,
    });
  } catch (error) {
    state.loadingState = "error";
    state.errorMessage = "数据加载失败，请稍后重试。";
    state.posts = [];
    state.filteredPosts = [];
    state.activeId = null;

    renderList();
    renderStatus();
    renderDetail();

    console.error("[archive] init failed:", error);
  }
}

tagSelectEl.addEventListener("change", (event) => {
  state.activeTag = event.target.value;
  applyFilter({ forceHashSync: window.location.hash !== "" });
});

keywordInputEl.addEventListener("input", (event) => {
  state.keyword = event.target.value;
  applyFilter({ forceHashSync: window.location.hash !== "" });
});

window.addEventListener("hashchange", () => {
  if (state.loadingState !== "ready") return;

  const hashId = getHashPostId();
  if (hashId !== null && state.posts.some((post) => post.id === hashId)) {
    state.activeTag = "all";
    state.keyword = "";
    tagSelectEl.value = "all";
    keywordInputEl.value = "";
  }

  applyFilter({
    preferHash: true,
    forceHashSync: window.location.hash !== "",
  });
});

init();
