const DEFAULT_MEMBER_SOURCE_URL = "https://sakurazaka46.com/s/s46/artist/62?ima=0000";
const LOCALE_STORAGE_KEY = "nagiblog_locale";
const SUPPORTED_LOCALES = ["zh-Hans", "zh-Hant", "en", "ja", "ko"];

const I18N = {
  "zh-Hans": {
    language: "语言",
    filter: "筛选",
    timeline: "时间线",
    tag: "标签",
    keyword: "关键词",
    keywordPlaceholder: "搜索标题或正文",
    all: "全部",
    loadingPosts: "正在加载文章...",
    loadError: "数据加载失败，请稍后重试。",
    noPosts: "暂无文章数据。",
    noMatches: "当前筛选条件下没有匹配文章。",
    postCount: "共 {count} 篇文章",
    noVisibleContent: "当前筛选条件下没有可展示内容。",
    viewSource: "查看原文",
    loadingMember: "正在加载成员资料...",
    memberLoadFailed: "成员资料暂时不可用。",
    memberProfileFail: "成员资料加载失败。",
    openOfficialPage: "成员官方页",
    greetingList: "问候列表",
    greeting: "问候",
    card: "卡片",
    photo: "照片",
  },
  "zh-Hant": {
    language: "語言",
    filter: "篩選",
    timeline: "時間線",
    tag: "標籤",
    keyword: "關鍵詞",
    keywordPlaceholder: "搜尋標題或正文",
    all: "全部",
    loadingPosts: "正在載入文章...",
    loadError: "資料載入失敗，請稍後重試。",
    noPosts: "暫無文章資料。",
    noMatches: "目前篩選條件下沒有匹配文章。",
    postCount: "共 {count} 篇文章",
    noVisibleContent: "目前篩選條件下沒有可展示內容。",
    viewSource: "檢視原文",
    loadingMember: "正在載入成員資料...",
    memberLoadFailed: "成員資料暫時不可用。",
    memberProfileFail: "成員資料載入失敗。",
    openOfficialPage: "成員官方頁",
    greetingList: "問候列表",
    greeting: "問候",
    card: "卡片",
    photo: "照片",
  },
  en: {
    language: "Language",
    filter: "Filters",
    timeline: "Timeline",
    tag: "Tag",
    keyword: "Keyword",
    keywordPlaceholder: "Search title or content",
    all: "All",
    loadingPosts: "Loading posts...",
    loadError: "Failed to load data. Please try again later.",
    noPosts: "No posts available.",
    noMatches: "No posts match the current filters.",
    postCount: "{count} posts",
    noVisibleContent: "No content available for the current filters.",
    viewSource: "View source",
    loadingMember: "Loading member profile...",
    memberLoadFailed: "Member profile is temporarily unavailable.",
    memberProfileFail: "Failed to load member profile.",
    openOfficialPage: "Official profile",
    greetingList: "Greeting list",
    greeting: "Greeting",
    card: "Card",
    photo: "Photo",
  },
  ja: {
    language: "言語",
    filter: "絞り込み",
    timeline: "タイムライン",
    tag: "タグ",
    keyword: "キーワード",
    keywordPlaceholder: "タイトルまたは本文を検索",
    all: "すべて",
    loadingPosts: "記事を読み込み中...",
    loadError: "データの読み込みに失敗しました。しばらくしてから再試行してください。",
    noPosts: "記事データがありません。",
    noMatches: "条件に一致する記事がありません。",
    postCount: "{count}件の記事",
    noVisibleContent: "現在の条件で表示できる内容がありません。",
    viewSource: "原文を見る",
    loadingMember: "メンバー情報を読み込み中...",
    memberLoadFailed: "メンバー情報を取得できませんでした。",
    memberProfileFail: "メンバー情報の読み込みに失敗しました。",
    openOfficialPage: "公式メンバーページ",
    greetingList: "グリーティング一覧",
    greeting: "グリーティング",
    card: "カード",
    photo: "写真",
  },
  ko: {
    language: "언어",
    filter: "필터",
    timeline: "타임라인",
    tag: "태그",
    keyword: "키워드",
    keywordPlaceholder: "제목 또는 본문 검색",
    all: "전체",
    loadingPosts: "게시글을 불러오는 중...",
    loadError: "데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.",
    noPosts: "게시글 데이터가 없습니다.",
    noMatches: "현재 조건에 맞는 게시글이 없습니다.",
    postCount: "게시글 {count}개",
    noVisibleContent: "현재 조건에서 표시할 내용이 없습니다.",
    viewSource: "원문 보기",
    loadingMember: "멤버 정보를 불러오는 중...",
    memberLoadFailed: "멤버 정보를 일시적으로 불러올 수 없습니다.",
    memberProfileFail: "멤버 정보 로드에 실패했습니다.",
    openOfficialPage: "멤버 공식 페이지",
    greetingList: "그리팅 목록",
    greeting: "그리팅",
    card: "카드",
    photo: "사진",
  },
};

function isSupportedLocaleKey(localeKey) {
  return SUPPORTED_LOCALES.includes(localeKey);
}

function normalizeLocale(rawLocale) {
  if (!rawLocale || typeof rawLocale !== "string") return null;

  const locale = rawLocale.toLowerCase();
  if (locale.startsWith("zh")) {
    if (
      locale.includes("hant") ||
      locale.includes("-tw") ||
      locale.includes("-hk") ||
      locale.includes("-mo")
    ) {
      return "zh-Hant";
    }
    return "zh-Hans";
  }

  if (locale.startsWith("ja")) return "ja";
  if (locale.startsWith("ko")) return "ko";
  if (locale.startsWith("en")) return "en";

  return null;
}

function detectLocaleKey() {
  const candidates = Array.isArray(navigator.languages) && navigator.languages.length
    ? navigator.languages
    : [navigator.language || ""];

  for (const candidate of candidates) {
    const normalized = normalizeLocale(candidate);
    if (normalized && isSupportedLocaleKey(normalized)) return normalized;
  }

  return "zh-Hans";
}

function getStoredLocaleKey() {
  try {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
    if (isSupportedLocaleKey(stored)) {
      return stored;
    }
  } catch {
    // ignore storage failures
  }
  return null;
}

function getInitialLocaleKey() {
  return getStoredLocaleKey() || detectLocaleKey();
}

function persistLocaleKey(localeKey) {
  try {
    localStorage.setItem(LOCALE_STORAGE_KEY, localeKey);
  } catch {
    // ignore storage failures
  }
}

function htmlLangFromLocale(localeKey) {
  if (localeKey === "zh-Hant") return "zh-Hant";
  if (localeKey === "zh-Hans") return "zh-CN";
  return localeKey;
}

const state = {
  localeKey: getInitialLocaleKey(),
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

function t(key, variables = {}) {
  const table = I18N[state.localeKey] || I18N.en;
  const fallback = I18N.en[key] || key;
  const raw = table[key] || fallback;

  return raw.replace(/\{(\w+)\}/g, (_, name) => String(variables[name] ?? ""));
}

const postListEl = document.getElementById("post-list");
const postDetailEl = document.getElementById("post-detail");
const tagSelectEl = document.getElementById("tag-select");
const keywordInputEl = document.getElementById("keyword-input");
const listStatusEl = document.getElementById("list-status");
const memberPanelEl = document.getElementById("member-panel");
const filterTitleEl = document.getElementById("filter-title");
const timelineTitleEl = document.getElementById("timeline-title");
const tagLabelEl = document.getElementById("tag-label");
const keywordLabelEl = document.getElementById("keyword-label");
const languageLabelEl = document.getElementById("language-label");
const languageSwitchEl = document.getElementById("language-switch");

function applyStaticI18n() {
  document.documentElement.lang = htmlLangFromLocale(state.localeKey);

  if (filterTitleEl) filterTitleEl.textContent = t("filter");
  if (timelineTitleEl) timelineTitleEl.textContent = t("timeline");
  if (tagLabelEl) tagLabelEl.textContent = t("tag");
  if (keywordLabelEl) keywordLabelEl.textContent = t("keyword");
  if (keywordInputEl) keywordInputEl.placeholder = t("keywordPlaceholder");
  if (languageLabelEl) languageLabelEl.textContent = t("language");
}

function renderLanguageSwitcher() {
  if (!languageSwitchEl) return;

  const buttons = languageSwitchEl.querySelectorAll("button[data-locale]");
  buttons.forEach((button) => {
    const locale = button.getAttribute("data-locale");
    const isActive = locale === state.localeKey;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-pressed", isActive ? "true" : "false");
  });
}

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
  tagSelectEl.innerHTML = "";

  const allOption = document.createElement("option");
  allOption.value = "all";
  allOption.textContent = t("all");
  tagSelectEl.appendChild(allOption);

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

  if (!Array.from(tagSelectEl.options).some((option) => option.value === state.activeTag)) {
    state.activeTag = "all";
  }

  tagSelectEl.value = state.activeTag;
}

function renderStatus() {
  listStatusEl.className = "status-message";

  if (state.loadingState === "loading") {
    listStatusEl.classList.add("info");
    listStatusEl.textContent = t("loadingPosts");
    return;
  }

  if (state.loadingState === "error") {
    listStatusEl.classList.add("error");
    listStatusEl.textContent = state.errorMessage || t("loadError");
    return;
  }

  if (state.posts.length === 0) {
    listStatusEl.classList.add("info");
    listStatusEl.textContent = t("noPosts");
    return;
  }

  if (state.filteredPosts.length === 0) {
    listStatusEl.classList.add("info");
    listStatusEl.textContent = t("noMatches");
    return;
  }

  listStatusEl.classList.add("info");
  listStatusEl.textContent = t("postCount", { count: state.filteredPosts.length });
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
    postDetailEl.innerHTML = `<p class="empty">${t("loadingPosts")}</p>`;
    return;
  }

  if (state.loadingState === "error") {
    postDetailEl.innerHTML = `<p class="empty error">${state.errorMessage || t("loadError")}</p>`;
    return;
  }

  const post = state.filteredPosts.find((item) => item.id === state.activeId);

  if (!post) {
    const emptyText = state.posts.length === 0 ? t("noPosts") : t("noVisibleContent");
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
  sourceLinkEl.textContent = t("viewSource");
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
    memberPanelEl.innerHTML = `<p class="empty">${t("loadingMember")}</p>`;
    return;
  }

  if (state.memberLoadingState === "error" || !state.member) {
    const errorEl = document.createElement("p");
    errorEl.className = "empty";
    errorEl.textContent = state.memberErrorMessage || t("memberProfileFail");

    const sourceWrapEl = document.createElement("p");
    sourceWrapEl.className = "member-source-link";
    const sourceLinkEl = document.createElement("a");
    sourceLinkEl.href = DEFAULT_MEMBER_SOURCE_URL;
    sourceLinkEl.target = "_blank";
    sourceLinkEl.rel = "noreferrer";
    sourceLinkEl.textContent = t("openOfficialPage");
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
    titleEl.textContent = t("greeting");
    greetingWrapEl.appendChild(titleEl);

    const gridEl = document.createElement("div");
    gridEl.className = "member-greeting-grid";

    if (typeof greetingCardSrc === "string" && greetingCardSrc.trim() !== "") {
      const cardFigure = document.createElement("figure");
      const cardImg = document.createElement("img");
      cardImg.src = greetingCardSrc;
      cardImg.alt = t("card");
      cardImg.loading = "lazy";
      const cardCaption = document.createElement("figcaption");
      cardCaption.textContent = t("card");
      cardFigure.append(cardImg, cardCaption);
      gridEl.appendChild(cardFigure);
    }

    if (typeof greetingPhotoSrc === "string" && greetingPhotoSrc.trim() !== "") {
      const photoFigure = document.createElement("figure");
      const photoImg = document.createElement("img");
      photoImg.src = greetingPhotoSrc;
      photoImg.alt = t("photo");
      photoImg.loading = "lazy";
      const photoCaption = document.createElement("figcaption");
      photoCaption.textContent = t("photo");
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
  profileLink.textContent = t("openOfficialPage");
  actionsEl.appendChild(profileLink);

  if (typeof member.greetingListUrl === "string" && member.greetingListUrl.trim() !== "") {
    const greetingListLink = document.createElement("a");
    greetingListLink.href = member.greetingListUrl;
    greetingListLink.target = "_blank";
    greetingListLink.rel = "noreferrer";
    greetingListLink.textContent = t("greetingList");
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

function setLocale(localeKey, { persist = true } = {}) {
  if (!isSupportedLocaleKey(localeKey)) return;

  if (state.localeKey === localeKey) {
    if (persist) persistLocaleKey(localeKey);
    renderLanguageSwitcher();
    return;
  }

  state.localeKey = localeKey;
  if (persist) persistLocaleKey(localeKey);

  applyStaticI18n();
  renderLanguageSwitcher();

  if (state.posts.length > 0) {
    renderTagOptions(state.posts);
  }

  renderStatus();
  renderDetail();
  renderMemberPanel();
}

function initializeLanguageSwitcher() {
  if (!languageSwitchEl) return;

  const buttons = languageSwitchEl.querySelectorAll("button[data-locale]");
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const locale = button.getAttribute("data-locale");
      if (!locale) return;
      setLocale(locale, { persist: true });
    });
  });
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} HTTP ${response.status}`);
  }
  return response.json();
}

async function init() {
  applyStaticI18n();
  initializeLanguageSwitcher();
  renderLanguageSwitcher();

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
    state.memberErrorMessage = t("memberLoadFailed");
    console.error(
      "[archive] member init failed:",
      memberResult.status === "rejected" ? memberResult.reason : memberResult.value,
    );
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
  state.errorMessage = t("loadError");
  state.posts = [];
  state.filteredPosts = [];
  state.activeId = null;

  renderList();
  renderStatus();
  renderDetail();

  console.error(
    "[archive] posts init failed:",
    postsResult.status === "rejected" ? postsResult.reason : postsResult.value,
  );
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
