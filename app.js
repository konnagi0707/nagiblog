const DEFAULT_MEMBER_SOURCE_URL = "https://sakurazaka46.com/s/s46/artist/62?ima=0000";

const state = {
  posts: [],
  filteredPosts: [],
  activeTag: "all",
  keyword: "",
  activeId: null,
  loadingState: "loading",
  errorMessage: "",
  member: null,
  memberLoadingState: "loading",
  memberErrorMessage: "",
};

const postListEl = document.getElementById("post-list");
const postDetailEl = document.getElementById("post-detail");
const tagSelectEl = document.getElementById("tag-select");
const keywordInputEl = document.getElementById("keyword-input");
const listStatusEl = document.getElementById("list-status");
const memberPanelEl = document.getElementById("member-panel");

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

function getPostSearchText(post) {
  if (typeof post.content === "string" && post.content.trim() !== "") {
    return post.content;
  }

  if (!Array.isArray(post.contentBlocks)) {
    return "";
  }

  return post.contentBlocks
    .filter((block) => block?.type === "text" && typeof block.text === "string")
    .map((block) => block.text)
    .join("\n\n");
}

function filterPosts(posts, activeTag, keyword) {
  const normalizedKeyword = normalizeKeyword(keyword);

  return posts.filter((post) => {
    const matchesTag = activeTag === "all" || post.tags.includes(activeTag);
    if (!matchesTag) return false;

    if (normalizedKeyword === "") return true;

    const searchableText = `${post.title} ${getPostSearchText(post)}`.toLowerCase();
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

function appendTextBlock(container, text) {
  const paragraphs = String(text)
    .split(/\n{2,}/)
    .map((segment) => segment.trim())
    .filter(Boolean);

  paragraphs.forEach((paragraphText) => {
    const paragraphEl = document.createElement("p");
    paragraphEl.className = "blog-paragraph";
    paragraphEl.textContent = paragraphText;
    container.appendChild(paragraphEl);
  });
}

function renderPostBody(post) {
  const bodyEl = document.createElement("div");
  bodyEl.className = "post-body";

  if (Array.isArray(post.contentBlocks) && post.contentBlocks.length > 0) {
    post.contentBlocks.forEach((block) => {
      if (!block || typeof block !== "object") return;

      if (block.type === "text" && typeof block.text === "string" && block.text.trim()) {
        appendTextBlock(bodyEl, block.text);
      }

      if (block.type === "image" && typeof block.src === "string" && block.src.trim()) {
        const imgEl = document.createElement("img");
        imgEl.className = "blog-image";
        imgEl.src = block.src;
        imgEl.alt = post.title;
        imgEl.loading = "lazy";
        bodyEl.appendChild(imgEl);
      }
    });
  } else if (typeof post.content === "string" && post.content.trim()) {
    appendTextBlock(bodyEl, post.content);
  }

  return bodyEl;
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

  const bodyEl = renderPostBody(post);

  const sourceWrapEl = document.createElement("p");
  const sourceLinkEl = document.createElement("a");
  sourceLinkEl.href = post.sourceUrl;
  sourceLinkEl.target = "_blank";
  sourceLinkEl.rel = "noreferrer";
  sourceLinkEl.textContent = "查看原文";
  sourceWrapEl.appendChild(sourceLinkEl);

  postDetailEl.append(titleEl, dateEl, tagsWrapEl, bodyEl, sourceWrapEl);
}

function normalizeMemberAttributes(attributes) {
  if (!Array.isArray(attributes)) return [];

  return attributes
    .filter((item) => item && typeof item === "object")
    .map((item) => ({
      label: String(item.label ?? "").trim(),
      value: String(item.value ?? "").trim(),
    }))
    .filter((item) => item.label !== "" && item.value !== "");
}

function renderMemberPanel() {
  memberPanelEl.innerHTML = "";

  if (state.memberLoadingState === "loading") {
    memberPanelEl.innerHTML = '<p class="empty">正在加载成员资料...</p>';
    return;
  }

  if (state.memberLoadingState === "error" || !state.member) {
    const errorEl = document.createElement("p");
    errorEl.className = "empty";
    errorEl.textContent = state.memberErrorMessage || "成员资料加载失败。";

    const sourceWrapEl = document.createElement("p");
    sourceWrapEl.className = "member-source-link";
    const sourceLinkEl = document.createElement("a");
    sourceLinkEl.href = DEFAULT_MEMBER_SOURCE_URL;
    sourceLinkEl.target = "_blank";
    sourceLinkEl.rel = "noreferrer";
    sourceLinkEl.textContent = "打开官方成员页";
    sourceWrapEl.appendChild(sourceLinkEl);

    memberPanelEl.append(errorEl, sourceWrapEl);
    return;
  }

  const member = state.member;
  const images = member.images && typeof member.images === "object" ? member.images : {};
  const attributes = normalizeMemberAttributes(member.attributes);
  const sourceUrl =
    typeof member.sourceUrl === "string" && member.sourceUrl.trim() !== ""
      ? member.sourceUrl
      : DEFAULT_MEMBER_SOURCE_URL;

  const headerEl = document.createElement("header");
  headerEl.className = "member-header";

  const nameEl = document.createElement("h3");
  nameEl.className = "member-name";
  nameEl.textContent = member.name || "小島 凪紗";

  const kanaEl = document.createElement("p");
  kanaEl.className = "member-kana";
  kanaEl.textContent = member.kana || "";

  headerEl.append(nameEl, kanaEl);
  memberPanelEl.appendChild(headerEl);

  const profileSrc = images.profile?.src;
  if (typeof profileSrc === "string" && profileSrc.trim() !== "") {
    const profileImg = document.createElement("img");
    profileImg.className = "member-photo-main";
    profileImg.src = profileSrc;
    profileImg.alt = `${member.name || "小島 凪紗"} 头像`;
    profileImg.loading = "lazy";
    memberPanelEl.appendChild(profileImg);
  }

  if (attributes.length > 0) {
    const infoListEl = document.createElement("dl");
    infoListEl.className = "member-info-list";

    attributes.forEach((item) => {
      const dtEl = document.createElement("dt");
      dtEl.textContent = item.label;
      const ddEl = document.createElement("dd");
      ddEl.textContent = item.value;
      infoListEl.append(dtEl, ddEl);
    });

    memberPanelEl.appendChild(infoListEl);
  }

  const greetingCardSrc = images.greetingCard?.src;
  const greetingPhotoSrc = images.greetingPhoto?.src;

  if (
    (typeof greetingCardSrc === "string" && greetingCardSrc.trim() !== "") ||
    (typeof greetingPhotoSrc === "string" && greetingPhotoSrc.trim() !== "")
  ) {
    const greetingWrapEl = document.createElement("section");
    greetingWrapEl.className = "member-greeting";

    const titleEl = document.createElement("h4");
    titleEl.textContent = "GREETING";
    greetingWrapEl.appendChild(titleEl);

    const gridEl = document.createElement("div");
    gridEl.className = "member-greeting-grid";

    if (typeof greetingCardSrc === "string" && greetingCardSrc.trim() !== "") {
      const cardFigure = document.createElement("figure");
      const cardImg = document.createElement("img");
      cardImg.src = greetingCardSrc;
      cardImg.alt = "Greeting Card";
      cardImg.loading = "lazy";
      const cardCaption = document.createElement("figcaption");
      cardCaption.textContent = "CARD";
      cardFigure.append(cardImg, cardCaption);
      gridEl.appendChild(cardFigure);
    }

    if (typeof greetingPhotoSrc === "string" && greetingPhotoSrc.trim() !== "") {
      const photoFigure = document.createElement("figure");
      const photoImg = document.createElement("img");
      photoImg.src = greetingPhotoSrc;
      photoImg.alt = "Greeting Photo";
      photoImg.loading = "lazy";
      const photoCaption = document.createElement("figcaption");
      photoCaption.textContent = "PHOTO";
      photoFigure.append(photoImg, photoCaption);
      gridEl.appendChild(photoFigure);
    }

    greetingWrapEl.appendChild(gridEl);
    memberPanelEl.appendChild(greetingWrapEl);
  }

  const actionsEl = document.createElement("div");
  actionsEl.className = "member-actions";

  const profileLink = document.createElement("a");
  profileLink.href = sourceUrl;
  profileLink.target = "_blank";
  profileLink.rel = "noreferrer";
  profileLink.textContent = "官方成员页";
  actionsEl.appendChild(profileLink);

  if (typeof member.greetingListUrl === "string" && member.greetingListUrl.trim() !== "") {
    const greetingListLink = document.createElement("a");
    greetingListLink.href = member.greetingListUrl;
    greetingListLink.target = "_blank";
    greetingListLink.rel = "noreferrer";
    greetingListLink.textContent = "GREETING LIST";
    actionsEl.appendChild(greetingListLink);
  }

  memberPanelEl.appendChild(actionsEl);
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

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} HTTP ${response.status}`);
  }
  return response.json();
}

async function init() {
  state.loadingState = "loading";
  state.errorMessage = "";
  state.memberLoadingState = "loading";
  state.memberErrorMessage = "";

  renderStatus();
  renderDetail();
  renderMemberPanel();

  const [postsResult, memberResult] = await Promise.allSettled([
    fetchJson("data/posts.json"),
    fetchJson("data/member.json"),
  ]);

  if (memberResult.status === "fulfilled" && memberResult.value && typeof memberResult.value === "object") {
    state.member = memberResult.value;
    state.memberLoadingState = "ready";
  } else {
    state.member = null;
    state.memberLoadingState = "error";
    state.memberErrorMessage = "成员资料暂时不可用。";
    console.error("[archive] member init failed:", memberResult.status === "rejected" ? memberResult.reason : memberResult.value);
  }
  renderMemberPanel();

  if (postsResult.status === "fulfilled" && Array.isArray(postsResult.value)) {
    state.posts = [...postsResult.value].sort((a, b) => new Date(b.date) - new Date(a.date));
    state.loadingState = "ready";

    renderTagOptions(state.posts);

    const hadHash = window.location.hash !== "";
    applyFilter({
      preferHash: true,
      forceHashSync: hadHash,
    });
    return;
  }

  state.loadingState = "error";
  state.errorMessage = "数据加载失败，请稍后重试。";
  state.posts = [];
  state.filteredPosts = [];
  state.activeId = null;

  renderList();
  renderStatus();
  renderDetail();

  console.error("[archive] posts init failed:", postsResult.status === "rejected" ? postsResult.reason : postsResult.value);
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
