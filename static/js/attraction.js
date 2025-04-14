import { checkAuthStatus } from "/static/js/auth.js";
const apiURL = "";
const tourPrice = document.querySelector(".tour-price");
const radioInput = document.querySelectorAll('input[name="tour-time"]');
const slideContainer = document.querySelector(".slide-container");
const orderButton = document.querySelector(".order-button");
const signinButton = document.querySelector(".sign-in-button");
const tourOrderForm = document.querySelector(".tour-order-form");
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
const year = tomorrow.getFullYear();
const month = String(tomorrow.getMonth() + 1).padStart(2, "0");
const day = String(tomorrow.getDate()).padStart(2, "0");
const formattedDate = `${year}-${month}-${day}`;
document.querySelector("#tour-date").min = formattedDate;

const getAttractionId = () => {
  try {
    const id = new URL(window.location.href).pathname.split("/").pop();
    return Number(id);
  } catch (error) {
    console.error("無法獲取景點 ID", error);
    return null;
  }
};

const fetchAttractionDataById = async (attractionId) => {
  try {
    const response = await fetch(`${apiURL}/api/attraction/${attractionId}`);
    if (!response.ok) {
      throw new Error(`API 無回應：${response.status}`);
    }
    const data = await response.json();
    const attraction = data["data"];
    addAttraction(attraction);
  } catch (error) {
    console.error("無法取得景點資料", error.message);
  }
};

const attractionId = getAttractionId();
if (attractionId) {
  fetchAttractionDataById(attractionId);
}

const addAttraction = (attraction) => {
  const name = document.createElement("h2");
  name.textContent = attraction["name"];
  const detail = document.createElement("p");
  const category = attraction["category"];
  const mrt = attraction["mrt"];
  detail.textContent = `${category} at ${mrt}`;
  const orderContainer = document.querySelector(".order-container");
  const form = orderContainer.querySelector("form");
  orderContainer.insertBefore(name, form);
  orderContainer.insertBefore(detail, form);
  const description = document.createElement("p");
  description.textContent = attraction["description"];
  const descriptionContainer = document.querySelector(".description-container");
  descriptionContainer.appendChild(description);
  const address = document.createElement("p");
  address.textContent = attraction["address"];
  const addressContainer = document.querySelector(".address-container");
  addressContainer.appendChild(address);
  const transport = document.createElement("p");
  transport.textContent = attraction["transport"];
  const transportContainer = document.querySelector(".transport-container");
  transportContainer.appendChild(transport);
  if (attraction["images"] && attraction["images"].length > 0) {
    setupSlideshow(attraction["images"]);
  } else {
    slideContainer.innerHTML = "";
    slideContainer.textContent = "無圖片可顯示";
  }
};

const setupSlideshow = (images) => {
  const dotsContainer = document.querySelector(".dots");
  images.forEach((imageURL, index) => {
    const img = document.createElement("img");
    img.src = imageURL;
    img.alt = `Attraction Image ${index + 1}`;
    img.classList.add("slide-img");
    if (index === 0) {
      img.classList.add("active");
    }
    slideContainer.appendChild(img);
    const dot = document.createElement("span");
    dot.classList.add("dot");
    if (index === 0) dot.classList.add("active");
    dotsContainer.appendChild(dot);
  });
  let currentIndex = 0;
  const slides = slideContainer.querySelectorAll(".slide-img");
  const dots = dotsContainer.querySelectorAll(".dot");
  const handleSlideChange = (index) => {
    if (index >= slides.length) {
      index = 0;
    } else if (index < 0) {
      index = slides.length - 1;
    }
    slides[currentIndex].classList.remove("active");
    dots[currentIndex].classList.remove("active");
    slides[index].classList.add("active");
    dots[index].classList.add("active");
    currentIndex = index;
  };
  document.querySelector(".slide-left-button").addEventListener("click", () => {
    handleSlideChange(currentIndex - 1);
  });

  document
    .querySelector(".slide-right-button")
    .addEventListener("click", () => {
      handleSlideChange(currentIndex + 1);
    });
};

const updatePrice = () => {
  const tourTime = document.querySelector(
    'input[name="tour-time"]:checked'
  ).value;
  tourPrice.textContent =
    tourTime === "morning" ? "新台幣 2000元" : "新台幣 2500元";
};

radioInput.forEach((radio) => {
  radio.addEventListener("change", updatePrice);
});

const bookTrip = async () => {
  const token = localStorage.getItem("TOKEN");
  if (!token) {
    return;
  }
  const date = document.querySelector("#tour-date").value;
  const time = document.querySelector("input[name='tour-time']:checked").value;
  const body = { attraction_id: attractionId, date: date, time: time };
  try {
    const response = await fetch(`${apiURL}/api/booking`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`伺服器錯誤: ${response.status}`);
    }
    const result = await response.json();
    if (result.ok) {
      window.location.href = "/booking";
    } else {
      console.error("預訂失敗", result.message);
    }
  } catch (error) {
    console.error("預訂失敗", error.message);
  }
};

orderButton.addEventListener("click", async () => {
  const isAuthenticated = await checkAuthStatus();
  if (isAuthenticated) {
    window.location.href = "/booking";
  } else {
    signinButton.click();
  }
});

tourOrderForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const isAuthenticated = await checkAuthStatus();
  if (isAuthenticated) {
    await bookTrip();
  } else {
    signinButton.click();
  }
});

document.addEventListener("DOMContentLoaded", () => {
  updatePrice();
  checkAuthStatus();
});
