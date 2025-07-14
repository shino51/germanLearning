let selectedText = "";

// 辞書別URL関数
const dictionaryURLs = {
  leo: (query) => `https://dict.leo.org/german-english/${query}`,
  dwds: (query) => `https://www.dwds.de/wb/${query}`,
  wadoku: (query) => `https://www.wadoku.de/search/${query}`
};

async function isEnabled() {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type: "getEnabled" }, (response) => {
      resolve(response.enabled);
    });
  });
}


// テキスト選択取得
document.addEventListener("mouseup", () => {
  const selection = window.getSelection().toString().trim();
  if (selection.length > 0) {
    selectedText = selection;
  }
});

// Control + L/D/W で辞書検索
document.addEventListener("keydown", async (event) => {
  if (!await isEnabled() || !selectedText) return;
  if (event.ctrlKey) {
    const query = encodeURIComponent(selectedText);
    let url = null;

    switch (event.key.toLowerCase()) {
      case "l":
        url = dictionaryURLs.leo(query);
        break;
      case "d":
        url = dictionaryURLs.dwds(query);
        break;
      case "j":
        url = dictionaryURLs.wadoku(query);
        break;
    }

    if (url) {
      window.open(url, "_blank");
      selectedText = ""; // reset
    }
  }
});
