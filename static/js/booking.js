import { checkAuthStatus } from "/static/js/auth.js";
const orderButton = document.querySelector(".order-button");
const signinButton = document.querySelector(".sign-in-button");
const bookingContainer = document.querySelector(".booking_container");
const paymentForm = document.querySelector(".payment-form");
const apiURL = "";

document.addEventListener("DOMContentLoaded", async () => {
  const isAuthenticated = await checkAuthStatus();
  if (isAuthenticated) {
    document.body.classList.remove("hidden");
    const user = JSON.parse(localStorage.getItem("USER"));
    const headline = document.querySelector(".headline");
    const name = document.querySelector("#name");
    const email = document.querySelector("#email");
    headline.textContent = `您好，${user["name"]}，待預定的行程如下：`;
    name.value = user["name"];
    email.value = user["email"];
    await get_booking();
  } else {
    window.location.href = "/";
    signinButton.click();
  }
});

const get_booking = async () => {
  const token = localStorage.getItem("TOKEN");
  if (!token) {
    return;
  }
  try {
    const response = await fetch(`${apiURL}/api/booking`, {
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
      const p = document.createElement("p");
      p.textContent = "目前沒有任何待預訂的行程";
      bookingContainer.appendChild(p);
      paymentForm.classList.add("hidden");
    } else {
      displayBooking(result.data);
    }
  } catch (error) {
    console.error("資料讀取發生錯誤:", error);
  }
};

const displayBooking = (booking) => {
  paymentForm.classList.remove("hidden");
  const figure = document.createElement("figure");
  const img = document.createElement("img");
  img.src = booking.attraction["image"];
  const figcaption = document.createElement("figcaption");
  const ul = document.createElement("ul");
  const time =
    booking.time === "morning" ? "早上九點到下午四點" : "下午2點到晚上9點";
  const bookingData = [
    { 台北一日遊: booking.attraction["name"] },
    { 日期: booking.date },
    { 時間: time },
    { 費用: `新台幣 ${booking.price} 元` },
    { 地點: booking.attraction["address"] },
  ];
  bookingData.forEach((item) => {
    const key = Object.keys(item)[0];
    const li = document.createElement("li");
    li.textContent = `${key}： ${item[key]}`;
    ul.appendChild(li);
  });
  figcaption.appendChild(ul);
  figure.appendChild(img);
  figure.appendChild(figcaption);
  const deleteButton = document.createElement("button");
  deleteButton.addEventListener("click", deleteBooking);
  bookingContainer.appendChild(figure);
  figure.appendChild(deleteButton);
  const total = document.querySelector(".total");
  total.textContent = `總價：新台幣 ${booking.price} 元`;
};

const deleteBooking = async () => {
  const token = localStorage.getItem("TOKEN");
  if (!token) {
    return;
  }
  try {
    const response = await fetch(`${apiURL}/api/booking`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const result = await response.json();
    if (response.ok && result.ok) {
      paymentForm.classList.add("hidden");
      window.location.href = "/booking";
    } else {
      alert("刪除失敗，請重試！");
    }
  } catch (error) {
    console.error("資料讀取發生錯誤:", error);
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
