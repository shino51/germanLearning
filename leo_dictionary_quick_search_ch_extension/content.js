let selectedText = "";

document.addEventListener("mouseup", () => {
  const selection = window.getSelection().toString().trim();
  if (selection.length > 0) {
    selectedText = selection;
  }
});

document.addEventListener("keydown", (event) => {
  // ここでは Shift キーをトリガーにしています（必要なら変更可能）
  if (event.key === "Shift" && selectedText) {
    const query = encodeURIComponent(selectedText);
    const leoURL = `https://dict.leo.org/german-english/${query}`;
    window.open(leoURL, "_blank");
    selectedText = ""; // 二重起動防止
  }
});
