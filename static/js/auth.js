import { setupModal } from "/static/js/modal.js";
const apiURL = "";

export const checkAuthStatus = async () => {
  const token = localStorage.getItem("TOKEN");
  if (!token) {
    resetUserStatus();
    return;
  }
  try {
    const response = await fetch(`${apiURL}/api/user/auth`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const result = await response.json();
    if (response.ok && result.data) {
      const signinButton = document.querySelector(".sign-in-button");
      signinButton.textContent = "登出系統";
      signinButton.dataset.action = "sign-out";
      signinButton.removeEventListener("click", setupModal);
      signinButton.addEventListener("click", signout);
      localStorage.setItem("USER", JSON.stringify(result.data));
      return true;
    } else {
      resetUserStatus();
      return false;
    }
  } catch (error) {
    console.error("檢查認證狀態失敗:", error);
    resetUserStatus();
    return false;
  }
};

const resetUserStatus = () => {
  const signinButton = document.querySelector(".sign-in-button");
  const modalContainer = document.querySelector(".modal-container");
  signinButton.textContent = "登入/註冊";
  signinButton.dataset.action = "sign-in";
  signinButton.removeEventListener("click", signout);
  signinButton.addEventListener("click", (e) => {
    e.preventDefault();
    setupModal("/static/modals/modal.html", modalContainer);
  });
};

const signout = () => {
  localStorage.removeItem("TOKEN");
  localStorage.removeItem("USER");
  window.location.reload();
};
