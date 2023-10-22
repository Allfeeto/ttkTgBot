const buyButtons = document.querySelectorAll('.buy-button');
const quantityDivs = document.querySelectorAll('.quantity');
const countElements = document.querySelectorAll('.count');
const incrementButtons = document.querySelectorAll('.increment');
const decrementButtons = document.querySelectorAll('.decrement');

if ("vibrate" in navigator) {
    // Настройка вибрации (параметры: длительность вибрации, пауза, длительность вибрации и так далее)
    const vibrationPattern = [100, 50, 100]; // Пример: 0.1 секунда вибрации, 0.05 секунды паузы, затем 0.1 секунда вибрации

    // Найти кнопку, для которой вы хотите добавить виброотклик
    const button = document.querySelector(".buy-button");

    // Добавить обработчик события для клика по кнопке
    button.addEventListener("click", () => {
        // Запуск вибрации
        navigator.vibrate(vibrationPattern);
    });
} else {
    console.log("Вибрация не поддерживается в вашем браузере.");
}







buyButtons.forEach((buyButton, index) => {
    buyButton.addEventListener('click', () => {
        buyButton.style.display = 'none'; // Скрываем кнопку "Купить"
        quantityDivs[index].style.display = 'flex';
        countElements[index].style.display = 'block'; // Показываем кнопки "плюс" и "минус"
        let count = parseInt(countElements[index].textContent);
        count++;
        countElements[index].textContent = count;
    });
});



incrementButtons.forEach((incrementButton, index) => {
    incrementButton.addEventListener('click', () => {
        let count = parseInt(countElements[index].textContent);
        count++;
        countElements[index].textContent = count;
    });
});

decrementButtons.forEach((decrementButton, index) => {
    decrementButton.addEventListener('click', () => {
        let count = parseInt(countElements[index].textContent);
        if (count > 0) {
            count--;
            countElements[index].textContent = count;
        }
        
        if (count === 0) {
            quantityDivs[index].style.display = 'none'; // Скрываем кнопки "плюс" и "минус"
            countElements[index].style.display = 'none';
            buyButtons[index].style.display = 'block'; // Показываем кнопку "Купить" снова
        }
    });
});
