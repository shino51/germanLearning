chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ enabled: true });
  chrome.action.setIcon({
    path: {
      16: "icons/icon_on_16.png",
      48: "icons/icon_on_48.png",
      128: "icons/icon_on_128.png"
    }
  });
});

// background.js

chrome.action.onClicked.addListener(async () => {
  const { enabled } = await chrome.storage.local.get("enabled");
  const newState = !enabled;
  await chrome.storage.local.set({ enabled: newState });

  chrome.action.setIcon({
    path: {
      16: newState ? "icons/icon_on_16.png" : "icons/icon_off_16.png",
      48: newState ? "icons/icon_on_48.png" : "icons/icon_off_48.png",
      128: newState ? "icons/icon_on_128.png" : "icons/icon_off_128.png"
    }
  });

  chrome.action.setTitle({
    title: newState ? "Dictionary Search: ON" : "Dictionary Search: OFF"
  });

  console.log("Toggled icon to", newState ? "ON" : "OFF");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "getEnabled") {
    chrome.storage.local.get("enabled").then((result) => {
      sendResponse({ enabled: result.enabled });
    });
    return true; // 👈 非同期で sendResponse を使う場合、true を返す
  }
});
