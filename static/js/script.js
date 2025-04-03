import { checkAuthStatus } from "/static/js/auth.js";
const cardContainer = document.querySelector(".attraction-container");
const searchInput = document.querySelector(".search-input");
const apiURL = "";
let nextPage = 0;
let isLoading = false;
let currentKeyword = "";

const fetchMrtData = async () => {
  try {
    const response = await fetch(`${apiURL}/api/mrts`);
    if (!response.ok) {
      throw new Error(`API 無回應：${response.status}`);
    }
    const data = await response.json();
    const mrt = data["data"];
    addCarouseItems(mrt);
    bindCarouselEvents();
    setupCarousel();
  } catch (error) {
    console.error("無法取得捷運站資料", error.message);
  }
};
const fetchAttractionData = async (page, keyword = "") => {
  if (isLoading || nextPage === null) return;
  isLoading = true;
  try {
    const url = keyword
      ? `${apiURL}/api/attractions?page=${page}&keyword=${encodeURIComponent(
          keyword
        )}`
      : `${apiURL}/api/attractions?page=${page}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error("API 無回應");
    }
    const data = await response.json();
    const attractions = data["data"];
    if (page === 0) {
      cardContainer.innerHTML = "";
    }
    addCardItems(attractions);
    nextPage = data["nextPage"];
  } catch (error) {
    console.error("無法取得景點資料", error.message);
  } finally {
    isLoading = false;
  }
};

const addCarouseItems = (mrt) => {
  const carousel = document.querySelector(".carousel");
  const track = document.createElement("div");
  track.className = "carousel-track";
  mrt.forEach((station) => {
    const item = document.createElement("div");
    item.className = "carousel-item";
    const stationButton = document.createElement("button");
    stationButton.className = "station-button";
    stationButton.textContent = station;
    item.appendChild(stationButton);
    track.appendChild(item);
  });
  carousel.appendChild(track);
};

const bindCarouselEvents = () => {
  document.querySelector(".carousel-track").addEventListener("click", (e) => {
    const stationButton = e.target.closest(".station-button");
    if (stationButton) {
      selectStation(stationButton.textContent);
    }
  });
};
const setupCarousel = () => {
  const track = document.querySelector(".carousel-track");
  const leftButton = document.querySelector(".carousel-left-button");
  const rightButton = document.querySelector(".carousel-right-button");
  const itemWidth = track.querySelector(".carousel-item").offsetWidth;
  const visibleItems = 2;
  const scrollDistance = itemWidth * visibleItems;
  const totalWidth = track.scrollWidth;
  const visibleWidth = track.offsetWidth;
  let scrollPosition = 0;
  const handleScroll = (distance) => {
    scrollPosition += distance;
    if (scrollPosition < 0) {
      scrollPosition = 0;
    } else if (scrollPosition > totalWidth - visibleWidth) {
      scrollPosition = totalWidth - visibleWidth;
    }
    track.scrollTo({ left: scrollPosition, behavior: "smooth" });
  };
  leftButton.addEventListener("click", () => handleScroll(-scrollDistance));
  rightButton.addEventListener("click", () => handleScroll(scrollDistance));
};

const addCardItems = (attractions) => {
  if (attractions.length === 0 && nextPage === 0) {
    cardContainer.textContent = "無符合搜尋結果";
    return;
  }
  attractions.forEach((attraction) => {
    const card = document.createElement("figure");
    card.className = "attraction-card";
    card.addEventListener("click", () => {
      window.location.href = `/attraction/${attraction["id"]}`;
    });
    const cardImage = document.createElement("img");
    cardImage.className = "attraction-image";
    cardImage.src = attraction["images"][0];
    cardImage.loading = "lazy";
    const cardContent = document.createElement("figcaption");
    cardContent.className = "attraction-card-content";
    const cardName = document.createElement("div");
    cardName.className = "attraction-name";
    cardName.textContent = attraction["name"];
    const details = document.createElement("div");
    details.className = "details-container";
    const metro = document.createElement("div");
    metro.className = "metro";
    metro.textContent = attraction["mrt"] || "無";
    const category = document.createElement("div");
    category.className = "category";
    category.textContent = attraction["category"];
    details.appendChild(metro);
    details.appendChild(category);
    cardContent.appendChild(cardName);
    cardContent.appendChild(details);
    card.appendChild(cardImage);
    card.appendChild(cardContent);
    cardContainer.appendChild(card);
  });
  observeLastCard();
};

const observer = new IntersectionObserver(
  (entries) => {
    const entry = entries[0];
    if (entry.isIntersecting && !isLoading && nextPage !== null) {
      fetchAttractionData(nextPage, currentKeyword);
    }
  },
  {
    threshold: 0.2,
  }
);

const observeLastCard = () => {
  observer.disconnect();
  const cards = document.querySelectorAll(".attraction-card");
  if (cards.length > 0) {
    const lastCard = cards[cards.length - 1];
    observer.observe(lastCard);
  }
};

const handleSearch = () => {
  const keyword = searchInput.value.trim();
  currentKeyword = keyword;
  nextPage = 0;
  fetchAttractionData(nextPage, currentKeyword);
};

const selectStation = (station) => {
  searchInput.value = station;
  currentKeyword = station;
  nextPage = 0;
  fetchAttractionData(nextPage, currentKeyword);
};

document.querySelector(".search-button").addEventListener("click", (e) => {
  e.preventDefault();
  handleSearch();
});

document.addEventListener("DOMContentLoaded", () => {
  fetchAttractionData(0);
  fetchMrtData();
  checkAuthStatus();
});
