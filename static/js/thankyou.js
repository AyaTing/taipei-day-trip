import { checkAuthStatus } from "/static/js/auth.js";
const orderButton = document.querySelector(".order-button");
const signinButton = document.querySelector(".sign-in-button");
const triggers = document.querySelectorAll(".accordion-header");
const apiURL = "";

const accordionToggle = (e) => {
  const content = e.currentTarget.nextElementSibling;
  const icon = e.currentTarget.querySelector(".accordion-icon");
  content.classList.toggle("active");
  icon.textContent = content.classList.contains("active") ? "-" : "+";
};
triggers.forEach((trigger) =>
  trigger.addEventListener("click", accordionToggle)
);

const getOrder = async (orderNumber) => {
  const token = localStorage.getItem("TOKEN");
  if (!token) {
    return;
  }
  try {
    const response = await fetch(`${apiURL}/api/order/${orderNumber}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error(`伺服器錯誤: ${response.status}`);
    }
    const result = await response.json();
    if (!result || !result.data) {
      alert("訂單讀取發生錯誤，請重試");
      console.error("資料讀取發生錯誤:", result);
    } else {
      displayOrder(result.data);
    }
  } catch (error) {
    alert("訂單讀取發生錯誤，請重試");
    console.error("資料讀取發生錯誤:", error);
  }
};

const displayOrder = (order) => {
  const orderDetail = document.querySelector(".order-detail");
  const ul = document.createElement("ul");
  const time =
    order.trip.time === "morning" ? "早上九點到下午四點" : "下午2點到晚上9點";
  const status = order.status === "PAID" ? "已付款" : "尚未付款";

  const orderData = [
    { 台北一日遊: order.trip.attraction["name"] },
    { 日期: order.trip.date },
    { 時間: time },
    { 費用: `新台幣 ${order.price} 元` },
    { 地點: order.trip.attraction["address"] },
    { 付款狀態: status },
    { 聯絡姓名: order.contact["name"] },
    { 手機號碼: order.contact["phone"] },
  ];
  orderData.forEach((item) => {
    const key = Object.keys(item)[0];
    const li = document.createElement("li");
    li.textContent = `${key}： ${item[key]}`;
    ul.appendChild(li);
  });
  orderDetail.appendChild(ul);
};

orderButton.addEventListener("click", async () => {
  const isAuthenticated = await checkAuthStatus();
  if (isAuthenticated) {
    window.location.href = "/booking";
  } else {
    signinButton.click();
  }
});

document.addEventListener("DOMContentLoaded", async () => {
  const isAuthenticated = await checkAuthStatus();
  if (isAuthenticated) {
    const urlParams = new URLSearchParams(window.location.search);
    const orderNumber = urlParams.get("number");
    const orderNumberElement = document.querySelector(".order-number");
    if (orderNumber) {
      orderNumberElement.textContent = `訂單編號：${orderNumber}`;
      getOrder(orderNumber);
    } else {
      window.location.href = "/";
    }
  } else {
    window.location.href = "/";
  }
});
