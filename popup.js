chrome.storage.sync.get(['imageSrcPrefix', 'identifierName', 'identifierNumber'], ( {imageSrcPrefix, identifierName, identifierNumber} ) => {
    document.getElementById('imageSrcPrefix').value = imageSrcPrefix
    document.getElementById('identifierName').value = identifierName
    document.getElementById('identifierNumber').value = identifierNumber
});

document.getElementById('sendImageLinks').addEventListener('click', () => {
    // 아래처럼 sendMessage를 하면 background.js의 이벤트 핸들러에서 수신한다.
    // chrome.runtime.sendMessage({ action: "TEST_ACTION" });

    const imageSrcPrefix = document.getElementById('imageSrcPrefix').value
    const identifierName = document.getElementById('identifierName').value
    const identifierNumber = document.getElementById('identifierNumber').value

    // 현재 window에 대해 sendMessage를 전송한다.
    // contentscript.js에서 이 메시지를 받게 된다.
    chrome.tabs.query({active: true, currentWindow: true}, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {
            action: "AGGREGATE",
            imageSrcPrefix: imageSrcPrefix,
            identifierName: identifierName,
            identifierNumber: identifierNumber
        }, /* callback */);
    });
});
