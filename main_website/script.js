
    // JavaScript for smooth card transitions
    document.addEventListener("DOMContentLoaded", () => {
        const cards = document.querySelectorAll(".card-content");
        const nextBtn = document.getElementById("next-btn");
        let currentIndex = 0;

        nextBtn.addEventListener("click", () => {
            // Hide the current card with fade-out and slide-down effect
            const currentCard = cards[currentIndex];
            currentCard.classList.remove("z-10");
            currentCard.classList.add("opacity-0", "translate-y-full", "z-0");

            // Move to the next card
            currentIndex = (currentIndex + 1) % cards.length;

            // Show the next card with fade-in and slide-up effect
            const nextCard = cards[currentIndex];
            nextCard.classList.remove("opacity-0", "translate-y-full", "z-0");
            nextCard.classList.add("opacity-100", "translate-y-0", "z-10");
        });
    });

