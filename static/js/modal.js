const apiURL = "";

export const setupModal = async (modalUrl, container) => {
  const response = await fetch(modalUrl);
  if (!response.ok) {
    throw new Error(`頁面載入出現錯誤：${response.status}`);
  }
  const html = await response.text();
  const parse = new DOMParser();
  const doc = parse.parseFromString(html, "text/html");
  const modal = doc.querySelector("dialog");
  container.replaceChildren(modal);
  modal.showModal();

  const closeButton = modal.querySelector(".close-modal-button");
  closeButton.addEventListener("click", () => {
    modal.close();
  });

  modal.addEventListener("pointerdown", (e) => {
    if (e.target === modal) {
      modal.close();
    }
  });

  const toggleButtons = modal.querySelectorAll(".form-toggle-button");
  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const signinForm = modal.querySelector(".sign-in-form");
      const signupForm = modal.querySelector(".sign-up-form");
      const signinMessage = document.querySelector(".sign-in-message");
      const signupMessage = document.querySelector(".sign-up-message");
      signinForm.classList.toggle("hidden");
      signupForm.classList.toggle("hidden");
      signinForm.reset();
      signupForm.reset();
      signinMessage.textContent = "";
      signupMessage.textContent = "";
    });
  });

  const signinForm = modal.querySelector(".sign-in-form");
  signinForm.addEventListener("submit", (e) => {
    e.preventDefault();
    signin();
  });
  const signupForm = modal.querySelector(".sign-up-form");
  signupForm.addEventListener("submit", (e) => {
    e.preventDefault();
    signup();
  });

  return modal;
};

const signin = async (email, password) => {
  email = document.querySelector("#sign-in-email").value.trim();
  password = document.querySelector("#sign-in-password").value;
  const message = document.querySelector(".sign-in-message");
  try {
    const response = await fetch(`${apiURL}/api/user/auth`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });
    const result = await response.json();
    if (response.ok) {
      if (result.token) {
        localStorage.setItem("TOKEN", result.token);
        window.location.reload();
      } else {
        message.textContent = "登入失敗，請重新登入";
      }
    } else {
      message.textContent = result.message || `登入失敗，無效的帳號或密碼`;
    }
  } catch (error) {
    message.textContent = "系統發生錯誤，請稍後再試";
  }
};

const signup = async (name, email, password) => {
  name = document.querySelector("#sign-up-name").value.trim();
  email = document.querySelector("#sign-up-email").value.trim();
  password = document.querySelector("#sign-up-password").value;
  const message = document.querySelector(".sign-up-message");
  message.textContent = "";
  message.style.color = "#ea5504";
  if (password.length < 6) {
    message.textContent = "密碼長度必須至少為6個字符";
    return;
  }
  try {
    const response = await fetch(`${apiURL}/api/user`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, email, password }),
    });
    const result = await response.json();
    if (result.ok) {
      message.textContent = "註冊成功";
      message.style.color = "#009D76";
    } else {
      message.textContent = result.message || "註冊失敗，請確認資料格式";
    }
  } catch (error) {
    message.textContent = "系統發生錯誤，請稍後再試";
  }
};
