import { checkAuthStatus } from "/static/js/auth.js";
const orderButton = document.querySelector(".order-button");
const signinButton = document.querySelector(".sign-in-button");
const bookingContainer = document.querySelector(".booking_container");
const paymentForm = document.querySelector(".payment-form");
const apiURL = "";
const submitButton = document.querySelector(".payment-submit-button");
const cardNumberInput = document.querySelector("#card-number");
const expirationDateInput = document.querySelector("#card-expiration-date");
const ccvInput = document.querySelector("#card-ccv");

const fields = {
  number: {
    element: "#card-number",
    placeholder: "**** **** **** ****",
  },
  expirationDate: {
    element: "#card-expiration-date",
    placeholder: "MM / YY",
  },
  ccv: {
    element: "#card-ccv",
    placeholder: "CVV",
  },
};

TPDirect.card.setup({
  fields: fields,
  styles: {
    input: {
      "font-size": "16px",
    },
    ":focus": {
      color: "black",
      outline: "solid",
    },
    ".valid": {
      color: "black",
    },
    ".invalid": {
      color: "#ea5504",
    },
  },
  isMaskCreditCardNumber: true,
  maskCreditCardNumberRange: {
    beginIndex: 4,
    endIndex: 11,
  },
});

TPDirect.card.onUpdate((update) => {
  if (update.canGetPrime) {
    submitButton.removeAttribute("disabled");
  } else {
    submitButton.setAttribute("disabled", true);
  }
  if (update.status.number === 2) {
    cardNumberInput.classList.add("error");
  } else {
    cardNumberInput.classList.remove("error");
  }
  if (update.status.expiry === 2) {
    expirationDateInput.classList.add("error");
  } else {
    expirationDateInput.classList.remove("error");
  }
  if (update.status.ccv === 2) {
    ccvInput.classList.add("error");
  } else {
    ccvInput.classList.remove("error");
  }
});

const setupTapPay = async () => {
  const token = localStorage.getItem("TOKEN");
  try {
    const response = await fetch(`${apiURL}/api/payment/config`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const result = await response.json();
    if (response.ok && result) {
      TPDirect.setupSDK(result.appId, result.appKey, "sandbox");
    } else {
      alert("付款系統載入失敗，請重新整理：" + (result.message || "未知錯誤"));
    }
  } catch (error) {
    console.error("資料讀取發生錯誤:", error);
  }
};

const onSubmit = async () => {
  const paymentFormStatus = TPDirect.card.getTappayFieldsStatus();
  console.log("TapPay Status:", paymentFormStatus); // 測試用
  const name = document.querySelector("#name").value;
  const email = document.querySelector("#email").value;
  const phone = document.querySelector('input[name="phone"]').value;
  if (!name || !email || !phone) {
    alert("請填寫完整聯絡資訊");
    return;
  }
  if (paymentFormStatus.canGetPrime === false) {
    alert("信用卡資訊填寫不完全或有誤，請重新檢查");
    return;
  }
  submitButton.setAttribute("disabled", true);

  try {
    const primeResult = await new Promise((resolve) => {
      TPDirect.card.getPrime((result) => {
        resolve(result);
      });
    });

    if (primeResult.status !== 0) {
      alert("付款系統回應失敗，請重試" + primeResult.msg);
      submitButton.removeAttribute("disabled");
      return;
    }
    const prime = primeResult.card.prime;
    const orderData = {
      prime: prime,
      name: name,
      email: email,
      phone: phone,
    };

    const token = localStorage.getItem("TOKEN");
    const response = await fetch(`${apiURL}/api/orders`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(orderData),
    });
    console.log(response);

    const result = await response.json();

    if (response.ok && result.data) {
      window.location.href = `/thankyou?number=${result.data.number}`;
    } else {
      alert("訂單建立失敗：" + (result.message || "未知錯誤"));
      submitButton.removeAttribute("disabled");
    }
  } catch (error) {
    console.error(`訂單處理錯誤 ${error}`);
    alert("訂單處理發生錯誤，請稍後再試！");
    submitButton.removeAttribute("disabled");
  }
};

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
    await setupTapPay();
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
    console.log(response);
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

paymentForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const isAuthenticated = await checkAuthStatus();
  if (isAuthenticated) {
    await onSubmit();
  } else {
    signinButton.click();
  }
});

orderButton.addEventListener("click", async () => {
  const isAuthenticated = await checkAuthStatus();
  if (isAuthenticated) {
    window.location.href = "/booking";
  } else {
    signinButton.click();
  }
});
