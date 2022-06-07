'use strict';

// 이 핸들러는 플러그인 팝업 안에서 동작한다.
// 때문에 console.log 또한 현재 탭 페이지가 아닌, 플러그인 팝업 안에서 실행된다.
chrome.runtime.onMessage.addListener(async function (request, sender, sendResponse) {
    console.log(request.action)

    if (request.action === "TEST_ACTION") {
        console.log('received message for action TEST_ACTION')
        sendResponse({message: "OK"});
    }
});