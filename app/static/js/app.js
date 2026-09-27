const requestText = document.getElementById("request_text");
const characterCount = document.getElementById("character-count");

if (requestText && characterCount) {

    const updateCharacterCount = () => {
        characterCount.textContent =
            `${requestText.value.length} / 1000`;
    };

    requestText.addEventListener(
        "input",
        updateCharacterCount
    );

    updateCharacterCount();
}