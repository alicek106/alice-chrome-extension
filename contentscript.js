ENDPOINT_URL = "http://localhost:8000/"

// 이 스크립트는 현재 웹 페이지 안에서 실행된다.
// 따라서 웹 페이지의 dom에 접근할 수 있다.
chrome.runtime.onMessage.addListener(async function (request, sender, sendResponse) {
    if (request.action === 'AGGREGATE') {
        aggregateImages(request)
    } else {
        console.log('unknown action type: ' + request.action)
    }
});

const aggregateImages = (request) => {
    const imageLinks = []
    const prefix = request.imageSrcPrefix

    // 현재 dom에서 img 태그를 빼온 후, prefix와 일치하는 이미지를 aggregate한다.
    const imgTagElements = [...document.getElementsByTagName('img')]
    imgTagElements.forEach((item) => {
        if (item.src.startsWith(prefix)) {
            imageLinks.push(item.src)
        }
    })

    const data = {
        'imageLinks': imageLinks,
        'identifierName': request.identifierName,
        'identifierNumber': Number(request.identifierNumber)
    }
    console.log(data)

    fetch(ENDPOINT_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then((response) => response.json())
        .then((data) => {
            alert('Successfully sent ' + String(imageLinks.length) + ' images')
        })
        .catch((error) => {
            alert('Failed to send images with error: ' + error)
        });
}